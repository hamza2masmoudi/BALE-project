"""
BALE Multi-Jurisdiction System
Detects and routes analysis to appropriate legal system agents.
"""
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

from src.logger import setup_logger

logger = setup_logger("bale_jurisdiction")


class Jurisdiction(str, Enum):
    """Supported legal jurisdictions."""
    FRANCE = "FRANCE"
    UK = "UK"
    US = "US"
    GERMANY = "GERMANY"
    EU = "EU"
    SINGAPORE = "SINGAPORE"
    INTERNATIONAL = "INTERNATIONAL"


class LegalFamily(str, Enum):
    """Major legal families/traditions."""
    CIVIL_LAW = "CIVIL_LAW"        # France, Germany, most of EU
    COMMON_LAW = "COMMON_LAW"      # UK, US, Singapore
    MIXED = "MIXED"                # Cross-border, hybrid
    EU_LAW = "EU_LAW"              # European Union regulations


@dataclass
class JurisdictionProfile:
    """Profile of a legal jurisdiction."""
    code: Jurisdiction
    name: str
    legal_family: LegalFamily
    primary_language: str
    key_statutes: List[str]
    key_courts: List[str]
    choice_of_law_weight: float  # Priority in conflict resolution


# Jurisdiction profiles database
JURISDICTION_PROFILES: Dict[Jurisdiction, JurisdictionProfile] = {
    Jurisdiction.FRANCE: JurisdictionProfile(
        code=Jurisdiction.FRANCE,
        name="French Republic",
        legal_family=LegalFamily.CIVIL_LAW,
        primary_language="fr",
        key_statutes=["Code Civil", "Code de Commerce", "Code du Travail"],
        key_courts=["Cour de Cassation", "Conseil d'État", "Cour d'Appel"],
        choice_of_law_weight=0.85
    ),
    Jurisdiction.UK: JurisdictionProfile(
        code=Jurisdiction.UK,
        name="United Kingdom",
        legal_family=LegalFamily.COMMON_LAW,
        primary_language="en",
        key_statutes=["Sale of Goods Act 1979", "UCTA 1977", "Contracts Act 1999"],
        key_courts=["Supreme Court", "Court of Appeal", "High Court"],
        choice_of_law_weight=0.90
    ),
    Jurisdiction.US: JurisdictionProfile(
        code=Jurisdiction.US,
        name="United States",
        legal_family=LegalFamily.COMMON_LAW,
        primary_language="en",
        key_statutes=["UCC", "Restatement (Second) of Contracts", "Federal Arbitration Act"],
        key_courts=["US Supreme Court", "Circuit Courts", "Delaware Chancery"],
        choice_of_law_weight=0.88
    ),
    Jurisdiction.GERMANY: JurisdictionProfile(
        code=Jurisdiction.GERMANY,
        name="Federal Republic of Germany",
        legal_family=LegalFamily.CIVIL_LAW,
        primary_language="de",
        key_statutes=["BGB", "HGB", "AGB-Gesetz"],
        key_courts=["Bundesgerichtshof", "Oberlandesgericht", "Landgericht"],
        choice_of_law_weight=0.87
    ),
    Jurisdiction.EU: JurisdictionProfile(
        code=Jurisdiction.EU,
        name="European Union",
        legal_family=LegalFamily.EU_LAW,
        primary_language="en",
        key_statutes=["Rome I Regulation", "GDPR", "Consumer Rights Directive"],
        key_courts=["ECJ", "General Court"],
        choice_of_law_weight=0.95
    ),
    Jurisdiction.SINGAPORE: JurisdictionProfile(
        code=Jurisdiction.SINGAPORE,
        name="Republic of Singapore",
        legal_family=LegalFamily.COMMON_LAW,
        primary_language="en",
        key_statutes=["Contracts Act", "Sale of Goods Act", "PDPA"],
        key_courts=["Court of Appeal", "High Court", "SICC"],
        choice_of_law_weight=0.82
    ),
    Jurisdiction.INTERNATIONAL: JurisdictionProfile(
        code=Jurisdiction.INTERNATIONAL,
        name="International/Cross-Border",
        legal_family=LegalFamily.MIXED,
        primary_language="en",
        key_statutes=["CISG", "UNIDROIT Principles", "ICC Rules"],
        key_courts=["ICC Arbitration", "LCIA", "SIAC"],
        choice_of_law_weight=0.80
    ),
}


