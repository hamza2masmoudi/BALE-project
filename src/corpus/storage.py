"""
BALE Corpus Storage System
Persistent storage for analysis results, entity profiles, and term evolution.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from pathlib import Path
from src.logger import setup_logger
logger = setup_logger("corpus_storage")
@dataclass
class StoredAnalysis:
"""A stored analysis record."""
analysis_id: str
contract_id: str
contract_name: str
contract_type: str
jurisdiction: str
industry: str
# Core analysis
risk_score: int
verdict_summary: str
# Frontier results
frontier_risk: float
frontier_data: Dict[str, Any]
# Negotiation
negotiation_playbook: Dict[str, Any]
# Metadata
analyzed_at: str
parties: List[str]
def to_dict(self) -> Dict[str, Any]:
return asdict(self)
@dataclass
class EntityProfileRecord:
"""Persistent entity profile."""
entity_id: str
entity_name: str
# Accumulated data
total_contracts: int
avg_risk_score: float
risk_scores: List[int]
# Behavioral patterns
typical_positions: Dict[str, int] # buyer/seller counts
jurisdictions: Dict[str, int]
industries: Dict[str, int]
# Risk trends
risk_trend: str # increasing, decreasing, stable
last_updated: str
class CorpusStorage:
"""
Persistent storage for BALE corpus data.
Uses file-based JSON storage (can be upgraded to database).
"""
def __init__(self, storage_dir: str = None):
if storage_dir is None:
storage_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "corpus")
self.storage_dir = Path(storage_dir)
self.storage_dir.mkdir(parents=True, exist_ok=True)
# Sub-directories
self.analyses_dir = self.storage_dir / "analyses"
self.entities_dir = self.storage_dir / "entities"
self.terms_dir = self.storage_dir / "terms"
self.reflexive_dir = self.storage_dir / "reflexive"
for d in [self.analyses_dir, self.entities_dir, self.terms_dir, self.reflexive_dir]:
d.mkdir(exist_ok=True)
logger.info(f"Corpus storage initialized at {self.storage_dir}")
# ==================== ANALYSIS STORAGE ====================
def store_analysis(self, analysis: StoredAnalysis) -> str:
"""Store an analysis result."""
filepath = self.analyses_dir / f"{analysis.analysis_id}.json"
with open(filepath, "w") as f:
json.dump(analysis.to_dict(), f, indent=2, default=str)
# Update entity profiles
for party in analysis.parties:
self._update_entity_from_analysis(party, analysis)
logger.info(f"Stored analysis {analysis.analysis_id}")
return str(filepath)
def get_analysis(self, analysis_id: str) -> Optional[StoredAnalysis]:
"""Retrieve an analysis by ID."""
filepath = self.analyses_dir / f"{analysis_id}.json"
if not filepath.exists():
return None
with open(filepath) as f:
data = json.load(f)
return StoredAnalysis(**data)
def list_analyses(
self,
limit: int = 50,
contract_type: str = None,
jurisdiction: str = None,
min_risk: int = None
) -> List[StoredAnalysis]:
"""List analyses with optional filters."""
analyses = []
for filepath in sorted(self.analyses_dir.glob("*.json"), reverse=True):
if len(analyses) >= limit:
break
with open(filepath) as f:
data = json.load(f)
# Apply filters
if contract_type and data.get("contract_type") != contract_type:
continue
if jurisdiction and data.get("jurisdiction") != jurisdiction:
continue
if min_risk and data.get("risk_score", 0) < min_risk:
continue
analyses.append(StoredAnalysis(**data))
return analyses
def get_analysis_count(self) -> int:
"""Get total number of stored analyses."""
return len(list(self.analyses_dir.glob("*.json")))
# ==================== ENTITY STORAGE ====================
def _update_entity_from_analysis(self, entity_name: str, analysis: StoredAnalysis):
"""Update entity profile from new analysis."""
entity_id = entity_name.lower().replace(" ", "_")[:50]
profile = self.get_entity(entity_id)
if profile is None:
profile = EntityProfileRecord(
entity_id=entity_id,
entity_name=entity_name,
total_contracts=0,
avg_risk_score=0,
risk_scores=[],
typical_positions={},
jurisdictions={},
industries={},
risk_trend="stable",
last_updated=datetime.utcnow().isoformat()
)
# Update counts
profile.total_contracts += 1
profile.risk_scores.append(analysis.risk_score)
profile.avg_risk_score = sum(profile.risk_scores) / len(profile.risk_scores)
# Update distributions
jur = analysis.jurisdiction
profile.jurisdictions[jur] = profile.jurisdictions.get(jur, 0) + 1
ind = analysis.industry
profile.industries[ind] = profile.industries.get(ind, 0) + 1
# Calculate trend
if len(profile.risk_scores) >= 3:
recent = profile.risk_scores[-3:]
older = profile.risk_scores[:-3] if len(profile.risk_scores) > 3 else recent
recent_avg = sum(recent) / len(recent)
older_avg = sum(older) / len(older)
if recent_avg > older_avg + 5:
profile.risk_trend = "increasing"
elif recent_avg < older_avg - 5:
profile.risk_trend = "decreasing"
else:
profile.risk_trend = "stable"
profile.last_updated = datetime.utcnow().isoformat()
self.store_entity(profile)
def store_entity(self, profile: EntityProfileRecord) -> str:
"""Store an entity profile."""
filepath = self.entities_dir / f"{profile.entity_id}.json"
with open(filepath, "w") as f:
json.dump(asdict(profile), f, indent=2)
return str(filepath)
def get_entity(self, entity_id: str) -> Optional[EntityProfileRecord]:
"""Retrieve an entity profile."""
filepath = self.entities_dir / f"{entity_id}.json"
if not filepath.exists():
return None
with open(filepath) as f:
data = json.load(f)
return EntityProfileRecord(**data)
def list_entities(self, limit: int = 50) -> List[EntityProfileRecord]:
"""List all entity profiles."""
entities = []
for filepath in sorted(self.entities_dir.glob("*.json")):
if len(entities) >= limit:
break
with open(filepath) as f:
data = json.load(f)
entities.append(EntityProfileRecord(**data))
return entities
# ==================== TERM EVOLUTION ====================
def track_term(self, term: str, usage_context: Dict[str, Any]):
"""Track a term's usage for evolution analysis."""
term_id = term.lower().replace(" ", "_")[:30]
filepath = self.terms_dir / f"{term_id}.json"
if filepath.exists():
with open(filepath) as f:
data = json.load(f)
else:
data = {"term": term, "usages": []}
data["usages"].append({
"timestamp": datetime.utcnow().isoformat(),
**usage_context
})
with open(filepath, "w") as f:
json.dump(data, f, indent=2)
# ==================== REFLEXIVE TRACKING ====================
def record_reflexive_event(self, event_type: str, data: Dict[str, Any]):
"""Record a reflexive event (system influence on contracts)."""
timestamp = datetime.utcnow().isoformat()
filename = f"{timestamp[:10]}_{event_type}.json"
filepath = self.reflexive_dir / filename
event = {
"timestamp": timestamp,
"event_type": event_type,
"data": data
}
with open(filepath, "w") as f:
json.dump(event, f, indent=2)
# ==================== STATISTICS ====================
def get_corpus_stats(self) -> Dict[str, Any]:
"""Get corpus-wide statistics."""
analyses = self.list_analyses(limit=1000)
if not analyses:
return {
"total_analyses": 0,
"total_entities": 0,
"avg_risk_score": 0,
"risk_distribution": {},
"jurisdiction_distribution": {},
"type_distribution": {},
}
risk_buckets = {"low": 0, "medium": 0, "high": 0}
jurisdictions = {}
types = {}
for a in analyses:
# Risk distribution
if a.risk_score < 30:
risk_buckets["low"] += 1
elif a.risk_score < 60:
risk_buckets["medium"] += 1
else:
risk_buckets["high"] += 1
# Jurisdiction distribution
jurisdictions[a.jurisdiction] = jurisdictions.get(a.jurisdiction, 0) + 1
# Type distribution
types[a.contract_type] = types.get(a.contract_type, 0) + 1
return {
"total_analyses": len(analyses),
"total_entities": len(list(self.entities_dir.glob("*.json"))),
"avg_risk_score": sum(a.risk_score for a in analyses) / len(analyses),
"risk_distribution": risk_buckets,
"jurisdiction_distribution": jurisdictions,
"type_distribution": types,
}
# Singleton
corpus_storage = CorpusStorage()
