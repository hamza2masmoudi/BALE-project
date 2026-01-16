"""
BALE Frontier Analysis Engine
Core infrastructure for second-order legal intelligence.

This module implements the 10 frontier capabilities that emerge when
first-order legal understanding is assumed solved.
"""
import os
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import re

from src.logger import setup_logger

logger = setup_logger("bale_frontier")


# ==================== CORE DATA STRUCTURES ====================

class ContractType(str, Enum):
    """Standard contract type classifications."""
    NDA = "nda"
    SLA = "sla"
    MSA = "msa"
    LICENSE = "license"
    EMPLOYMENT = "employment"
    VENDOR = "vendor"
    PARTNERSHIP = "partnership"
    DISTRIBUTION = "distribution"
    CONSULTING = "consulting"
    LOAN = "loan"
    LEASE = "lease"
    MERGER = "merger"
    UNKNOWN = "unknown"


@dataclass
class ContractMetadata:
    """Rich metadata for a contract in the corpus."""
    id: str
    contract_type: ContractType
    jurisdiction: str
    industry: str
    parties: List[str]
    effective_date: Optional[str]
    ingestion_date: str
    word_count: int
    clause_count: int
    
    # Analysis results
    risk_score: int = 0
    verdict: str = ""
    
    # Fingerprinting
    style_hash: str = ""
    structure_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["contract_type"] = self.contract_type.value
        return d


@dataclass
class ClauseTemplate:
    """Expected clause for a contract type."""
    name: str
    description: str
    keywords: List[str]
    prevalence: float  # 0-1, how often this appears
    risk_if_absent: int  # Risk increase if missing
    category: str


@dataclass
class TemporalSnapshot:
    """Point-in-time snapshot for tracking drift."""
    timestamp: str
    jurisdiction: str
    metric_type: str
    metric_value: float
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityProfile:
    """Profile of an entity across contracts."""
    entity_id: str
    name: str
    contract_count: int = 0
    avg_risk_score: float = 0
    typical_position: str = ""  # buyer, seller, licensor, etc.
    industries: List[str] = field(default_factory=list)
    jurisdictions: List[str] = field(default_factory=list)
    
    # Behavioral patterns
    risk_tolerance_trend: float = 0  # +/- change over time
    negotiation_power_score: float = 0.5  # 0=weak, 1=strong
    consistency_score: float = 1.0  # How consistent are their terms


# ==================== CORPUS TRACKER ====================

class CorpusTracker:
    """
    Tracks statistics across the contract corpus for population-level inference.
    """
    
    def __init__(self):
        self.contracts: Dict[str, ContractMetadata] = {}
        self.entities: Dict[str, EntityProfile] = {}
        self.temporal_snapshots: List[TemporalSnapshot] = []
        
        # Clause statistics by contract type
        self.clause_frequencies: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Term evolution tracking
        self.term_history: Dict[str, List[Tuple[str, float]]] = defaultdict(list)  # term -> [(date, value)]
        
        # Ambiguity tracking
        self.ambiguous_terms: Dict[str, int] = defaultdict(int)
    
    def add_contract(self, metadata: ContractMetadata, clauses: List[str]):
        """Add a contract to the corpus."""
        self.contracts[metadata.id] = metadata
        
        # Update clause frequencies
        ct = metadata.contract_type.value
        for clause in clauses:
            clause_type = self._classify_clause(clause)
            self.clause_frequencies[ct][clause_type] += 1
        
        # Update entity profiles
        for party in metadata.parties:
            self._update_entity(party, metadata)
        
        logger.debug(f"Added contract {metadata.id} to corpus")
    
    def _classify_clause(self, clause_text: str) -> str:
        """Simple clause classification by keywords."""
        clause_lower = clause_text.lower()
        
        patterns = {
            "force_majeure": ["force majeure", "act of god", "unforeseen circumstances"],
            "limitation_liability": ["limitation of liability", "liability shall not exceed", "cap on damages"],
            "indemnification": ["indemnify", "hold harmless", "indemnification"],
            "termination": ["termination", "terminate this agreement", "right to cancel"],
            "confidentiality": ["confidential", "non-disclosure", "proprietary information"],
            "ip_assignment": ["intellectual property", "work product", "invention assignment"],
            "warranty": ["warranty", "warranties", "represents and warrants"],
            "dispute": ["dispute resolution", "arbitration", "governing law"],
            "data_protection": ["personal data", "data protection", "gdpr", "privacy"],
            "payment": ["payment terms", "invoice", "fees", "compensation"],
        }
        
        for clause_type, keywords in patterns.items():
            if any(kw in clause_lower for kw in keywords):
                return clause_type
        
        return "other"
    
    def _update_entity(self, entity_name: str, contract: ContractMetadata):
        """Update entity profile with new contract."""
        entity_id = self._entity_id(entity_name)
        
        if entity_id not in self.entities:
            self.entities[entity_id] = EntityProfile(
                entity_id=entity_id,
                name=entity_name
            )
        
        profile = self.entities[entity_id]
        profile.contract_count += 1
        
        # Running average of risk
        n = profile.contract_count
        profile.avg_risk_score = ((profile.avg_risk_score * (n-1)) + contract.risk_score) / n
        
        if contract.jurisdiction not in profile.jurisdictions:
            profile.jurisdictions.append(contract.jurisdiction)
        
        if contract.industry and contract.industry not in profile.industries:
            profile.industries.append(contract.industry)
    
    def _entity_id(self, name: str) -> str:
        """Generate stable entity ID."""
        normalized = name.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
    
    def get_expected_clauses(self, contract_type: ContractType) -> Dict[str, float]:
        """Get expected clause frequencies for a contract type."""
        ct = contract_type.value
        total = sum(self.clause_frequencies[ct].values())
        if total == 0:
            return {}
        return {k: v/total for k, v in self.clause_frequencies[ct].items()}
    
    def record_snapshot(self, snapshot: TemporalSnapshot):
        """Record a temporal snapshot."""
        self.temporal_snapshots.append(snapshot)


