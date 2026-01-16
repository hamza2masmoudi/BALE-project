"""
BALE Legal Ontology (BALE-Onto)
Extends LKIF-core for contract analysis.

Novel IP: Structured representation of contract obligations, rights, and risks.
"""
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum


# =============================================================================
# CORE ENUMERATIONS
# =============================================================================

class PartyRole(Enum):
    """Party roles in contracts."""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    LICENSOR = "licensor"
    LICENSEE = "licensee"
    EMPLOYER = "employer"
    EMPLOYEE = "employee"
    LANDLORD = "landlord"
    TENANT = "tenant"
    LENDER = "lender"
    BORROWER = "borrower"


class ObligationType(Enum):
    """Deontic obligation types (Hohfeldian analysis)."""
    POSITIVE = "must_do"        # O(action) - obligated to perform
    NEGATIVE = "must_not_do"    # F(action) - forbidden
    CONDITIONAL = "if_then"     # If X then O(Y)
    DISCRETIONARY = "may_do"    # P(action) - permitted


class RightType(Enum):
    """Legal right types (Hohfeldian)."""
    CLAIM = "claim"           # Can demand performance
    LIBERTY = "liberty"       # Free to act
    POWER = "power"           # Can change legal relations
    IMMUNITY = "immunity"     # Protected from change


class ClauseCategory(Enum):
    """CUAD-aligned clause categories + extensions."""
    # Risk Allocation
    INDEMNIFICATION = "indemnification"
    LIMITATION_OF_LIABILITY = "limitation_of_liability"
    WARRANTY = "warranty"
    INSURANCE = "insurance"
    
    # Behavioral
    CONFIDENTIALITY = "confidentiality"
    NON_COMPETE = "non_compete"
    NON_SOLICITATION = "non_solicitation"
    EXCLUSIVITY = "exclusivity"
    
    # Structural
    TERMINATION = "termination"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"
    ASSIGNMENT = "assignment"
    AMENDMENT = "amendment"
    
    # IP
    IP_OWNERSHIP = "ip_ownership"
    LICENSE_GRANT = "license_grant"
    
    # Data
    DATA_PROTECTION = "data_protection"
    AUDIT_RIGHTS = "audit_rights"
    
    # Financial
    PAYMENT_TERMS = "payment_terms"
    PRICE_CHANGES = "price_changes"
    
    # Other
    FORCE_MAJEURE = "force_majeure"
    NOTICE = "notice"
    SURVIVAL = "survival"


class RiskFactor(Enum):
    """Risk factors identified in clauses."""
    UNLIMITED_LIABILITY = "unlimited_liability"
    NO_LIABILITY_CAP = "no_liability_cap"
    BROAD_INDEMNITY = "broad_indemnity"
    ONE_SIDED_TERMINATION = "one_sided_termination"
    PERPETUAL_OBLIGATION = "perpetual_obligation"
    OVERBROAD_NONCOMPETE = "overbroad_noncompete"
    VAGUE_DEFINITION = "vague_definition"
    MISSING_CARVEOUT = "missing_carveout"
    ASYMMETRIC_NOTICE = "asymmetric_notice"
    UNFAVORABLE_JURISDICTION = "unfavorable_jurisdiction"
    RETROACTIVE_EFFECT = "retroactive_effect"
    UNILATERAL_AMENDMENT = "unilateral_amendment"


class Jurisdiction(Enum):
    """Supported jurisdictions with legal specifics."""
    US_FEDERAL = "US"
    US_CALIFORNIA = "US-CA"  # Special non-compete rules
    US_DELAWARE = "US-DE"    # Common for corporate
    US_NEW_YORK = "US-NY"    # Finance standard
    UK = "UK"
    EU_GDPR = "EU"
    GERMANY = "DE"
    SINGAPORE = "SG"


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Obligation:
    """
    Represents a legal obligation extracted from a clause.
    
    This is a novel structured representation that enables:
    - Graph-based power analysis
    - Deontic conflict detection
    - Quantitative asymmetry scoring
    """
    obligor: str                    # Who must perform
    beneficiary: str                # Who benefits
    action: str                     # What must be done
    obligation_type: ObligationType
    conditions: List[str] = field(default_factory=list)  # Triggering conditions
    exceptions: List[str] = field(default_factory=list)  # Carve-outs
    severity: float = 0.5          # 0-1 scale of obligation weight
    source_clause: Optional[str] = None


