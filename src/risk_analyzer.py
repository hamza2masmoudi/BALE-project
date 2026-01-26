"""
BALE Enhanced Risk Analyzer

Improves risk detection accuracy through:
1. Improved prompt engineering with risk-reasoning guidance
2. Rule-based risk indicator detection
3. Confidence scoring

Works with the existing V8 model at inference time - no retraining needed.
"""

from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass


# =============================================================================
# RISK INDICATORS
# =============================================================================

# HIGH risk patterns - clauses containing these are likely high risk
HIGH_RISK_PATTERNS = {
    # Unlimited scope (English)
    "unlimited": 3,
    "without limit": 3,
    "without limitation": 2,
    "any and all": 2,
    "regardless of": 2,
    "under any circumstances": 3,
    "in no event": 2,
    
    # Perpetual/extreme duration
    "perpetuity": 3,
    "in perpetuity": 3,
    "forever": 2,
    "permanent": 2,
    "irrevocable": 2,
    "irrevocably": 2,
    
    # One-sided terms
    "sole discretion": 3,
    "absolute discretion": 3,
    "without cause": 2,
    "at any time": 1,
    "immediately": 1,
    "without notice": 3,
    "without prior notice": 3,
    
    # Warranty disclaimers
    "as is": 3,
    "as-is": 3,
    "without warranty": 3,
    "no warranty": 3,
    "disclaims all": 2,
    "no representations": 2,
    
    # Liability exclusions
    "no liability": 3,
    "not be liable": 2,
    "expressly disclaim": 2,
    "waives": 2,
    "waive all": 3,
    "forfeit": 2,
    
    # Harsh terms
    "non-refundable": 2,
    "2% per month": 2,
    "24 hours": 2,
    "7 days": 1,
    
    # Offshore/unusual jurisdictions
    "cayman islands": 4,
    "british virgin islands": 4,
    "seychelles": 3,
    "îles caïmans": 4,
    
    # Broad scope
    "worldwide": 2,
    "anywhere in the world": 2,
    "including but not limited to": 1,
    
    # Fault exclusion
    "regardless of fault": 3,
    "regardless of negligence": 3,
    "even if advised": 2,
    "including negligence": 2,
    
    # Data/privacy violations
    "sell all data": 3,
    "unrestricted rights": 3,
    "marketing to third parties": 2,
    
    # Non-compete overreach
    "five years": 2,
    "10 years": 3,
    "ten years": 3,
    
    # ============================================================
    # FRENCH HIGH RISK PATTERNS
    # ============================================================
    
    # Unlimited scope (French)
    "illimité": 3,
    "sans limite": 3,
    "sans limitation": 2,
    "quelle que soit": 2,
    "en aucun cas": 2,
    "quelles que soient": 2,
    "quoi que ce soit": 2,
    
    # Perpetual (French)
    "perpétuité": 3,
    "à perpétuité": 3,
    "permanent": 2,
    "irrévocable": 2,
    "irrévocablement": 2,
    
    # One-sided (French)
    "seule discrétion": 3,
    "discrétion absolue": 3,
    "sans motif": 2,
    "à tout moment": 1,
    "immédiatement": 1,
    "sans préavis": 3,
    "sans notification": 3,
    
    # Warranty disclaimers (French)
    "en l'état": 3,
    "sans garantie": 3,
    "sans aucune garantie": 3,
    "décline toute": 2,
    "exclut toute": 2,
    
    # Liability exclusions (French)
    "aucune responsabilité": 3,
    "ne sera pas responsable": 2,
    "ne saurait être responsable": 2,
    "renonce": 2,
    "renonciation": 2,
    
    # Harsh terms (French)
    "non remboursable": 2,
    "2% par mois": 2,
    "24 heures": 2,
    "7 jours": 1,
    
    # Fault exclusion (French)
    "quelle que soit la faute": 3,
    "indépendamment de la faute": 3,
    "même en cas de négligence": 2,
    
    # Non-compete overreach (French)
    "cinq ans": 2,
    "dix ans": 3,
    "partout dans le monde": 2,
}

# MEDIUM risk patterns
MEDIUM_RISK_PATTERNS = {
    # Standard but noteworthy (English)
    "reasonable": 0,
    "industry standard": 0,
    "commercially reasonable": 0,
    
    # Common limitations
    "12 months": 1,
    "twelve months": 1,
    "material breach": 0,
    "30 days": 0,
    "60 days": 0,
    
    # Mutual terms (reduce risk)
    "mutual": -1,
    "each party": -1,
    "neither party": 0,
    
    # Sub-processors/third parties
    "sub-processor": 1,
    "third party": 1,
    
    # Change clauses
    "may be updated": 1,
    "from time to time": 1,
    "at its option": 1,
    
    # FRENCH MEDIUM PATTERNS
    "raisonnable": 0,
    "norme de l'industrie": 0,
    "commercialement raisonnable": 0,
    "12 mois": 1,
    "douze mois": 1,
    "30 jours": 0,
    "60 jours": 0,
    "manquement substantiel": 0,
    "mutuel": -1,
    "chaque partie": -1,
    "aucune des parties": 0,
}

