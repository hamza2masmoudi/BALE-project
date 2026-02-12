"""
BALE V12 — Neuro-Symbolic Legal Reasoning Engine
=================================================
Encodes legal doctrines as formal rules and evaluates them against
neural classifier outputs. Combines symbolic deduction with neural
perception for legally grounded risk assessment.

Innovation: No existing open-source contract analyzer fuses neural
embeddings with symbolic legal logic. BALE V12 is the first.

Architecture:
    Neural layer  →  clause_type, confidence, risk_weight
    Symbolic layer →  doctrine_violations, remedies, severity
    Fusion        →  risk = α·neural + (1-α)·symbolic (α adaptive)
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger("bale_v12_symbolic")


# ==================== LEGAL DOCTRINE TAXONOMY ====================

class DoctrineFamiliy(Enum):
    """Families of legal principles from contract law."""
    PROPORTIONALITY = "proportionality"
    GOOD_FAITH = "good_faith"
    GAP_FILLING = "gap_filling"
    UNCONSCIONABILITY = "unconscionability"
    INTERPRETATION = "interpretation"
    PUBLIC_POLICY = "public_policy"
    FORMATION = "formation"
    PERFORMANCE = "performance"


class ViolationSeverity(Enum):
    """Severity levels for doctrine violations."""
    CRITICAL = "critical"      # Contract may be unenforceable
    HIGH = "high"              # Likely to be challenged
    MEDIUM = "medium"          # Potential vulnerability
    LOW = "low"                # Best practice concern
    ADVISORY = "advisory"      # Informational only


# ==================== DATA STRUCTURES ====================

@dataclass
class DoctrineRule:
    """A single legal doctrine rule expressed as formal logic."""
    id: str
    name: str
    family: DoctrineFamiliy
    description: str
    preconditions: Dict[str, Any]     # What must be true for rule to fire
    violation_text: str               # What violation is triggered
    severity: ViolationSeverity
    risk_contribution: float          # 0-1, how much risk this adds
    remedy: str                       # Suggested fix
    jurisdictions: List[str]          # Which jurisdictions this applies to
    citation: str                     # Legal basis


@dataclass
class SymbolicViolation:
    """A triggered violation from symbolic reasoning."""
    rule_id: str
    rule_name: str
    family: str
    severity: str
    description: str
    violation_text: str
    remedy: str
    citation: str
    risk_contribution: float
    triggering_clauses: List[str]     # Which clause types triggered it
    confidence: float                 # How confident we are in this firing


@dataclass
class SymbolicVerdict:
    """Complete symbolic reasoning output."""
    total_rules_evaluated: int
    violations_triggered: int
    violations: List[SymbolicViolation]
    doctrine_coverage: Dict[str, int]   # family → count of rules checked
    symbolic_risk_score: float          # 0-100
    neural_risk_score: float            # Original from V11
    fused_risk_score: float             # α-blended
    alpha: float                        # Blending weight
    reasoning_chain: List[str]          # Human-readable reasoning steps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_rules_evaluated": self.total_rules_evaluated,
            "violations_triggered": self.violations_triggered,
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "rule_name": v.rule_name,
                    "family": v.family,
                    "severity": v.severity,
                    "description": v.description,
                    "violation_text": v.violation_text,
                    "remedy": v.remedy,
                    "citation": v.citation,
                    "risk_contribution": v.risk_contribution,
                    "triggering_clauses": v.triggering_clauses,
                    "confidence": v.confidence,
                }
                for v in self.violations
            ],
            "doctrine_coverage": self.doctrine_coverage,
            "symbolic_risk_score": round(self.symbolic_risk_score, 2),
            "neural_risk_score": round(self.neural_risk_score, 2),
            "fused_risk_score": round(self.fused_risk_score, 2),
            "alpha": round(self.alpha, 3),
            "reasoning_chain": self.reasoning_chain,
        }


# ==================== 42 LEGAL DOCTRINE RULES ====================

DOCTRINE_RULES: List[DoctrineRule] = [
    # ──────────── PROPORTIONALITY (8 rules) ────────────
    DoctrineRule(
        id="PROP-001",
        name="Uncapped Indemnification",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="Indemnification without a liability cap is disproportionate.",
        preconditions={
            "requires_clause": "indemnification",
            "missing_clause": "limitation_of_liability",
        },
        violation_text="Unlimited indemnification obligation without corresponding liability cap creates disproportionate risk exposure.",
        severity=ViolationSeverity.CRITICAL,
        risk_contribution=0.15,
        remedy="Add a mutual liability cap, typically set at the value of fees paid in the preceding 12-month period.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Restatement (Second) of Contracts §356; Dunlop Pneumatic Tyre Co v New Garage [1915] AC 79",
    ),
    DoctrineRule(
        id="PROP-002",
        name="Unilateral Termination Without Cure Period",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="One-sided termination without a cure period is disproportionate.",
        preconditions={
            "requires_clause": "termination",
            "clause_pattern": "unilateral|at will|without cause|sole discretion",
            "missing_pattern": "cure period|cure right|opportunity to remedy|days to cure",
        },
        violation_text="Unilateral termination right without a cure period allows abrupt contract dissolution.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.12,
        remedy="Add a 30-day cure period allowing the breaching party to remedy before termination takes effect.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="UCC §2-309; Hadley v Baxendale [1854] EWHC J70",
    ),
    DoctrineRule(
        id="PROP-003",
        name="Disproportionate Liquidated Damages",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="Liquidated damages must be a reasonable estimate, not a penalty.",
        preconditions={
            "requires_clause": "payment_terms",
            "clause_pattern": "liquidated damages|penalty|late fee|interest.*exceed",
        },
        violation_text="Liquidated damages clause may constitute an unenforceable penalty if disproportionate to actual loss.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.08,
        remedy="Ensure liquidated damages represent a genuine pre-estimate of loss, not punitive in nature.",
        jurisdictions=["US", "UK", "EU"],
        citation="Cavendish Square v Makdessi [2015] UKSC 67; Restatement (Second) §356",
    ),
    DoctrineRule(
        id="PROP-004",
        name="Unlimited Consequential Damages",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="Failure to exclude or cap consequential damages.",
        preconditions={
            "requires_clause": "limitation_of_liability",
            "missing_pattern": "consequential|indirect|special damages.*excluded",
        },
        violation_text="No exclusion of consequential or indirect damages exposes party to unpredictable liability.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.10,
        remedy="Add explicit carve-out excluding indirect, consequential, and special damages.",
        jurisdictions=["US", "UK", "international"],
        citation="Hadley v Baxendale [1854]; Victoria Laundry v Newman [1949]",
    ),
    DoctrineRule(
        id="PROP-005",
        name="Asymmetric Insurance Requirements",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="One party must carry insurance while the other is exempt.",
        preconditions={
            "requires_clause": "insurance",
            "clause_pattern": "shall maintain|shall procure|shall carry",
            "missing_pattern": "mutual|each party|both parties",
        },
        violation_text="Insurance requirements are unilateral, creating asymmetric financial burden.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.06,
        remedy="Make insurance obligations mutual or ensure requirements are proportionate to each party's risk exposure.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="General commercial law principles; insurance allocation best practices",
    ),
    DoctrineRule(
        id="PROP-006",
        name="Excessive Non-Compete Scope",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="Non-compete clauses must be reasonable in scope, duration, and geography.",
        preconditions={
            "requires_clause": "non_compete",
            "clause_pattern": "worldwide|perpetual|indefinite|all businesses|any capacity",
        },
        violation_text="Non-compete is unreasonably broad in geographic scope or duration, likely unenforceable.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.10,
        remedy="Limit non-compete to specific geography, reasonable duration (typically 1-2 years), and relevant business activities.",
        jurisdictions=["US", "UK", "EU"],
        citation="Nordenfelt v Maxim Nordenfelt [1894]; BDO Seidman v Hirshberg (1999)",
    ),
    DoctrineRule(
        id="PROP-007",
        name="Warranty Without Remedies",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="Warranties provided without corresponding remedies for breach.",
        preconditions={
            "requires_clause": "warranty",
            "missing_pattern": "remedy|remedies|replacement|repair|refund",
        },
        violation_text="Warranty obligations lack specified remedies for breach, creating ambiguity.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.05,
        remedy="Specify warranty remedies: repair, replacement, refund, or re-performance.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Sale of Goods Act 1979 §48A-F; UCC §2-714",
    ),
    DoctrineRule(
        id="PROP-008",
        name="Unilateral Audit Rights",
        family=DoctrineFamiliy.PROPORTIONALITY,
        description="Audit rights without notice period or frequency limits.",
        preconditions={
            "requires_clause": "audit_rights",
            "clause_pattern": "at any time|unlimited|without notice|sole discretion",
        },
        violation_text="Unrestricted audit rights without notice or frequency limits are disproportionate.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.05,
        remedy="Limit audits to once per year with 30-day advance written notice during business hours.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Standard commercial audit clause best practices",
    ),

    # ──────────── GOOD FAITH (7 rules) ────────────
    DoctrineRule(
        id="GF-001",
        name="Entire Agreement Without Good Faith",
        family=DoctrineFamiliy.GOOD_FAITH,
        description="Entire agreement clause combined with no good faith obligation.",
        preconditions={
            "clause_pattern": "entire agreement|whole agreement|complete agreement",
            "missing_pattern": "good faith|fair dealing|reasonable efforts",
        },
        violation_text="Entire agreement clause without an express good faith obligation may allow bad-faith enforcement of strict contractual terms.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.06,
        remedy="Add an implied covenant of good faith and fair dealing, especially for long-term agreements.",
        jurisdictions=["US", "EU"],
        citation="UCC §1-304; EU Directive 93/13/EEC on Unfair Terms",
    ),
    DoctrineRule(
        id="GF-002",
        name="Discretionary Performance Standards",
        family=DoctrineFamiliy.GOOD_FAITH,
        description="Performance measured by one party's sole discretion.",
        preconditions={
            "clause_pattern": "sole discretion|absolute discretion|sole judgment|exclusive determination",
        },
        violation_text="Performance evaluation at one party's sole discretion violates good faith requirements.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.08,
        remedy="Replace 'sole discretion' with 'reasonable discretion' or objective measurable criteria.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Bhasin v Hrynew [2014] SCC 71; UCC §2-306",
    ),
    DoctrineRule(
        id="GF-003",
        name="Unilateral Amendment Rights",
        family=DoctrineFamiliy.GOOD_FAITH,
        description="One party can unilaterally modify the agreement without consent.",
        preconditions={
            "clause_pattern": "right to modify|right to amend|may change.*terms|reserves the right to alter",
            "missing_pattern": "mutual|consent|agreement of both|written approval",
        },
        violation_text="Unilateral amendment power without notice or consent violates mutuality of obligation.",
        severity=ViolationSeverity.CRITICAL,
        risk_contribution=0.12,
        remedy="Require mutual written consent for amendments or at minimum 30-day notice with opt-out rights.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Williams v Roffey Bros [1991] 1 QB 1; Stilk v Myrick [1809]",
    ),
    DoctrineRule(
        id="GF-004",
        name="Best Efforts Without Definition",
        family=DoctrineFamiliy.GOOD_FAITH,
        description="Best efforts obligation without defining what constitutes best efforts.",
        preconditions={
            "clause_pattern": "best efforts|best endeavours|commercially reasonable efforts",
            "missing_pattern": "including|such as|defined as|meaning",
        },
        violation_text="'Best efforts' language lacks objective definition, creating performance ambiguity.",
        severity=ViolationSeverity.LOW,
        risk_contribution=0.03,
        remedy="Define specific actions or benchmarks that constitute 'best efforts' performance.",
        jurisdictions=["US", "UK", "international"],
        citation="Bloor v Falstaff Brewing (1979); Jet2.com v Blackpool Airport [2012]",
    ),
    DoctrineRule(
        id="GF-005",
        name="Waiver of Consequential Rights",
        family=DoctrineFamiliy.GOOD_FAITH,
        description="Blanket waiver of claims without carve-outs for fraud or willful misconduct.",
        preconditions={
            "clause_pattern": "waives? all claims|releases? all liability|hold harmless.*all",
            "missing_pattern": "fraud|willful|gross negligence|intentional|bad faith",
        },
        violation_text="Blanket liability waiver without carve-outs for fraud or willful misconduct is unconscionable.",
        severity=ViolationSeverity.CRITICAL,
        risk_contribution=0.14,
        remedy="Add explicit carve-outs preserving rights for fraud, willful misconduct, and gross negligence.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="UCTA 1977 §2(1); UCC §2-302",
    ),
    DoctrineRule(
        id="GF-006",
        name="No Right to Assignment Without Consent",
        family=DoctrineFamiliy.GOOD_FAITH,
        description="One party can freely assign, but the other cannot without consent.",
        preconditions={
            "requires_clause": "assignment",
            "clause_pattern": "may assign|freely assign|right to assign",
            "missing_pattern": "mutual|either party|consent.*both",
        },
        violation_text="Asymmetric assignment rights allow one party to transfer obligations without the other's consent.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.06,
        remedy="Make assignment rights mutual or require written consent from the non-assigning party.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="General contract law principles; Novation doctrine",
    ),
    DoctrineRule(
        id="GF-007",
        name="Automatic Renewal Without Notice",
        family=DoctrineFamiliy.GOOD_FAITH,
        description="Contract auto-renews without adequate advance notice to opt out.",
        preconditions={
            "clause_pattern": "auto.*renew|automatic.*renew|shall renew|will renew",
            "missing_pattern": "notice|opt.?out|cancel|terminate.*prior|days.*before",
        },
        violation_text="Automatic renewal without opt-out notice period operates as a trap clause.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.06,
        remedy="Add a clear opt-out window (typically 30-90 days before renewal) with written notice provisions.",
        jurisdictions=["US", "UK", "EU"],
        citation="Various state auto-renewal statutes; EU Consumer Rights Directive",
    ),

    # ──────────── GAP FILLING (7 rules) ────────────
    DoctrineRule(
        id="GAP-001",
        name="Missing Governing Law",
        family=DoctrineFamiliy.GAP_FILLING,
        description="Contract lacks choice of law clause.",
        preconditions={
            "missing_clause": "governing_law",
        },
        violation_text="No governing law specified. Courts will apply conflict-of-laws analysis creating unpredictability.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.10,
        remedy="Add explicit governing law clause specifying applicable jurisdiction's laws.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Rome I Regulation (EU) 593/2008; Restatement (Second) Conflict of Laws",
    ),
    DoctrineRule(
        id="GAP-002",
        name="Missing Dispute Resolution",
        family=DoctrineFamiliy.GAP_FILLING,
        description="Contract lacks dispute resolution mechanism.",
        preconditions={
            "missing_clause": "dispute_resolution",
        },
        violation_text="No dispute resolution mechanism. Parties face costly and uncertain litigation.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.09,
        remedy="Add tiered dispute resolution: negotiation → mediation → arbitration/litigation.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Federal Arbitration Act 9 USC §1-16; Arbitration Act 1996 (UK)",
    ),
    DoctrineRule(
        id="GAP-003",
        name="Missing Confidentiality in IP-Heavy Contract",
        family=DoctrineFamiliy.GAP_FILLING,
        description="Intellectual property clauses without confidentiality protection.",
        preconditions={
            "requires_clause": "intellectual_property",
            "missing_clause": "confidentiality",
        },
        violation_text="IP provisions without confidentiality clause leave trade secrets unprotected.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.09,
        remedy="Add confidentiality clause covering all disclosed intellectual property and trade secrets.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="DTSA 18 USC §1836; Trade Secrets Directive (EU) 2016/943",
    ),
    DoctrineRule(
        id="GAP-004",
        name="Missing Force Majeure",
        family=DoctrineFamiliy.GAP_FILLING,
        description="No force majeure clause in a long-term agreement.",
        preconditions={
            "missing_clause": "force_majeure",
            "contract_types": ["MSA", "License", "Supply", "Franchise"],
        },
        violation_text="No force majeure provision. Parties remain liable during extraordinary events.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.06,
        remedy="Add force majeure clause covering natural disasters, pandemics, government actions, and war.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Taylor v Caldwell [1863]; UCC §2-615",
    ),
    DoctrineRule(
        id="GAP-005",
        name="Missing Data Protection",
        family=DoctrineFamiliy.GAP_FILLING,
        description="Contract involves personal data but lacks data protection clause.",
        preconditions={
            "missing_clause": "data_protection",
            "clause_pattern": "personal data|customer data|user data|PII|data processing|data subject",
        },
        violation_text="Personal data processing without data protection provisions violates GDPR/CCPA.",
        severity=ViolationSeverity.CRITICAL,
        risk_contribution=0.14,
        remedy="Add GDPR/CCPA-compliant data processing agreement as an annex.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="GDPR Art 28; CCPA §1798.140",
    ),
    DoctrineRule(
        id="GAP-006",
        name="Missing Termination Clause",
        family=DoctrineFamiliy.GAP_FILLING,
        description="Contract lacks explicit termination provisions.",
        preconditions={
            "missing_clause": "termination",
        },
        violation_text="No termination clause. Contract may be perpetual or terminable only by breach.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.10,
        remedy="Add termination provisions including: for cause, for convenience (with notice), and automatic expiry.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="General contract law; UCC §2-309",
    ),
    DoctrineRule(
        id="GAP-007",
        name="Missing Insurance for High-Risk Obligations",
        family=DoctrineFamiliy.GAP_FILLING,
        description="High indemnification obligations without insurance backing.",
        preconditions={
            "requires_clause": "indemnification",
            "missing_clause": "insurance",
            "risk_threshold": 0.7,
        },
        violation_text="Substantial indemnification obligations are not backed by insurance requirements.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.05,
        remedy="Require commercial general liability insurance with minimum coverage proportionate to indemnification exposure.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Commercial risk management best practices",
    ),

    # ──────────── UNCONSCIONABILITY (6 rules) ────────────
    DoctrineRule(
        id="UNCON-001",
        name="One-Sided Indemnification",
        family=DoctrineFamiliy.UNCONSCIONABILITY,
        description="Only one party indemnifies the other with no reciprocal obligation.",
        preconditions={
            "requires_clause": "indemnification",
            "clause_pattern": "shall indemnify|agrees to indemnify|will indemnify",
            "missing_pattern": "mutual|each party|reciprocal|both parties shall indemnify",
        },
        violation_text="Indemnification is unilateral. One party bears all liability while the other is fully shielded.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.10,
        remedy="Make indemnification mutual, or at minimum ensure the indemnified party has reciprocal obligations.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="UCC §2-302 (unconscionability); Williams v Walker-Thomas [1965]",
    ),
    DoctrineRule(
        id="UNCON-002",
        name="Waiver of Jury Trial",
        family=DoctrineFamiliy.UNCONSCIONABILITY,
        description="Waiver of constitutional right to jury trial.",
        preconditions={
            "clause_pattern": "waive.*jury|jury.*waiver|waives.*right.*jury|waiver of jury trial",
        },
        violation_text="Jury trial waiver removes constitutional protection. May be unconscionable in consumer contexts.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.05,
        remedy="Consider whether jury waiver is appropriate. Ensure it is prominently displayed and voluntarily agreed to.",
        jurisdictions=["US"],
        citation="7th Amendment; National Westminster Bank v Ross [1999]",
    ),
    DoctrineRule(
        id="UNCON-003",
        name="Unilateral Choice of Forum",
        family=DoctrineFamiliy.UNCONSCIONABILITY,
        description="Dispute resolution forum heavily favors one party's location.",
        preconditions={
            "requires_clause": "dispute_resolution",
            "clause_pattern": "exclusive jurisdiction|exclusive venue|only in|solely in",
        },
        violation_text="Exclusive forum selection may create practical barrier to dispute resolution for one party.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.05,
        remedy="Allow disputes in either party's jurisdiction or use neutral arbitration forum.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Carnival Cruise Lines v Shute [1991]; Brussels I Regulation",
    ),
    DoctrineRule(
        id="UNCON-004",
        name="Penalty Disguised as Fee",
        family=DoctrineFamiliy.UNCONSCIONABILITY,
        description="Excessive early termination fees that function as penalties.",
        preconditions={
            "clause_pattern": "early termination fee|cancellation fee|break fee|exit fee",
            "missing_pattern": "reasonable|actual|direct damages|proportionate",
        },
        violation_text="Early termination fees without reference to actual damages may constitute unenforceable penalty.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.07,
        remedy="Tie termination fees to actual anticipated damages or remaining contract value prorated.",
        jurisdictions=["US", "UK", "EU"],
        citation="Cavendish Square v Makdessi [2015]; Restatement §356",
    ),
    DoctrineRule(
        id="UNCON-005",
        name="Waiver of Class Action Rights",
        family=DoctrineFamiliy.UNCONSCIONABILITY,
        description="Forced individual arbitration waiving class action participation.",
        preconditions={
            "clause_pattern": "class action waiver|waive.*class|no class|class.*prohibited|individual.*arbitration",
        },
        violation_text="Class action waiver may be unconscionable depending on jurisdiction and contract type.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.05,
        remedy="Review enforceability in relevant jurisdiction. May need carve-outs for statutory claims.",
        jurisdictions=["US"],
        citation="AT&T v Concepcion [2011]; Epic Systems v Lewis [2018]",
    ),
    DoctrineRule(
        id="UNCON-006",
        name="Indemnification for Own Negligence",
        family=DoctrineFamiliy.UNCONSCIONABILITY,
        description="Party must indemnify the other even for the other's own negligence.",
        preconditions={
            "requires_clause": "indemnification",
            "clause_pattern": "regardless of.*cause|including.*negligence.*indemnified|even if.*fault",
        },
        violation_text="Requiring indemnification for the indemnitee's own negligence is unconscionable in many jurisdictions.",
        severity=ViolationSeverity.CRITICAL,
        risk_contribution=0.12,
        remedy="Exclude indemnification obligations for the indemnitee's own negligence or willful misconduct.",
        jurisdictions=["US", "UK"],
        citation="Anti-indemnity statutes (various US states); UCTA 1977 §2",
    ),

    # ──────────── INTERPRETATION (5 rules) ────────────
    DoctrineRule(
        id="INTERP-001",
        name="Ambiguous Defined Terms",
        family=DoctrineFamiliy.INTERPRETATION,
        description="Key terms used but not defined in the agreement.",
        preconditions={
            "clause_pattern": r'"[A-Z][a-zA-Z\s]+"',
            "missing_pattern": "definitions|defined terms|means|shall mean|as defined",
        },
        violation_text="Capitalized terms referenced without a definitions section create interpretation uncertainty.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.04,
        remedy="Add a comprehensive definitions section at the beginning of the agreement.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Contra proferentem rule; Investors Compensation Scheme v West Bromwich [1998]",
    ),
    DoctrineRule(
        id="INTERP-002",
        name="Conflicting Survival and Termination",
        family=DoctrineFamiliy.INTERPRETATION,
        description="Survival clause conflicts with termination provisions.",
        preconditions={
            "requires_clause": "termination",
            "clause_pattern": "surviv|shall survive|continues after|notwithstanding termination",
            "requires_clause_secondary": "confidentiality",
        },
        violation_text="Survival provisions may conflict with termination scope, creating ambiguity about post-termination obligations.",
        severity=ViolationSeverity.LOW,
        risk_contribution=0.03,
        remedy="Explicitly enumerate which sections survive termination and for how long.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Standard drafting practice; Photo Production Ltd v Securicor Transport [1980]",
    ),
    DoctrineRule(
        id="INTERP-003",
        name="Material vs Immaterial Breach Ambiguity",
        family=DoctrineFamiliy.INTERPRETATION,
        description="Right to terminate for 'breach' without specifying material vs immaterial.",
        preconditions={
            "requires_clause": "termination",
            "clause_pattern": "breach of|any breach|breach of any",
            "missing_pattern": "material breach|material default|substantial breach",
        },
        violation_text="Termination triggered by 'any breach' (including immaterial) creates disproportionate risk.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.08,
        remedy="Limit termination to 'material breach' and define what constitutes materiality.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Restatement (Second) §241; Hongkong Fir Shipping v Kawasaki [1962]",
    ),
    DoctrineRule(
        id="INTERP-004",
        name="Time-Is-of-the-Essence Without Specifics",
        family=DoctrineFamiliy.INTERPRETATION,
        description="Time-of-essence clause without specified deadlines.",
        preconditions={
            "clause_pattern": "time is of the essence|time shall be of the essence",
            "missing_pattern": "within.*days|by.*date|deadline|no later than",
        },
        violation_text="'Time is of the essence' without specific deadlines is ambiguous and may be unenforceable.",
        severity=ViolationSeverity.LOW,
        risk_contribution=0.03,
        remedy="Specify exact deadlines for performance obligations where time is critical.",
        jurisdictions=["US", "UK"],
        citation="United Scientific Holdings v Burnley Borough Council [1978]",
    ),
    DoctrineRule(
        id="INTERP-005",
        name="Inconsistent Standards of Care",
        family=DoctrineFamiliy.INTERPRETATION,
        description="Different performance standards used inconsistently (best efforts vs reasonable efforts).",
        preconditions={
            "clause_pattern": "best efforts|best endeavours",
            "clause_pattern_secondary": "reasonable efforts|commercially reasonable|reasonable endeavours",
        },
        violation_text="Inconsistent standards of care (best efforts AND reasonable efforts) create ambiguity about actual standard.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.04,
        remedy="Standardize on a single effort standard throughout the agreement.",
        jurisdictions=["US", "UK", "international"],
        citation="Rhodia International Holdings v Huntsman [2007]",
    ),

    # ──────────── PUBLIC POLICY (5 rules) ────────────
    DoctrineRule(
        id="PP-001",
        name="Exclusion of Statutory Rights",
        family=DoctrineFamiliy.PUBLIC_POLICY,
        description="Attempt to contractually exclude non-waivable statutory protections.",
        preconditions={
            "clause_pattern": "waives? all statutory|notwithstanding any statute|regardless of any law|override.*statutory",
        },
        violation_text="Attempting to waive mandatory statutory protections is void as against public policy.",
        severity=ViolationSeverity.CRITICAL,
        risk_contribution=0.15,
        remedy="Remove blanket statutory waivers. Identify specific non-mandatory provisions that can be modified.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="UCTA 1977; Magnuson-Moss Warranty Act; EU Consumer Rights Directive",
    ),
    DoctrineRule(
        id="PP-002",
        name="Excessive Restraint of Trade",
        family=DoctrineFamiliy.PUBLIC_POLICY,
        description="Non-compete or exclusivity clause that unreasonably restrains trade.",
        preconditions={
            "requires_clause": "non_compete",
            "clause_pattern": "shall not engage|shall not compete|exclusive|restrictive covenant",
            "missing_pattern": "reasonable|limited to|not exceeding|within the scope",
        },
        violation_text="Restraint of trade without reasonable limitations violates public policy.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.10,
        remedy="Add explicit limitations: specific activities, reasonable geographic scope, maximum duration.",
        jurisdictions=["US", "UK", "EU"],
        citation="Nordenfelt v Maxim [1894]; Sherman Act §1; Treaty on Functioning of EU Art 101",
    ),
    DoctrineRule(
        id="PP-003",
        name="GDPR Non-Compliance",
        family=DoctrineFamiliy.PUBLIC_POLICY,
        description="Contract processes EU personal data without GDPR safeguards.",
        preconditions={
            "clause_pattern": "personal data|data subject|data controller|data processor",
            "missing_pattern": "GDPR|data protection act|data processing agreement|DPA|sub-processor",
        },
        violation_text="Processing EU personal data without explicit GDPR compliance provisions violates mandatory data protection law.",
        severity=ViolationSeverity.CRITICAL,
        risk_contribution=0.15,
        remedy="Add a GDPR-compliant Data Processing Agreement (DPA) as a schedule/annex.",
        jurisdictions=["EU", "UK"],
        citation="GDPR Articles 28, 32, 44; UK Data Protection Act 2018",
    ),
    DoctrineRule(
        id="PP-004",
        name="Anti-Competitive Exclusivity",
        family=DoctrineFamiliy.PUBLIC_POLICY,
        description="Exclusive dealing arrangements that may violate competition law.",
        preconditions={
            "clause_pattern": "exclusive|sole supplier|sole provider|exclusive right",
            "clause_pattern_secondary": "during the term|for the duration|throughout",
        },
        violation_text="Long-term exclusivity may violate antitrust/competition law, especially with market power.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.06,
        remedy="Add market share exception, term limits, and competition law compliance clause.",
        jurisdictions=["US", "EU"],
        citation="Sherman Act §2; TFEU Art 102; EU Block Exemption Regulations",
    ),
    DoctrineRule(
        id="PP-005",
        name="Mandatory Arbitration in Consumer Context",
        family=DoctrineFamiliy.PUBLIC_POLICY,
        description="Forced arbitration in potentially consumer-facing agreement.",
        preconditions={
            "clause_pattern": "mandatory arbitration|binding arbitration|shall be arbitrated|must submit to arbitration",
            "missing_pattern": "opt.?out|voluntary|may elect|right to litigate",
        },
        violation_text="Mandatory arbitration without opt-out may be unenforceable in consumer contexts in some jurisdictions.",
        severity=ViolationSeverity.MEDIUM,
        risk_contribution=0.05,
        remedy="Add opt-out provision for arbitration, especially in B2C contexts.",
        jurisdictions=["US", "EU"],
        citation="Directive 93/13/EEC; CFPB Arbitration Rule (rescinded but influential)",
    ),

    # ──────────── FORMATION (4 rules) ────────────
    DoctrineRule(
        id="FORM-001",
        name="Missing Consideration",
        family=DoctrineFamiliy.FORMATION,
        description="No clear exchange of value evident in the agreement.",
        preconditions={
            "missing_clause": "payment_terms",
            "missing_pattern": "consideration|in exchange for|in return for|for and in consideration",
        },
        violation_text="No identifiable consideration. Contract may fail for want of consideration.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.12,
        remedy="Ensure clear recital of consideration exchanged by each party.",
        jurisdictions=["US", "UK"],
        citation="Currie v Misa [1875]; Chappell v Nestle [1960]",
    ),
    DoctrineRule(
        id="FORM-002",
        name="Conditional Agreement Without Clear Conditions",
        family=DoctrineFamiliy.FORMATION,
        description="Agreement subject to conditions that are unclear or undefined.",
        preconditions={
            "clause_pattern": "subject to|conditioned upon|contingent upon|provided that",
            "missing_pattern": "defined|specific|measurable|objective criteria|deadline",
        },
        violation_text="Conditions precedent are vague, creating uncertainty about when obligations arise.",
        severity=ViolationSeverity.LOW,
        risk_contribution=0.04,
        remedy="Define all conditions precedent with objective criteria and deadlines.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="Pym v Campbell [1856]; general contract formation law",
    ),
    DoctrineRule(
        id="FORM-003",
        name="Agreement to Agree in the Future",
        family=DoctrineFamiliy.FORMATION,
        description="Essential terms left to future negotiation.",
        preconditions={
            "clause_pattern": "to be agreed|to be determined|to be negotiated|TBD|TBC|to be confirmed",
        },
        violation_text="Essential terms left for future agreement may render the contract unenforceable for uncertainty.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.10,
        remedy="Define all essential terms now or provide a clear mechanism for determination.",
        jurisdictions=["US", "UK"],
        citation="Walford v Miles [1992]; May & Butcher v The King [1934]",
    ),
    DoctrineRule(
        id="FORM-004",
        name="Indefinite Duration Without Exit",
        family=DoctrineFamiliy.FORMATION,
        description="Contract with no term or termination mechanism (potentially perpetual).",
        preconditions={
            "missing_clause": "termination",
            "missing_pattern": "term|duration|period|years|months|expir",
        },
        violation_text="Perpetual contract without exit mechanism creates indefinite obligation.",
        severity=ViolationSeverity.HIGH,
        risk_contribution=0.08,
        remedy="Add a defined term (with renewal options) and a termination-for-convenience clause.",
        jurisdictions=["US", "UK", "EU", "international"],
        citation="UCC §2-309; general common law principles",
    ),
]


# ==================== SYMBOLIC REASONING ENGINE ====================

class SymbolicReasoner:
    """
    Neuro-Symbolic Legal Reasoning Engine.
    
    Evaluates 42 legal doctrine rules against the neural classifier's
    outputs, graph analysis, and power analysis from the V11 pipeline.
    
    Architecture:
        1. Extract facts from V11 report (clause types, patterns, relationships)
        2. Evaluate each rule's preconditions against extracted facts
        3. Collect triggered violations with confidence weighting
        4. Compute symbolic risk score from triggered rules
        5. Fuse with neural risk using adaptive α-blending
    """

    def __init__(self, rules: List[DoctrineRule] = None):
        self.rules = rules or DOCTRINE_RULES
        logger.info(f"SymbolicReasoner initialized with {len(self.rules)} doctrine rules")

    def evaluate(self, v11_report) -> SymbolicVerdict:
        """
        Evaluate all doctrine rules against a V11 analysis report.
        
        Args:
            v11_report: V10Report from the V11 pipeline
            
        Returns:
            SymbolicVerdict with all triggered violations and fused risk
        """
        import re

        # Step 1: Extract facts from V11 report
        facts = self._extract_facts(v11_report)
        reasoning_chain = [f"Extracted {len(facts['clause_types'])} clause types from contract"]

        # Step 2: Evaluate each rule
        violations = []
        doctrine_coverage = {}
        total_evaluated = 0

        for rule in self.rules:
            family_name = rule.family.value
            doctrine_coverage[family_name] = doctrine_coverage.get(family_name, 0) + 1
            total_evaluated += 1

            triggered, confidence, triggering_clauses = self._evaluate_rule(rule, facts)

            if triggered:
                violations.append(SymbolicViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    family=family_name,
                    severity=rule.severity.value,
                    description=rule.description,
                    violation_text=rule.violation_text,
                    remedy=rule.remedy,
                    citation=rule.citation,
                    risk_contribution=rule.risk_contribution,
                    triggering_clauses=triggering_clauses,
                    confidence=confidence,
                ))
                reasoning_chain.append(
                    f"[{rule.severity.value.upper()}] {rule.id}: {rule.name} — "
                    f"triggered by {', '.join(triggering_clauses)} (conf: {confidence:.2f})"
                )

        # Step 3: Compute symbolic risk score
        symbolic_risk = self._compute_symbolic_risk(violations)
        neural_risk = getattr(v11_report, 'risk_score', 50.0)
        if isinstance(neural_risk, str):
            try:
                neural_risk = float(neural_risk)
            except (ValueError, TypeError):
                neural_risk = 50.0

        # Step 4: Adaptive α-blending
        avg_confidence = self._get_avg_confidence(v11_report)
        alpha = self._compute_alpha(avg_confidence, len(violations))
        fused_risk = alpha * neural_risk + (1 - alpha) * symbolic_risk

        reasoning_chain.append(
            f"Symbolic risk: {symbolic_risk:.1f}, Neural risk: {neural_risk:.1f}, "
            f"α={alpha:.3f}, Fused: {fused_risk:.1f}"
        )

        return SymbolicVerdict(
            total_rules_evaluated=total_evaluated,
            violations_triggered=len(violations),
            violations=sorted(violations, key=lambda v: v.risk_contribution, reverse=True),
            doctrine_coverage=doctrine_coverage,
            symbolic_risk_score=symbolic_risk,
            neural_risk_score=neural_risk,
            fused_risk_score=fused_risk,
            alpha=alpha,
            reasoning_chain=reasoning_chain,
        )

    def _extract_facts(self, report) -> Dict[str, Any]:
        """Extract structured facts from V11 report for rule evaluation."""
        facts: Dict[str, Any] = {
            "clause_types": set(),
            "clause_texts": {},        # type → full text
            "full_text": "",
            "contract_type": getattr(report, 'contract_type', 'MSA'),
            "risk_score": 0.0,
            "has_conflicts": False,
            "conflict_count": 0,
            "power_asymmetry": 0.0,
        }

        # Extract clause classifications
        classifications = getattr(report, 'clause_classifications', [])
        for cls in classifications:
            if isinstance(cls, dict):
                ctype = cls.get('clause_type', cls.get('type', ''))
                text = cls.get('text', '')
                confidence = cls.get('confidence', 0)
                if ctype and confidence > 0.3:
                    facts["clause_types"].add(ctype)
                    existing = facts["clause_texts"].get(ctype, "")
                    facts["clause_texts"][ctype] = existing + " " + text

        # Build full text from all clauses
        for t in facts["clause_texts"].values():
            facts["full_text"] += t + " "

        # Extract graph info
        graph = getattr(report, 'graph', {})
        if isinstance(graph, dict):
            facts["conflict_count"] = graph.get('conflict_count', 0)
            facts["has_conflicts"] = facts["conflict_count"] > 0

        # Extract power info
        power = getattr(report, 'power', {})
        if isinstance(power, dict):
            facts["power_asymmetry"] = abs(power.get('power_score', 50) - 50) / 50

        # Extract risk
        facts["risk_score"] = getattr(report, 'risk_score', 50.0)
        if isinstance(facts["risk_score"], str):
            try:
                facts["risk_score"] = float(facts["risk_score"])
            except (ValueError, TypeError):
                facts["risk_score"] = 50.0

        return facts

    def _evaluate_rule(
        self, rule: DoctrineRule, facts: Dict[str, Any]
    ) -> Tuple[bool, float, List[str]]:
        """
        Evaluate a single rule's preconditions against extracted facts.
        
        Returns:
            (triggered, confidence, triggering_clause_types)
        """
        import re
        
        triggering = []
        conditions_met = 0
        conditions_total = 0

        preconds = rule.preconditions

        # Check: requires_clause (clause type must be present)
        if "requires_clause" in preconds:
            conditions_total += 1
            required = preconds["requires_clause"]
            if required in facts["clause_types"]:
                conditions_met += 1
                triggering.append(required)
            else:
                return False, 0.0, []

        # Check: requires_clause_secondary
        if "requires_clause_secondary" in preconds:
            conditions_total += 1
            required = preconds["requires_clause_secondary"]
            if required in facts["clause_types"]:
                conditions_met += 1
                triggering.append(required)

        # Check: missing_clause (clause type must be absent)
        if "missing_clause" in preconds:
            conditions_total += 1
            missing = preconds["missing_clause"]
            if missing not in facts["clause_types"]:
                conditions_met += 1
                triggering.append(f"missing:{missing}")
            else:
                return False, 0.0, []

        # Check: contract_types (only applies to certain types)
        if "contract_types" in preconds:
            conditions_total += 1
            if facts["contract_type"] in preconds["contract_types"]:
                conditions_met += 1
            else:
                return False, 0.0, []

        # Check: risk_threshold
        if "risk_threshold" in preconds:
            conditions_total += 1
            threshold = preconds["risk_threshold"]
            if facts["risk_score"] >= threshold * 100:
                conditions_met += 1
            else:
                return False, 0.0, []

        # Check: clause_pattern (regex pattern in clause text)
        full_text = facts["full_text"].lower()
        if "clause_pattern" in preconds:
            conditions_total += 1
            pattern = preconds["clause_pattern"]
            try:
                if re.search(pattern, full_text, re.IGNORECASE):
                    conditions_met += 1
                    triggering.append(f"pattern:{pattern[:30]}")
                else:
                    return False, 0.0, []
            except re.error:
                if pattern.lower() in full_text:
                    conditions_met += 1
                    triggering.append(f"pattern:{pattern[:30]}")
                else:
                    return False, 0.0, []

        # Check: clause_pattern_secondary
        if "clause_pattern_secondary" in preconds:
            conditions_total += 1
            pattern = preconds["clause_pattern_secondary"]
            try:
                if re.search(pattern, full_text, re.IGNORECASE):
                    conditions_met += 1
                else:
                    pass  # Secondary is soft
            except re.error:
                pass

        # Check: missing_pattern (pattern must NOT be present)
        if "missing_pattern" in preconds:
            conditions_total += 1
            pattern = preconds["missing_pattern"]
            try:
                if not re.search(pattern, full_text, re.IGNORECASE):
                    conditions_met += 1
                    triggering.append(f"absent:{pattern[:30]}")
                else:
                    return False, 0.0, []
            except re.error:
                if pattern.lower() not in full_text:
                    conditions_met += 1
                    triggering.append(f"absent:{pattern[:30]}")
                else:
                    return False, 0.0, []

        # Calculate confidence
        if conditions_total == 0:
            return False, 0.0, []

        confidence = conditions_met / conditions_total

        # Rule triggers if enough conditions met (at least 70%)
        triggered = confidence >= 0.7
        return triggered, confidence, triggering

    def _compute_symbolic_risk(self, violations: List[SymbolicViolation]) -> float:
        """Compute aggregate symbolic risk score from all violations."""
        if not violations:
            return 0.0

        total_contribution = sum(v.risk_contribution * v.confidence for v in violations)
        # Scale to 0-100, caps at 95
        symbolic_risk = min(total_contribution * 100, 95.0)
        return symbolic_risk

    def _get_avg_confidence(self, report) -> float:
        """Get average classification confidence from V11 report."""
        classifications = getattr(report, 'clause_classifications', [])
        if not classifications:
            return 0.5
        
        confidences = []
        for cls in classifications:
            if isinstance(cls, dict):
                conf = cls.get('calibrated_confidence', cls.get('confidence', 0.5))
                confidences.append(conf)
        
        return sum(confidences) / len(confidences) if confidences else 0.5

    def _compute_alpha(self, avg_confidence: float, num_violations: int) -> float:
        """
        Compute adaptive α for neural⊗symbolic risk fusion.
        
        High confidence → trust neural more (α → 0.7)
        Low confidence + many violations → trust symbolic more (α → 0.3)
        """
        # Base α starts at 0.5 (equal weight)
        alpha = 0.5

        # Adjust based on classification confidence
        # High confidence: neural is reliable → increase α
        alpha += (avg_confidence - 0.5) * 0.4  # range: -0.2 to +0.2

        # Adjust based on number of violations
        # Many symbolic violations → symbolic is finding things → decrease α
        violation_factor = min(num_violations / 10, 1.0) * 0.15
        alpha -= violation_factor

        # Clamp to [0.25, 0.75]
        alpha = max(0.25, min(0.75, alpha))
        return alpha
