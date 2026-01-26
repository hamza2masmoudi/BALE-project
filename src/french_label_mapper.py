"""
French Label Mapper for BALE V8 Ultimate
Maps French legal terms to standardized English labels.
Fixes the 10% French accuracy issue by normalizing outputs.
"""
from typing import Dict, Tuple, Optional
import re


# French term → English label mapping
FRENCH_TO_ENGLISH = {
    # Indemnification
    "garantie": "indemnification_broad",
    "indemnisation": "indemnification_broad",
    "indemnité": "indemnification_broad",
    "dédommagement": "indemnification_broad",
    "responsabilité": "indemnification_broad",
    
    # Limitation of Liability
    "limitation": "limitation_liability",
    "plafonnement": "limitation_liability",
    "exclusion": "exclusion_consequential",
    "dommages indirects": "exclusion_consequential",
    
    # Confidentiality
    "confidentialité": "confidentiality_mutual",
    "confidentialite": "confidentiality_mutual",
    "secret": "confidentiality_mutual",
    "non-divulgation": "confidentiality_mutual",
    
    # Termination
    "résiliation": "termination_cause",
    "resiliation": "termination_cause",
    "rupture": "termination_cause",
    "fin du contrat": "termination_convenience",
    
    # Governing Law
    "droit": "governing_law_fr",
    "droit français": "governing_law_fr",
    "droit francais": "governing_law_fr",
    "loi applicable": "governing_law_fr",
    "juridiction": "governing_law_fr",
    "tribunaux": "governing_law_fr",
    
    # Force Majeure
    "force majeure": "force_majeure_broad",
    "cas fortuit": "force_majeure_broad",
    "événement imprévisible": "force_majeure_broad",
    
    # Arbitration
    "arbitrage": "arbitration_icc",
    "médiation": "mediation",
    "règlement des litiges": "dispute_resolution",
    
    # Non-Compete
    "non-concurrence": "non_compete_12mo",
    "clause de non concurrence": "non_compete_12mo",
    "interdiction de concurrence": "non_compete_12mo",
    
    # IP
    "propriété intellectuelle": "ip_ownership_provider",
    "propriete intellectuelle": "ip_ownership_provider",
    "droits d'auteur": "ip_ownership_provider",
    "licence": "ip_license_nonexclusive",
    
    # Warranty
    "garantie légale": "warranty_express",
    "garantie contractuelle": "warranty_express",
    
    # GDPR/Data Protection
    "rgpd": "gdpr_processor",
    "données personnelles": "gdpr_processor",
    "donnees personnelles": "gdpr_processor",
    "protection des données": "gdpr_processor",
    "sous-traitance": "gdpr_processor",
    
    # General
    "général": "general",
    "general": "general",
    "dispositions diverses": "general",
}

# Risk level mapping (French → English)
FRENCH_RISK_TO_ENGLISH = {
    "élevé": "HIGH",
    "eleve": "HIGH",
    "haut": "HIGH",
    "moyen": "MEDIUM",
    "modéré": "MEDIUM",
    "modere": "MEDIUM",
    "faible": "LOW",
    "bas": "LOW",
}

# Reverse mapping for generating French outputs
ENGLISH_TO_FRENCH = {
    # Clause types
    "indemnification_broad": "INDEMNISATION",
    "indemnification_narrow": "INDEMNISATION LIMITÉE",
    "limitation_liability": "LIMITATION DE RESPONSABILITÉ",
    "exclusion_consequential": "EXCLUSION DES DOMMAGES INDIRECTS",
    "confidentiality_mutual": "CONFIDENTIALITÉ MUTUELLE",
    "termination_cause": "RÉSILIATION POUR CAUSE",
    "termination_convenience": "RÉSILIATION DE CONVENANCE",
    "governing_law_fr": "LOI APPLICABLE (FRANCE)",
    "governing_law_uk": "LOI APPLICABLE (UK)",
    "force_majeure_broad": "FORCE MAJEURE",
    "arbitration_icc": "ARBITRAGE CCI",
    "non_compete_12mo": "NON-CONCURRENCE (12 MOIS)",
    "ip_ownership_provider": "PROPRIÉTÉ INTELLECTUELLE",
    "ip_license_nonexclusive": "LICENCE NON EXCLUSIVE",
    "warranty_express": "GARANTIE EXPRESSE",
    "gdpr_processor": "RGPD - SOUS-TRAITANCE",
    "general": "GÉNÉRAL",
    
    # Risk levels
    "HIGH": "ÉLEVÉ",
    "MEDIUM": "MOYEN",
    "LOW": "FAIBLE",
}


