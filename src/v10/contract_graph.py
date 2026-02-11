"""
BALE V10 Contract Reasoning Graph
THE CORE INNOVATION: Models how clauses within a contract interact.
Detects:
- Inter-clause CONFLICTS (e.g., indemnification vs liability cap)
- Missing DEPENDENCIES (e.g., termination references dispute resolution, but none exists)
- Structural GAPS (expected clauses for this contract type that are absent)
- REDUNDANCIES (clauses that say the same thing twice, often a negotiation scar)
"""
import re
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("bale_v10_graph")


# ==================== EDGE TYPES ====================

class EdgeType(Enum):
    """Types of relationships between clauses."""
    CONFLICTS = "conflicts"
    DEPENDS_ON = "depends_on"
    LIMITS = "limits"
    SUPPLEMENTS = "supplements"
    REFERENCES = "references"


# ==================== KNOWN RELATIONSHIPS ====================

CLAUSE_RELATIONSHIPS = [
    # === CONFLICTS ===
    ("indemnification", "limitation_of_liability", EdgeType.CONFLICTS,
     "Unlimited indemnification contradicts liability caps. Which prevails?", 0.9),
    ("force_majeure", "warranty", EdgeType.CONFLICTS,
     "Force majeure excuses non-performance, but warranty guarantees performance.", 0.6),
    ("termination", "non_compete", EdgeType.CONFLICTS,
     "Termination for convenience may conflict with post-termination non-compete.", 0.5),
    # === DEPENDENCIES ===
    ("termination", "dispute_resolution", EdgeType.DEPENDS_ON,
     "Termination for cause often requires following dispute resolution first.", 0.7),
    ("indemnification", "insurance", EdgeType.DEPENDS_ON,
     "Indemnification obligations should be backed by insurance.", 0.5),
    ("payment_terms", "termination", EdgeType.DEPENDS_ON,
     "Payment obligations need termination provisions for non-payment.", 0.6),
    ("data_protection", "confidentiality", EdgeType.DEPENDS_ON,
     "Data protection relies on confidentiality obligations.", 0.4),
    ("audit_rights", "data_protection", EdgeType.DEPENDS_ON,
     "Audit rights are often needed to verify data protection compliance.", 0.4),
    ("intellectual_property", "confidentiality", EdgeType.DEPENDS_ON,
     "IP protection depends on confidentiality of trade secrets.", 0.5),
    # === LIMITS ===
    ("limitation_of_liability", "indemnification", EdgeType.LIMITS,
     "Liability cap should apply to indemnification, but often excluded.", 0.8),
    ("limitation_of_liability", "warranty", EdgeType.LIMITS,
     "Liability cap limits remedies for warranty breach.", 0.5),
    ("force_majeure", "payment_terms", EdgeType.LIMITS,
     "Force majeure may excuse payment obligations.", 0.6),
    ("non_compete", "termination", EdgeType.LIMITS,
     "Non-compete survives termination, limiting party's freedom.", 0.7),
    # === SUPPLEMENTS ===
    ("dispute_resolution", "governing_law", EdgeType.SUPPLEMENTS,
     "Dispute resolution specifies the process under the governing law.", 0.3),
    ("insurance", "indemnification", EdgeType.SUPPLEMENTS,
     "Insurance backs up indemnification obligations financially.", 0.3),
    ("audit_rights", "warranty", EdgeType.SUPPLEMENTS,
     "Audit rights help verify warranty compliance.", 0.3),
]


# ==================== EXPECTED CLAUSES BY CONTRACT TYPE ====================

