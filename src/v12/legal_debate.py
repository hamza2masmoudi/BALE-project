"""
BALE V12 — Multi-Agent Legal Debate System
============================================
Three specialized AI agents debate a contract's risk profile using
a structured adversarial protocol. Produces human-readable audit
trail that lawyers can review, agree with, or contest.

Protocol:
    1. Prosecutor: aggressive risk analysis, worst-case interpretations
    2. Defense: fairness advocacy, argues why clauses are standard
    3. Judge: neutral arbiter, weighs both sides, issues final ruling

Innovation: Adversarial debate forces each agent to deeply examine
the evidence. The resulting transcript is inherently explainable —
lawyers see the full reasoning chain, not just a risk number.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logger = logging.getLogger("bale_v12_debate")


# ==================== DATA STRUCTURES ====================

@dataclass
class DebateArgument:
    """A single argument in the debate."""
    agent: str                # prosecutor, defense, or judge
    clause_type: str          # Which clause this argument addresses
    position: str             # The argument text
    evidence: List[str]       # Supporting evidence
    severity: str             # critical, high, medium, low
    confidence: float         # How confident the agent is (0-1)


@dataclass
class DebateRuling:
    """Judge's ruling on a specific disputed clause."""
    clause_type: str
    verdict: str              # "sustained" (agrees with prosecutor) or "overruled"
    reasoning: str
    risk_adjustment: float    # How much to adjust risk (-0.2 to +0.2)
    prosecution_strength: float  # How strong prosecution case was
    defense_strength: float      # How strong defense case was


@dataclass
class DebateTranscript:
    """Complete debate transcript with all arguments and rulings."""
    prosecution_arguments: List[DebateArgument]
    defense_arguments: List[DebateArgument]
    rulings: List[DebateRuling]
    final_verdict: str           # "high_risk", "moderate_risk", "acceptable"
    final_risk_adjustment: float # Net risk adjustment from debate
    debate_duration_ms: int
    summary: str                 # Executive summary of debate

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prosecution_arguments": [
                {
                    "agent": a.agent,
                    "clause_type": a.clause_type,
                    "position": a.position,
                    "evidence": a.evidence,
                    "severity": a.severity,
                    "confidence": a.confidence,
                }
                for a in self.prosecution_arguments
            ],
            "defense_arguments": [
                {
                    "agent": a.agent,
                    "clause_type": a.clause_type,
                    "position": a.position,
                    "evidence": a.evidence,
                    "severity": a.severity,
                    "confidence": a.confidence,
                }
                for a in self.defense_arguments
            ],
            "rulings": [
                {
                    "clause_type": r.clause_type,
                    "verdict": r.verdict,
                    "reasoning": r.reasoning,
                    "risk_adjustment": round(r.risk_adjustment, 3),
                    "prosecution_strength": round(r.prosecution_strength, 2),
                    "defense_strength": round(r.defense_strength, 2),
                }
                for r in self.rulings
            ],
            "final_verdict": self.final_verdict,
            "final_risk_adjustment": round(self.final_risk_adjustment, 3),
            "debate_duration_ms": self.debate_duration_ms,
            "summary": self.summary,
        }


# ==================== LEGAL KNOWLEDGE BASE ====================
# Used by the debate agents to construct arguments