class FrenchLabelMapper:
    """Maps French legal terms to standardized English labels."""
    
    def __init__(self):
        self.fr_to_en = FRENCH_TO_ENGLISH
        self.en_to_fr = ENGLISH_TO_FRENCH
        self.risk_fr_to_en = FRENCH_RISK_TO_ENGLISH
    
    def normalize_french_output(self, output: str) -> Tuple[str, str]:
        """
        Normalize French model output to English labels.
        
        Args:
            output: Raw model output (may contain French terms)
            
        Returns:
            Tuple of (clause_type, risk_level) in English
        """
        output_lower = output.lower()
        
        # Extract clause type
        clause_type = "general"
        for fr_term, en_type in self.fr_to_en.items():
            if fr_term in output_lower:
                clause_type = en_type
                break
        
        # Extract risk level
        risk_level = "MEDIUM"  # default
        for fr_risk, en_risk in self.risk_fr_to_en.items():
            if fr_risk in output_lower:
                risk_level = en_risk
                break
        
        # Also check for English risk levels in output
        if "high" in output_lower:
            risk_level = "HIGH"
        elif "low" in output_lower:
            risk_level = "LOW"
        
        return clause_type, risk_level
    
    def translate_to_french(self, clause_type: str, risk_level: str) -> Tuple[str, str]:
        """
        Translate English labels to French for display.
        
        Args:
            clause_type: English clause type
            risk_level: English risk level
            
        Returns:
            Tuple of (french_clause_type, french_risk_level)
        """
        fr_type = self.en_to_fr.get(clause_type, clause_type.upper().replace("_", " "))
        fr_risk = self.en_to_fr.get(risk_level, risk_level)
        
        return fr_type, fr_risk
    
    def parse_model_output(self, output: str, is_french: bool = False, input_text: str = "") -> Dict:
        """
        Parse model output and return structured result.
        Uses input text analysis for French to improve accuracy.
        
        Args:
            output: Raw model output
            is_french: Whether the input was French
            input_text: Original input text for additional analysis
            
        Returns:
            Dict with clause_type, risk_level, confidence
        """
        # For French, analyze the INPUT text directly (more reliable than model output)
        if is_french and input_text:
            clause_type, risk_level = self._classify_french_input(input_text)
        else:
            clause_type, risk_level = self.normalize_french_output(output)
        
        return {
            "clause_type": clause_type,
            "risk_level": risk_level,
            "is_french_input": is_french
        }
    
    def _classify_french_input(self, text: str) -> Tuple[str, str]:
        """
        Classify French text directly by analyzing keywords.
        This is more reliable than depending on model output.
        """
        text_lower = text.lower()
        
        # Indemnification patterns
        if any(term in text_lower for term in ["indemniser", "garantir", "indemnité", "dédommag"]):
            return "indemnification_broad", "HIGH"
        
        # Limitation of liability patterns
        if any(term in text_lower for term in ["responsabilité", "en aucun cas", "ne saurait excéder", "plafond", "limitation"]):
            if "indirect" in text_lower or "consécutif" in text_lower:
                return "exclusion_consequential", "HIGH"
            return "limitation_liability", "HIGH"
        
        # Confidentiality patterns
        if any(term in text_lower for term in ["confidential", "secret", "non-divulgation", "divulguer"]):
            return "confidentiality_mutual", "LOW"
        
        # Termination patterns
        if any(term in text_lower for term in ["résilier", "résiliation", "mettre fin", "rupture"]):
            if "préavis" in text_lower or "convenance" in text_lower:
                return "termination_convenience", "MEDIUM"
            return "termination_cause", "MEDIUM"
        
        # Governing law patterns
        if any(term in text_lower for term in ["droit français", "loi française", "tribunaux", "juridiction", "régi par"]):
            return "governing_law_fr", "LOW"
        
        # Force majeure patterns
        if any(term in text_lower for term in ["force majeure", "cas fortuit", "événement imprévisible"]):
            return "force_majeure_broad", "MEDIUM"
        
        # Arbitration patterns
        if any(term in text_lower for term in ["arbitrage", "arbitre", "cci", "icc"]):
            return "arbitration_icc", "LOW"
        
        # Non-compete patterns
        if any(term in text_lower for term in ["non-concurrence", "concurrence", "concurrent"]):
            return "non_compete_12mo", "HIGH"
        
        # IP patterns
        if any(term in text_lower for term in ["propriété intellectuelle", "droits d'auteur", "brevet", "marque"]):
            return "ip_ownership_provider", "HIGH"
        
        # GDPR patterns
        if any(term in text_lower for term in ["rgpd", "données personnelles", "sous-traitant", "article 28"]):
            return "gdpr_processor", "MEDIUM"
        
        # Warranty patterns
        if any(term in text_lower for term in ["garantie", "vice caché", "conformité"]):
            return "warranty_express", "LOW"
        
        # Default
        return "general", "MEDIUM"


def detect_language(text: str) -> str:
    """Detect if text is French or English."""
    french_indicators = [
        "le ", "la ", "les ", "du ", "de ", "des ", 
        "contrat", "prestataire", "client", "société",
        "conformément", "présent", "aux termes"
    ]
    
    text_lower = text.lower()
    french_count = sum(1 for ind in french_indicators if ind in text_lower)
    
    return "fr" if french_count >= 2 else "en"


# Singleton instance
mapper = FrenchLabelMapper()


def normalize_output(output: str, input_text: str) -> Dict:
    """
    Main function to normalize model output.
    Detects language and applies appropriate mapping.
    """
    lang = detect_language(input_text)
    return mapper.parse_model_output(output, is_french=(lang == "fr"))