# LOW risk patterns - clauses containing these suggest lower risk
LOW_RISK_PATTERNS = {
    # Balanced terms (English)
    "balanced": -2,
    "proportional": -2,
    "pro rata": -1,
    "fair": -1,
    
    # Protective caps
    "capped at": -2,
    "limited to": -1,
    "shall not exceed": -1,
    "up to the": -1,
    "maximum of": -1,
    
    # Non-exclusive
    "non-exclusive": -2,
    "nonexclusive": -2,
    
    # Standard exclusions
    "standard exclusions": -2,
    "customary": -1,
    "typical": -1,
    
    # Carve-outs (protection)
    "except for": -1,
    "carve-out": -2,
    "excluding": -1,
    
    # Reasonable timeframes
    "3 years": -1,
    "three years": -1,
    "2 years": -1,
    "two years": -1,
    "6 months": -1,
    "six months": -1,
    
    # Consent requirements
    "mutual consent": -2,
    "written consent": -1,
    "prior consent": -1,
    
    # Compliance
    "gdpr": 0,
    "article 28": -1,
    "iso 27001": -2,
    "soc 2": -2,
    
    # Dispute options
    "non-binding": -1,
    "may pursue": -1,
    "courts of competent jurisdiction": -1,
    
    # ============================================================
    # FRENCH LOW RISK PATTERNS
    # ============================================================
    
    # Balanced (French)
    "équilibré": -2,
    "proportionnel": -2,
    "au prorata": -1,
    "équitable": -1,
    
    # Protective caps (French)
    "plafonné": -2,
    "limité à": -1,
    "plafonnée": -2,
    "ne dépassera pas": -1,
    "ne saurait excéder": -1,
    "maximum de": -1,
    "concurrence de": -1,
    
    # Non-exclusive (French)
    "non exclusif": -2,
    "non-exclusive": -2,
    "non exclusive": -2,
    
    # Standard exclusions (French)
    "exclusions standard": -2,
    "usage habituel": -1,
    "pratique courante": -1,
    
    # Reasonable timeframes (French)
    "3 ans": -2,
    "trois ans": -2,
    "2 ans": -1,
    "deux ans": -1,
    "6 mois": -1,
    "six mois": -1,
    
    # Consent requirements (French)
    "consentement mutuel": -2,
    "consentement écrit": -1,
    "consentement préalable": -1,
    "accord préalable": -1,
    
    # Compliance (French)
    "rgpd": 0,
    "article 28": -1,
    
    # Standard terms (French)
    "conforme": -1,
    "standard": -1,
    "usuel": -1,
}


@dataclass
class RiskAssessment:
    """Result of risk analysis."""
    risk_level: str  # "low", "medium", "high"
    confidence: float  # 0.0 to 1.0
    risk_score: float  # Raw score
    high_indicators: List[str]
    low_indicators: List[str]
    rationale: str
    needs_review: bool