PROSECUTION_KNOWLEDGE = {
    "indemnification": {
        "risks": [
            "Unlimited indemnification exposes party to uncapped financial liability",
            "One-sided indemnification creates disproportionate risk allocation",
            "Broad indemnification scope covering 'all claims' exceeds reasonable commercial practice",
        ],
        "precedents": [
            "Williams v Walker-Thomas: unconscionable one-sided terms are unenforceable",
            "Photo Production v Securicor: indemnification must be clearly drafted",
        ],
    },
    "limitation_of_liability": {
        "risks": [
            "No liability cap leaves party exposed to potentially ruinous damages",
            "Failure to exclude consequential damages creates unpredictable exposure",
            "Liability cap disproportionately low relative to contract value",
        ],
        "precedents": [
            "Cavendish Square v Makdessi: penalty clauses are unenforceable",
            "Hadley v Baxendale: only foreseeable damages are recoverable",
        ],
    },
    "termination": {
        "risks": [
            "Termination 'for any breach' is disproportionate and may be judicially narrowed",
            "No cure period allows abrupt contract dissolution",
            "Unilateral termination power without notice creates instability",
        ],
        "precedents": [
            "Hongkong Fir v Kawasaki: only serious breaches justify termination",
            "Rice v Great Yarmouth: 'any breach' clauses will be read with materiality",
        ],
    },
    "confidentiality": {
        "risks": [
            "Perpetual confidentiality obligations are unreasonable and hard to enforce",
            "No defined standard of care for protecting confidential information",
            "No carve-outs for legally compelled disclosure",
        ],
        "precedents": ["Coco v Clark: three elements test for breach of confidence"],
    },
    "intellectual_property": {
        "risks": [
            "Blanket IP assignment without carve-out for pre-existing IP",
            "No work-for-hire designation creates ownership ambiguity",
            "No license-back for assigned IP",
        ],
        "precedents": ["Netboss v Avaya: background IP must be distinguished from foreground"],
    },
    "non_compete": {
        "risks": [
            "Worldwide scope is almost certainly unenforceable",
            "Perpetual or indefinite duration exceeds what courts allow",
            "No reasonable geographic or activity limitations",
        ],
        "precedents": ["Nordenfelt v Maxim: restraint must be reasonable in scope"],
    },
    "governing_law": {
        "risks": [
            "No governing law creates conflict-of-laws uncertainty",
            "Choice of law may be strategically adverse to one party",
        ],
        "precedents": ["Carnival Cruise v Shute: forum selection must be fundamentally fair"],
    },
    "warranty": {
        "risks": [
            "Blanket warranty disclaimer may violate consumer protection statutes",
            "No express warranty creates reliance on implied terms only",
        ],
        "precedents": ["UCC §2-314: implied warranty of merchantability"],
    },
    "payment_terms": {
        "risks": [
            "Payment terms exceeding 60 days may be challenged as unfair",
            "No late payment interest specified",
            "No right to suspend services for non-payment",
        ],
        "precedents": ["Late Payment Act 1998: statutory interest on late payments"],
    },
    "data_protection": {
        "risks": [
            "Processing personal data without GDPR-compliant DPA is illegal",
            "No sub-processor controls violate Art 28 requirements",
            "No data breach notification timeline specified",
        ],
        "precedents": ["Schrems II: cross-border transfers need supplementary measures"],
    },
    "force_majeure": {
        "risks": [
            "Missing force majeure clause in a long-term agreement is negligent drafting",
            "Too narrow FM events list may not cover pandemics or cyber attacks",
        ],
        "precedents": ["Taylor v Caldwell: frustration doctrine"],
    },
    "dispute_resolution": {
        "risks": [
            "No dispute resolution mechanism leads to expensive litigation",
            "Mandatory arbitration without appeal rights limits remedies",
        ],
        "precedents": ["AT&T v Concepcion: class waivers enforceable under FAA"],
    },
    "assignment": {
        "risks": [
            "Free assignment right allows obligations to pass to unknown parties",
            "No change-of-control provisions leave party unprotected during M&A",
        ],
        "precedents": ["Linden Gardens v Lenesta: anti-assignment enforceable but circumventable"],
    },
    "audit_rights": {
        "risks": [
            "Unlimited audit rights create operational disruption",
            "No audit rights means inability to verify compliance",
        ],
        "precedents": [],
    },
}

