"""
BALE V8 Unified Analyzer
Integrates all V8 components for comprehensive contract analysis.
"""
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from src.logger import setup_logger
from src.ontology.clause_ontology import CLAUSE_TYPES, get_clause_type, calculate_clause_risk
from src.specialist_agents import SpecialistRouter
from src.explainability_v8 import (
ExplainableVerdictBuilder, LegalCitation,
get_relevant_citations
)
from src.risk_model_v8 import (
LitigationRiskModel,
ClauseRiskCalculator,
PartyPosition,
get_risk_model,
get_clause_calculator
)
from src.types import BaleState
logger = setup_logger("bale_v8_analyzer")
@dataclass
class V8AnalysisResult:
"""Complete V8 analysis result."""
clause_id: str
clause_text: str
# Classification
clause_type: str
clause_category: str
# Risk assessment
risk_score: float
risk_level: str
uk_risk: float
fr_risk: float
# Confidence
confidence: float
confidence_lower: float
confidence_upper: float
# Problems and recommendations
problems: List[str]
recommendations: List[str]
# Legal citations
citations: List[Dict]
# Specialist analyses
specialist_analyses: Dict[str, str]
specialists_used: List[str]
# Litigation prediction
outcome_probabilities: Dict[str, float]
expected_costs: tuple
expected_duration_months: tuple
# Explainability
reasoning_steps: List[Dict]
risk_factors: List[Dict]
# Audit
analysis_time_ms: int
model_version: str = "V8"
decision_hash: str = ""
class BALEV8Analyzer:
"""
BALE V8 Unified Analyzer
Integrates:
- Clause classification (75 types)
- Specialist agents (M&A, Data Privacy, Employment, Dispute)
- Probabilistic risk model
- Explainable AI with citations
- FR/UK dual jurisdiction analysis
"""
def __init__(self):
self.specialist_router = SpecialistRouter()
self.risk_model = get_risk_model()
self.clause_calculator = get_clause_calculator()
logger.info("BALE V8 Analyzer initialized")
def classify_clause(self, clause_text: str) -> tuple:
"""Classify a clause into one of 75 types."""
clause_lower = clause_text.lower()
# Score each clause type based on keyword matching
scores = {}
for clause_id, clause_type in CLAUSE_TYPES.items():
score = 0
# Check key phrases
if clause_type.key_phrases_en:
for phrase in clause_type.key_phrases_en:
if phrase.lower() in clause_lower:
score += 10
if clause_type.key_phrases_fr:
for phrase in clause_type.key_phrases_fr:
if phrase.lower() in clause_lower:
score += 10
if score > 0:
scores[clause_id] = score
# Get best match
if scores:
best_match = max(scores, key=scores.get)
clause_type = CLAUSE_TYPES[best_match]
return best_match, clause_type.category.value, scores[best_match]
return "unknown", "GENERAL", 0
def detect_problems(self, clause_type: str, clause_text: str) -> List[str]:
"""Detect potential problems in a clause."""
problems = []
clause_lower = clause_text.lower()
ct = get_clause_type(clause_type)
if ct and ct.red_flags:
for flag in ct.red_flags:
if any(word in clause_lower for word in flag.lower().split()):
problems.append(flag)
# Generic problem detection
if "all claims" in clause_lower and "indemnif" in clause_lower:
problems.append("Overly broad indemnification scope")
if "no liability" in clause_lower or "exclude all" in clause_lower:
problems.append("May attempt to exclude mandatory liability")
if "perpetual" in clause_lower and ("non-compete" in clause_lower or "confidential" in clause_lower):
problems.append("Perpetual restriction may be unenforceable")
if "24 month" in clause_lower or "two year" in clause_lower:
if "non-compete" in clause_lower or "non-concurrence" in clause_lower:
problems.append("Extended non-compete may be unenforceable in UK/FR")
return problems
def generate_recommendations(self, clause_type: str, problems: List[str], party: str = "buyer") -> List[str]:
"""Generate recommendations for improving a clause."""
recommendations = []
ct = get_clause_type(clause_type)
if ct and ct.best_practices:
recommendations.extend(ct.best_practices)
# Problem-specific recommendations
for problem in problems:
if "broad" in problem.lower():
recommendations.append("Negotiate narrower scope with specific exclusions")
if "unenforceable" in problem.lower():
recommendations.append("Consider more market-standard terms")
if "liability" in problem.lower():
recommendations.append("Add reasonable cap on liability (e.g., 100% of fees)")
if "non-compete" in problem.lower():
recommendations.append("FR: Ensure financial compensation clause exists")
return list(set(recommendations)) # Dedupe
def analyze_clause(
self,
clause_text: str,
clause_id: str = "clause_1",
party: PartyPosition = PartyPosition.BUYER,
contract_value: float = 1000000,
run_specialists: bool = True
) -> V8AnalysisResult:
"""
Perform comprehensive V8 analysis on a clause.
Args:
clause_text: The clause text to analyze
clause_id: Identifier for the clause
party: Party position (BUYER, SELLER, etc.)
contract_value: Value of the contract for cost estimation
run_specialists: Whether to run specialist agents
Returns:
V8AnalysisResult with complete analysis
"""
start_time = time.time()
# Build explainable verdict
builder = ExplainableVerdictBuilder(clause_id, clause_text)
# Step 1: Classify clause
builder.add_reasoning_step(
action="Clause Classification",
result="Analyzing clause type using ontology matching",
agent="Classifier"
)
clause_type, category, confidence_score = self.classify_clause(clause_text)
builder.set_clause_type(clause_type)
builder.add_reasoning_step(
action="Classification Complete",
result=f"Identified as {clause_type} ({category})",
agent="Classifier"
)
# Step 2: Calculate base risk
uk_risk_data = self.clause_calculator.calculate(clause_type, party, "UK")
fr_risk_data = self.clause_calculator.calculate(clause_type, party, "FR")
builder.add_reasoning_step(
action="Risk Calculation",
result=f"UK Risk: {uk_risk_data['risk_score']:.0f}%, FR Risk: {fr_risk_data['risk_score']:.0f}%",
agent="RiskModel"
)
# Add risk factors
ct = get_clause_type(clause_type)
if ct:
if ct.risk_level.value == "HIGH":
builder.add_risk_factor(
name="high_risk_clause_type",
description=f"{clause_type} is inherently high risk",
contribution=+15,
confidence=0.9
)
elif ct.risk_level.value == "MEDIUM":
builder.add_risk_factor(
name="medium_risk_clause_type",
description=f"{clause_type} has moderate risk",
contribution=+5,
confidence=0.85
)
# Step 3: Detect problems
problems = self.detect_problems(clause_type, clause_text)
for problem in problems:
builder.add_problem(problem)
builder.add_risk_factor(
name="problem_detected",
description=problem,
contribution=+5,
confidence=0.8
)
builder.add_reasoning_step(
action="Problem Detection",
result=f"Found {len(problems)} potential issues",
agent="ProblemDetector"
)
# Step 4: Get relevant citations
builder.add_citations_for_type(clause_type)
# Step 5: Run specialist agents if enabled
specialist_analyses = {}
specialists_used = []
if run_specialists:
state = BaleState(
raw_clause=clause_text,
inference_mode="local"
)
try:
agents_to_run = self.specialist_router.route(clause_text)
if agents_to_run and agents_to_run != ["general"]:
builder.add_reasoning_step(
action="Specialist Analysis",
result=f"Routing to specialists: {', '.join(agents_to_run)}",
agent="Router"
)
state = self.specialist_router.analyze(state)
specialist_analyses = state.get("specialist_analyses", {})
specialists_used = state.get("specialists_used", [])
for specialist, analysis in specialist_analyses.items():
builder.add_specialist_analysis(specialist, analysis)
except Exception as e:
logger.warning(f"Specialist analysis failed: {e}")
# Step 6: Generate recommendations
recommendations = self.generate_recommendations(clause_type, problems, party.value.lower())
for rec in recommendations:
builder.add_recommendation(rec)
# Step 7: Build verdict
verdict = builder.build()
# Step 8: Get litigation prediction
factors = {
"ambiguity_score": 0.3 if len(problems) > 0 else 0.1,
"exclusion_validity": 0.7 if "exclusion" in clause_type else 0.3,
"drafting_quality": 0.6,
"overall_balance": 0.5
}
prediction = self.risk_model.predict(
factors=factors,
party=party,
jurisdiction="UK",
contract_value=contract_value
)
# Calculate analysis time
analysis_time_ms = int((time.time() - start_time) * 1000)
return V8AnalysisResult(
clause_id=clause_id,
clause_text=clause_text,
clause_type=clause_type,
clause_category=category,
risk_score=verdict.risk_score,
risk_level=verdict.risk_level,
uk_risk=uk_risk_data["risk_score"],
fr_risk=fr_risk_data["risk_score"],
confidence=verdict.confidence_score,
confidence_lower=verdict.confidence_lower,
confidence_upper=verdict.confidence_upper,
problems=verdict.problems_detected,
recommendations=verdict.recommendations,
citations=[c.to_dict() for c in verdict.citations],
specialist_analyses=specialist_analyses,
specialists_used=specialists_used,
outcome_probabilities=prediction.outcome_probabilities,
expected_costs=prediction.expected_legal_costs,
expected_duration_months=prediction.expected_duration_months,
reasoning_steps=[s.to_dict() for s in verdict.reasoning_steps],
risk_factors=[f.to_dict() for f in verdict.risk_factors],
analysis_time_ms=analysis_time_ms,
decision_hash=verdict.decision_hash
)
def analyze_contract(
self,
clauses: List[str],
party: PartyPosition = PartyPosition.BUYER,
contract_value: float = 1000000
) -> Dict[str, Any]:
"""
Analyze all clauses in a contract.
Returns comprehensive contract-level analysis.
"""
results = []
total_risk = 0
high_risk_count = 0
medium_risk_count = 0
low_risk_count = 0
all_problems = []
all_recommendations = set()
for i, clause in enumerate(clauses):
result = self.analyze_clause(
clause_text=clause,
clause_id=f"clause_{i+1}",
party=party,
contract_value=contract_value,
run_specialists=True
)
results.append(result)
total_risk += result.risk_score
if result.risk_level == "HIGH" or result.risk_level == "CRITICAL":
high_risk_count += 1
elif result.risk_level == "MEDIUM":
medium_risk_count += 1
else:
low_risk_count += 1
all_problems.extend(result.problems)
all_recommendations.update(result.recommendations)
# Calculate aggregate metrics
avg_risk = total_risk / len(clauses) if clauses else 50
# Determine overall risk level
if avg_risk >= 70 or high_risk_count >= 3:
overall_level = "HIGH"
elif avg_risk >= 40 or high_risk_count >= 1:
overall_level = "MEDIUM"
else:
overall_level = "LOW"
return {
"summary": {
"total_clauses": len(clauses),
"average_risk": round(avg_risk, 1),
"overall_risk_level": overall_level,
"high_risk_clauses": high_risk_count,
"medium_risk_clauses": medium_risk_count,
"low_risk_clauses": low_risk_count,
"total_problems": len(all_problems),
"party_position": party.value
},
"critical_issues": all_problems[:10],
"top_recommendations": list(all_recommendations)[:10],
"clause_analyses": [
{
"clause_id": r.clause_id,
"type": r.clause_type,
"risk_score": r.risk_score,
"risk_level": r.risk_level,
"problems": r.problems,
"uk_risk": r.uk_risk,
"fr_risk": r.fr_risk
}
for r in results
]
}
# Singleton
_analyzer: Optional[BALEV8Analyzer] = None
def get_v8_analyzer() -> BALEV8Analyzer:
"""Get V8 analyzer singleton."""
global _analyzer
if _analyzer is None:
_analyzer = BALEV8Analyzer()
return _analyzer
# Export
__all__ = [
"BALEV8Analyzer",
"V8AnalysisResult",
"get_v8_analyzer"
]