class JurisdictionDetector:
    """
    Detects applicable jurisdiction from contract text.
    Uses keyword matching, citation detection, and language analysis.
    """
    
    # Jurisdiction-specific keyword patterns
    KEYWORDS = {
        Jurisdiction.FRANCE: [
            r"\bcode civil\b", r"\barticle\s+\d+\s+cc\b", r"\bcour de cassation\b",
            r"\bbonne foi\b", r"\bforce majeure\b", r"\btribunal de commerce\b",
            r"\border public\b", r"\bloi française\b", r"\bfrench law\b"
        ],
        Jurisdiction.UK: [
            r"\benglish law\b", r"\blaw of england\b", r"\bcommon law\b",
            r"\bhigh court\b", r"\bucta\b", r"\bunfair contract terms\b",
            r"\blord\s+\w+\s+in\b", r"\b\[\d{4}\]\s+\w+\s+\d+\b"  # UK case citation
        ],
        Jurisdiction.US: [
            r"\bucc\b", r"\buniform commercial code\b", r"\bdelaware\b",
            r"\bstate of new york\b", r"\bus law\b", r"\bamerican law\b",
            r"\brestatement\b", r"\b\d+\s+f\.\d+d\s+\d+\b",  # Federal reporter
            r"\b\d+\s+u\.s\.\s+\d+\b"  # US Reports
        ],
        Jurisdiction.GERMANY: [
            r"\bbgb\b", r"\bhgb\b", r"\bgerman law\b", r"\bdeutsches recht\b",
            r"\bbundesgerichtshof\b", r"\brecht der bundesrepublik\b",
            r"\btreu und glauben\b", r"\bagb\b"
        ],
        Jurisdiction.EU: [
            r"\become i\b", r"\bgdpr\b", r"\beu law\b", r"\beuropean union\b",
            r"\becj\b", r"\bbrussels regulation\b", r"\beu directive\b",
            r"\bearticle\s+\d+\s+tfeu\b"
        ],
        Jurisdiction.SINGAPORE: [
            r"\bsingapore law\b", r"\bsicc\b", r"\bsiac\b",
            r"\bsingapore contracts act\b", r"\bsupreme court of singapore\b"
        ],
        Jurisdiction.INTERNATIONAL: [
            r"\bcisg\b", r"\bunidroit\b", r"\bincoterms\b",
            r"\bicc arbitration\b", r"\blcia\b", r"\binternational law\b",
            r"\bvienna convention\b"
        ]
    }
    
    # Choice of law clause patterns
    CHOICE_OF_LAW_PATTERNS = [
        r"governed\s+by\s+(?:the\s+)?(?:laws?\s+of\s+)?(\w+(?:\s+\w+)?)",
        r"subject\s+to\s+(?:the\s+)?(?:laws?\s+of\s+)?(\w+(?:\s+\w+)?)",
        r"(?:law|laws)\s+of\s+(\w+(?:\s+\w+)?)\s+(?:shall\s+)?(?:govern|apply)",
        r"this\s+agreement\s+(?:shall\s+be\s+)?(?:construed|interpreted)\s+(?:in\s+accordance\s+with|under)\s+(?:the\s+)?(?:laws?\s+of\s+)?(\w+(?:\s+\w+)?)"
    ]
    
    # Mapping from detected terms to jurisdictions
    JURISDICTION_ALIASES = {
        "france": Jurisdiction.FRANCE,
        "french": Jurisdiction.FRANCE,
        "england": Jurisdiction.UK,
        "english": Jurisdiction.UK,
        "united kingdom": Jurisdiction.UK,
        "uk": Jurisdiction.UK,
        "wales": Jurisdiction.UK,
        "united states": Jurisdiction.US,
        "us": Jurisdiction.US,
        "usa": Jurisdiction.US,
        "new york": Jurisdiction.US,
        "delaware": Jurisdiction.US,
        "california": Jurisdiction.US,
        "germany": Jurisdiction.GERMANY,
        "german": Jurisdiction.GERMANY,
        "bundesrepublik": Jurisdiction.GERMANY,
        "european union": Jurisdiction.EU,
        "eu": Jurisdiction.EU,
        "singapore": Jurisdiction.SINGAPORE,
    }
    
    def detect(self, text: str) -> Tuple[Jurisdiction, float, Dict[str, any]]:
        """
        Detect the most likely jurisdiction from contract text.
        
        Returns:
            (jurisdiction, confidence, metadata)
        """
        text_lower = text.lower()
        scores: Dict[Jurisdiction, float] = {j: 0.0 for j in Jurisdiction}
        matches: Dict[Jurisdiction, List[str]] = {j: [] for j in Jurisdiction}
        
        # 1. Check for explicit choice of law clause (highest priority)
        explicit_choice = self._detect_choice_of_law(text_lower)
        if explicit_choice:
            scores[explicit_choice] += 50.0
            matches[explicit_choice].append("EXPLICIT_CHOICE_OF_LAW")
        
        # 2. Keyword matching
        for jurisdiction, patterns in self.KEYWORDS.items():
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    scores[jurisdiction] += len(found) * 2.0
                    matches[jurisdiction].extend(found[:3])  # Keep first 3
        
        # 3. Citation analysis
        citation_scores = self._analyze_citations(text)
        for j, score in citation_scores.items():
            scores[j] += score
        
        # 4. Find winner
        if max(scores.values()) == 0:
            # No jurisdiction detected, default to international
            return (
                Jurisdiction.INTERNATIONAL, 
                0.5, 
                {"reason": "No explicit jurisdiction indicators found"}
            )
        
        winner = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = min(0.95, scores[winner] / max(total_score, 1) + 0.3)
        
        # Metadata for explainability
        metadata = {
            "detected": winner.value,
            "confidence": confidence,
            "scores": {j.value: round(s, 2) for j, s in scores.items() if s > 0},
            "evidence": matches[winner][:5],
            "explicit_choice": explicit_choice is not None
        }
        
        logger.info(f"Jurisdiction detected: {winner.value} (confidence: {confidence:.2f})")
        return (winner, confidence, metadata)
    
    def _detect_choice_of_law(self, text: str) -> Optional[Jurisdiction]:
        """Detect explicit choice of law clause."""
        for pattern in self.CHOICE_OF_LAW_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                jurisdiction_text = match.group(1).lower().strip()
                for alias, jurisdiction in self.JURISDICTION_ALIASES.items():
                    if alias in jurisdiction_text:
                        return jurisdiction
        return None
    
    def _analyze_citations(self, text: str) -> Dict[Jurisdiction, float]:
        """Analyze legal citations to infer jurisdiction."""
        scores: Dict[Jurisdiction, float] = {j: 0.0 for j in Jurisdiction}
        
        # UK case citations: [2020] UKSC 1, [2019] EWCA Civ 123
        uk_citations = re.findall(r'\[\d{4}\]\s+(?:UKSC|EWCA|EWHC|AC|QB|Ch)\s+\w+', text)
        scores[Jurisdiction.UK] += len(uk_citations) * 3.0
        
        # US case citations: 123 F.3d 456, 550 U.S. 123
        us_citations = re.findall(r'\d+\s+(?:F\.\d+d|U\.S\.|S\.Ct\.|L\.Ed)\s+\d+', text)
        scores[Jurisdiction.US] += len(us_citations) * 3.0
        
        # French citations: Cass. Com. 2020-1234
        fr_citations = re.findall(r'Cass\.\s*(?:Com|Civ|Soc)\.\s*\d+', text)
        scores[Jurisdiction.FRANCE] += len(fr_citations) * 3.0
        
        # German citations: BGH XII ZR 123/20
        de_citations = re.findall(r'BGH\s+[IVX]+\s+\w+\s+\d+/\d+', text)
        scores[Jurisdiction.GERMANY] += len(de_citations) * 3.0
        
        # EU citations: C-123/20
        eu_citations = re.findall(r'C-\d+/\d+', text)
        scores[Jurisdiction.EU] += len(eu_citations) * 3.0
        
        return scores
    
    def get_applicable_agents(self, jurisdiction: Jurisdiction) -> List[str]:
        """
        Returns list of agent types to invoke for a jurisdiction.
        """
        profile = JURISDICTION_PROFILES.get(jurisdiction)
        if not profile:
            return ["civilist", "commonist"]  # Default
        
        if profile.legal_family == LegalFamily.CIVIL_LAW:
            if jurisdiction == Jurisdiction.GERMANY:
                return ["germanist", "civilist"]
            return ["civilist", "commonist"]
        
        elif profile.legal_family == LegalFamily.COMMON_LAW:
            if jurisdiction == Jurisdiction.US:
                return ["us_commercial", "commonist"]
            return ["commonist", "civilist"]
        
        elif profile.legal_family == LegalFamily.EU_LAW:
            return ["eu_law", "civilist", "commonist"]
        
        else:  # MIXED / INTERNATIONAL
            return ["civilist", "commonist", "cross_border"]
    
    def get_conflict_rules(self, jurisdictions: List[Jurisdiction]) -> Dict[str, any]:
        """
        Determine conflict of law rules when multiple jurisdictions apply.
        """
        if len(jurisdictions) <= 1:
            return {"conflict": False}
        
        profiles = [JURISDICTION_PROFILES[j] for j in jurisdictions if j in JURISDICTION_PROFILES]
        families = set(p.legal_family for p in profiles)
        
        return {
            "conflict": len(families) > 1,
            "families": [f.value for f in families],
            "primary": max(profiles, key=lambda p: p.choice_of_law_weight).code.value,
            "applicable_rules": self._get_applicable_conflict_rules(families)
        }
    
    def _get_applicable_conflict_rules(self, families: set) -> List[str]:
        """Get relevant conflict of law rules."""
        rules = []
        if LegalFamily.CIVIL_LAW in families and LegalFamily.COMMON_LAW in families:
            rules.extend([
                "Rome I Regulation (if EU involved)",
                "Restatement (Second) Conflict of Laws (if US involved)",
                "Choice of law clause takes precedence"
            ])
        if LegalFamily.EU_LAW in families:
            rules.append("EU law primacy applies to Member State conflicts")
        return rules


# Singleton instance
detector = JurisdictionDetector()


def detect_jurisdiction(text: str) -> Tuple[Jurisdiction, float, Dict]:
    """Convenience function to detect jurisdiction."""
    return detector.detect(text)


def get_jurisdiction_profile(jurisdiction: Jurisdiction) -> Optional[JurisdictionProfile]:
    """Get profile for a jurisdiction."""
    return JURISDICTION_PROFILES.get(jurisdiction)
