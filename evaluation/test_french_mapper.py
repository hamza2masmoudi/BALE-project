"""
French Performance Test with Label Mapper
Tests V8 Ultimate French accuracy with the new French label mapping layer.
"""
import sys
sys.path.insert(0, '/Users/hamza/BALE-project')

from mlx_lm import load, generate
from src.french_label_mapper import FrenchLabelMapper, detect_language

# French test cases with expected labels
FRENCH_TEST_CASES = [
    # Indemnification
    (
        "Le Prestataire s'engage à indemniser et garantir le Client contre tout dommage.",
        "indemnification",
        "HIGH"
    ),
    (
        "Le Fournisseur garantit l'Acheteur contre toute réclamation de tiers.",
        "indemnification",
        "HIGH"
    ),
    
    # Limitation of Liability
    (
        "La responsabilité totale du Prestataire ne saurait excéder le montant des sommes versées.",
        "limitation",
        "HIGH"
    ),
    (
        "EN AUCUN CAS LE PRESTATAIRE NE POURRA ÊTRE TENU RESPONSABLE DES DOMMAGES INDIRECTS.",
        "limitation",
        "HIGH"
    ),
    
    # Confidentiality
    (
        "Les parties s'engagent à maintenir la confidentialité des informations échangées.",
        "confidentiality",
        "LOW"
    ),
    
    # Governing Law
    (
        "Le présent Contrat est régi par le droit français.",
        "governing",
        "LOW"
    ),
    (
        "Tout litige sera soumis aux tribunaux de Paris.",
        "governing",
        "LOW"
    ),
    
    # Termination
    (
        "Chaque partie peut résilier le Contrat moyennant un préavis de 90 jours.",
        "termination",
        "MEDIUM"
    ),
    
    # Force Majeure
    (
        "Aucune des parties ne sera responsable en cas de force majeure.",
        "force_majeure",
        "MEDIUM"
    ),
    
    # GDPR
    (
        "Le Sous-traitant traite les données conformément à l'article 28 du RGPD.",
        "gdpr",
        "MEDIUM"
    ),
]


def run_french_test_with_mapper():
    """Run French tests with label mapping."""
    print("Loading V8 Ultimate model...")
    model, tokenizer = load(
        "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
        adapter_path="models/bale-legal-lora-v8-ultimate"
    )
    print("Model loaded!")
    
    mapper = FrenchLabelMapper()
    
    print("\n" + "=" * 70)
    print("FRENCH PERFORMANCE TEST WITH LABEL MAPPER")
    print("=" * 70)
    
    correct_type = 0
    correct_risk = 0
    total = len(FRENCH_TEST_CASES)
    
    for i, (text, expected_type, expected_risk) in enumerate(FRENCH_TEST_CASES, 1):
        # Create prompt
        prompt_text = f"Classifiez cette clause contractuelle:\n\n{text}"
        messages = [{"role": "user", "content": prompt_text}]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        # Generate
        response = generate(model, tokenizer, prompt=prompt, max_tokens=100, verbose=False)
        
        # Use mapper to normalize - pass input text for direct analysis
        result = mapper.parse_model_output(response, is_french=True, input_text=text)
        predicted_type = result["clause_type"]
        predicted_risk = result["risk_level"]
        
        # Check accuracy (flexible matching)
        type_correct = expected_type in predicted_type or predicted_type.startswith(expected_type[:5])
        risk_correct = predicted_risk == expected_risk
        
        if type_correct:
            correct_type += 1
        if risk_correct:
            correct_risk += 1
        
        status = "✅" if type_correct else "❌"
        print(f"\n[{i}/{total}] {status}")
        print(f"  Input: {text[:60]}...")
        print(f"  Raw output: {response.split(chr(10))[0][:50]}...")
        print(f"  Mapped: {predicted_type} / {predicted_risk}")
        print(f"  Expected: {expected_type} / {expected_risk}")
    
    type_acc = correct_type / total * 100
    risk_acc = correct_risk / total * 100
    
    print("\n" + "=" * 70)
    print("RESULTS WITH LABEL MAPPER")
    print("=" * 70)
    print(f"  Type Accuracy:  {type_acc:.1f}% ({correct_type}/{total})")
    print(f"  Risk Accuracy:  {risk_acc:.1f}% ({correct_risk}/{total})")
    print(f"  Combined:       {(type_acc + risk_acc) / 2:.1f}%")
    print()
    print(f"  Improvement: 10% → {type_acc:.1f}% (+{type_acc - 10:.1f}%)")
    print("=" * 70)
    
    return {"type_accuracy": type_acc, "risk_accuracy": risk_acc}


if __name__ == "__main__":
    run_french_test_with_mapper()