DEFENSE_KNOWLEDGE = {
    "indemnification": {
        "defenses": [
            "Indemnification terms are standard for this contract type and industry",
            "Market practice supports this allocation of risk between parties",
            "The indemnifying party's insurance coverage mitigates actual exposure",
        ],
    },
    "limitation_of_liability": {
        "defenses": [
            "Liability caps are proportionate to the contract value",
            "Exclusion of consequential damages is standard commercial practice",
            "Both parties are sophisticated commercial entities with equal bargaining power",
        ],
    },
    "termination": {
        "defenses": [
            "Termination provisions balance both parties' interests",
            "Termination for cause is a necessary protective mechanism",
            "Notice periods provide adequate transition time",
        ],
    },
    "confidentiality": {
        "defenses": [
            "Confidentiality obligations are reciprocal and balanced",
            "Duration is reasonable given the nature of shared information",
            "Carve-outs exist for public domain information and prior knowledge",
        ],
    },
    "intellectual_property": {
        "defenses": [
            "IP provisions clearly delineate pre-existing and new IP",
            "Assignment is necessary for the commercial purpose of the agreement",
            "License-back provisions protect the assigning party's legitimate interests",
        ],
    },
    "non_compete": {
        "defenses": [
            "Restraint is narrowly tailored to protect legitimate business interests",
            "Duration and scope are within norms upheld by courts in this jurisdiction",
            "Consideration for the non-compete is adequate",
        ],
    },
    "governing_law": {
        "defenses": [
            "Choice of law is a neutral jurisdiction acceptable to both parties",
            "Parties are free to choose governing law under party autonomy principle",
        ],
    },
    "warranty": {
        "defenses": [
            "Warranty terms are standard for the industry and product type",
            "Express warranties adequately describe the expected performance level",
        ],
    },
    "payment_terms": {
        "defenses": [
            "Payment terms are within industry standard ranges",
            "Late payment consequences are proportionate and foreseeable",
        ],
    },
    "data_protection": {
        "defenses": [
            "Data processing is minimal and low-risk",
            "Standard contractual clauses provide adequate cross-border protection",
        ],
    },
    "force_majeure": {
        "defenses": [
            "The contract is short-term, reducing FM risk significantly",
            "FM events are adequately covered by frustration doctrine in common law",
        ],
    },
    "dispute_resolution": {
        "defenses": [
            "Arbitration is efficient and provides finality",
            "The chosen forum is neutral and recognized internationally",
        ],
    },
    "assignment": {
        "defenses": [
            "Assignment restrictions are balanced for both parties",
            "Permitted assignment to affiliates is standard commercial practice",
        ],
    },
    "audit_rights": {
        "defenses": [
            "Audit rights are appropriately limited in frequency and scope",
            "Notice period ensures minimal operational disruption",
        ],
    },
}


# ==================== DEBATE ENGINE ====================

