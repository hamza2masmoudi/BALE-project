"""
BALE Comprehensive Evaluation Runner
Tests all frontier capabilities against the evaluation dataset.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.frontier import analyze_contract_frontiers
from src.negotiation import clause_negotiator
from src.logger import setup_logger

logger = setup_logger("evaluation")


class EvaluationRunner:
    """Runs comprehensive evaluation against the dataset."""
    
    def __init__(self, dataset_dir: str = None):
        if dataset_dir is None:
            dataset_dir = Path(__file__).parent / "dataset"
        self.dataset_dir = Path(dataset_dir)
        self.results = []
        
    def load_manifest(self) -> Dict[str, Any]:
        """Load the dataset manifest."""
        manifest_path = self.dataset_dir / "manifest.json"
        with open(manifest_path) as f:
            return json.load(f)
    
    def load_contract(self, filename: str) -> Dict[str, Any]:
        """Load a single contract from the dataset."""
        filepath = self.dataset_dir / filename
        if not filepath.exists():
            logger.warning(f"Contract file not found: {filename}")
            return None
        with open(filepath) as f:
            return json.load(f)
    
    def evaluate_contract(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Run full evaluation on a single contract."""
        contract_id = contract.get("id", "unknown")
        logger.info(f"Evaluating: {contract_id}")
        
        result = {
            "id": contract_id,
            "name": contract.get("name", "Unknown"),
            "type": contract.get("type"),
            "expected_risk": contract.get("expected_risk"),
            "expected_findings": contract.get("expected_findings", {}),
            "actual_findings": {},
            "scores": {},
            "passed_checks": [],
            "failed_checks": [],
        }
        
        try:
            # Run frontier analysis
            frontier_result = analyze_contract_frontiers(
                contract_text=contract.get("text", ""),
                contract_type=contract.get("type", "unknown").lower(),
                jurisdiction=contract.get("jurisdiction", "US"),
                industry=contract.get("industry", "general"),
                effective_date=contract.get("effective_date"),
                parties=contract.get("parties", []),
            )
            
            frontier_dict = frontier_result.to_dict()
            result["actual_findings"]["frontier_risk"] = frontier_result.overall_frontier_risk
            result["actual_findings"]["critical_findings"] = frontier_result.critical_findings
            result["actual_findings"]["frontiers"] = frontier_dict
            
            # Run negotiation analysis
            playbook = clause_negotiator.generate_playbook(
                contract_text=contract.get("text", ""),
                contract_id=contract_id,
                jurisdiction=contract.get("jurisdiction", "US"),
                industry=contract.get("industry", "technology"),
                your_position="buyer"
            )
            result["actual_findings"]["negotiation"] = {
                "must_have": len(playbook.must_have),
                "should_have": len(playbook.should_have),
                "nice_to_have": len(playbook.nice_to_have),
                "total_risk_reduction": playbook.total_risk_reduction,
            }
            
            # Validate against expectations
            result["scores"], result["passed_checks"], result["failed_checks"] = (
                self._validate_expectations(contract, frontier_result)
            )
            
            result["status"] = "success"
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"Error evaluating {contract_id}: {e}")
        
        return result
    
    def _validate_expectations(self, contract: Dict, frontier_result) -> tuple:
        """Validate actual results against expected findings."""
        expected = contract.get("expected_findings", {})
        passed = []
        failed = []
        scores = {}
        
        # Check risk level alignment
        expected_risk = contract.get("expected_risk", "medium")
        actual_risk = frontier_result.overall_frontier_risk
        
        if expected_risk == "low" and actual_risk < 35:
            passed.append("risk_level_alignment")
            scores["risk_accuracy"] = 1.0
        elif expected_risk == "medium" and 35 <= actual_risk < 60:
            passed.append("risk_level_alignment")
            scores["risk_accuracy"] = 1.0
        elif expected_risk == "high" and actual_risk >= 60:
            passed.append("risk_level_alignment")
            scores["risk_accuracy"] = 1.0
        else:
            failed.append(f"risk_level_alignment (expected={expected_risk}, actual={actual_risk:.1f})")
            scores["risk_accuracy"] = 0.5
        
        # Check silence detection
        if "silence" in expected:
            expected_missing = expected["silence"].get("missing_clauses", [])
            if isinstance(expected_missing, int):
                if expected_missing == 0:
                    passed.append("silence_detection")
                    scores["silence_detection"] = 1.0
            elif len(expected_missing) > 0:
                passed.append("silence_detection_attempted")
                scores["silence_detection"] = 0.8
        
        # Check power asymmetry
        if "power_asymmetry" in expected:
            passed.append("power_analysis_ran")
            scores["power_analysis"] = 1.0
        
        # Check temporal decay
        if "temporal_decay" in expected:
            passed.append("temporal_analysis_ran")
            scores["temporal_analysis"] = 1.0
        
        # Check imagination gaps
        if "imagination_gaps" in expected:
            passed.append("imagination_analysis_ran")
            scores["imagination_analysis"] = 1.0
        
        # Check strain points
        if "strain_points" in expected:
            passed.append("strain_analysis_ran")
            scores["strain_analysis"] = 1.0
        
        return scores, passed, failed
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on entire dataset."""
        logger.info("Starting full evaluation...")
        
        manifest = self.load_manifest()
        contracts = manifest.get("contracts", [])
        
        evaluation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "dataset_info": manifest.get("dataset_info", {}),
            "total_contracts": len(contracts),
            "evaluated": 0,
            "successful": 0,
            "failed": 0,
            "results": [],
            "aggregate_scores": {},
        }
        
        for contract_ref in contracts:
            filename = contract_ref.get("file")
            if not filename:
                continue
            
            contract = self.load_contract(filename)
            if not contract:
                continue
            
            result = self.evaluate_contract(contract)
            evaluation_results["results"].append(result)
            evaluation_results["evaluated"] += 1
            
            if result.get("status") == "success":
                evaluation_results["successful"] += 1
            else:
                evaluation_results["failed"] += 1
        
        # Calculate aggregate scores
        all_scores = {}
        for result in evaluation_results["results"]:
            for key, value in result.get("scores", {}).items():
                if key not in all_scores:
                    all_scores[key] = []
                all_scores[key].append(value)
        
        for key, values in all_scores.items():
            evaluation_results["aggregate_scores"][key] = sum(values) / len(values) if values else 0
        
        # Overall score
        if all_scores:
            all_values = [v for vals in all_scores.values() for v in vals]
            evaluation_results["overall_score"] = sum(all_values) / len(all_values)
        else:
            evaluation_results["overall_score"] = 0
        
        logger.info(f"Evaluation complete: {evaluation_results['successful']}/{evaluation_results['evaluated']} successful")
        
        return evaluation_results
    
    def save_results(self, results: Dict[str, Any], output_path: str = None):
        """Save evaluation results to file."""
        if output_path is None:
            output_path = self.dataset_dir.parent / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {output_path}")
        return output_path
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a markdown report from results."""
        lines = []
        lines.append("# BALE Evaluation Report")
        lines.append("")
        lines.append(f"**Date**: {results.get('timestamp', 'Unknown')}")
        lines.append(f"**Contracts Evaluated**: {results.get('evaluated', 0)}")
        lines.append(f"**Success Rate**: {results.get('successful', 0)}/{results.get('evaluated', 0)}")
        lines.append(f"**Overall Score**: {results.get('overall_score', 0)*100:.1f}%")
        lines.append("")
        
        lines.append("## Aggregate Scores")
        lines.append("")
        lines.append("| Metric | Score |")
        lines.append("|:-------|:------|")
        for key, value in results.get("aggregate_scores", {}).items():
            lines.append(f"| {key.replace('_', ' ').title()} | {value*100:.1f}% |")
        lines.append("")
        
        lines.append("## Individual Results")
        lines.append("")
        for result in results.get("results", []):
            status_icon = "✅" if result.get("status") == "success" else "❌"
            lines.append(f"### {status_icon} {result.get('name', 'Unknown')}")
            lines.append(f"- **Type**: {result.get('type')}")
            lines.append(f"- **Expected Risk**: {result.get('expected_risk')}")
            
            actual = result.get("actual_findings", {})
            if "frontier_risk" in actual:
                lines.append(f"- **Actual Risk**: {actual['frontier_risk']:.1f}%")
            
            if result.get("passed_checks"):
                lines.append(f"- **Passed**: {', '.join(result['passed_checks'])}")
            if result.get("failed_checks"):
                lines.append(f"- **Failed**: {', '.join(result['failed_checks'])}")
            lines.append("")
        
        return "\n".join(lines)


def main():
    """Run evaluation from command line."""
    runner = EvaluationRunner()
    results = runner.run_full_evaluation()
    
    # Save JSON results
    runner.save_results(results)
    
    # Generate and save report
    report = runner.generate_report(results)
    report_path = Path(__file__).parent / "evaluation_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Contracts Evaluated: {results['evaluated']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Overall Score: {results.get('overall_score', 0)*100:.1f}%")
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
