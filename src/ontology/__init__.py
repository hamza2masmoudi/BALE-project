"""BALE Ontology Module."""
import enum
from typing import Optional
from pydantic import BaseModel
from src.ontology.legal_ontology import (
PartyRole,
ObligationType,
RightType,
ClauseCategory,
RiskFactor,
Jurisdiction,
Obligation,
Right,
Clause,
Party,
ContractOntology,
CLAUSE_EXPECTATIONS,
RISK_FACTOR_WEIGHTS,
LEGAL_REGIME_CHANGES,
get_clause_expectations,
get_risk_weight,
)
# Legacy classes (previously in src/ontology.py, re-defined here for backward compatibility)
class LegalSystem(str, enum.Enum):
CIVIL_LAW = "CIVIL_LAW"
COMMON_LAW = "COMMON_LAW"
class AuthorityLevel(int, enum.Enum):
CONSTITUTIONAL = 100
STATUTORY = 90
REGULATORY = 80
SUPREME_COURT = 70
APPELLATE_COURT = 60
TRIAL_COURT = 50
DOCTRINE = 40
CONTRACTUAL = 30
class BindingStatus(str, enum.Enum):
MANDATORY = "MANDATORY"
DEFAULT = "DEFAULT"
PERSUASIVE = "PERSUASIVE"
DISTINGUISHABLE = "DISTINGUISHABLE"
class LegalNode(BaseModel):
"""Represents a unit of legal knowledge in the graph."""
id: str
text_content: str
system: LegalSystem
authority_level: AuthorityLevel
binding_status: BindingStatus = BindingStatus.DEFAULT
citation: Optional[str] = None
date: Optional[str] = None
def calculate_weight(self) -> float:
base_weight = self.authority_level.value / 100.0
if self.binding_status == BindingStatus.MANDATORY:
base_weight *= 1.5
elif self.binding_status == BindingStatus.PERSUASIVE:
base_weight *= 0.7
return min(base_weight, 1.0)
__all__ = [
"PartyRole",
"ObligationType", "RightType",
"ClauseCategory",
"RiskFactor",
"Jurisdiction",
"Obligation",
"Right",
"Clause",
"Party",
"ContractOntology",
"CLAUSE_EXPECTATIONS",
"RISK_FACTOR_WEIGHTS",
"LEGAL_REGIME_CHANGES",
"get_clause_expectations",
"get_risk_weight",
# Legacy exports
"LegalNode",
"LegalSystem", "AuthorityLevel",
"BindingStatus",
]
