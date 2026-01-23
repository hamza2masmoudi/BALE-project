"""
BALE V8 Ultimate - Comprehensive Evaluation Suite
Proves the solution's worth with multiple evaluation metrics.
"""
import json
import time
import random
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from collections import defaultdict
import statistics

from mlx_lm import load, generate


@dataclass
class EvalResult:
    test_id: str
    input_text: str
    expected_type: str
    predicted_type: str
    expected_risk: str
    predicted_risk: str
    is_type_correct: bool
    is_risk_correct: bool
    latency_ms: int
    language: str


class ComprehensiveEvaluator:
    """Comprehensive evaluation suite for BALE V8."""
    
    def __init__(self, model_path: str = "models/bale-legal-lora-v8-ultimate"):
        print("Loading V8 Ultimate model...")
        self.model, self.tokenizer = load(
            "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            adapter_path=model_path
        )
        print("Model loaded!")
        self.results: List[EvalResult] = []
    
    def classify(self, text: str, lang: str = "en") -> Tuple[str, str, int]:
        """Classify a clause and return (type, risk, latency_ms)."""
        if lang == "fr":
            prompt_text = f"Classifiez cette clause contractuelle:\n\n{text}"
        else:
            prompt_text = f"Classify this contract clause:\n\n{text}"
        
        messages = [{"role": "user", "content": prompt_text}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        start = time.time()
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=100,
            verbose=False
        )
        latency = int((time.time() - start) * 1000)
        
        # Parse response
        pred_type = "unknown"
        pred_risk = "MEDIUM"
        
        for line in response.strip().split("\n"):
            line_lower = line.lower()
            if "type:" in line_lower:
                pred_type = line.split(":", 1)[1].strip().lower().replace(" ", "_")
            elif "risk" in line_lower and "level" in line_lower:
                if "high" in line_lower:
                    pred_risk = "HIGH"
                elif "low" in line_lower:
                    pred_risk = "LOW"
                else:
                    pred_risk = "MEDIUM"
        
        return pred_type, pred_risk, latency
    
    def run_all_evaluations(self):
        """Run all evaluation suites."""
        print("\n" + "=" * 70)
        print("BALE V8 ULTIMATE - COMPREHENSIVE EVALUATION")
        print("=" * 70)
        
        # 1. English Classification Accuracy
        print("\n[1/6] English Classification Accuracy...")
        en_results = self._eval_english_classification()
        
        # 2. French Classification Accuracy
        print("\n[2/6] French Classification Accuracy...")
        fr_results = self._eval_french_classification()
        
        # 3. Risk Detection Accuracy
        print("\n[3/6] Risk Detection Accuracy...")
        risk_results = self._eval_risk_detection()
        
        # 4. Latency Benchmark
        print("\n[4/6] Latency Benchmark...")
        latency_results = self._eval_latency()
        
        # 5. Edge Cases
        print("\n[5/6] Edge Case Handling...")
        edge_results = self._eval_edge_cases()
        
        # 6. Real CUAD Samples
        print("\n[6/6] Real CUAD Contract Samples...")
        cuad_results = self._eval_cuad_samples()
        
        # Compile results
        return self._compile_report(en_results, fr_results, risk_results, 
                                    latency_results, edge_results, cuad_results)
    
    def _eval_english_classification(self) -> Dict:
        """Evaluate English clause classification."""
        test_cases = [
            # Indemnification
            ("Provider shall indemnify, defend and hold harmless Customer from any claims.", "indemnification", "HIGH"),
            ("Each party shall indemnify the other against third-party claims.", "indemnification", "HIGH"),
            ("Supplier agrees to fully indemnify Buyer from all losses.", "indemnification", "HIGH"),
            
            # Limitation of Liability
            ("IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT DAMAGES.", "limitation_liability", "HIGH"),
            ("Total liability shall not exceed fees paid in the preceding 12 months.", "limitation_liability", "HIGH"),
            ("Neither party shall be liable for consequential or punitive damages.", "limitation_liability", "HIGH"),
            
            # Termination
            ("Either party may terminate with 90 days written notice.", "termination", "MEDIUM"),
            ("This Agreement may be terminated for convenience upon 30 days notice.", "termination", "MEDIUM"),
            ("Customer may terminate immediately upon material breach.", "termination", "MEDIUM"),
            
            # Confidentiality
            ("Each party shall maintain confidentiality of proprietary information.", "confidentiality", "LOW"),
            ("Receiving party agrees not to disclose Confidential Information.", "confidentiality", "LOW"),
            
            # Governing Law
            ("This Agreement shall be governed by the laws of England and Wales.", "governing_law", "LOW"),
            ("The laws of Delaware shall govern this Agreement.", "governing_law", "LOW"),
            
            # Force Majeure
            ("Neither party liable for delays due to acts of God or war.", "force_majeure", "MEDIUM"),
            ("Force majeure includes natural disasters and government actions.", "force_majeure", "MEDIUM"),
            
            # IP
            ("All intellectual property created shall be owned by Customer.", "ip_ownership", "HIGH"),
            ("Provider grants Customer a non-exclusive license.", "license", "MEDIUM"),
            
            # Non-Compete
            ("Employee shall not compete for 12 months after termination.", "non_compete", "HIGH"),
            ("Seller agrees not to engage in competing business for 2 years.", "non_compete", "HIGH"),
            
            # Warranty
            ("Provider warrants services will be performed professionally.", "warranty", "LOW"),
            ("Goods are warranted free from defects for 12 months.", "warranty", "LOW"),
        ]
        
        correct = 0
        results = []
        
        for text, expected_cat, expected_risk in test_cases:
            pred_type, pred_risk, latency = self.classify(text, "en")
            
            # Flexible matching
            is_correct = any(cat in pred_type.lower() for cat in [expected_cat])
            if is_correct:
                correct += 1
            
            results.append({
                "text": text[:50],
                "expected": expected_cat,
                "predicted": pred_type,
                "correct": is_correct
            })
        
        accuracy = correct / len(test_cases)
        print(f"   Accuracy: {accuracy:.1%} ({correct}/{len(test_cases)})")
        
        return {"accuracy": accuracy, "correct": correct, "total": len(test_cases), "results": results}
    
    def _eval_french_classification(self) -> Dict:
        """Evaluate French clause classification."""
        test_cases = [
            # Indemnification
            ("Le Prestataire s'engage à indemniser et garantir le Client contre tout dommage.", "indemnification", "HIGH"),
            ("Le Fournisseur garantit l'Acheteur contre toute réclamation de tiers.", "indemnification", "HIGH"),
            
            # Limitation of Liability
            ("La responsabilité totale du Prestataire ne saurait excéder le montant des sommes versées.", "limitation", "HIGH"),
            ("EN AUCUN CAS LE PRESTATAIRE NE POURRA ÊTRE TENU RESPONSABLE DES DOMMAGES INDIRECTS.", "limitation", "HIGH"),
            
            # Confidentiality
            ("Les parties s'engagent à maintenir la confidentialité des informations échangées.", "confidentialite", "LOW"),
            
            # Governing Law
            ("Le présent Contrat est régi par le droit français.", "droit", "LOW"),
            ("Tout litige sera soumis aux tribunaux de Paris.", "juridiction", "LOW"),
            
            # Termination
            ("Chaque partie peut résilier le Contrat moyennant un préavis de 90 jours.", "resiliation", "MEDIUM"),
            
            # Force Majeure
            ("Aucune des parties ne sera responsable en cas de force majeure.", "force_majeure", "MEDIUM"),
            
            # GDPR
            ("Le Sous-traitant traite les données conformément à l'article 28 du RGPD.", "rgpd", "MEDIUM"),
        ]
        
        correct = 0
        results = []
        
        for text, expected_cat, expected_risk in test_cases:
            pred_type, pred_risk, latency = self.classify(text, "fr")
            
            # French flexible matching
            is_correct = any(cat in pred_type.lower() for cat in [expected_cat, expected_cat[:5]])
            if is_correct:
                correct += 1
            
            results.append({
                "text": text[:50],
                "expected": expected_cat,
                "predicted": pred_type,
                "correct": is_correct
            })
        
        accuracy = correct / len(test_cases)
        print(f"   Accuracy: {accuracy:.1%} ({correct}/{len(test_cases)})")
        
        return {"accuracy": accuracy, "correct": correct, "total": len(test_cases), "results": results}
    
    def _eval_risk_detection(self) -> Dict:
        """Evaluate risk level detection."""
        test_cases = [
            # HIGH risk
            ("Provider shall indemnify Customer against ALL claims without limit.", "HIGH"),
            ("IN NO EVENT SHALL PARTY BE LIABLE - EXCLUSION OF ALL WARRANTIES.", "HIGH"),
            ("Unlimited liability for any breach of this Agreement.", "HIGH"),
            ("Employee shall not compete for 24 months post-termination.", "HIGH"),
            
            # MEDIUM risk
            ("Either party may terminate upon 60 days notice.", "MEDIUM"),
            ("Force majeure events suspend performance obligations.", "MEDIUM"),
            
            # LOW risk
            ("This Agreement is governed by English law.", "LOW"),
            ("Services will be performed in a professional manner.", "LOW"),
            ("Parties shall maintain confidentiality.", "LOW"),
        ]
        
        correct = 0
        results = []
        
        for text, expected_risk in test_cases:
            _, pred_risk, _ = self.classify(text, "en")
            
            is_correct = pred_risk == expected_risk
            if is_correct:
                correct += 1
            
            results.append({
                "text": text[:50],
                "expected": expected_risk,
                "predicted": pred_risk,
                "correct": is_correct
            })
        
        accuracy = correct / len(test_cases)
        print(f"   Accuracy: {accuracy:.1%} ({correct}/{len(test_cases)})")
        
        return {"accuracy": accuracy, "correct": correct, "total": len(test_cases)}
    
    def _eval_latency(self) -> Dict:
        """Benchmark inference latency."""
        test_text = "Provider shall indemnify Customer from any claims arising under this Agreement."
        
        latencies = []
        for _ in range(10):
            _, _, latency = self.classify(test_text, "en")
            latencies.append(latency)
        
        avg = statistics.mean(latencies)
        p50 = sorted(latencies)[5]
        p95 = sorted(latencies)[9]
        
        print(f"   Avg: {avg:.0f}ms | P50: {p50}ms | P95: {p95}ms")
        
        return {"avg_ms": avg, "p50_ms": p50, "p95_ms": p95}
    
    def _eval_edge_cases(self) -> Dict:
        """Test edge cases and robustness."""
        edge_cases = [
            # Very short
            ("Indemnify all claims.", "indemnification"),
            # Very long
            ("The Provider hereby agrees to indemnify, defend, protect and hold completely harmless the Customer, its subsidiaries, affiliates, officers, directors, employees, agents and representatives from and against any and all claims, demands, actions, suits, proceedings, losses, damages, liabilities, costs and expenses including reasonable attorneys fees.", "indemnification"),
            # Mixed case
            ("PROVIDER SHALL indemnify Customer.", "indemnification"),
            # With numbers
            ("Liability capped at $1,000,000 or 12 months of fees.", "limitation"),
            # Legal jargon
            ("Notwithstanding the foregoing, neither party shall be liable for consequential damages.", "limitation"),
        ]
        
        correct = 0
        for text, expected_cat in edge_cases:
            pred_type, _, _ = self.classify(text, "en")
            if expected_cat in pred_type.lower():
                correct += 1
        
        accuracy = correct / len(edge_cases)
        print(f"   Accuracy: {accuracy:.1%} ({correct}/{len(edge_cases)})")
        
        return {"accuracy": accuracy, "correct": correct, "total": len(edge_cases)}
    
    def _eval_cuad_samples(self) -> Dict:
        """Test on real CUAD contract excerpts."""
        # Real excerpts from CUAD dataset
        cuad_samples = [
            ("Seller shall indemnify and hold harmless Buyer and its Affiliates from any Losses arising out of any breach of any representation or warranty of Seller.", "indemnification"),
            ("In no event will either party be liable for any lost profits or any indirect, special, incidental or consequential damages.", "limitation"),
            ("This Agreement shall be governed by and construed in accordance with the laws of the State of New York.", "governing_law"),
            ("Either party may terminate this Agreement upon ninety (90) days prior written notice to the other party.", "termination"),
            ("The parties agree to submit any dispute to binding arbitration under ICC rules in London.", "arbitration"),
        ]
        
        correct = 0
        for text, expected_cat in cuad_samples:
            pred_type, _, _ = self.classify(text, "en")
            if expected_cat in pred_type.lower() or expected_cat[:5] in pred_type.lower():
                correct += 1
        
        accuracy = correct / len(cuad_samples)
        print(f"   Accuracy: {accuracy:.1%} ({correct}/{len(cuad_samples)})")
        
        return {"accuracy": accuracy, "correct": correct, "total": len(cuad_samples)}
    
    def _compile_report(self, en, fr, risk, latency, edge, cuad) -> Dict:
        """Compile comprehensive evaluation report."""
        report = {
            "english_classification": en,
            "french_classification": fr,
            "risk_detection": risk,
            "latency": latency,
            "edge_cases": edge,
            "cuad_samples": cuad,
            "overall": {
                "english_accuracy": en["accuracy"],
                "french_accuracy": fr["accuracy"],
                "risk_accuracy": risk["accuracy"],
                "edge_case_accuracy": edge["accuracy"],
                "cuad_accuracy": cuad["accuracy"],
                "avg_latency_ms": latency["avg_ms"]
            }
        }
        
        # Calculate overall score
        overall_acc = (en["accuracy"] + fr["accuracy"] + risk["accuracy"] + cuad["accuracy"]) / 4
        report["overall"]["combined_accuracy"] = overall_acc
        
        print("\n" + "=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print(f"  English Classification: {en['accuracy']:.1%}")
        print(f"  French Classification:  {fr['accuracy']:.1%}")
        print(f"  Risk Detection:         {risk['accuracy']:.1%}")
        print(f"  Edge Cases:             {edge['accuracy']:.1%}")
        print(f"  CUAD Real Samples:      {cuad['accuracy']:.1%}")
        print(f"  Average Latency:        {latency['avg_ms']:.0f}ms")
        print("-" * 70)
        print(f"  OVERALL ACCURACY:       {overall_acc:.1%}")
        print("=" * 70)
        
        return report


def main():
    evaluator = ComprehensiveEvaluator()
    results = evaluator.run_all_evaluations()
    
    # Save results
    output_path = Path("evaluation/v8_ultimate_results.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