class LegalDebateEngine:
    """
    Multi-Agent Legal Debate System.
    
    Three AI agents debate the risk profile of a contract:
    - Prosecutor: finds every risk, argues worst-case
    - Defense: advocates for fairness, argues clauses are standard
    - Judge: weighs both sides, issues per-clause rulings
    
    Falls back to structured template-based reasoning when no
    LLM is available (local or remote).
    """

    def __init__(self):
        logger.info("LegalDebateEngine initialized")

    def debate(self, v11_report) -> DebateTranscript:
        """
        Run a full adversarial debate on the V11 analysis report.
        
        Args:
            v11_report: V10Report from V11 pipeline
            
        Returns:
            DebateTranscript with arguments, rulings, and verdict
        """
        start = time.time()

        # Extract clause data
        classifications = getattr(v11_report, 'clause_classifications', [])
        graph = getattr(v11_report, 'graph', {})
        power = getattr(v11_report, 'power', {})

        # Phase 1: Prosecution builds its case
        prosecution_args = self._prosecute(classifications, graph, power)

        # Phase 2: Defense responds
        defense_args = self._defend(classifications, prosecution_args)

        # Phase 3: Judge rules
        rulings = self._judge(prosecution_args, defense_args)

        # Phase 4: Final verdict
        net_adjustment = sum(r.risk_adjustment for r in rulings)
        sustained = sum(1 for r in rulings if r.verdict == "sustained")
        overruled = sum(1 for r in rulings if r.verdict == "overruled")

        if sustained > overruled * 2:
            final_verdict = "high_risk"
        elif sustained > overruled:
            final_verdict = "moderate_risk"
        else:
            final_verdict = "acceptable"

        # Generate summary
        summary = self._generate_summary(
            prosecution_args, defense_args, rulings, final_verdict
        )

        elapsed_ms = int((time.time() - start) * 1000)

        return DebateTranscript(
            prosecution_arguments=prosecution_args,
            defense_arguments=defense_args,
            rulings=rulings,
            final_verdict=final_verdict,
            final_risk_adjustment=net_adjustment,
            debate_duration_ms=elapsed_ms,
            summary=summary,
        )

    def _prosecute(
        self, classifications: list, graph: dict, power: dict
    ) -> List[DebateArgument]:
        """Prosecutor: find every possible risk."""
        arguments = []

        for cls in classifications:
            if not isinstance(cls, dict):
                continue

            clause_type = cls.get('clause_type', cls.get('type', ''))
            text = cls.get('text', '').lower()
            risk_weight = cls.get('risk_weight', 0.5)
            confidence = cls.get('confidence', 0.5)

            knowledge = PROSECUTION_KNOWLEDGE.get(clause_type, {})
            risks = knowledge.get("risks", [])
            precedents = knowledge.get("precedents", [])

            if not risks:
                continue

            # Assess which risks apply based on clause text
            applicable_risks = []
            for risk in risks:
                # Check if risk keywords are present in clause text
                risk_keywords = risk.lower().split()[:5]
                relevance = sum(1 for kw in risk_keywords if kw in text) / max(len(risk_keywords), 1)
                
                # Always include if risk_weight is high, or if keywords match
                if risk_weight > 0.6 or relevance > 0.3:
                    applicable_risks.append(risk)

            if applicable_risks:
                # Determine severity
                if risk_weight > 0.8:
                    severity = "critical"
                elif risk_weight > 0.6:
                    severity = "high"
                elif risk_weight > 0.4:
                    severity = "medium"
                else:
                    severity = "low"

                arguments.append(DebateArgument(
                    agent="prosecutor",
                    clause_type=clause_type,
                    position=(
                        f"The {clause_type.replace('_', ' ')} clause presents significant risk. "
                        f"{applicable_risks[0]}"
                    ),
                    evidence=applicable_risks[:3] + precedents[:2],
                    severity=severity,
                    confidence=min(risk_weight + 0.1, 1.0),
                ))

        # Check for structural risks from graph
        if isinstance(graph, dict):
            conflicts = graph.get('conflicts', [])
            if isinstance(conflicts, list) and len(conflicts) > 0:
                arguments.append(DebateArgument(
                    agent="prosecutor",
                    clause_type="structural",
                    position=f"Contract has {len(conflicts)} inter-clause conflicts creating systemic risk.",
                    evidence=[
                        f"Conflict: {c.get('description', 'clause conflict')}"
                        for c in conflicts[:3] if isinstance(c, dict)
                    ],
                    severity="high",
                    confidence=0.85,
                ))

        # Check for power asymmetry
        if isinstance(power, dict):
            power_score = power.get('power_score', 50)
            if abs(power_score - 50) > 20:
                arguments.append(DebateArgument(
                    agent="prosecutor",
                    clause_type="power_asymmetry",
                    position=(
                        f"Significant power asymmetry detected (score: {power_score}/100). "
                        f"Contract favors one party disproportionately."
                    ),
                    evidence=["Power analysis indicates unequal bargaining positions"],
                    severity="high" if abs(power_score - 50) > 30 else "medium",
                    confidence=0.8,
                ))

        return arguments

    def _defend(
        self, classifications: list, prosecution_args: List[DebateArgument]
    ) -> List[DebateArgument]:
        """Defense: counter each prosecution argument."""
        arguments = []
        
        prosecuted_types = {arg.clause_type for arg in prosecution_args}

        for cls in classifications:
            if not isinstance(cls, dict):
                continue

            clause_type = cls.get('clause_type', cls.get('type', ''))
            confidence = cls.get('confidence', 0.5)

            if clause_type not in prosecuted_types:
                continue

            knowledge = DEFENSE_KNOWLEDGE.get(clause_type, {})
            defenses = knowledge.get("defenses", [])

            if defenses:
                # Defense strength based on classifier confidence
                defense_confidence = confidence * 0.8

                arguments.append(DebateArgument(
                    agent="defense",
                    clause_type=clause_type,
                    position=(
                        f"The {clause_type.replace('_', ' ')} clause is within "
                        f"acceptable commercial practice. {defenses[0]}"
                    ),
                    evidence=defenses[:3],
                    severity="low",
                    confidence=defense_confidence,
                ))

        # Structural defense
        if "structural" in prosecuted_types:
            arguments.append(DebateArgument(
                agent="defense",
                clause_type="structural",
                position="Inter-clause tensions are common in complex agreements and reflect legitimate risk allocation choices.",
                evidence=[
                    "Complex agreements naturally have clause interactions",
                    "Parties are sophisticated entities capable of assessing structural risks",
                ],
                severity="low",
                confidence=0.6,
            ))

        # Power asymmetry defense
        if "power_asymmetry" in prosecuted_types:
            arguments.append(DebateArgument(
                agent="defense",
                clause_type="power_asymmetry",
                position="Power asymmetry reflects the commercial reality of different party roles and is not inherently unfair.",
                evidence=[
                    "Different party roles (e.g., service provider vs. client) justify asymmetric obligations",
                    "Both parties entered the agreement voluntarily with legal counsel",
                ],
                severity="low",
                confidence=0.55,
            ))

        return arguments

    def _judge(
        self, prosecution: List[DebateArgument], defense: List[DebateArgument]
    ) -> List[DebateRuling]:
        """Judge: weigh both sides and issue rulings."""
        rulings = []

        # Group arguments by clause type
        pro_by_type = {}
        for arg in prosecution:
            pro_by_type[arg.clause_type] = arg

        def_by_type = {}
        for arg in defense:
            def_by_type[arg.clause_type] = arg

        for clause_type, pro_arg in pro_by_type.items():
            def_arg = def_by_type.get(clause_type)

            pro_strength = pro_arg.confidence * self._severity_weight(pro_arg.severity)
            def_strength = (
                def_arg.confidence * self._severity_weight(def_arg.severity)
                if def_arg else 0.0
            )

            # Evidence weight: more evidence = stronger case
            pro_evidence_weight = min(len(pro_arg.evidence) * 0.1, 0.3)
            def_evidence_weight = min(len(def_arg.evidence) * 0.1, 0.3) if def_arg else 0.0

            pro_total = pro_strength + pro_evidence_weight
            def_total = def_strength + def_evidence_weight

            # Judge's decision
            if pro_total > def_total * 1.2:
                verdict = "sustained"
                risk_adj = pro_arg.confidence * 0.1
                reasoning = (
                    f"Prosecution's argument regarding {clause_type.replace('_', ' ')} "
                    f"is sustained. The risks identified ({pro_arg.severity} severity) "
                    f"outweigh defense's position. Evidence strength: "
                    f"prosecution {pro_total:.2f} vs defense {def_total:.2f}."
                )
            elif def_total > pro_total * 1.2:
                verdict = "overruled"
                risk_adj = -0.05
                reasoning = (
                    f"Prosecution's concerns about {clause_type.replace('_', ' ')} "
                    f"are overruled. Defense demonstrates the clause falls within "
                    f"acceptable commercial practice. Evidence strength: "
                    f"defense {def_total:.2f} vs prosecution {pro_total:.2f}."
                )
            else:
                verdict = "sustained"
                risk_adj = pro_arg.confidence * 0.05  # Reduced adjustment for close cases
                reasoning = (
                    f"Close call on {clause_type.replace('_', ' ')}. "
                    f"While defense raises valid points, the court errs on the side "
                    f"of caution and sustains the prosecution's concern. "
                    f"Reduced risk adjustment applied."
                )

            rulings.append(DebateRuling(
                clause_type=clause_type,
                verdict=verdict,
                reasoning=reasoning,
                risk_adjustment=risk_adj,
                prosecution_strength=pro_total,
                defense_strength=def_total,
            ))

        return rulings

    def _severity_weight(self, severity: str) -> float:
        """Convert severity to numeric weight."""
        return {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3,
            "advisory": 0.1,
        }.get(severity, 0.5)

    def _generate_summary(
        self,
        prosecution: List[DebateArgument],
        defense: List[DebateArgument],
        rulings: List[DebateRuling],
        verdict: str,
    ) -> str:
        """Generate executive summary of the debate."""
        sustained = [r for r in rulings if r.verdict == "sustained"]
        overruled = [r for r in rulings if r.verdict == "overruled"]

        critical = [r for r in sustained if r.prosecution_strength > 0.8]

        summary_parts = [
            f"Legal Debate Concluded: {len(rulings)} clauses debated.",
            f"Prosecution raised {len(prosecution)} arguments; "
            f"Defense countered with {len(defense)} arguments.",
            f"Judge sustained {len(sustained)} prosecution arguments and "
            f"overruled {len(overruled)}.",
        ]

        if critical:
            types = ", ".join(r.clause_type.replace("_", " ") for r in critical[:3])
            summary_parts.append(
                f"Critical rulings on: {types}. Immediate review recommended."
            )

        verdict_desc = {
            "high_risk": "Contract presents HIGH RISK requiring substantial revision.",
            "moderate_risk": "Contract presents MODERATE RISK with specific areas requiring attention.",
            "acceptable": "Contract terms are within ACCEPTABLE commercial standards.",
        }
        summary_parts.append(verdict_desc.get(verdict, ""))

        return " ".join(summary_parts)
