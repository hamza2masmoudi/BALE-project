"""
BALE V5 Local Inference Module
Provides local MLX-based inference for the IntegratedAnalyzer.
Features:
- Local Mistral-7B with V5 LoRA adapters
- Risk detection with detailed reasoning
- Clause classification
- No API calls required
"""
import os
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
logger = logging.getLogger(__name__)
# Check if MLX is available
try:
from mlx_lm import load, generate
MLX_AVAILABLE = True
except ImportError:
MLX_AVAILABLE = False
logger.warning("mlx_lm not available - local inference disabled")
class RiskLevel(Enum):
LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"
UNKNOWN = "UNKNOWN"
@dataclass
class RiskAnalysisResult:
"""Result of risk analysis."""
level: RiskLevel
score: float # 0-100
reasoning: str
problems: List[str]
recommendations: List[str]
@dataclass
class ClassificationResult:
"""Result of clause classification."""
clause_type: str
confidence: float
reasoning: str
key_indicators: List[str]
class BALELocalInference:
"""Local V5 inference engine using MLX."""
MODEL_ID = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
ADAPTER_PATH = "models/bale-legal-lora-v7"
def __init__(self, adapter_path: Optional[str] = None):
"""Initialize the local inference engine."""
self.adapter_path = adapter_path or self.ADAPTER_PATH
self.model = None
self.tokenizer = None
self._loaded = False
def is_available(self) -> bool:
"""Check if local inference is available."""
if not MLX_AVAILABLE:
return False
return os.path.exists(os.path.join(self.adapter_path, "adapters.safetensors"))
def load(self) -> bool:
"""Load the model and adapters."""
if self._loaded:
return True
if not MLX_AVAILABLE:
logger.error("MLX not available")
return False
if not os.path.exists(os.path.join(self.adapter_path, "adapters.safetensors")):
logger.error(f"Adapter not found at {self.adapter_path}")
return False
try:
logger.info(f"Loading model with V7 adapters from {self.adapter_path}")
self.model, self.tokenizer = load(
self.MODEL_ID,
adapter_path=self.adapter_path
)
self._loaded = True
logger.info("V7 model loaded successfully")
return True
except Exception as e:
logger.error(f"Failed to load model: {e}")
return False
def analyze_risk(self, clause_text: str) -> RiskAnalysisResult:
"""Analyze a clause for consumer risk."""
if not self._loaded and not self.load():
return RiskAnalysisResult(
level=RiskLevel.UNKNOWN,
score=50,
reasoning="Model not available",
problems=[],
recommendations=[]
)
# Detect language (simple heuristic)
lang_instruction = "Analyze this clause for consumer risk."
if "est" in clause_text and "le" in clause_text: # Very basic FR detection
lang_instruction = "Analysez cette clause pour le risque consommateur."
elif "und" in clause_text and "der" in clause_text: # Very basic DE detection
lang_instruction = "Analysieren Sie diese Klausel auf Verbraucherrisiko."
messages = [{"role": "user", "content": f"{lang_instruction}\n\n{clause_text[:2000]}"}]
prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
try:
response = generate(
self.model,
self.tokenizer,
prompt=prompt,
max_tokens=200,
verbose=False
)
return self._parse_risk_response(response)
except Exception as e:
logger.error(f"Risk analysis failed: {e}")
return RiskAnalysisResult(
level=RiskLevel.UNKNOWN,
score=50,
reasoning=f"Analysis failed: {str(e)}",
problems=[],
recommendations=[]
)
def classify_clause(self, clause_text: str) -> ClassificationResult:
"""Classify a contract clause."""
if not self._loaded and not self.load():
return ClassificationResult(
clause_type="unknown",
confidence=0.0,
reasoning="Model not available",
key_indicators=[]
)
# Detect language
lang_instruction = "Classify this contract clause."
if "est" in clause_text and "le" in clause_text:
lang_instruction = "Classifiez cette clause contractuelle."
elif "und" in clause_text and "der" in clause_text:
lang_instruction = "Klassifizieren Sie diese Vertragsklausel."
messages = [{"role": "user", "content": f"{lang_instruction}\n\n{clause_text[:2000]}"}]
prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
try:
response = generate(
self.model,
self.tokenizer,
prompt=prompt,
max_tokens=150,
verbose=False
)
return self._parse_classification_response(response)
except Exception as e:
logger.error(f"Classification failed: {e}")
return ClassificationResult(
clause_type="unknown",
confidence=0.0,
reasoning=f"Classification failed: {str(e)}",
key_indicators=[]
)
def _parse_risk_response(self, response: str) -> RiskAnalysisResult:
"""Parse risk analysis response."""
response = response.strip()
# Detect risk level
if "HIGH" in response.upper() or "" in response:
level = RiskLevel.HIGH
score = 85
elif "MEDIUM" in response.upper():
level = RiskLevel.MEDIUM
score = 50
elif "LOW" in response.upper() or "" in response:
level = RiskLevel.LOW
score = 15
else:
level = RiskLevel.UNKNOWN
score = 50
# Extract problems
problems = []
if "PROBLEMS IDENTIFIED:" in response or "CRITICAL ISSUES" in response:
lines = response.split("\n")
for line in lines:
if line.strip().startswith(("1.", "2.", "3.", "•", "-")) and "-" in line:
problems.append(line.strip())
# Extract recommendations
recommendations = []
if "RECOMMENDATION:" in response:
rec_start = response.find("RECOMMENDATION:")
rec_text = response[rec_start:].split("\n")[0]
recommendations.append(rec_text.replace("RECOMMENDATION:", "").strip())
return RiskAnalysisResult(
level=level,
score=score,
reasoning=response,
problems=problems[:5],
recommendations=recommendations[:3]
)
def _parse_classification_response(self, response: str) -> ClassificationResult:
"""Parse classification response."""
response = response.strip()
# Common clause types
clause_types = [
"INDEMNIFICATION", "INSURANCE", "CONFIDENTIALITY", "TERMINATION",
"LIABILITY", "GOVERNING LAW", "WARRANTY", "INTELLECTUAL PROPERTY",
"NON-COMPETE", "PAYMENT", "FORCE MAJEURE", "ARBITRATION"
]
# Detect clause type
detected_type = "unknown"
for ct in clause_types:
if ct in response.upper():
detected_type = ct.lower().replace(" ", "_")
break
# Extract key indicators
indicators = []
if "Key Indicators" in response or "key phrases" in response.lower():
lines = response.split("\n")
for line in lines:
if line.strip().startswith(("•", "-", "*")):
indicators.append(line.strip().lstrip("•-* "))
return ClassificationResult(
clause_type=detected_type,
confidence=0.85 if detected_type != "unknown" else 0.0,
reasoning=response,
key_indicators=indicators[:5]
)
def analyze_contract(self, contract_text: str) -> Dict:
"""Analyze an entire contract for risks and clause types."""
if not self._loaded and not self.load():
return {"error": "Model not available"}
# Split into potential clauses (simple heuristic)
import re
sections = re.split(r'\n\s*\n|\n\d+\.|\n[A-Z][A-Z\s]+:', contract_text)
sections = [s.strip() for s in sections if len(s.strip()) > 50]
results = {
"total_sections": len(sections),
"high_risk_clauses": [],
"medium_risk_clauses": [],
"low_risk_clauses": [],
"classifications": [],
"overall_risk_score": 0
}
risk_scores = []
for i, section in enumerate(sections[:20]): # Limit to 20 sections
# Classify
classification = self.classify_clause(section)
# Analyze risk for Terms-of-Service-like content
risk = self.analyze_risk(section)
risk_scores.append(risk.score)
clause_data = {
"index": i,
"text": section[:200] + "..." if len(section) > 200 else section,
"type": classification.clause_type,
"risk_level": risk.level.value,
"risk_score": risk.score,
"problems": risk.problems
}
if risk.level == RiskLevel.HIGH:
results["high_risk_clauses"].append(clause_data)
elif risk.level == RiskLevel.MEDIUM:
results["medium_risk_clauses"].append(clause_data)
else:
results["low_risk_clauses"].append(clause_data)
results["classifications"].append({
"index": i,
"type": classification.clause_type,
"confidence": classification.confidence
})
# Calculate overall risk
if risk_scores:
results["overall_risk_score"] = sum(risk_scores) / len(risk_scores)
return results
# Singleton instance for easy access
_inference_engine: Optional[BALELocalInference] = None
def get_inference_engine() -> BALELocalInference:
"""Get the singleton inference engine."""
global _inference_engine
if _inference_engine is None:
_inference_engine = BALELocalInference()
return _inference_engine
def analyze_risk(clause_text: str) -> RiskAnalysisResult:
"""Convenience function for risk analysis."""
return get_inference_engine().analyze_risk(clause_text)
def classify_clause(clause_text: str) -> ClassificationResult:
"""Convenience function for clause classification."""
return get_inference_engine().classify_clause(clause_text)
