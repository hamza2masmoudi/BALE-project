"""Inference module for BALE local model."""
from .local_v5 import (
BALELocalInference,
RiskLevel,
RiskAnalysisResult,
ClassificationResult,
get_inference_engine,
analyze_risk,
classify_clause,
)
__all__ = [
"BALELocalInference",
"RiskLevel", "RiskAnalysisResult",
"ClassificationResult",
"get_inference_engine",
"analyze_risk",
"classify_clause",
]
