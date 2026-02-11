"""
BALE V10 Pipeline
End-to-end contract analysis: Chunk → Classify → Graph → Power → Dispute → Report
This is the main entry point for V10 analysis.
No LLM calls required for the core pipeline.
"""
import re
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
from src.v10.classifier_v10 import EmbeddingClassifier, get_classifier, ClassificationResult
from src.v10.contract_graph import ContractGraph, ClauseNode, build_contract_graph, GraphAnalysis
from src.v10.power_analyzer import PowerAnalyzer, PowerAnalysis
from src.v10.dispute_predictor import DisputePredictor, DisputePrediction
logger = logging.getLogger("bale_v10_pipeline")
@dataclass
class V10Report:
"""Complete V10 analysis report."""
# Metadata
contract_type: str
total_clauses: int
analysis_time_ms: int
# Classification
clause_classifications: List[Dict[str, Any]]
# Graph Analysis
graph: Dict[str, Any]
# Power Analysis
power: Dict[str, Any]
# Dispute Prediction
disputes: Dict[str, Any]
# Overall
overall_risk_score: float
risk_level: str
executive_summary: str
def to_dict(self) -> Dict:
return {
"metadata": {
"contract_type": self.contract_type,
"total_clauses": self.total_clauses,
"analysis_time_ms": self.analysis_time_ms,
"engine_version": "V10",
},
"classifications": self.clause_classifications,
"graph_analysis": self.graph,
"power_analysis": self.power,
"dispute_prediction": self.disputes,
"overall": {
"risk_score": round(self.overall_risk_score, 1),
"risk_level": self.risk_level,
"executive_summary": self.executive_summary,
}
}
def to_json(self, indent: int = 2) -> str:
return json.dumps(self.to_dict(), indent=indent, default=str)
class V10Pipeline:
"""
The BALE V10 Contract Reasoning Pipeline.
Architecture:
1. CHUNK: Split contract into clauses
2. CLASSIFY: Embedding-based clause classification
3. GRAPH: Build clause relationship graph
4. POWER: Analyze party power asymmetry
5. DISPUTE: Predict dispute hotspots
6. REPORT: Generate actionable output
"""
def __init__(self, multilingual: bool = True):
self.classifier = get_classifier(multilingual=multilingual)
self.power_analyzer = PowerAnalyzer()
self.dispute_predictor = DisputePredictor()
def analyze(
self,
contract_text: str,
contract_type: str = "MSA",
) -> V10Report:
"""
Run full V10 analysis on a contract.
Args:
contract_text: Full contract text
contract_type: Type of contract (MSA, NDA, SLA, etc.)
Returns:
V10Report with all analysis results
"""
start = time.time()
# Step 1: CHUNK
clauses = self._chunk_contract(contract_text)
logger.info(f"Chunked contract into {len(clauses)} clauses")
# Step 2: CLASSIFY
classified = self._classify_clauses(clauses)
logger.info(f"Classified {len(classified)} clauses")
# Step 3: GRAPH
graph, graph_analysis = build_contract_graph(classified, contract_type)
logger.info(f"Built graph: {graph_analysis.conflict_count} conflicts, "
f"{graph_analysis.dependency_gap_count} gaps")
# Step 4: POWER
power_analysis = self.power_analyzer.analyze(classified, contract_text)
logger.info(f"Power score: {power_analysis.power_score:.1f}")
# Step 5: DISPUTE
dispute_prediction = self.dispute_predictor.predict(
graph_analysis, power_analysis, classified
)
logger.info(f"Predicted {len(dispute_prediction.hotspots)} dispute hotspots")
# Step 6: REPORT
elapsed_ms = int((time.time() - start) * 1000)
# Overall risk = weighted combination
overall_risk = (
graph_analysis.structural_risk * 0.3 +
power_analysis.power_score * 0.2 +
dispute_prediction.overall_dispute_risk * 0.5
)
overall_risk = min(100, overall_risk)
if overall_risk >= 70:
risk_level = "HIGH"
elif overall_risk >= 40:
risk_level = "MEDIUM"
else:
risk_level = "LOW"
summary = self._generate_summary(
graph_analysis, power_analysis, dispute_prediction, risk_level
)
return V10Report(
contract_type=contract_type,
total_clauses=len(classified),
analysis_time_ms=elapsed_ms,
clause_classifications=[
{
"id": c["id"],
"clause_type": c["clause_type"],
"confidence": round(c["confidence"], 3),
"text_preview": c["text"][:100] + "...",
}
for c in classified
],
graph=graph_analysis.to_dict(),
power=power_analysis.to_dict(),
disputes=dispute_prediction.to_dict(),
overall_risk_score=overall_risk,
risk_level=risk_level,
executive_summary=summary,
)
def _chunk_contract(self, text: str) -> List[Dict[str, str]]:
"""
Split a contract into individual clauses.
Strategy: Split on TOP-LEVEL numbered sections only (e.g., "1.", "2.").
Sub-sections (1.1, 1.2) stay grouped with their parent.
Preserves section headers for classification context.
"""
clauses = []
# Split on top-level sections: "1. TITLE", "2. TITLE", "Section 1", "Article 1"
# Only match single-digit sections (no dots = top-level)
top_level_pattern = r'(?=(?:^|\n)\s*(?:(?:Section|Article|Clause)\s+)?\d{1,2}\.\s+[A-Z])'
sections = re.split(top_level_pattern, text, flags=re.IGNORECASE)
if len(sections) > 3:
for i, section in enumerate(sections):
section = section.strip()
if len(section) > 30:
# Extract section title from first line for context
first_line = section.split('\n')[0].strip()
clauses.append({
"id": f"section_{i}",
"text": section[:3000], # Larger cap for grouped sections
"header": first_line,
})
else:
# Fallback: paragraph splitting
paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
for i, para in enumerate(paragraphs):
if len(para) > 30:
clauses.append({
"id": f"clause_{i}",
"text": para[:2000],
})
return clauses
def _classify_clauses(self, clauses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
"""Classify each clause and enrich with metadata."""
texts = [c["text"] for c in clauses]
results = self.classifier.classify_batch(texts)
classified = []
for clause, result in zip(clauses, results):
classified.append({
**clause,
"clause_type": result.clause_type,
"confidence": result.confidence,
"top_3": result.top_3,
"language": result.language_detected,
"risk_weight": self.classifier.get_risk_weight(result.clause_type),
"category": self.classifier.get_category(result.clause_type),
})
return classified
def _generate_summary(
self,
graph: GraphAnalysis,
power: PowerAnalysis, disputes: DisputePrediction,
risk_level: str,
) -> str:
"""Generate a human-readable executive summary."""
parts = []
parts.append(f"Contract Risk Level: {risk_level}.")
if graph.conflict_count > 0:
parts.append(f"{graph.conflict_count} inter-clause conflict(s) detected.")
if graph.dependency_gap_count > 0:
parts.append(f"{graph.dependency_gap_count} missing clause dependency(ies).")
if len(graph.missing_expected) > 0:
top_missing = [m["clause_type"].replace("_", " ") for m in graph.missing_expected[:3]]
parts.append(f"Missing expected clauses: {', '.join(top_missing)}.")
if power.power_score > 30:
parts.append(f"Power imbalance detected (score: {power.power_score:.0f}/100): "
f"{power.dominant_party} holds dominant position.")
if disputes.hotspots:
top = disputes.hotspots[0]
parts.append(f"Highest dispute risk: {top.clause_type.replace('_', ' ')} "
f"({top.dispute_probability:.0%} probability).")
parts.append(f"Completeness: {graph.completeness_score:.0%}.")
return " ".join(parts)
# ==================== CONVENIENCE FUNCTIONS ====================
def analyze_contract(text: str, contract_type: str = "MSA") -> V10Report:
"""Quick analysis of a contract."""
pipeline = V10Pipeline(multilingual=True)
return pipeline.analyze(text, contract_type)
__all__ = ["V10Pipeline", "V10Report", "analyze_contract"]
