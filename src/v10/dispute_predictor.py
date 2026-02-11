"""
BALE V10 Dispute Hotspot Predictor
Combines graph analysis + power analysis to predict which clauses will be contested.
Innovation: Predicts WHERE a dispute will happen, not just IF risk exists.
"""
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

from src.v10.contract_graph import GraphAnalysis, EdgeType
from src.v10.power_analyzer import PowerAnalysis

logger = logging.getLogger("bale_v10_dispute")


@dataclass
class DisputeHotspot:
    """A predicted dispute hotspot."""
    clause_type: str
    clause_id: str
    dispute_probability: float
    severity: str
    reason: str
    category: str
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "clause_type": self.clause_type,
            "clause_id": self.clause_id,
            "dispute_probability": round(self.dispute_probability, 2),
            "severity": self.severity,
            "reason": self.reason,
            "category": self.category,
            "recommendation": self.recommendation,
        }


@dataclass
class DisputePrediction:
    """Complete dispute prediction for a contract."""
    hotspots: List[DisputeHotspot]
    overall_dispute_risk: float
    top_3_risks: List[str]
    dispute_count_prediction: str

    def to_dict(self) -> Dict:
        return {
            "overall_dispute_risk": round(self.overall_dispute_risk, 1),
            "top_3_risks": self.top_3_risks,
            "dispute_count_prediction": self.dispute_count_prediction,
            "hotspots": [h.to_dict() for h in self.hotspots],
        }


class DisputePredictor:
    """
    Predicts which clauses in a contract are most likely to be disputed.
    Combines three signals:
    1. Structural conflicts from the Contract Graph
    2. Power imbalance from the Power Analyzer
    3. Missing dependencies that create legal gaps
    """

    def predict(
        self,
        graph_analysis: GraphAnalysis,
        power_analysis: PowerAnalysis,
        classified_clauses: List[Dict[str, Any]],
    ) -> DisputePrediction:
        """
        Predict dispute hotspots.

        Args:
            graph_analysis: Output from ContractGraph.analyze()
            power_analysis: Output from PowerAnalyzer.analyze()
            classified_clauses: Original classified clauses
        """
        hotspots: List[DisputeHotspot] = []

        # Signal 1: Clauses involved in CONFLICTS
        for conflict in graph_analysis.conflicts:
            prob = min(0.95, conflict["severity"] * 0.8 + 0.1)
            hotspots.append(DisputeHotspot(
                clause_type=conflict["clause_a"],
                clause_id=conflict.get("clause_a_id", "?"),
                dispute_probability=prob,
                severity=self._severity(prob),
                reason=conflict["description"],
                category="conflict",
                recommendation=(
                    f"Reconcile {conflict['clause_a']} with {conflict['clause_b']}. "
                    f"Add explicit carve-out or priority clause."
                ),
            ))

        # Signal 2: Missing DEPENDENCIES
        for dep in graph_analysis.missing_dependencies:
            prob = min(0.85, dep["severity"] * 0.7 + 0.15)
            hotspots.append(DisputeHotspot(
                clause_type=dep["clause_has"],
                clause_id="?",
                dispute_probability=prob,
                severity=self._severity(prob),
                reason=(
                    f"{dep['clause_has']} depends on {dep['clause_needs']}, "
                    f"but {dep['clause_needs']} is missing. {dep['description']}"
                ),
                category="gap",
                recommendation=(
                    f"Add a {dep['clause_needs'].replace('_', ' ')} clause to "
                    f"support the {dep['clause_has'].replace('_', ' ')} provision."
                ),
            ))

        # Signal 3: ONE-SIDED clauses from power analysis
        for asym in power_analysis.asymmetric_clauses:
            prob = min(0.80, 0.4 + (power_analysis.power_score / 100) * 0.4)
            hotspots.append(DisputeHotspot(
                clause_type=asym["clause_type"],
                clause_id=asym.get("clause_id", "?"),
                dispute_probability=prob,
                severity=self._severity(prob),
                reason=(
                    f"One-sided clause favoring {asym.get('favors', 'unknown')}. "
                    f"Triggers: {', '.join(asym.get('triggers', [])[:2])}"
                ),
                category="power",
                recommendation=(
                    f"Negotiate more balanced terms in "
                    f"{asym['clause_type'].replace('_', ' ')}."
                ),
            ))

        # Signal 4: HIGH-RISK missing expected clauses
        for missing in graph_analysis.missing_expected:
            if missing["expected_prevalence"] >= 0.8:
                prob = missing["expected_prevalence"] * 0.5
                hotspots.append(DisputeHotspot(
                    clause_type=missing["clause_type"],
                    clause_id="MISSING",
                    dispute_probability=prob,
                    severity=self._severity(prob),
                    reason=(
                        f"Expected clause '{missing['clause_type'].replace('_', ' ')}' "
                        f"is missing. Present in "
                        f"{int(missing['expected_prevalence'] * 100)}% of similar contracts."
                    ),
                    category="gap",
                    recommendation=missing["recommendation"],
                ))

        # Sort by probability
        hotspots.sort(key=lambda h: h.dispute_probability, reverse=True)

        # Deduplicate by clause_type (keep highest probability)
        seen_types = set()
        unique_hotspots = []
        for h in hotspots:
            if h.clause_type not in seen_types:
                seen_types.add(h.clause_type)
                unique_hotspots.append(h)
        hotspots = unique_hotspots

        # Overall risk
        if hotspots:
            weighted_risk = sum(
                h.dispute_probability * (1 if h.severity == "CRITICAL" else 0.7)
                for h in hotspots[:5]
            )
            overall = min(100, weighted_risk * 25 + graph_analysis.structural_risk * 0.3)
        else:
            overall = max(0, graph_analysis.structural_risk * 0.3)

        # Top 3 human-readable risks
        top_3 = []
        for h in hotspots[:3]:
            top_3.append(f"{h.severity}: {h.reason}")

        # Dispute count prediction
        high_prob = sum(1 for h in hotspots if h.dispute_probability >= 0.6)
        if high_prob >= 4:
            count_pred = "High (5+ potential disputes)"
        elif high_prob >= 2:
            count_pred = "Medium (2-4 potential disputes)"
        else:
            count_pred = "Low (0-1 potential disputes)"

        return DisputePrediction(
            hotspots=hotspots,
            overall_dispute_risk=overall,
            top_3_risks=top_3,
            dispute_count_prediction=count_pred,
        )

    def _severity(self, probability: float) -> str:
        if probability >= 0.8:
            return "CRITICAL"
        elif probability >= 0.6:
            return "HIGH"
        elif probability >= 0.4:
            return "MEDIUM"
        return "LOW"


__all__ = ["DisputePredictor", "DisputePrediction", "DisputeHotspot"]
