import enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

class LegalSystem(str, enum.Enum):
    CIVIL_LAW = "CIVIL_LAW"
    COMMON_LAW = "COMMON_LAW"

class AuthorityLevel(int, enum.Enum):
    # Higher is more authoritative
    CONSTITUTIONAL = 100
    STATUTORY = 90      # Acts of Parliament / Code Civil
    REGULATORY = 80     # Decrees
    SUPREME_COURT = 70  # Cass. / Supreme Court
    APPELLATE_COURT = 60
    TRIAL_COURT = 50
    DOCTRINE = 40       # Academic opinion
    CONTRACTUAL = 30    # The contract itself (law of the parties)

class BindingStatus(str, enum.Enum):
    MANDATORY = "MANDATORY"       # Must be followed (Ordre Public)
    DEFAULT = "DEFAULT"           # Applies unless excluded (Suppletive)
    PERSUASIVE = "PERSUASIVE"     # Good to know (Foreign case law)
    DISTINGUISHABLE = "DISTINGUISHABLE"

class LegalNode(BaseModel):
    """
    Represents a unit of legal knowledge in the graph.
    """
    id: str
    text_content: str
    system: LegalSystem
    authority_level: AuthorityLevel
    binding_status: BindingStatus = BindingStatus.DEFAULT
    citation: Optional[str] = None
    date: Optional[str] = None

    def calculate_weight(self) -> float:
        """
        Returns a normalized weight (0-1.0) for retrieval boosting.
        """
        base_weight = self.authority_level.value / 100.0
        if self.binding_status == BindingStatus.MANDATORY:
            base_weight *= 1.5
        elif self.binding_status == BindingStatus.PERSUASIVE:
            base_weight *= 0.7
        
        return min(base_weight, 1.0)
