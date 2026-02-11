"""
Frontier I: Detecting the Shape of Silence
What is NOT in a contract, and why?
Frontier II: Contract Archaeology
What prior versions, negotiations, or relationships left traces in the text?
"""
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
from src.frontier.core import (
ContractType, ClauseTemplate, EXPECTED_CLAUSES, corpus
)
from src.logger import setup_logger
logger = setup_logger("frontier_silence")
# ==================== FRONTIER I: SILENCE DETECTION ====================
@dataclass
class SilenceAnalysis:
"""Analysis of what's missing from a contract."""
contract_id: str
contract_type: ContractType
# Missing clauses
missing_clauses: List[Dict[str, Any]] # [{name, expected_prevalence, risk_increase}]
total_expected: int
total_present: int
silence_score: float # 0-100, higher = more suspicious omissions
# Interpretation
likely_strategic_omissions: List[str]
likely_oversights: List[str]
likely_asymmetric_sophistication: List[str]
# Risk impact
cumulative_risk_from_silence: int
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["contract_type"] = self.contract_type.value
return d
class SilenceDetector:
"""
Detects meaningful absences in contracts by comparing against
expected clause patterns for the contract type.
"""
def __init__(self):
self.sophistication_indicators = [
"whereas", "notwithstanding", "provided however",
"subject to", "without limiting", "for the avoidance of doubt"
]
def analyze(
self,
contract_text: str,
contract_type: ContractType,
contract_id: str = "unknown",
party_sophistication: Dict[str, float] = None
) -> SilenceAnalysis:
"""
Analyze what's missing from a contract.
Args:
contract_text: Full contract text
contract_type: Type of contract
contract_id: Identifier
party_sophistication: Dict of party name -> sophistication score (0-1)
"""
text_lower = contract_text.lower()
# Get expected clauses for this type
expected = EXPECTED_CLAUSES.get(contract_type, [])
# Detect which clauses are present
present_clauses = []
missing_clauses = []
for template in expected:
is_present = any(kw in text_lower for kw in template.keywords)
if is_present:
present_clauses.append(template.name)
else:
missing_clauses.append({
"name": template.name,
"description": template.description,
"expected_prevalence": template.prevalence,
"risk_increase": template.risk_if_absent,
"category": template.category
})
# Calculate silence score (weighted by prevalence)
if not expected:
silence_score = 0
else:
weighted_missing = sum(
m["expected_prevalence"] * m["risk_increase"] for m in missing_clauses
)
max_possible = sum(t.prevalence * t.risk_if_absent for t in expected)
silence_score = (weighted_missing / max_possible * 100) if max_possible > 0 else 0
# Classify omissions
strategic, oversight, asymmetric = self._classify_omissions(
missing_clauses, text_lower, party_sophistication
)
# Calculate cumulative risk
cumulative_risk = sum(m["risk_increase"] for m in missing_clauses)
return SilenceAnalysis(
contract_id=contract_id,
contract_type=contract_type,
missing_clauses=missing_clauses,
total_expected=len(expected),
total_present=len(present_clauses),
silence_score=round(silence_score, 2),
likely_strategic_omissions=strategic,
likely_oversights=oversight,
likely_asymmetric_sophistication=asymmetric,
cumulative_risk_from_silence=cumulative_risk
)
def _classify_omissions(
self,
missing: List[Dict],
text: str,
party_sophistication: Dict[str, float] = None
) -> Tuple[List[str], List[str], List[str]]:
"""
Classify why clauses might be missing.
Returns: (strategic, oversight, asymmetric)
"""
strategic = []
oversight = []
asymmetric = []
# Detect overall contract sophistication
sophistication_score = sum(
1 for ind in self.sophistication_indicators if ind in text
) / len(self.sophistication_indicators)
for m in missing:
name = m["name"]
prevalence = m["expected_prevalence"]
# High prevalence + sophisticated contract = likely strategic
if prevalence > 0.85 and sophistication_score > 0.3:
strategic.append(name)
# Low prevalence + simple contract = likely oversight
elif prevalence < 0.7 and sophistication_score < 0.2:
oversight.append(name)
# High prevalence + simple contract = asymmetric sophistication
elif prevalence > 0.8 and sophistication_score < 0.2:
asymmetric.append(name)
else:
# Default to oversight for uncertain cases
oversight.append(name)
return strategic, oversight, asymmetric
# ==================== FRONTIER II: CONTRACT ARCHAEOLOGY ====================
@dataclass
class ArchaeologyAnalysis:
"""Analysis of a contract's drafting history."""
contract_id: str
# Stylometric analysis
style_fingerprints: List[Dict[str, Any]] # [{section, fingerprint, source_guess}]
detected_source_templates: List[str]
style_collision_locations: List[Tuple[int, int]] # (start, end) of style changes
# Negotiation traces
defensive_insertions: List[Dict[str, Any]]
over_specifications: List[Dict[str, Any]] # Unusually specific terms suggesting prior disputes
placeholder_scars: List[Dict[str, Any]] # Generic text that should've been customized
# Draft layer inference
estimated_draft_layers: int
template_vs_custom_ratio: float
# Summary
negotiation_intensity_score: float # 0-1, how heavily negotiated
archaeology_confidence: float
def to_dict(self) -> Dict[str, Any]:
return asdict(self)
class ContractArchaeologist:
"""
Analyzes contracts to infer their drafting history, template sources,
and negotiation dynamics from textual fossils.
"""
def __init__(self):
# Defensive insertion patterns
self.defensive_patterns = [
(r"under no circumstances shall", "absolute_exclusion"),
(r"notwithstanding any(?:thing)? (?:else )?(?:in|to) (?:the|this)", "override"),
(r"for the avoidance of doubt", "clarification"),
(r"without limiting the foregoing", "expansion"),
(r"in no event shall .{0,50} be liable", "liability_shield"),
(r"shall not .{0,30} under any circumstances", "absolute_prohibition"),
]
# Over-specification patterns (suggests prior disputes)
self.overspec_patterns = [
(r"including but not limited to .{50,200}", "extensive_examples"),
(r"specifically\s+(?:including|excluding)", "targeted_carveout"),
(r"\d+\s+(?:business\s+)?days\s+(?:after|from|following)\s+(?:the|receipt)", "precise_timeline"),
(r"except\s+(?:for|in\s+the\s+case\s+of)\s+.{30,100}", "exception_carveout"),
]
# Placeholder scars (text that should've been customized)
self.placeholder_patterns = [
(r"\[?\s*(?:COMPANY|PARTY|CLIENT|VENDOR)\s*\]?", "uncustomized_party"),
(r"\[?\s*(?:DATE|TBD|INSERT)\s*\]?", "missing_date"),
(r"(?:the|a)\s+(?:applicable|relevant|appropriate)\s+(?:party|entity)", "vague_reference"),
]
# Known boilerplate sources (simplified - in production, this would be learned)
self.boilerplate_signatures = {
"legal_zoom": ["this agreement shall be governed by", "entire agreement of the parties"],
"docusign": ["electronic signature", "counterparts"],
"standard_merger": ["representations and warranties", "material adverse change"],
}
def analyze(
self,
contract_text: str,
contract_id: str = "unknown"
) -> ArchaeologyAnalysis:
"""
Perform archaeological analysis on a contract.
"""
sections = self._split_into_sections(contract_text)
# Stylometric fingerprinting
fingerprints = []
for i, section in enumerate(sections):
fp = self._fingerprint_section(section, i)
fingerprints.append(fp)
# Detect style collisions
collisions = self._detect_style_collisions(fingerprints)
# Detect template sources
sources = self._detect_sources(contract_text)
# Find defensive insertions
defensive = self._find_defensive_insertions(contract_text)
# Find over-specifications
overspecs = self._find_overspecifications(contract_text)
# Find placeholder scars
placeholders = self._find_placeholder_scars(contract_text)
# Estimate draft layers
draft_layers = len(set(fp["fingerprint"] for fp in fingerprints))
# Calculate template vs custom ratio
template_chars = sum(
len(s) for s in [contract_text] if any(sig in s.lower() for sigs in self.boilerplate_signatures.values() for sig in sigs)
)
custom_chars = len(contract_text) - template_chars
ratio = template_chars / len(contract_text) if contract_text else 0
# Negotiation intensity
negotiation_score = min(1.0, (
len(defensive) * 0.15 +
len(overspecs) * 0.1 +
len(collisions) * 0.2 +
(1 - ratio) * 0.3
))
return ArchaeologyAnalysis(
contract_id=contract_id,
style_fingerprints=fingerprints,
detected_source_templates=sources,
style_collision_locations=collisions,
defensive_insertions=defensive,
over_specifications=overspecs,
placeholder_scars=placeholders,
estimated_draft_layers=draft_layers,
template_vs_custom_ratio=round(ratio, 3),
negotiation_intensity_score=round(negotiation_score, 3),
archaeology_confidence=0.75 # Fixed for now
)
def _split_into_sections(self, text: str) -> List[str]:
"""Split contract into logical sections."""
# Simple approach: split on numbered sections or double newlines
sections = re.split(r'\n\s*\d+[\.\)]\s+|\n\n+', text)
return [s.strip() for s in sections if len(s.strip()) > 100]
def _fingerprint_section(self, section: str, index: int) -> Dict[str, Any]:
"""Generate stylometric fingerprint for a section."""
words = section.lower().split()
# Features
avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
sentence_count = len(re.findall(r'[.!?]', section))
avg_sentence_length = len(words) / sentence_count if sentence_count else len(words)
# Passive voice detection
passive_count = len(re.findall(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', section.lower()))
# Create fingerprint hash
features = f"{avg_word_length:.1f}-{avg_sentence_length:.1f}-{passive_count}"
fingerprint = hashlib.md5(features.encode()).hexdigest()[:8]
return {
"section_index": index,
"fingerprint": fingerprint,
"avg_word_length": round(avg_word_length, 2),
"avg_sentence_length": round(avg_sentence_length, 2),
"passive_voice_count": passive_count,
"source_guess": "custom" if avg_sentence_length < 25 else "template"
}
def _detect_style_collisions(
self, fingerprints: List[Dict]
) -> List[Tuple[int, int]]:
"""Detect where writing style changes abruptly."""
collisions = []
for i in range(1, len(fingerprints)):
prev = fingerprints[i-1]
curr = fingerprints[i]
# Significant style change
if prev["fingerprint"] != curr["fingerprint"]:
word_diff = abs(prev["avg_word_length"] - curr["avg_word_length"])
sent_diff = abs(prev["avg_sentence_length"] - curr["avg_sentence_length"])
if word_diff > 1.5 or sent_diff > 15:
collisions.append((prev["section_index"], curr["section_index"]))
return collisions
def _detect_sources(self, text: str) -> List[str]:
"""Detect likely template sources."""
text_lower = text.lower()
sources = []
for source, signatures in self.boilerplate_signatures.items():
if all(sig in text_lower for sig in signatures):
sources.append(source)
return sources
def _find_defensive_insertions(self, text: str) -> List[Dict[str, Any]]:
"""Find clauses that appear to be defensive insertions."""
results = []
text_lower = text.lower()
for pattern, pattern_type in self.defensive_patterns:
matches = re.finditer(pattern, text_lower)
for match in matches:
context_start = max(0, match.start() - 50)
context_end = min(len(text), match.end() + 50)
results.append({
"type": pattern_type,
"text": match.group(),
"context": text[context_start:context_end],
"position": match.start()
})
return results
def _find_overspecifications(self, text: str) -> List[Dict[str, Any]]:
"""Find unusually specific terms suggesting prior disputes."""
results = []
for pattern, pattern_type in self.overspec_patterns:
matches = re.finditer(pattern, text.lower())
for match in matches:
results.append({
"type": pattern_type,
"text": match.group()[:100] + "..." if len(match.group()) > 100 else match.group(),
"position": match.start(),
"suggests": "Prior dispute or specific concern led to this specificity"
})
return results
def _find_placeholder_scars(self, text: str) -> List[Dict[str, Any]]:
"""Find remnants of template placeholders."""
results = []
for pattern, pattern_type in self.placeholder_patterns:
matches = re.finditer(pattern, text, re.IGNORECASE)
for match in matches:
results.append({
"type": pattern_type,
"text": match.group(),
"position": match.start(),
"issue": "Template not fully customized"
})
return results
# Module instances
silence_detector = SilenceDetector()
archaeologist = ContractArchaeologist()
