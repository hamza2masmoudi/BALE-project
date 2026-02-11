"""
BALE V10 Power Asymmetry Analyzer
Detects who benefits from each clause and measures party-level power imbalance.
Innovation: No existing tool quantifies power asymmetry at the clause level.
"""
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("bale_v10_power")


# ==================== OBLIGATION PATTERNS ====================

OBLIGATION_MARKERS = [
    r'\bshall\b', r'\bmust\b', r'\bwill\b', r'\bagrees?\s+to\b',
    r'\bundertakes?\s+to\b', r'\bwarrants?\b', r'\bguarantees?\b',
    r'\bis\s+obligated\b', r'\bis\s+required\b', r'\bis\s+responsible\b',
    r'\bcommits?\s+to\b', r'\bcovenants?\b',
]

OBLIGATION_MARKERS_FR = [
    r"\bs'engage\b", r"\bdoit\b", r"\bgarantit\b", r"\best\s+tenu\b",
    r"\best\s+responsable\b", r"\bs'oblige\b",
]

PROTECTION_MARKERS = [
    r'\bshall\s+not\s+be\s+liable\b', r'\bno\s+liability\b',
    r'\bexcludes?\s+liability\b', r'\bdisclaims?\b',
    r'\bholds?\s+harmless\b', r'\bindemnif\w+\b',
    r'\blimitation\s+of\s+liability\b', r'\bwithout\s+recourse\b',
    r'\bin\s+no\s+event\b', r'\bwaive\w*\b',
]

ONE_SIDED_TRIGGERS = [
    r'\bsolely\s+responsible\b', r'\bsolely\s+at\b',
    r'\bat\s+its\s+own\s+expense\b', r'\bentirely\s+at\b',
    r'\bsole\s+discretion\b', r'\bsole\s+and\s+absolute\b',
    r'\bwithout\s+limitation\b', r'\bregardless\s+of\s+fault\b',
    r'\birrespective\s+of\b', r'\bunconditionally\b',
    r'\bperpetual\b', r'\birrevocable\b',
    r'\bworldwide\b.*\blicense\b',
]


# ==================== DATA STRUCTURES ====================

@dataclass
class PartyProfile:
    """Profile of how a contract treats one party."""
    name: str
    obligation_count: int = 0
    protection_count: int = 0
    one_sided_burden_count: int = 0
    favorable_clauses: List[str] = field(default_factory=list)
    burdensome_clauses: List[str] = field(default_factory=list)

    @property
    def burden_score(self) -> float:
        """Higher = more burdened (0-100)."""
        if self.obligation_count + self.protection_count == 0:
            return 50.0
        ratio = self.obligation_count / (self.obligation_count + self.protection_count + 1)
        base = ratio * 70
        penalty = min(30, self.one_sided_burden_count * 10)
        return min(100, base + penalty)


@dataclass
class PowerAnalysis:
    """Complete power asymmetry analysis of a contract."""
    parties: List[PartyProfile]
    power_score: float
    dominant_party: str
    burdened_party: str
    asymmetric_clauses: List[Dict[str, Any]]
    total_obligations: int
    total_protections: int
    summary: str

    def to_dict(self) -> Dict:
        return {
            "power_score": round(self.power_score, 1),
            "dominant_party": self.dominant_party,
            "burdened_party": self.burdened_party,
            "asymmetric_clauses": self.asymmetric_clauses,
            "total_obligations": self.total_obligations,
            "total_protections": self.total_protections,
            "summary": self.summary,
            "parties": [
                {
                    "name": p.name,
                    "obligations": p.obligation_count,
                    "protections": p.protection_count,
                    "one_sided_burdens": p.one_sided_burden_count,
                    "burden_score": round(p.burden_score, 1),
                }
                for p in self.parties
            ],
        }


# ==================== ANALYZER ====================

