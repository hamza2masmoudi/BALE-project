"""
BALE V11 Corpus Intelligence
Learns statistical patterns across analyzed contracts to flag outliers.

Innovation: Each contract is compared against a learned corpus profile.
"This liability cap is 2.3 std devs more restrictive than average MSA"
is something no other tool can say without a proprietary dataset.
"""
import json
import os
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import logging

logger = logging.getLogger("bale_v11_corpus")


@dataclass
class ClauseStatistics:
    """Running statistics for a single clause type."""
    count: int = 0
    confidence_sum: float = 0.0
    confidence_sq_sum: float = 0.0
    risk_weight_sum: float = 0.0
    risk_weight_sq_sum: float = 0.0
    text_length_sum: int = 0
    text_length_sq_sum: int = 0
    presence_count: int = 0  # how many contracts contain this clause

    @property
    def mean_confidence(self) -> float:
        return self.confidence_sum / max(1, self.count)

    @property
    def std_confidence(self) -> float:
        if self.count < 2:
            return 0.1
        variance = (self.confidence_sq_sum / self.count) - (self.mean_confidence ** 2)
        return max(0.01, math.sqrt(max(0, variance)))

    @property
    def mean_risk_weight(self) -> float:
        return self.risk_weight_sum / max(1, self.count)

    @property
    def std_risk_weight(self) -> float:
        if self.count < 2:
            return 0.1
        mean = self.mean_risk_weight
        variance = (self.risk_weight_sq_sum / self.count) - (mean ** 2)
        return max(0.01, math.sqrt(max(0, variance)))

    @property
    def mean_text_length(self) -> float:
        return self.text_length_sum / max(1, self.count)

    def to_dict(self) -> Dict:
        return {
            "count": self.count,
            "mean_confidence": round(self.mean_confidence, 3),
            "std_confidence": round(self.std_confidence, 3),
            "mean_risk_weight": round(self.mean_risk_weight, 3),
            "std_risk_weight": round(self.std_risk_weight, 3),
            "mean_text_length": round(self.mean_text_length, 0),
            "presence_count": self.presence_count,
        }


@dataclass
class CorpusProfile:
    """Statistical profile of the entire analyzed corpus."""
    total_contracts: int = 0
    contract_type_counts: Dict[str, int] = field(default_factory=dict)
    clause_stats: Dict[str, Dict] = field(default_factory=dict)
    # Aggregate distributions
    risk_score_sum: float = 0.0
    risk_score_sq_sum: float = 0.0
    clause_count_sum: int = 0
    clause_count_sq_sum: int = 0

    @property
    def mean_risk(self) -> float:
        return self.risk_score_sum / max(1, self.total_contracts)

    @property
    def std_risk(self) -> float:
        if self.total_contracts < 2:
            return 10.0
        mean = self.mean_risk
        variance = (self.risk_score_sq_sum / self.total_contracts) - (mean ** 2)
        return max(1.0, math.sqrt(max(0, variance)))

    @property
    def mean_clause_count(self) -> float:
        return self.clause_count_sum / max(1, self.total_contracts)

    def to_dict(self) -> Dict:
        return {
            "total_contracts": self.total_contracts,
            "contract_type_counts": self.contract_type_counts,
            "mean_risk_score": round(self.mean_risk, 1),
            "std_risk_score": round(self.std_risk, 1),
            "mean_clause_count": round(self.mean_clause_count, 1),
            "clause_statistics": self.clause_stats,
        }


@dataclass
class ClauseAnomaly:
    """An anomalous clause detected via corpus comparison."""
    clause_type: str
    clause_id: str
    anomaly_type: str  # "outlier", "missing", "unusual_confidence", "unusual_length"
    z_score: float
    description: str
    severity: str  # "info", "warning", "alert"

    def to_dict(self) -> Dict:
        return {
            "clause_type": self.clause_type,
            "clause_id": self.clause_id,
            "anomaly_type": self.anomaly_type,
            "z_score": round(self.z_score, 2),
            "description": self.description,
            "severity": self.severity,
        }