class EnhancedRiskAnalyzer:
    """
    Analyzes contract clauses for risk level using:
    1. Pattern-based indicator detection
    2. Enhanced prompts for model inference
    3. Confidence scoring
    """
    
    def __init__(self):
        self.high_patterns = HIGH_RISK_PATTERNS
        self.medium_patterns = MEDIUM_RISK_PATTERNS
        self.low_patterns = LOW_RISK_PATTERNS
    
    def analyze_risk(self, clause_text: str, model_output: str = None) -> RiskAssessment:
        """
        Analyze risk level of a clause.
        
        Args:
            clause_text: The contract clause to analyze
            model_output: Optional model response if already generated
            
        Returns:
            RiskAssessment with level, confidence, and explanation
        """
        text_lower = clause_text.lower()
        
        # Find all matching indicators
        high_indicators = []
        low_indicators = []
        risk_score = 0
        
        # Check HIGH risk patterns
        for pattern, weight in self.high_patterns.items():
            if pattern.lower() in text_lower:
                high_indicators.append(pattern)
                risk_score += weight
        
        # Check MEDIUM patterns (neutral/slight adjustment)
        for pattern, weight in self.medium_patterns.items():
            if pattern.lower() in text_lower:
                risk_score += weight
        
        # Check LOW risk patterns
        for pattern, weight in self.low_patterns.items():
            if pattern.lower() in text_lower:
                low_indicators.append(pattern)
                risk_score += weight  # These have negative weights
        
        # ============================================================
        # SMART LOW RISK DETECTION
        # If NO high risk indicators found AND has positive signals
        # ============================================================
        
        if len(high_indicators) == 0:
            # Check for mutual/symmetrical language (moderate LOW signal)
            mutual_patterns = [
                "each party", "either party", "both parties", "mutual",
                "chaque partie", "les parties", "mutuel", "mutuellement"
            ]
            has_mutual = False
            for pattern in mutual_patterns:
                if pattern in text_lower:
                    has_mutual = True
                    low_indicators.append(f"mutual: {pattern}")
                    break
            
            # Only bias toward LOW if we have BOTH no red flags AND positive signals
            if has_mutual and len(low_indicators) >= 1:
                risk_score -= 1  # Strong LOW signal
            elif has_mutual or len(low_indicators) >= 1:
                risk_score -= 0.5  # Weak LOW signal
        
        # Determine risk level from score
        if risk_score >= 3:
            risk_level = "high"
        elif risk_score <= -2:  # Back to -2 for balanced detection
            risk_level = "low"
        else:
            risk_level = "medium"
        
        # ============================================================
        # MODEL OUTPUT INTEGRATION
        # Trust model more when rule-based is uncertain
        # ============================================================
        
        model_risk = None
        if model_output:
            model_risk = self._extract_model_risk(model_output)
            
            # If rule-based says MEDIUM, let model tip the balance
            if risk_level == "medium":
                # Model says LOW and we have no red flags and some positive signals
                if model_risk == "low" and len(high_indicators) == 0 and len(low_indicators) >= 1:
                    risk_level = "low"
                # Model says HIGH and we have at least one concerning pattern
                elif model_risk == "high" and len(high_indicators) >= 1:
                    risk_level = "high"
        
        # Calculate confidence
        indicator_count = len(high_indicators) + len(low_indicators)
        if indicator_count >= 3:
            confidence = 0.9
        elif indicator_count >= 2:
            confidence = 0.75
        elif indicator_count >= 1:
            confidence = 0.6
        else:
            confidence = 0.4  # No clear indicators
        
        # Boost confidence if model agrees
        if model_risk and model_risk == risk_level:
            confidence = min(confidence + 0.1, 0.95)
        elif model_risk and model_risk != risk_level:
            confidence = max(confidence - 0.1, 0.3)
        
        # Generate rationale
        rationale = self._generate_rationale(risk_level, high_indicators, low_indicators, risk_score)
        
        # Flag for review if low confidence
        needs_review = confidence < 0.6
        
        return RiskAssessment(
            risk_level=risk_level,
            confidence=confidence,
            risk_score=risk_score,
            high_indicators=high_indicators,
            low_indicators=low_indicators,
            rationale=rationale,
            needs_review=needs_review
        )
    
    def _extract_model_risk(self, model_output: str) -> Optional[str]:
        """Extract risk level from model output."""
        output_lower = model_output.lower()
        
        if "high" in output_lower:
            return "high"
        elif "medium" in output_lower:
            return "medium"
        elif "low" in output_lower:
            return "low"
        return None
    
    def _generate_rationale(self, risk_level: str, high_ind: List[str], 
                           low_ind: List[str], score: float) -> str:
        """Generate human-readable risk rationale."""
        parts = []
        
        if risk_level == "high":
            if high_ind:
                parts.append(f"Contains high-risk terms: {', '.join(high_ind[:3])}")
            else:
                parts.append("Multiple concerning patterns detected")
        elif risk_level == "low":
            if low_ind:
                parts.append(f"Contains protective terms: {', '.join(low_ind[:3])}")
            else:
                parts.append("Balanced structure with limited exposure")
        else:
            if high_ind and low_ind:
                parts.append(f"Mixed signals: risks ({', '.join(high_ind[:2])}) balanced by ({', '.join(low_ind[:2])})")
            else:
                parts.append("Standard terms with moderate exposure")
        
        return ". ".join(parts)
    
    def get_enhanced_prompt(self, clause_text: str) -> str:
        """
        Generate an enhanced prompt that guides the model to reason about risk.
        """
        return f"""<s>[INST] You are an expert contract attorney analyzing legal clauses for risk.

Analyze this contract clause and determine:
1. The clause TYPE (e.g., indemnification, limitation_of_liability, termination, confidentiality, intellectual_property, governing_law, force_majeure, warranty, payment_terms, non_compete, data_protection, assignment, dispute_resolution, insurance, audit_rights)
2. The RISK LEVEL (low, medium, high) based on these criteria:

HIGH RISK indicators:
- Unlimited liability or indemnification without caps
- "As-is" warranties or complete disclaimers
- One-sided termination rights
- Perpetual obligations
- Offshore jurisdiction (Cayman Islands, BVI, etc.)
- Waiver of legal rights
- "Regardless of fault" language

LOW RISK indicators:
- Mutual obligations applying to both parties
- Liability caps tied to contract value
- Standard carve-outs and exclusions
- Reasonable timeframes (2-3 years)
- Non-exclusive jurisdiction
- Consent requirements

CLAUSE TO ANALYZE:
"{clause_text}"

Respond in this exact format:
Type: [clause type]
Risk: [low/medium/high]
Reason: [one sentence explaining the risk level] [/INST]"""


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Global analyzer instance
_analyzer = EnhancedRiskAnalyzer()