# ==================== EXPECTED CLAUSE TEMPLATES ====================

EXPECTED_CLAUSES: Dict[ContractType, List[ClauseTemplate]] = {
    ContractType.NDA: [
        ClauseTemplate("confidentiality", "Core confidentiality obligations", 
                      ["confidential", "proprietary"], 0.99, 50, "core"),
        ClauseTemplate("term", "Duration of confidentiality", 
                      ["term", "duration", "period"], 0.95, 20, "temporal"),
        ClauseTemplate("exclusions", "Exclusions from confidentiality", 
                      ["exclusions", "does not include", "excepted"], 0.85, 15, "scope"),
        ClauseTemplate("return_materials", "Return of confidential materials", 
                      ["return", "destroy", "materials"], 0.75, 10, "operational"),
        ClauseTemplate("injunctive_relief", "Right to seek injunction", 
                      ["injunctive", "irreparable harm"], 0.60, 5, "remedies"),
    ],
    ContractType.SLA: [
        ClauseTemplate("uptime", "Uptime/availability commitment", 
                      ["uptime", "availability", "99."], 0.95, 40, "performance"),
        ClauseTemplate("credits", "Service credits for outages", 
                      ["credit", "refund", "compensation"], 0.85, 25, "remedies"),
        ClauseTemplate("exclusions", "SLA exclusions", 
                      ["excluded", "does not apply", "maintenance"], 0.80, 15, "scope"),
        ClauseTemplate("measurement", "How metrics are measured", 
                      ["measured", "calculated", "monitoring"], 0.70, 10, "operational"),
    ],
    ContractType.MSA: [
        ClauseTemplate("scope", "Scope of services", 
                      ["scope", "services", "deliverables"], 0.99, 35, "core"),
        ClauseTemplate("payment", "Payment terms", 
                      ["payment", "invoice", "fees"], 0.98, 30, "commercial"),
        ClauseTemplate("limitation_liability", "Liability caps", 
                      ["limitation", "liability", "cap"], 0.90, 25, "risk"),
        ClauseTemplate("indemnification", "Indemnification provisions", 
                      ["indemnify", "hold harmless"], 0.85, 20, "risk"),
        ClauseTemplate("termination", "Termination rights", 
                      ["termination", "terminate", "cancel"], 0.95, 20, "exit"),
        ClauseTemplate("ip_ownership", "IP ownership provisions", 
                      ["intellectual property", "ownership", "work product"], 0.80, 25, "ip"),
    ],
    ContractType.EMPLOYMENT: [
        ClauseTemplate("compensation", "Salary and benefits", 
                      ["salary", "compensation", "benefits"], 0.99, 40, "commercial"),
        ClauseTemplate("duties", "Job duties and responsibilities", 
                      ["duties", "responsibilities", "position"], 0.95, 25, "core"),
        ClauseTemplate("termination", "Termination conditions", 
                      ["termination", "at-will", "notice period"], 0.90, 30, "exit"),
        ClauseTemplate("non_compete", "Non-compete clause", 
                      ["non-compete", "competitive", "not engage"], 0.50, 15, "restrictive"),
        ClauseTemplate("ip_assignment", "IP assignment to employer", 
                      ["inventions", "work product", "assign"], 0.75, 20, "ip"),
    ],
}


# Global corpus tracker instance
corpus = CorpusTracker()
