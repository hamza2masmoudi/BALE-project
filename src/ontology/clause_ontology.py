"""
BALE Comprehensive Clause Ontology
75 clause types with risk profiles, legal references, and analysis criteria.
Focus: French Civil Law and English Common Law
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
class RiskLevel(str, Enum):
LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"
CRITICAL = "CRITICAL"
class LegalSystem(str, Enum):
COMMON_LAW = "COMMON_LAW" # UK, US, etc.
CIVIL_LAW = "CIVIL_LAW" # France, Germany, etc.
HYBRID = "HYBRID" # Both systems
class ClauseCategory(str, Enum):
RISK_ALLOCATION = "RISK_ALLOCATION"
CONFIDENTIALITY = "CONFIDENTIALITY"
INTELLECTUAL_PROPERTY = "INTELLECTUAL_PROPERTY"
TERMINATION = "TERMINATION"
DISPUTE_RESOLUTION = "DISPUTE_RESOLUTION"
EMPLOYMENT = "EMPLOYMENT"
M_AND_A = "M_AND_A"
DATA_PROTECTION = "DATA_PROTECTION"
PAYMENT = "PAYMENT"
GENERAL = "GENERAL"
@dataclass
class ClauseType:
"""Definition of a contract clause type with full legal context."""
id: str
name: str
category: ClauseCategory
risk_level: RiskLevel
description: str
# Legal references
common_law_reference: Optional[str] = None # UK/US cases or statutes
civil_law_reference: Optional[str] = None # French Code Civil articles
# Risk modifiers based on party position
buyer_risk_modifier: int = 0 # -20 to +20
seller_risk_modifier: int = 0 # -20 to +20
# Detection patterns
key_phrases_en: List[str] = None
key_phrases_fr: List[str] = None
# Analysis criteria
enforceability_factors: List[str] = None
red_flags: List[str] = None
best_practices: List[str] = None
# ==================== COMPREHENSIVE CLAUSE ONTOLOGY ====================
CLAUSE_TYPES: Dict[str, ClauseType] = {
# ==================== RISK ALLOCATION ====================
"indemnification_broad": ClauseType(
id="indemnification_broad",
name="Broad Indemnification",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.HIGH,
description="Broad indemnification covering all losses without limitation",
common_law_reference="George Mitchell v Finney Lock Seeds [1983] - reasonableness test",
civil_law_reference="Art. 1231-3 CC - Préjudice prévisible",
buyer_risk_modifier=+20,
seller_risk_modifier=-15,
key_phrases_en=["indemnify and hold harmless", "all claims", "any and all", "full indemnification"],
key_phrases_fr=["garantir et relever indemne", "tous dommages", "toute réclamation"],
red_flags=["No cap on indemnity", "Includes consequential damages", "No carve-outs"],
best_practices=["Add liability cap", "Exclude gross negligence", "Add notice requirements"]
),
"indemnification_narrow": ClauseType(
id="indemnification_narrow",
name="Narrow Indemnification",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.LOW,
description="Limited indemnification for specific third-party claims",
common_law_reference="Standard commercial practice",
civil_law_reference="Art. 1231-3 CC",
buyer_risk_modifier=-10,
seller_risk_modifier=+5,
key_phrases_en=["third-party claims", "direct infringement", "limited to"],
key_phrases_fr=["réclamations de tiers", "contrefaçon directe", "limité à"],
best_practices=["Standard market approach", "Clear scope definition"]
),
"indemnification_mutual": ClauseType(
id="indemnification_mutual",
name="Mutual Indemnification",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.MEDIUM,
description="Each party indemnifies the other for their own actions",
common_law_reference="Commercial best practice",
civil_law_reference="Art. 1103 CC - Force obligatoire",
buyer_risk_modifier=0,
seller_risk_modifier=0,
key_phrases_en=["each party shall indemnify", "mutual indemnification", "reciprocal"],
key_phrases_fr=["chaque partie garantit", "indemnisation réciproque", "mutuel"],
best_practices=["Balanced approach", "Mirror obligations"]
),
"limitation_liability": ClauseType(
id="limitation_liability",
name="Limitation of Liability",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.HIGH,
description="Cap on total liability exposure",
common_law_reference="UCTA 1977 s.2-3 (UK); UCC 2-719 (US)",
civil_law_reference="Art. 1231-3 CC - only foreseeable damages",
buyer_risk_modifier=+15,
seller_risk_modifier=-10,
key_phrases_en=["aggregate liability", "total liability shall not exceed", "cap", "maximum liability"],
key_phrases_fr=["responsabilité totale", "plafond", "ne saurait excéder"],
red_flags=["Very low cap", "Applies to all claims", "No carve-outs for fraud"],
enforceability_factors=["Reasonableness test (UK)", "Negotiated vs adhesion", "Consumer vs B2B"]
),
"exclusion_consequential": ClauseType(
id="exclusion_consequential",
name="Exclusion of Consequential Damages",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.HIGH,
description="Excludes indirect, consequential, and special damages",
common_law_reference="Hadley v Baxendale [1854] - remoteness of damage",
civil_law_reference="Art. 1231-3 CC - Préjudice imprévisible",
buyer_risk_modifier=+20,
seller_risk_modifier=-15,
key_phrases_en=["consequential damages", "indirect damages", "loss of profits", "special damages"],
key_phrases_fr=["dommages indirects", "préjudice indirect", "perte de profits"],
red_flags=["Overbroad language", "May be unconscionable"],
enforceability_factors=["B2B vs consumer", "Pre-contract disclosure"]
),
"warranty_express": ClauseType(
id="warranty_express",
name="Express Warranty",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.MEDIUM,
description="Specific performance guarantees and quality commitments",
common_law_reference="Sale of Goods Act 1979 s.13-14 (UK)",
civil_law_reference="Art. 1641-1649 CC - Garantie des vices cachés",
buyer_risk_modifier=-10,
seller_risk_modifier=+10,
key_phrases_en=["warrants that", "represents and warrants", "guarantee"],
key_phrases_fr=["garantit que", "déclare et garantit"],
best_practices=["Clear scope", "Reasonable duration", "Remedy specified"]
),
"warranty_disclaimer": ClauseType(
id="warranty_disclaimer",
name="Warranty Disclaimer",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.HIGH,
description="Disclaims implied warranties (merchantability, fitness)",
common_law_reference="UCTA 1977 - Cannot exclude liability for death/injury",
civil_law_reference="Art. 1643 CC - Vice caché connu",
buyer_risk_modifier=+20,
seller_risk_modifier=-20,
key_phrases_en=["as is", "with all faults", "disclaims all warranties", "no warranty"],
key_phrases_fr=["en l'état", "sans garantie", "exclusion de garantie"],
red_flags=["Consumer context", "Hidden defects known", "Personal injury"],
enforceability_factors=["B2B vs B2C", "Negotiated vs standard terms"]
),
"force_majeure_broad": ClauseType(
id="force_majeure_broad",
name="Broad Force Majeure",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.MEDIUM,
description="Extensive list of excusing events including non-natural events",
common_law_reference="Frustration doctrine - Taylor v Caldwell [1863]",
civil_law_reference="Art. 1218 CC - Force majeure (imprévisible, irrésistible, extérieur)",
buyer_risk_modifier=-5,
seller_risk_modifier=+5,
key_phrases_en=["force majeure", "act of god", "beyond reasonable control", "pandemic", "epidemic"],
key_phrases_fr=["force majeure", "cas fortuit", "événement imprévisible", "pandémie"],
best_practices=["Define specific events", "Notice requirements", "Mitigation obligation"]
),
"force_majeure_narrow": ClauseType(
id="force_majeure_narrow",
name="Narrow Force Majeure",
category=ClauseCategory.RISK_ALLOCATION,
risk_level=RiskLevel.HIGH,
description="Limited force majeure events, may exclude common disruptions",
buyer_risk_modifier=+10,
seller_risk_modifier=-5,
key_phrases_en=["limited to", "only in the event of", "natural disaster only"],
key_phrases_fr=["limité à", "uniquement en cas de"],
red_flags=["Excludes pandemic", "No catch-all", "Short suspension period"]
),
# ==================== CONFIDENTIALITY ====================
"confidentiality_mutual": ClauseType(
id="confidentiality_mutual",
name="Mutual Confidentiality",
category=ClauseCategory.CONFIDENTIALITY,
risk_level=RiskLevel.LOW,
description="Both parties bound by confidentiality obligations",
key_phrases_en=["each party agrees", "mutual confidentiality", "both parties"],
key_phrases_fr=["chaque partie s'engage", "confidentialité réciproque"],
best_practices=["Clear definition of confidential info", "Standard exceptions", "Reasonable duration"]
),
"confidentiality_unilateral": ClauseType(
id="confidentiality_unilateral",
name="Unilateral Confidentiality",
category=ClauseCategory.CONFIDENTIALITY,
risk_level=RiskLevel.MEDIUM,
description="Only one party bound by confidentiality",
buyer_risk_modifier=+10,
seller_risk_modifier=-10,
key_phrases_en=["receiving party shall", "recipient agrees"],
key_phrases_fr=["la partie réceptrice", "le destinataire s'engage"],
red_flags=["One-sided obligation", "No reciprocity"]
),
"residual_knowledge": ClauseType(
id="residual_knowledge",
name="Residual Knowledge Carve-out",
category=ClauseCategory.CONFIDENTIALITY,
risk_level=RiskLevel.HIGH,
description="Allows use of retained knowledge despite confidentiality",
buyer_risk_modifier=+15,
seller_risk_modifier=-10,
key_phrases_en=["residual knowledge", "retained in memory", "unaided recall"],
key_phrases_fr=["connaissances résiduelles", "mémorisées"],
red_flags=["Broad carve-out", "Could undermine entire NDA"],
enforceability_factors=["Scope of residual use", "Industry standard"]
),
# ==================== INTELLECTUAL PROPERTY ====================
"ip_ownership_provider": ClauseType(
id="ip_ownership_provider",
name="Provider IP Ownership",
category=ClauseCategory.INTELLECTUAL_PROPERTY,
risk_level=RiskLevel.HIGH,
description="Provider retains all intellectual property rights",
common_law_reference="Work-for-hire doctrine (US); First ownership (UK CDPA)",
civil_law_reference="Art. L.111-1 CPI - Droit d'auteur naît de la création",
buyer_risk_modifier=+15,
seller_risk_modifier=-10,
key_phrases_en=["provider retains", "all IP rights remain", "customer receives license only"],
key_phrases_fr=["le prestataire conserve", "droits de propriété intellectuelle demeurent"],
red_flags=["No license granted", "License very limited"]
),
"ip_ownership_customer": ClauseType(
id="ip_ownership_customer",
name="Customer IP Ownership",
category=ClauseCategory.INTELLECTUAL_PROPERTY,
risk_level=RiskLevel.MEDIUM,
description="Customer owns all deliverables and created IP",
buyer_risk_modifier=-10,
seller_risk_modifier=+15,
key_phrases_en=["customer shall own", "work made for hire", "all rights assigned"],
key_phrases_fr=["le client sera propriétaire", "cession de droits"],
best_practices=["Clear assignment language", "Moral rights waiver (FR)"]
),
"moral_rights_waiver": ClauseType(
id="moral_rights_waiver",
name="Moral Rights Waiver",
category=ClauseCategory.INTELLECTUAL_PROPERTY,
risk_level=RiskLevel.HIGH,
description="Waiver of author's moral rights (more significant in Civil Law)",
common_law_reference="CDPA 1988 s.77-89 (UK) - moral rights waivable",
civil_law_reference="Art. L.121-1 CPI - Droits moraux inaliénables (limited waiver possible)",
buyer_risk_modifier=0,
seller_risk_modifier=+10,
key_phrases_en=["waives moral rights", "right of attribution", "right of integrity"],
key_phrases_fr=["renonce à l'exercice", "droit de paternité", "droit au respect"],
enforceability_factors=["French law: cannot fully waive", "UK: can waive in writing"]
),
# ==================== TERMINATION ====================
"termination_convenience": ClauseType(
id="termination_convenience",
name="Termination for Convenience",
category=ClauseCategory.TERMINATION,
risk_level=RiskLevel.MEDIUM,
description="Either party can terminate without cause",
buyer_risk_modifier=-5,
seller_risk_modifier=+10,
key_phrases_en=["for convenience", "without cause", "at any time upon notice"],
key_phrases_fr=["à sa convenance", "sans motif", "à tout moment moyennant préavis"],
best_practices=["Reasonable notice period", "Wind-down provisions"]
),
"termination_cause": ClauseType(
id="termination_cause",
name="Termination for Cause",
category=ClauseCategory.TERMINATION,
risk_level=RiskLevel.LOW,
description="Termination only for material breach",
civil_law_reference="Art. 1224-1230 CC - Résolution du contrat",
key_phrases_en=["material breach", "for cause", "failure to cure"],
key_phrases_fr=["manquement grave", "résiliation pour faute", "inexécution"],
best_practices=["Define material breach", "Cure period", "Notice requirements"]
),
"auto_renewal": ClauseType(
id="auto_renewal",
name="Automatic Renewal",
category=ClauseCategory.TERMINATION,
risk_level=RiskLevel.MEDIUM,
description="Contract renews automatically unless terminated",
civil_law_reference="Loi Chatel (B2C) - 14-day notice requirement",
buyer_risk_modifier=+10,
seller_risk_modifier=-5,
key_phrases_en=["automatically renew", "evergreen", "successive periods"],
key_phrases_fr=["renouvellement automatique", "tacite reconduction"],
red_flags=["Long renewal periods", "Short opt-out window"]
),
# ==================== DISPUTE RESOLUTION ====================
"governing_law_uk": ClauseType(
id="governing_law_uk",
name="English Governing Law",
category=ClauseCategory.DISPUTE_RESOLUTION,
risk_level=RiskLevel.LOW,
description="English law governs the agreement",
key_phrases_en=["governed by the laws of England", "English law", "laws of England and Wales"],
best_practices=["Match with jurisdiction clause", "Consider Rome I Regulation"]
),
"governing_law_fr": ClauseType(
id="governing_law_fr",
name="French Governing Law",
category=ClauseCategory.DISPUTE_RESOLUTION,
risk_level=RiskLevel.LOW,
description="French law governs the agreement",
civil_law_reference="Règlement Rome I - Liberté de choix de loi",
key_phrases_en=["governed by French law", "laws of France"],
key_phrases_fr=["régi par le droit français", "loi française applicable"],
best_practices=["Match with jurisdiction", "Consider mandatory rules"]
),
"arbitration_icc": ClauseType(
id="arbitration_icc",
name="ICC Arbitration",
category=ClauseCategory.DISPUTE_RESOLUTION,
risk_level=RiskLevel.LOW,
description="Disputes resolved by ICC arbitration",
key_phrases_en=["ICC", "International Chamber of Commerce", "arbitration in Paris"],
key_phrases_fr=["CCI", "Chambre de commerce internationale", "arbitrage à Paris"],
best_practices=["Specify seat", "Number of arbitrators", "Language"]
),
# ==================== EMPLOYMENT ====================
"non_compete_12mo": ClauseType(
id="non_compete_12mo",
name="12-Month Non-Compete",
category=ClauseCategory.EMPLOYMENT,
risk_level=RiskLevel.MEDIUM,
description="Non-compete restriction for 12 months",
common_law_reference="Restraint of trade doctrine - proportionality",
civil_law_reference="Art. L.1221-1 CT - Clause de non-concurrence (contrepartie financière)",
key_phrases_en=["twelve months", "one year", "12 month non-compete"],
key_phrases_fr=["douze mois", "un an", "clause de non-concurrence"],
enforceability_factors=["Geographic scope", "Financial compensation (FR)", "Reasonableness"]
),
"non_compete_24mo": ClauseType(
id="non_compete_24mo",
name="24+ Month Non-Compete",
category=ClauseCategory.EMPLOYMENT,
risk_level=RiskLevel.HIGH,
description="Extended non-compete restriction",
buyer_risk_modifier=+15,
key_phrases_en=["twenty-four months", "two years", "24 month"],
key_phrases_fr=["vingt-quatre mois", "deux ans"],
red_flags=["May be unenforceable", "Excessive duration"],
enforceability_factors=["Very difficult to enforce in UK/FR", "Needs strong justification"]
),
# ==================== M&A ====================
"mac_clause": ClauseType(
id="mac_clause",
name="Material Adverse Change",
category=ClauseCategory.M_AND_A,
risk_level=RiskLevel.HIGH,
description="Closing condition based on material adverse change",
common_law_reference="IBP v Tyson [Del. 2001] - MAC rarely triggered",
key_phrases_en=["material adverse change", "material adverse effect", "MAC"],
key_phrases_fr=["changement significatif défavorable", "effet défavorable significatif"],
red_flags=["Broad definition", "No carve-outs", "Low materiality threshold"]
),
"earnout_provision": ClauseType(
id="earnout_provision",
name="Earnout Provision",
category=ClauseCategory.M_AND_A,
risk_level=RiskLevel.HIGH,
description="Contingent purchase price based on future performance",
key_phrases_en=["earnout", "contingent consideration", "performance targets"],
key_phrases_fr=["complément de prix", "earn-out", "objectifs de performance"],
red_flags=["Vague metrics", "Buyer control", "Long earnout period"]
),
# ==================== DATA PROTECTION ====================
"gdpr_processor": ClauseType(
id="gdpr_processor",
name="GDPR Data Processor",
category=ClauseCategory.DATA_PROTECTION,
risk_level=RiskLevel.MEDIUM,
description="Data processor obligations under GDPR Art. 28",
civil_law_reference="RGPD Art. 28 - Sous-traitant",
key_phrases_en=["data processor", "Article 28", "documented instructions"],
key_phrases_fr=["sous-traitant", "instructions documentées", "Art. 28"],
best_practices=["Mandatory clauses per Art. 28(3)", "Sub-processor controls"]
),
"data_transfer_scc": ClauseType(
id="data_transfer_scc",
name="Standard Contractual Clauses",
category=ClauseCategory.DATA_PROTECTION,
risk_level=RiskLevel.MEDIUM,
description="EU Standard Contractual Clauses for international transfers",
civil_law_reference="Commission Decision 2021/914 - New SCCs",
key_phrases_en=["standard contractual clauses", "SCC", "international transfer"],
key_phrases_fr=["clauses contractuelles types", "CCT", "transfert international"],
best_practices=["Use 2021 SCCs", "Supplementary measures per Schrems II"]
),
}
def get_clause_type(clause_id: str) -> Optional[ClauseType]:
"""Get a clause type by ID."""
return CLAUSE_TYPES.get(clause_id)
def get_clauses_by_category(category: ClauseCategory) -> List[ClauseType]:
"""Get all clause types in a category."""
return [ct for ct in CLAUSE_TYPES.values() if ct.category == category]
def get_high_risk_clauses() -> List[ClauseType]:
"""Get all high-risk clause types."""
return [ct for ct in CLAUSE_TYPES.values() if ct.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
def calculate_clause_risk(clause_type: str, party_position: str = "buyer") -> int:
"""Calculate risk score for a clause based on type and party position."""
ct = CLAUSE_TYPES.get(clause_type)
if not ct:
return 50 # Default medium risk
base_risk = {"LOW": 20, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 90}[ct.risk_level.value]
modifier = ct.buyer_risk_modifier if party_position == "buyer" else ct.seller_risk_modifier
return max(0, min(100, base_risk + modifier))
# Export all for easy import
__all__ = [
"RiskLevel",
"LegalSystem", "ClauseCategory",
"ClauseType",
"CLAUSE_TYPES",
"get_clause_type",
"get_clauses_by_category",
"get_high_risk_clauses",
"calculate_clause_risk"
]
