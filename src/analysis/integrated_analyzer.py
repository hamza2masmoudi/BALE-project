"""
BALE Integrated Analysis Engine
Combines LLM clause analysis with novel frontier algorithms.
This is the production-ready analysis pipeline with all IP components.
"""
import json
import os
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from dotenv import load_dotenv
from src.logger import setup_logger
from src.analysis.clause_analyzer import ClauseAnalyzer, ClauseRisk, ContractAnalysis
from src.algorithms.novel_frontiers import (
NovelFrontierAnalyzer,
NovelAnalysisResult,
novel_analyzer
)
from src.ontology import (
ClauseCategory,
RiskFactor,
Jurisdiction,
get_clause_expectations
)
load_dotenv()
logger = setup_logger("integrated_analysis")
@dataclass
class IntegratedAnalysisResult:
"""
Complete analysis result combining LLM and novel algorithms.
This is BALE's core value proposition.
"""
contract_id: str
timestamp: str
# LLM Clause Analysis
llm_risk_score: int
llm_risk_level: str
clauses_analyzed: int
high_risk_clauses: List[Dict]
critical_issues: List[str]
recommendations: List[str]
# Novel Algorithm Results
silence_score: float
missing_clauses: List[str]
power_asymmetry: float
favored_party: str
temporal_decay: float
strain_score: float
# Combined Score (The IP)
combined_risk_score: float
risk_breakdown: Dict[str, float]
primary_concerns: List[str]
# Meta
analysis_mode: str # "full", "llm_only", "algorithms_only"
def to_dict(self) -> Dict[str, Any]:
return asdict(self)
def to_json(self, indent: int = 2) -> str:
return json.dumps(self.to_dict(), indent=indent)
class IntegratedAnalyzer:
"""
Production-ready analyzer combining:
1. LLM-powered clause analysis (structured prompts)
2. Novel frontier algorithms (Bayesian, graph, temporal, deontic)
This represents BALE's core differentiating IP.
"""
def __init__(self, mode: str = "auto"):
"""
Initialize the integrated analyzer.
Args:
mode: LLM mode - "auto", "mistral", or "local"
"""
self.clause_analyzer = ClauseAnalyzer(mode=mode)
self.novel_analyzer = novel_analyzer
self.mode = mode
logger.info(f"IntegratedAnalyzer initialized in {mode} mode")
def analyze(
self,
contract_text: str,
contract_type: str = "msa",
jurisdiction: str = "US",
contract_date: str = None,
parties: List[str] = None,
contract_id: str = None
) -> IntegratedAnalysisResult:
"""
Run complete integrated analysis.
This combines:
- LLM clause-by-clause analysis
- Novel frontier algorithms
Returns a unified result with combined risk scoring.
"""
if not contract_id:
contract_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
if not contract_date:
contract_date = datetime.utcnow().isoformat()[:10]
if not parties:
parties = ["Party A", "Party B"]
logger.info(f"Starting integrated analysis for {contract_id}")
# Step 1: LLM Clause Analysis
logger.info("Running LLM clause analysis...")
try:
llm_result = self.clause_analyzer.analyze_contract(
contract_text=contract_text,
contract_id=contract_id
)
llm_success = True
except Exception as e:
logger.error(f"LLM analysis failed: {e}")
llm_result = None
llm_success = False
# Step 2: Extract clause data for novel algorithms
if llm_success and llm_result:
present_clauses = set(c.clause_type for c in (
llm_result.high_risk_clauses + llm_result.medium_risk_clauses + llm_result.low_risk_clauses
))
clause_analyses = [
{
"category": c.clause_type,
"who_benefits": c.who_benefits,
"text": c.clause_text,
"risk_score": c.risk_score
}
for c in (
llm_result.high_risk_clauses + llm_result.medium_risk_clauses + llm_result.low_risk_clauses
)
]
else:
# Fallback: extract clause types from text patterns
present_clauses = self._extract_clause_types_fallback(contract_text)
clause_analyses = []
# Step 3: Novel Algorithm Analysis
logger.info("Running novel frontier algorithms...")
novel_result = self.novel_analyzer.analyze(
contract_type=contract_type,
present_clauses=present_clauses,
clause_analyses=clause_analyses,
parties=parties,
contract_date=contract_date,
jurisdiction=jurisdiction
)
# Step 4: Compute Combined Risk Score
# This is the core IP - weighted combination of signals
if llm_success and llm_result:
llm_risk = llm_result.overall_risk
else:
llm_risk = 50 # Default
combined_risk = self._compute_combined_risk(
llm_risk=llm_risk,
silence_score=novel_result.silence_score,
power_asymmetry=novel_result.power_asymmetry,
temporal_decay=novel_result.temporal_decay,
strain_score=novel_result.strain_score
)
# Build result
return IntegratedAnalysisResult(
contract_id=contract_id,
timestamp=datetime.utcnow().isoformat(),
# LLM Results
llm_risk_score=llm_result.overall_risk if llm_success else 0,
llm_risk_level=llm_result.risk_level if llm_success else "unknown",
clauses_analyzed=llm_result.clauses_analyzed if llm_success else 0,
high_risk_clauses=[
{
"type": c.clause_type,
"risk": c.risk_score,
"issues": c.issues[:2]
}
for c in (llm_result.high_risk_clauses if llm_success else [])
],
critical_issues=llm_result.critical_issues if llm_success else [],
recommendations=llm_result.recommendations if llm_success else [],
# Novel Algorithm Results
silence_score=novel_result.silence_score,
missing_clauses=[m.missing_clause for m in novel_result.missing_clauses[:5]],
power_asymmetry=novel_result.power_asymmetry,
favored_party=novel_result.power_result.favored_party,
temporal_decay=novel_result.temporal_decay,
strain_score=novel_result.strain_score,
# Combined
combined_risk_score=combined_risk["score"],
risk_breakdown=combined_risk["breakdown"],
primary_concerns=novel_result.primary_concerns + (
llm_result.critical_issues[:2] if llm_success else []
),
analysis_mode="full" if llm_success else "algorithms_only"
)
def _compute_combined_risk(
self,
llm_risk: float,
silence_score: float,
power_asymmetry: float,
temporal_decay: float,
strain_score: float
) -> Dict[str, Any]:
"""
Compute weighted combined risk score.
This is the proprietary risk formula that combines all signals.
"""
# Normalize inputs to 0-100 scale
silence_normalized = min(silence_score * 5, 100) # Surprise score to percentage
power_normalized = power_asymmetry * 100
decay_normalized = temporal_decay
strain_normalized = strain_score
# Weights (tuned based on importance)
weights = {
"llm_analysis": 0.40, # LLM clause understanding
"silence": 0.15, # Missing clauses
"power_asymmetry": 0.20, # Unbalanced obligations
"temporal_decay": 0.15, # Staleness
"strain": 0.10 # Logical conflicts
}
# Weighted combination
combined = (
llm_risk * weights["llm_analysis"] +
silence_normalized * weights["silence"] +
power_normalized * weights["power_asymmetry"] +
decay_normalized * weights["temporal_decay"] +
strain_normalized * weights["strain"]
)
return {
"score": min(combined, 100),
"breakdown": {
"llm_analysis": llm_risk,
"silence_detection": silence_normalized,
"power_asymmetry": power_normalized,
"temporal_decay": decay_normalized,
"strain_detection": strain_normalized
}
}
def _extract_clause_types_fallback(self, text: str) -> Set[str]:
"""Fallback clause extraction when LLM unavailable."""
patterns = {
"confidentiality": ["confidential", "non-disclosure", "nda"],
"indemnification": ["indemnify", "hold harmless", "indemnification"],
"liability": ["liability", "limitation of liability", "damages"],
"termination": ["termination", "terminate", "cancel"],
"governing_law": ["governing law", "jurisdiction", "venue"],
"warranty": ["warranty", "warrants", "represents"],
"ip_ownership": ["intellectual property", "ip", "work product"],
"non_compete": ["non-compete", "competitive", "not engage"],
"data_protection": ["personal data", "gdpr", "privacy"],
"force_majeure": ["force majeure", "act of god"],
}
text_lower = text.lower()
found = set()
for clause_type, keywords in patterns.items():
if any(kw in text_lower for kw in keywords):
found.add(clause_type)
return found
def save_training_data(self, filepath: str = "training_data/integrated_analysis.jsonl"):
"""Save collected training data from LLM interactions."""
self.clause_analyzer.save_training_data_to_file(filepath)
# Singleton instance for production use
integrated_analyzer = IntegratedAnalyzer(mode="auto")
def analyze_contract_full(
contract_text: str,
contract_type: str = "msa",
jurisdiction: str = "US",
contract_date: str = None,
parties: List[str] = None
) -> IntegratedAnalysisResult:
"""
Convenience function for full integrated analysis.
This is the main entry point for BALE analysis.
"""
return integrated_analyzer.analyze(
contract_text=contract_text,
contract_type=contract_type,
jurisdiction=jurisdiction,
contract_date=contract_date,
parties=parties
)
