"""
BALE Frontier Analysis Package
10 second-order legal intelligence capabilities.
"""
from .core import (
corpus, CorpusTracker, ContractMetadata, ContractType,
ClauseTemplate, TemporalSnapshot, EntityProfile, EXPECTED_CLAUSES
)
from .silence_archaeology import (
silence_detector, archaeologist, SilenceAnalysis, ArchaeologyAnalysis
)
from .temporal_network import (
temporal_tracker, network_analyzer, TemporalDecayAnalysis, NetworkInference
)
from .strain_social import (
strain_detector, social_analyzer, StrainAnalysis, SocialStructureAnalysis
)
from .ambiguity_dispute import (
ambiguity_tracker, dispute_predictor, AmbiguityAnalysis, DisputeCartography
)
from .imagination_reflexive import (
imagination_analyzer, reflexive_monitor, ImaginationAnalysis, ReflexiveAnalysis
)
from .api import (
frontier_analyzer, FrontierAnalyzer, FrontierAnalysisRequest,
ComprehensiveFrontierAnalysis, analyze_contract_frontiers
)
__all__ = [
# Core
"corpus", "CorpusTracker", "ContractMetadata", "ContractType",
"EXPECTED_CLAUSES",
# I & II: Silence & Archaeology
"silence_detector", "archaeologist",
"SilenceAnalysis", "ArchaeologyAnalysis",
# III & IV: Temporal & Network
"temporal_tracker", "network_analyzer",
"TemporalDecayAnalysis", "NetworkInference",
# V & VI: Strain & Social
"strain_detector", "social_analyzer",
"StrainAnalysis", "SocialStructureAnalysis",
# VII & VIII: Ambiguity & Dispute
"ambiguity_tracker", "dispute_predictor",
"AmbiguityAnalysis", "DisputeCartography",
# IX & X: Imagination & Reflexive
"imagination_analyzer", "reflexive_monitor",
"ImaginationAnalysis", "ReflexiveAnalysis",
# Unified API
"frontier_analyzer", "analyze_contract_frontiers",
"FrontierAnalysisRequest", "ComprehensiveFrontierAnalysis",
]
