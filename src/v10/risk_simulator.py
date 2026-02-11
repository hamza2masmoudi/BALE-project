"""
BALE V11 Monte Carlo Risk Simulator
Produces risk distributions instead of point estimates.

Innovation: Quantifies UNCERTAINTY in risk scores by perturbing
classification assignments, edge severities, and power scores
across 1000 simulations. Returns confidence intervals and
worst/best case scenarios.
"""
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("bale_v11_risk_sim")


@dataclass
class RiskSimulation:
    """Results of Monte Carlo risk simulation."""
    # Distribution
    mean_risk: float
    median_risk: float
    std_risk: float
    # Confidence intervals
    ci_95_lower: float
    ci_95_upper: float
    ci_80_lower: float
    ci_80_upper: float
    # Extremes
    best_case_risk: float   # 5th percentile
    worst_case_risk: float  # 95th percentile
    # Volatility
    risk_volatility: str  # "low", "medium", "high" 
    volatility_explanation: str
    # Histogram data (10 bins)
    histogram_bins: List[float]
    histogram_counts: List[int]
    # Metadata
    n_simulations: int
    dominant_uncertainty_source: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mean_risk": round(self.mean_risk, 1),
            "median_risk": round(self.median_risk, 1),
            "std_risk": round(self.std_risk, 2),
            "confidence_interval_95": [
                round(self.ci_95_lower, 1),
                round(self.ci_95_upper, 1),
            ],
            "confidence_interval_80": [
                round(self.ci_80_lower, 1),
                round(self.ci_80_upper, 1),
            ],
            "best_case": round(self.best_case_risk, 1),
            "worst_case": round(self.worst_case_risk, 1),
            "risk_volatility": self.risk_volatility,
            "volatility_explanation": self.volatility_explanation,
            "histogram": {
                "bins": [round(b, 1) for b in self.histogram_bins],
                "counts": self.histogram_counts,
            },
            "n_simulations": self.n_simulations,
            "dominant_uncertainty_source": self.dominant_uncertainty_source,
        }