@dataclass
class CorpusComparison:
    """Result of comparing a contract against the corpus."""
    anomalies: List[ClauseAnomaly]
    risk_z_score: float  # how unusual is this contract's risk score
    structural_similarity: float  # 0-1, how similar to corpus average
    clause_coverage_percentile: float  # what % of typical clauses are present
    summary: str

    def to_dict(self) -> Dict:
        return {
            "anomalies": [a.to_dict() for a in self.anomalies],
            "risk_z_score": round(self.risk_z_score, 2),
            "structural_similarity": round(self.structural_similarity, 2),
            "clause_coverage_percentile": round(self.clause_coverage_percentile, 1),
            "summary": self.summary,
        }


class CorpusIntelligence:
    """
    Learns statistical patterns from analyzed contracts.
    Compares new contracts against learned distributions to flag outliers.
    
    Persists profiles to JSON for cross-session learning.
    """

    def __init__(self, profile_path: Optional[str] = None):
        if profile_path is None:
            profile_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "evaluation", "corpus_profile.json"
            )
        self.profile_path = profile_path
        self._profile: Optional[CorpusProfile] = None
        self._clause_stats: Dict[str, ClauseStatistics] = defaultdict(ClauseStatistics)
        self._load_profile()

    def _load_profile(self):
        """Load corpus profile from disk if it exists."""
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r") as f:
                    data = json.load(f)
                self._profile = CorpusProfile(
                    total_contracts=data.get("total_contracts", 0),
                    contract_type_counts=data.get("contract_type_counts", {}),
                    clause_stats=data.get("clause_statistics", {}),
                    risk_score_sum=data.get("_risk_score_sum", 0.0),
                    risk_score_sq_sum=data.get("_risk_score_sq_sum", 0.0),
                    clause_count_sum=data.get("_clause_count_sum", 0),
                    clause_count_sq_sum=data.get("_clause_count_sq_sum", 0),
                )
                # Reconstruct ClauseStatistics
                raw_stats = data.get("_raw_clause_stats", {})
                for ct, stats in raw_stats.items():
                    cs = ClauseStatistics(**stats)
                    self._clause_stats[ct] = cs
                logger.info(
                    f"Loaded corpus profile: {self._profile.total_contracts} contracts"
                )
            except Exception as e:
                logger.warning(f"Failed to load corpus profile: {e}")
                self._profile = CorpusProfile()
        else:
            self._profile = CorpusProfile()

    def _save_profile(self):
        """Persist corpus profile to disk."""
        try:
            data = self._profile.to_dict()
            # Save raw stats for reconstruction
            data["_risk_score_sum"] = self._profile.risk_score_sum
            data["_risk_score_sq_sum"] = self._profile.risk_score_sq_sum
            data["_clause_count_sum"] = self._profile.clause_count_sum
            data["_clause_count_sq_sum"] = self._profile.clause_count_sq_sum
            data["_raw_clause_stats"] = {
                ct: asdict(stats) for ct, stats in self._clause_stats.items()
            }
            os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
            with open(self.profile_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved corpus profile ({self._profile.total_contracts} contracts)")
        except Exception as e:
            logger.warning(f"Failed to save corpus profile: {e}")

    def ingest(self, report_dict: Dict[str, Any]):
        """
        Learn from an analyzed contract report.
        Updates running statistics incrementally.
        
        Args:
            report_dict: Output of V10Report.to_dict()
        """
        meta = report_dict.get("metadata", {})
        contract_type = meta.get("contract_type", "UNKNOWN")
        total_clauses = meta.get("total_clauses", 0)
        risk_score = report_dict.get("overall", {}).get("risk_score", 50.0)

        # Update aggregate stats
        self._profile.total_contracts += 1
        self._profile.contract_type_counts[contract_type] = (
            self._profile.contract_type_counts.get(contract_type, 0) + 1
        )
        self._profile.risk_score_sum += risk_score
        self._profile.risk_score_sq_sum += risk_score ** 2
        self._profile.clause_count_sum += total_clauses
        self._profile.clause_count_sq_sum += total_clauses ** 2

        # Track which clause types are present
        seen_types = set()

        # Update per-clause statistics
        classifications = report_dict.get("classifications", [])
        for clause in classifications:
            ct = clause.get("clause_type", "unknown")
            conf = clause.get("confidence", 0.5)
            text_len = len(clause.get("text_preview", ""))
            rw = clause.get("risk_weight", 0.5) if "risk_weight" in clause else 0.5

            stats = self._clause_stats[ct]
            stats.count += 1
            stats.confidence_sum += conf
            stats.confidence_sq_sum += conf ** 2
            stats.risk_weight_sum += rw
            stats.risk_weight_sq_sum += rw ** 2
            stats.text_length_sum += text_len
            stats.text_length_sq_sum += text_len ** 2

            seen_types.add(ct)

        # Update presence counts
        for ct in seen_types:
            self._clause_stats[ct].presence_count += 1

        # Update readable stats
        self._profile.clause_stats = {
            ct: stats.to_dict() for ct, stats in self._clause_stats.items()
        }

        # Save to disk
        self._save_profile()

    def compare(self, report_dict: Dict[str, Any]) -> CorpusComparison:
        """
        Compare a contract against the learned corpus profile.
        
        Returns anomalies, z-scores, and structural comparison.
        """
        if self._profile.total_contracts < 3:
            return CorpusComparison(
                anomalies=[],
                risk_z_score=0.0,
                structural_similarity=0.5,
                clause_coverage_percentile=50.0,
                summary="Insufficient corpus data for comparison (need 3+ contracts).",
            )

        anomalies: List[ClauseAnomaly] = []
        risk_score = report_dict.get("overall", {}).get("risk_score", 50.0)
        contract_type = report_dict.get("metadata", {}).get("contract_type", "UNKNOWN")

        # Risk z-score
        risk_z = (risk_score - self._profile.mean_risk) / self._profile.std_risk

        # Check classifications for anomalies
        classifications = report_dict.get("classifications", [])
        present_types = set()

        for clause in classifications:
            ct = clause.get("clause_type", "unknown")
            conf = clause.get("confidence", 0.5)
            present_types.add(ct)

            if ct in self._clause_stats and self._clause_stats[ct].count >= 3:
                stats = self._clause_stats[ct]

                # Confidence z-score
                conf_z = (conf - stats.mean_confidence) / stats.std_confidence
                if abs(conf_z) > 2.0:
                    anomalies.append(ClauseAnomaly(
                        clause_type=ct,
                        clause_id=clause.get("id", "?"),
                        anomaly_type="unusual_confidence",
                        z_score=conf_z,
                        description=(
                            f"Classification confidence ({conf:.2f}) is "
                            f"{'unusually low' if conf_z < 0 else 'unusually high'} "
                            f"compared to the corpus average ({stats.mean_confidence:.2f}). "
                            f"This clause may be atypical or misclassified."
                        ),
                        severity="warning" if abs(conf_z) > 2.5 else "info",
                    ))

        # Check for missing common clauses
        for ct, stats in self._clause_stats.items():
            if stats.count < 3:
                continue
            prevalence = stats.presence_count / self._profile.total_contracts
            if prevalence > 0.7 and ct not in present_types:
                anomalies.append(ClauseAnomaly(
                    clause_type=ct,
                    clause_id="MISSING",
                    anomaly_type="missing",
                    z_score=-prevalence * 3,
                    description=(
                        f"Clause type '{ct.replace('_', ' ')}' is present in "
                        f"{prevalence:.0%} of similar contracts but missing here."
                    ),
                    severity="warning" if prevalence > 0.85 else "info",
                ))

        # Check for unusual clause types (present here but rare in corpus)
        for ct in present_types:
            if ct in self._clause_stats:
                stats = self._clause_stats[ct]
                prevalence = stats.presence_count / self._profile.total_contracts
                if prevalence < 0.15 and stats.presence_count >= 1:
                    anomalies.append(ClauseAnomaly(
                        clause_type=ct,
                        clause_id="PRESENT",
                        anomaly_type="outlier",
                        z_score=2.0,
                        description=(
                            f"Clause type '{ct.replace('_', ' ')}' is unusual "
                            f"(only in {prevalence:.0%} of similar contracts)."
                        ),
                        severity="info",
                    ))

        # Risk z-score anomaly
        if abs(risk_z) > 2.0:
            anomalies.append(ClauseAnomaly(
                clause_type="overall",
                clause_id="RISK",
                anomaly_type="outlier",
                z_score=risk_z,
                description=(
                    f"Overall risk score ({risk_score:.0f}) is "
                    f"{'significantly higher' if risk_z > 0 else 'significantly lower'} "
                    f"than the corpus average ({self._profile.mean_risk:.0f} +/- "
                    f"{self._profile.std_risk:.0f})."
                ),
                severity="alert" if abs(risk_z) > 3.0 else "warning",
            ))

        # Structural similarity: Jaccard similarity of clause types
        all_corpus_types = set(self._clause_stats.keys())
        common_types = present_types.intersection(all_corpus_types)
        if all_corpus_types:
            structural_sim = len(common_types) / len(all_corpus_types.union(present_types))
        else:
            structural_sim = 0.5

        # Clause coverage percentile
        total_expected = sum(
            1 for ct, stats in self._clause_stats.items()
            if stats.presence_count / max(1, self._profile.total_contracts) > 0.5
        )
        coverage = len(present_types.intersection(
            ct for ct, stats in self._clause_stats.items()
            if stats.presence_count / max(1, self._profile.total_contracts) > 0.5
        )) / max(1, total_expected) * 100

        # Sort anomalies by severity
        severity_order = {"alert": 0, "warning": 1, "info": 2}
        anomalies.sort(key=lambda a: (severity_order.get(a.severity, 3), -abs(a.z_score)))

        # Generate summary
        summary = self._generate_summary(anomalies, risk_z, structural_sim, coverage)

        return CorpusComparison(
            anomalies=anomalies,
            risk_z_score=risk_z,
            structural_similarity=structural_sim,
            clause_coverage_percentile=coverage,
            summary=summary,
        )

    def _generate_summary(
        self,
        anomalies: List[ClauseAnomaly],
        risk_z: float,
        structural_sim: float,
        coverage: float,
    ) -> str:
        """Generate natural language summary of corpus comparison."""
        parts = []

        n_contracts = self._profile.total_contracts
        parts.append(f"Compared against corpus of {n_contracts} analyzed contracts.")

        if abs(risk_z) > 2:
            parts.append(
                f"Risk score is {'unusually high' if risk_z > 0 else 'unusually low'} "
                f"(z={risk_z:.1f})."
            )
        elif abs(risk_z) > 1:
            parts.append(
                f"Risk score is {'above' if risk_z > 0 else 'below'} average "
                f"(z={risk_z:.1f})."
            )
        else:
            parts.append("Risk score is within normal range.")

        alerts = sum(1 for a in anomalies if a.severity == "alert")
        warnings = sum(1 for a in anomalies if a.severity == "warning")
        if alerts:
            parts.append(f"{alerts} critical anomaly(ies) detected.")
        if warnings:
            parts.append(f"{warnings} warning(s) flagged.")
        if not alerts and not warnings:
            parts.append("No significant anomalies detected.")

        parts.append(f"Clause coverage: {coverage:.0f}% of typical clauses present.")
        return " ".join(parts)

    @property
    def profile(self) -> CorpusProfile:
        """Get the current corpus profile."""
        return self._profile


__all__ = [
    "CorpusIntelligence", "CorpusProfile", "CorpusComparison",
    "ClauseAnomaly", "ClauseStatistics",
]