class PowerAnalyzer:
    """
    Analyzes the power balance between parties in a contract.
    Looks at:
    1. Who has more obligations (shall, must, agrees to)
    2. Who gets more protections (not liable, disclaims, holds harmless)
    3. Which clauses are one-sided (solely responsible, sole discretion)
    """

    def __init__(self):
        self.obligation_re = re.compile(
            '|'.join(OBLIGATION_MARKERS + OBLIGATION_MARKERS_FR), re.IGNORECASE
        )
        self.protection_re = re.compile(
            '|'.join(PROTECTION_MARKERS), re.IGNORECASE
        )
        self.one_sided_re = re.compile(
            '|'.join(ONE_SIDED_TRIGGERS), re.IGNORECASE
        )

    def extract_parties(self, full_text: str) -> List[str]:
        """Extract party names from the contract text."""
        parties = []
        non_parties = {
            "agreement", "contract", "section", "article", "clause",
            "party", "parties", "herein", "hereof", "thereof",
            "date", "effective", "terms", "conditions",
        }
        patterns = [
            r'["\u201c](\w+(?:\s+\w+)?)["\u201d]\s*\)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, full_text[:3000], re.IGNORECASE)
            for match in matches:
                role = match.strip().strip('"').strip("'")
                if (role and len(role) < 30
                        and role.lower() not in non_parties
                        and role not in parties):
                    parties.append(role)

        if len(parties) < 2:
            common_roles = [
                "Provider", "Customer", "Supplier", "Buyer", "Seller",
                "Licensor", "Licensee", "Employer", "Employee",
                "Client", "Contractor", "Vendor", "Company",
                "Discloser", "Recipient", "Landlord", "Tenant",
                "Lender", "Borrower", "Franchisor", "Franchisee",
            ]
            for role in common_roles:
                if re.search(r'\b' + role + r'\b', full_text, re.IGNORECASE):
                    if role not in parties:
                        parties.append(role)
                    if len(parties) >= 2:
                        break

        if len(parties) < 2:
            parties = ["Party A", "Party B"]
        return parties[:2]

    def analyze(
        self,
        clauses: List[Dict[str, Any]],
        full_text: str = "",
    ) -> PowerAnalysis:
        """
        Analyze power asymmetry across all clauses.

        Args:
            clauses: List of classified clauses with 'text', 'clause_type', 'id'
            full_text: Full contract text for party extraction
        """
        parties = self.extract_parties(full_text)
        profiles = {p: PartyProfile(name=p) for p in parties}
        asymmetric = []
        total_obligations = 0
        total_protections = 0

        for clause in clauses:
            text = clause.get("text", "")
            clause_type = clause.get("clause_type", "unknown")

            obligations = len(self.obligation_re.findall(text))
            total_obligations += obligations

            protections = len(self.protection_re.findall(text))
            total_protections += protections

            one_sided_matches = self.one_sided_re.findall(text)

            p0_mentioned = bool(re.search(
                r'\b' + re.escape(parties[0]) + r'\b', text, re.IGNORECASE
            ))
            p1_mentioned = bool(re.search(
                r'\b' + re.escape(parties[1]) + r'\b', text, re.IGNORECASE
            ))

            if p0_mentioned and not p1_mentioned:
                profiles[parties[0]].obligation_count += obligations
                profiles[parties[1]].protection_count += protections
                if one_sided_matches:
                    profiles[parties[0]].one_sided_burden_count += 1
                    profiles[parties[0]].burdensome_clauses.append(clause_type)
                    profiles[parties[1]].favorable_clauses.append(clause_type)
            elif p1_mentioned and not p0_mentioned:
                profiles[parties[1]].obligation_count += obligations
                profiles[parties[0]].protection_count += protections
                if one_sided_matches:
                    profiles[parties[1]].one_sided_burden_count += 1
                    profiles[parties[1]].burdensome_clauses.append(clause_type)
                    profiles[parties[0]].favorable_clauses.append(clause_type)
            else:
                for p in parties:
                    profiles[p].obligation_count += obligations // 2
                    profiles[p].protection_count += protections // 2

            if one_sided_matches:
                asymmetric.append({
                    "clause_type": clause_type,
                    "clause_id": clause.get("id", "?"),
                    "triggers": [m for m in one_sided_matches[:3]],
                    "text_preview": text[:120] + "...",
                    "favors": parties[1] if p0_mentioned else parties[0],
                })

        party_list = list(profiles.values())
        if len(party_list) >= 2:
            burden_diff = abs(party_list[0].burden_score - party_list[1].burden_score)
            power_score = min(100, burden_diff + len(asymmetric) * 5)
            if party_list[0].burden_score > party_list[1].burden_score:
                burdened = party_list[0].name
                dominant = party_list[1].name
            else:
                burdened = party_list[1].name
                dominant = party_list[0].name
        else:
            power_score = 0
            dominant = "Unknown"
            burdened = "Unknown"

        if power_score < 20:
            summary = "Contract appears relatively balanced between parties."
        elif power_score < 50:
            summary = (
                f"Moderate power imbalance favoring {dominant}. "
                f"{len(asymmetric)} one-sided clauses detected."
            )
        else:
            summary = (
                f"Significant power imbalance. {dominant} holds dominant position "
                f"with {len(asymmetric)} asymmetric clauses. "
                f"{burdened} bears disproportionate obligations."
            )

        return PowerAnalysis(
            parties=party_list,
            power_score=power_score,
            dominant_party=dominant,
            burdened_party=burdened,
            asymmetric_clauses=asymmetric,
            total_obligations=total_obligations,
            total_protections=total_protections,
            summary=summary,
        )


__all__ = ["PowerAnalyzer", "PowerAnalysis", "PartyProfile"]