def analyze_clause_risk(clause_text: str, model_output: str = None) -> Dict:
    """
    Analyze risk of a contract clause.
    
    Args:
        clause_text: The clause to analyze
        model_output: Optional model response
        
    Returns:
        Dict with risk_level, confidence, rationale, etc.
    """
    assessment = _analyzer.analyze_risk(clause_text, model_output)
    
    return {
        "risk_level": assessment.risk_level,
        "confidence": assessment.confidence,
        "risk_score": assessment.risk_score,
        "high_indicators": assessment.high_indicators,
        "low_indicators": assessment.low_indicators,
        "rationale": assessment.rationale,
        "needs_review": assessment.needs_review
    }


def get_risk_prompt(clause_text: str) -> str:
    """Get enhanced prompt for risk-aware inference."""
    return _analyzer.get_enhanced_prompt(clause_text)


def combine_assessments(model_risk: str, rule_based: Dict) -> Dict:
    """
    Combine model prediction with rule-based analysis.
    
    When they agree: high confidence
    When they disagree: prefer rule-based, flag for review
    """
    rb_risk = rule_based["risk_level"]
    
    if model_risk == rb_risk:
        # Agreement - high confidence
        return {
            "risk_level": rb_risk,
            "confidence": min(rule_based["confidence"] + 0.15, 0.95),
            "source": "consensus",
            "rationale": rule_based["rationale"],
            "needs_review": False
        }
    else:
        # Disagreement - prefer rule-based but flag
        return {
            "risk_level": rb_risk,
            "confidence": max(rule_based["confidence"] - 0.1, 0.4),
            "source": "rule_based",
            "model_said": model_risk,
            "rationale": f"{rule_based['rationale']} (Model predicted {model_risk})",
            "needs_review": True
        }


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    # Test cases
    test_clauses = [
        {
            "text": "Provider shall not be liable for any damages whatsoever, including direct, indirect, or consequential damages, regardless of fault.",
            "expected": "high"
        },
        {
            "text": "Each party shall indemnify the other for direct damages caused by material breach, limited to 12 months' fees.",
            "expected": "low"
        },
        {
            "text": "Either party may terminate upon 60 days' notice. Liability is capped at contract value.",
            "expected": "low"  
        },
        {
            "text": "Customer grants Provider unlimited rights to use all data for any purpose including marketing to third parties.",
            "expected": "high"
        },
        {
            "text": "This Agreement is governed by the laws of the Cayman Islands. All disputes shall be resolved by arbitration in Singapore.",
            "expected": "high"
        },
        {
            "text": "Services are provided AS IS without warranty of any kind.",
            "expected": "high"
        },
        {
            "text": "Confidential information shall be protected for 3 years using reasonable care. Standard exclusions apply.",
            "expected": "low"
        }
    ]
    
    print("="*60)
    print("ENHANCED RISK ANALYZER TEST")
    print("="*60)
    
    correct = 0
    for i, test in enumerate(test_clauses, 1):
        result = analyze_clause_risk(test["text"])
        match = "✓" if result["risk_level"] == test["expected"] else "✗"
        if result["risk_level"] == test["expected"]:
            correct += 1
            
        print(f"\n[{i}] {match} Expected: {test['expected'].upper()} | Got: {result['risk_level'].upper()}")
        print(f"    Confidence: {result['confidence']:.0%}")
        print(f"    Rationale: {result['rationale']}")
        if result["high_indicators"]:
            print(f"    High indicators: {result['high_indicators']}")
        if result["low_indicators"]:
            print(f"    Low indicators: {result['low_indicators']}")
    
    print(f"\n{'='*60}")
    print(f"Accuracy: {correct}/{len(test_clauses)} ({100*correct/len(test_clauses):.0f}%)")