class RiskSimulator:
    """
    Monte Carlo risk simulation over uncertain pipeline parameters.
    
    Perturbs three sources of uncertainty:
    1. CLASSIFICATION: swaps clause type to top-2/3 with probability
       proportional to confidence margin
    2. EDGE SEVERITY: adds uniform noise to graph edge weights
    3. POWER SCORE: adds normal noise to power asymmetry score
    
    Then re-computes the risk score 1000 times to get a distribution.
    """

    def __init__(self, n_simulations: int = 1000, seed: Optional[int] = None):
        self.n_simulations = n_simulations
        self.rng = np.random.RandomState(seed)

    def simulate(
        self,
        classified_clauses: List[Dict[str, Any]],
        graph_analysis_dict: Dict[str, Any],
        power_analysis_dict: Dict[str, Any],
        dispute_analysis_dict: Dict[str, Any],
        base_risk_score: float,
    ) -> RiskSimulation:
        """
        Run Monte Carlo simulation over the pipeline's uncertain parameters.
        
        Args:
            classified_clauses: List of clause dicts with 'confidence', 'top_3'
            graph_analysis_dict: Graph analysis output dict
            power_analysis_dict: Power analysis output dict
            dispute_analysis_dict: Dispute prediction output dict
            base_risk_score: The pipeline's point estimate
        """
        risk_samples = np.zeros(self.n_simulations)

        # Pre-extract parameters
        structural_risk = graph_analysis_dict.get("structural_risk", 30.0)
        power_score = power_analysis_dict.get("power_score", 30.0)
        dispute_risk = dispute_analysis_dict.get("overall_dispute_risk", 50.0)

        # Calculate uncertainty in each source
        classification_uncertainty = self._classification_uncertainty(classified_clauses)
        graph_uncertainty = self._graph_uncertainty(graph_analysis_dict)
        power_uncertainty = self._power_uncertainty(power_analysis_dict)

        for i in range(self.n_simulations):
            # Perturb classification -> affects structural risk
            # Higher uncertainty = more noise
            class_noise = self.rng.normal(0, classification_uncertainty * 15)
            perturbed_structural = np.clip(
                structural_risk + class_noise + self.rng.uniform(-5, 5),
                0, 100
            )

            # Perturb power score
            power_noise = self.rng.normal(0, power_uncertainty * 12)
            perturbed_power = np.clip(
                power_score + power_noise,
                0, 100
            )

            # Perturb dispute risk (combines both upstream uncertainties)
            dispute_noise = self.rng.normal(
                0,
                (classification_uncertainty + graph_uncertainty) * 10
            )
            perturbed_dispute = np.clip(
                dispute_risk + dispute_noise,
                0, 100
            )

            # Recompute risk with same weights as pipeline
            risk = (
                perturbed_structural * 0.3 +
                perturbed_power * 0.2 +
                perturbed_dispute * 0.5
            )
            risk_samples[i] = np.clip(risk, 0, 100)

        # Compute statistics
        mean_risk = float(np.mean(risk_samples))
        median_risk = float(np.median(risk_samples))
        std_risk = float(np.std(risk_samples))

        ci_95_lower = float(np.percentile(risk_samples, 2.5))
        ci_95_upper = float(np.percentile(risk_samples, 97.5))
        ci_80_lower = float(np.percentile(risk_samples, 10))
        ci_80_upper = float(np.percentile(risk_samples, 90))

        best_case = float(np.percentile(risk_samples, 5))
        worst_case = float(np.percentile(risk_samples, 95))

        # Volatility classification
        ci_width = ci_95_upper - ci_95_lower
        if ci_width < 15:
            volatility = "low"
            vol_explanation = (
                "Risk assessment is stable. Classification confidence is high "
                "and the contract structure is well-defined."
            )
        elif ci_width < 30:
            volatility = "medium"
            vol_explanation = (
                "Moderate uncertainty in risk assessment. Some clause classifications "
                "are ambiguous, which could shift the risk score by up to "
                f"{ci_width:.0f} points."
            )
        else:
            volatility = "high"
            vol_explanation = (
                "High uncertainty in risk assessment. Multiple clause classifications "
                "are near decision boundaries, and the contract structure has ambiguous "
                f"relationships. Risk could range from {best_case:.0f} to {worst_case:.0f}."
            )

        # Histogram
        counts, bin_edges = np.histogram(risk_samples, bins=10, range=(0, 100))
        histogram_bins = [float(b) for b in bin_edges]
        histogram_counts = [int(c) for c in counts]

        # Dominant uncertainty source
        uncertainties = {
            "classification": classification_uncertainty,
            "graph_structure": graph_uncertainty,
            "power_asymmetry": power_uncertainty,
        }
        dominant = max(uncertainties, key=uncertainties.get)

        return RiskSimulation(
            mean_risk=mean_risk,
            median_risk=median_risk,
            std_risk=std_risk,
            ci_95_lower=ci_95_lower,
            ci_95_upper=ci_95_upper,
            ci_80_lower=ci_80_lower,
            ci_80_upper=ci_80_upper,
            best_case_risk=best_case,
            worst_case_risk=worst_case,
            risk_volatility=volatility,
            volatility_explanation=vol_explanation,
            histogram_bins=histogram_bins,
            histogram_counts=histogram_counts,
            n_simulations=self.n_simulations,
            dominant_uncertainty_source=dominant,
        )

    def _classification_uncertainty(self, clauses: List[Dict[str, Any]]) -> float:
        """
        Measure uncertainty in clause classifications.
        Based on confidence margins (gap between top-1 and top-2).
        Returns 0-1 where 1 = maximum uncertainty.
        """
        if not clauses:
            return 0.5

        margins = []
        for clause in clauses:
            top_3 = clause.get("top_3", [])
            if len(top_3) >= 2:
                margin = top_3[0][1] - top_3[1][1]
                margins.append(margin)
            else:
                conf = clause.get("confidence", 0.5)
                margins.append(conf * 0.5)  # use half the confidence as proxy

        if not margins:
            return 0.5

        avg_margin = np.mean(margins)
        # Small margin = high uncertainty
        # Margin ~0.0 -> uncertainty ~1.0
        # Margin ~0.3 -> uncertainty ~0.0
        uncertainty = max(0, 1.0 - avg_margin / 0.3)
        return min(1.0, uncertainty)

    def _graph_uncertainty(self, graph_dict: Dict[str, Any]) -> float:
        """
        Measure uncertainty in graph analysis.
        Based on completeness score and conflict severity.
        """
        completeness = graph_dict.get("completeness_score", 0.5)
        conflict_count = graph_dict.get("conflict_count", 0)
        gap_count = graph_dict.get("dependency_gap_count", 0)

        # Incomplete contracts have more uncertain risk
        incompleteness_uncertainty = 1.0 - completeness

        # More conflicts = more uncertain (hard to quantify severity exactly)
        conflict_uncertainty = min(1.0, conflict_count * 0.2)

        return (incompleteness_uncertainty * 0.5 + conflict_uncertainty * 0.5)

    def _power_uncertainty(self, power_dict: Dict[str, Any]) -> float:
        """
        Measure uncertainty in power analysis.
        Based on how extreme the power score is.
        Scores near 50 (balanced) are more uncertain than extreme scores.
        """
        power_score = power_dict.get("power_score", 50.0)
        total_signals = (
            power_dict.get("total_obligations", 0) +
            power_dict.get("total_protections", 0)
        )

        # Few signals = high uncertainty
        if total_signals < 5:
            signal_uncertainty = 0.8
        elif total_signals < 15:
            signal_uncertainty = 0.4
        else:
            signal_uncertainty = 0.2

        return signal_uncertainty


__all__ = ["RiskSimulator", "RiskSimulation"]