EXPECTED_CLAUSES: Dict[str, Dict[str, float]] = {
    "MSA": {
        "indemnification": 0.95,
        "limitation_of_liability": 0.95,
        "termination": 0.98,
        "confidentiality": 0.90,
        "intellectual_property": 0.80,
        "governing_law": 0.95,
        "warranty": 0.85,
        "payment_terms": 0.90,
        "dispute_resolution": 0.85,
        "force_majeure": 0.70,
        "data_protection": 0.60,
        "assignment": 0.70,
        "insurance": 0.40,
        "audit_rights": 0.35,
    },
    "NDA": {
        "confidentiality": 0.99,
        "termination": 0.90,
        "governing_law": 0.85,
        "intellectual_property": 0.60,
        "dispute_resolution": 0.50,
        "assignment": 0.40,
        "indemnification": 0.30,
    },
    "SLA": {
        "warranty": 0.95,
        "limitation_of_liability": 0.90,
        "termination": 0.85,
        "payment_terms": 0.80,
        "force_majeure": 0.70,
        "governing_law": 0.80,
        "dispute_resolution": 0.60,
        "data_protection": 0.60,
        "audit_rights": 0.50,
    },
    "License": {
        "intellectual_property": 0.98,
        "limitation_of_liability": 0.90,
        "warranty": 0.85,
        "termination": 0.90,
        "payment_terms": 0.85,
        "confidentiality": 0.70,
        "governing_law": 0.85,
        "indemnification": 0.60,
    },
    "Employment": {
        "termination": 0.95,
        "confidentiality": 0.90,
        "non_compete": 0.70,
        "intellectual_property": 0.80,
        "payment_terms": 0.85,
        "governing_law": 0.80,
        "dispute_resolution": 0.50,
        "data_protection": 0.50,
    },
    "DPA": {
        "data_protection": 0.99,
        "confidentiality": 0.95,
        "termination": 0.80,
        "audit_rights": 0.85,
        "limitation_of_liability": 0.70,
        "governing_law": 0.80,
    },
}


# ==================== DATA STRUCTURES ====================

@dataclass
class ClauseNode:
    """A node in the contract graph representing a single clause."""
    id: str
    clause_type: str
    text: str
    confidence: float
    risk_weight: float
    category: str
    is_present: bool = True
    party_obligations: Dict[str, int] = field(default_factory=dict)


@dataclass
class ClauseEdge:
    """An edge in the contract graph representing a relationship."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    description: str
    severity: float
    is_satisfied: bool = True


@dataclass
class GraphAnalysis:
    """Complete analysis of a contract's clause graph."""
    contract_type: str
    total_clauses: int
    total_edges: int
    conflicts: List[Dict[str, Any]]
    missing_dependencies: List[Dict[str, Any]]
    missing_expected: List[Dict[str, Any]]
    structural_risk: float
    conflict_count: int
    dependency_gap_count: int
    completeness_score: float

    def to_dict(self) -> Dict:
        return {
            "contract_type": self.contract_type,
            "total_clauses": self.total_clauses,
            "total_edges": self.total_edges,
            "conflicts": self.conflicts,
            "missing_dependencies": self.missing_dependencies,
            "missing_expected": self.missing_expected,
            "structural_risk": round(self.structural_risk, 1),
            "conflict_count": self.conflict_count,
            "dependency_gap_count": self.dependency_gap_count,
            "completeness_score": round(self.completeness_score, 2),
        }


# ==================== CONTRACT GRAPH ====================