@dataclass
class Right:
    """
    Represents a legal right.
    Correlates with Obligations (claim-duty relationship).
    """
    holder: str                     # Who has the right
    against: str                    # Against whom
    subject: str                    # Right to what
    right_type: RightType
    conditions: List[str] = field(default_factory=list)
    source_clause: Optional[str] = None


@dataclass
class Clause:
    """
    Structured clause representation.
    """
    id: str
    text: str
    category: ClauseCategory
    start_char: int
    end_char: int
    
    # Extracted elements
    obligations: List[Obligation] = field(default_factory=list)
    rights: List[Right] = field(default_factory=list)
    
    # Risk assessment
    risk_score: float = 0.0
    risk_factors: List[RiskFactor] = field(default_factory=list)
    party_favored: Optional[str] = None
    enforceability: str = "unknown"
    
    # Metadata
    is_standard: bool = False  # vs. negotiated
    market_deviation: float = 0.0  # How far from market standard


@dataclass
class Party:
    """Contract party with role and characteristics."""
    name: str
    role: PartyRole
    aliases: List[str] = field(default_factory=list)
    is_drafting_party: bool = False


@dataclass 
class ContractOntology:
    """
    Complete ontological representation of a contract.
    
    This structured format enables:
    - Novel algorithm application (silence, power, strain)
    - Training data generation
    - Benchmark evaluation
    """
    contract_id: str
    contract_type: str
    jurisdiction: Jurisdiction
    effective_date: Optional[str]
    
    # Parties
    parties: List[Party] = field(default_factory=list)
    
    # Clauses
    clauses: List[Clause] = field(default_factory=list)
    
    # Aggregated obligations graph
    obligation_graph: Dict[str, List[str]] = field(default_factory=dict)
    
    # Missing clauses (silence detection)
    expected_clauses: Set[ClauseCategory] = field(default_factory=set)
    present_clauses: Set[ClauseCategory] = field(default_factory=set)
    missing_clauses: Set[ClauseCategory] = field(default_factory=set)
    
    # Computed metrics
    power_asymmetry_score: float = 0.0
    overall_risk_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "jurisdiction": self.jurisdiction.value,
            "effective_date": self.effective_date,
            "parties": [asdict(p) for p in self.parties],
            "clauses": [
                {
                    **asdict(c),
                    "category": c.category.value,
                    "risk_factors": [rf.value for rf in c.risk_factors]
                }
                for c in self.clauses
            ],
            "missing_clauses": [mc.value for mc in self.missing_clauses],
            "power_asymmetry_score": self.power_asymmetry_score,
            "overall_risk_score": self.overall_risk_score
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export as JSON."""
        return json.dumps(self.to_dict(), indent=indent)


# =============================================================================
# CLAUSE TYPE EXPECTATIONS BY CONTRACT TYPE
# =============================================================================

CLAUSE_EXPECTATIONS = {
    "msa": {
        ClauseCategory.INDEMNIFICATION,
        ClauseCategory.LIMITATION_OF_LIABILITY,
        ClauseCategory.CONFIDENTIALITY,
        ClauseCategory.IP_OWNERSHIP,
        ClauseCategory.TERMINATION,
        ClauseCategory.GOVERNING_LAW,
        ClauseCategory.DISPUTE_RESOLUTION,
        ClauseCategory.WARRANTY,
        ClauseCategory.PAYMENT_TERMS,
        ClauseCategory.FORCE_MAJEURE,
    },
    "nda": {
        ClauseCategory.CONFIDENTIALITY,
        ClauseCategory.TERMINATION,
        ClauseCategory.GOVERNING_LAW,
        ClauseCategory.NOTICE,
    },
    "sla": {
        ClauseCategory.WARRANTY,
        ClauseCategory.LIMITATION_OF_LIABILITY,
        ClauseCategory.TERMINATION,
        ClauseCategory.NOTICE,
    },
    "employment": {
        ClauseCategory.CONFIDENTIALITY,
        ClauseCategory.NON_COMPETE,
        ClauseCategory.NON_SOLICITATION,
        ClauseCategory.IP_OWNERSHIP,
        ClauseCategory.TERMINATION,
        ClauseCategory.GOVERNING_LAW,
    },
    "license": {
        ClauseCategory.LICENSE_GRANT,
        ClauseCategory.IP_OWNERSHIP,
        ClauseCategory.WARRANTY,
        ClauseCategory.LIMITATION_OF_LIABILITY,
        ClauseCategory.INDEMNIFICATION,
        ClauseCategory.TERMINATION,
    },
    "dpa": {
        ClauseCategory.DATA_PROTECTION,
        ClauseCategory.CONFIDENTIALITY,
        ClauseCategory.AUDIT_RIGHTS,
        ClauseCategory.TERMINATION,
        ClauseCategory.INDEMNIFICATION,
    },
}


# =============================================================================
# RISK SEVERITY WEIGHTS
# =============================================================================

RISK_FACTOR_WEIGHTS = {
    RiskFactor.UNLIMITED_LIABILITY: 0.95,
    RiskFactor.NO_LIABILITY_CAP: 0.85,
    RiskFactor.BROAD_INDEMNITY: 0.80,
    RiskFactor.ONE_SIDED_TERMINATION: 0.70,
    RiskFactor.PERPETUAL_OBLIGATION: 0.75,
    RiskFactor.OVERBROAD_NONCOMPETE: 0.85,
    RiskFactor.VAGUE_DEFINITION: 0.50,
    RiskFactor.MISSING_CARVEOUT: 0.60,
    RiskFactor.ASYMMETRIC_NOTICE: 0.40,
    RiskFactor.UNFAVORABLE_JURISDICTION: 0.55,
    RiskFactor.RETROACTIVE_EFFECT: 0.65,
    RiskFactor.UNILATERAL_AMENDMENT: 0.80,
}


# =============================================================================
# REGIME CHANGES DATABASE (for Temporal Decay)
# =============================================================================

LEGAL_REGIME_CHANGES = [
    {
        "id": "gdpr",
        "name": "EU General Data Protection Regulation",
        "effective_date": "2018-05-25",
        "jurisdictions": [Jurisdiction.EU_GDPR, Jurisdiction.UK, Jurisdiction.GERMANY],
        "affected_clauses": [ClauseCategory.DATA_PROTECTION, ClauseCategory.CONFIDENTIALITY],
        "impact_score": 0.9,
    },
    {
        "id": "ccpa",
        "name": "California Consumer Privacy Act",
        "effective_date": "2020-01-01",
        "jurisdictions": [Jurisdiction.US_CALIFORNIA],
        "affected_clauses": [ClauseCategory.DATA_PROTECTION],
        "impact_score": 0.7,
    },
    {
        "id": "ftc_noncompete",
        "name": "FTC Non-Compete Ban (proposed)",
        "effective_date": "2024-09-04",
        "jurisdictions": [Jurisdiction.US_FEDERAL],
        "affected_clauses": [ClauseCategory.NON_COMPETE],
        "impact_score": 0.95,
    },
    {
        "id": "uk_gdpr",
        "name": "UK GDPR (post-Brexit)",
        "effective_date": "2021-01-01",
        "jurisdictions": [Jurisdiction.UK],
        "affected_clauses": [ClauseCategory.DATA_PROTECTION],
        "impact_score": 0.6,
    },
]


def get_clause_expectations(contract_type: str) -> Set[ClauseCategory]:
    """Get expected clauses for a contract type."""
    return CLAUSE_EXPECTATIONS.get(contract_type.lower(), set())


def get_risk_weight(factor: RiskFactor) -> float:
    """Get severity weight for a risk factor."""
    return RISK_FACTOR_WEIGHTS.get(factor, 0.5)