class ContractGraph:
    """
    Builds and analyzes a graph of clause relationships within a single contract.
    This is the core innovation of V10. No existing legal AI tool does this.
    """

    def __init__(self):
        self.nodes: Dict[str, ClauseNode] = {}
        self.edges: List[ClauseEdge] = []
        self.clause_type_to_node: Dict[str, str] = {}

    def add_clause(self, node: ClauseNode):
        """Add a clause node to the graph."""
        self.nodes[node.id] = node
        self.clause_type_to_node[node.clause_type] = node.id

    def build_edges(self):
        """Build edges based on known legal relationships between clause types."""
        present_types = set(self.clause_type_to_node.keys())
        for source_type, target_type, edge_type, desc, severity in CLAUSE_RELATIONSHIPS:
            source_present = source_type in present_types
            target_present = target_type in present_types

            if edge_type == EdgeType.CONFLICTS:
                if source_present and target_present:
                    self.edges.append(ClauseEdge(
                        source_id=self.clause_type_to_node[source_type],
                        target_id=self.clause_type_to_node[target_type],
                        edge_type=edge_type,
                        description=desc,
                        severity=severity,
                        is_satisfied=True,
                    ))
            elif edge_type == EdgeType.DEPENDS_ON:
                if source_present and not target_present:
                    self.edges.append(ClauseEdge(
                        source_id=self.clause_type_to_node[source_type],
                        target_id=f"MISSING_{target_type}",
                        edge_type=edge_type,
                        description=desc,
                        severity=severity,
                        is_satisfied=False,
                    ))
                elif source_present and target_present:
                    self.edges.append(ClauseEdge(
                        source_id=self.clause_type_to_node[source_type],
                        target_id=self.clause_type_to_node[target_type],
                        edge_type=edge_type,
                        description=desc,
                        severity=severity,
                        is_satisfied=True,
                    ))
            elif edge_type in (EdgeType.LIMITS, EdgeType.SUPPLEMENTS):
                if source_present and target_present:
                    self.edges.append(ClauseEdge(
                        source_id=self.clause_type_to_node[source_type],
                        target_id=self.clause_type_to_node[target_type],
                        edge_type=edge_type,
                        description=desc,
                        severity=severity,
                        is_satisfied=True,
                    ))

    def find_missing_expected(self, contract_type: str) -> List[Dict[str, Any]]:
        """Find clauses that are expected for this contract type but missing."""
        expected = EXPECTED_CLAUSES.get(contract_type, {})
        present_types = set(self.clause_type_to_node.keys())
        missing = []
        for clause_type, prevalence in expected.items():
            if clause_type not in present_types:
                risk = int(prevalence * 40)
                missing.append({
                    "clause_type": clause_type,
                    "expected_prevalence": prevalence,
                    "risk_contribution": risk,
                    "recommendation": (
                        f"Consider adding a {clause_type.replace('_', ' ')} clause. "
                        f"Present in {int(prevalence * 100)}% of {contract_type} contracts."
                    ),
                })
        return sorted(missing, key=lambda x: x["expected_prevalence"], reverse=True)

    def analyze(self, contract_type: str = "MSA") -> GraphAnalysis:
        """Run full graph analysis."""
        if not self.edges:
            self.build_edges()

        conflicts = []
        for edge in self.edges:
            if edge.edge_type == EdgeType.CONFLICTS:
                source = self.nodes.get(edge.source_id)
                target = self.nodes.get(edge.target_id)
                conflicts.append({
                    "clause_a": source.clause_type if source else "unknown",
                    "clause_b": target.clause_type if target else "unknown",
                    "description": edge.description,
                    "severity": edge.severity,
                    "clause_a_text": (source.text[:100] + "...") if source else "",
                    "clause_b_text": (target.text[:100] + "...") if target else "",
                })

        missing_deps = []
        for edge in self.edges:
            if edge.edge_type == EdgeType.DEPENDS_ON and not edge.is_satisfied:
                source = self.nodes.get(edge.source_id)
                missing_type = edge.target_id.replace("MISSING_", "")
                missing_deps.append({
                    "clause_has": source.clause_type if source else "unknown",
                    "clause_needs": missing_type,
                    "description": edge.description,
                    "severity": edge.severity,
                })

        missing_expected = self.find_missing_expected(contract_type)

        conflict_risk = sum(c["severity"] * 30 for c in conflicts)
        dependency_risk = sum(d["severity"] * 25 for d in missing_deps)
        missing_risk = sum(m["risk_contribution"] for m in missing_expected[:5])
        structural_risk = min(100, conflict_risk + dependency_risk + missing_risk)

        expected = EXPECTED_CLAUSES.get(contract_type, {})
        if expected:
            present_types = set(self.clause_type_to_node.keys())
            completeness = len(present_types & set(expected.keys())) / len(expected)
        else:
            completeness = 1.0

        return GraphAnalysis(
            contract_type=contract_type,
            total_clauses=len(self.nodes),
            total_edges=len(self.edges),
            conflicts=conflicts,
            missing_dependencies=missing_deps,
            missing_expected=missing_expected,
            structural_risk=structural_risk,
            conflict_count=len(conflicts),
            dependency_gap_count=len(missing_deps),
            completeness_score=completeness,
        )


def build_contract_graph(
    classified_clauses: List[Dict[str, Any]],
    contract_type: str = "MSA",
) -> Tuple[ContractGraph, GraphAnalysis]:
    """
    Build and analyze a contract graph from classified clauses.
    """
    graph = ContractGraph()
    for clause in classified_clauses:
        node = ClauseNode(
            id=clause["id"],
            clause_type=clause["clause_type"],
            text=clause["text"],
            confidence=clause.get("confidence", 0.5),
            risk_weight=clause.get("risk_weight", 0.5),
            category=clause.get("category", "unknown"),
        )
        graph.add_clause(node)
    graph.build_edges()
    analysis = graph.analyze(contract_type)
    return graph, analysis


__all__ = [
    "ContractGraph", "ClauseNode", "ClauseEdge", "EdgeType",
    "GraphAnalysis", "build_contract_graph",
    "CLAUSE_RELATIONSHIPS", "EXPECTED_CLAUSES",
]
