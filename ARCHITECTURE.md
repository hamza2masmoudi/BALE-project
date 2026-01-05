# BALE 2.1 Cognitive Architecture

**Status**: Phase 11 - Open Neural Validation  
**Date**: January 2026  
**Version**: 2.1.0 (Open-Weight)

---

## 1. Purpose & Scope

### What BALE Is
BALE (Binary Adjudication & Litigation Engine) is a **deterministic neuro-symbolic engine** designed to predict litigation risk in commercial contract disputes. It simulates the interaction between conflicting legal systems (Civil Law vs. Common Law) using an adversarial multi-agent architecture, culminating in a rigorous, symbolically grounded verdict.

### BALE 2.1: The Open Neural Reasoner
In Version 2.1, BALE explicitly rejects proprietary AI dependencies.
*   **No Wrappers**: The system does not use LangChain wrappers or proprietary SDKs (OpenAI/Anthropic).
*   **Local Inference**: All neural reasoning is performed via raw HTTP calls to a local inference endpoint (e.g., `localhost:8000`).
*   **Model Agnostic**: Ideally powered by **Qwen2.5-32B-Instruct** or similar high-reasoning open-weight models.

---

## 2. Ontology-First Principle

BALE 2.0 rejects the idea that "Code is Law" or "Text is Law." Instead, it enforces a strict **Legal Ontology**.

### The LegalNode
All legal data is structured as `LegalNode` objects, not raw strings.

```python
class LegalNode:
    id: str
    text_content: str
    system: LegalSystem      # CIVIL_LAW | COMMON_LAW
    authority_level: int     # 0-100
    binding_status: str      # MANDATORY | DEFAULT | PERSUASIVE
```

### Authority Hierarchy
Weights are hardcoded to preventing "LLM Hallucinated Priority."

| Level | Type | Example | Weight |
| :--- | :--- | :--- | :--- |
| **100** | CONSTITUTIONAL | Constitution / Basic Law | Absolute Override |
| **90** | STATUTORY | Civil Code / Acts of Parliament | Mandatory |
| **70** | SUPREME COURT | Cour de Cassation / Supreme Court | Strong Precedent |
| **30** | CONTRACTUAL | The Agreement itself | Subject to Law |

**Core Axiom**: *A lower-level authority (e.g., Contract) cannot override a higher-level Mandatory authority (e.g., Statue).*

---

## 3. Neuro-Symbolic Pipeline (Open Slots)

The architecture follows a strict linear data flow, where Neural components are treated as interchangeable "Scientific Instruments".

1.  **Ingestion**: Raw clause text is received.
2.  **Authority Retrieval (Gatekeeper)**: Vector Database retrieves relevant `LegalNode` citations.
3.  **Interpretation (Neural Agents)**:
    *   **Slot**: Local Inference Endpoint (`/v1/chat/completions`).
    *   **Civilist**: Interprets via Statute.
    *   **Commonist**: Interprets via Precedent.
    *   **Synthesizer**: Measures the "Interpretive Gap" (0-100).
4.  **Adversarial Simulation**:
    *   **Slot**: Local Inference Endpoint (`/v1/chat/completions`).
    *   **Plaintiff**: Maximizes claim using Contra Proferentem.
    *   **Defense**: Minimizes claim using Strict Construction.
5.  **Fact Extraction (Judge Clerk)**: An LLM acts *only* as a clerk to extract Boolean features (e.g., `is_ambiguous=True`) from the arguments.
6.  **Symbolic Adjudication**: A deterministic Python function calculates the final Risk Score.
7.  **Output**: Final Verdict and Litigation Risk %.

---

## 4. Judge Decision Checklist (FORMAL)

The `Judge` does not "think"; it **computes**. The logic is formalized in `src/adjudication.py` and strictly enforces the following decision tree:

```python
# PSEUDO-CODE LOGIC

def adjudicate(factors):
    risk = 50 (Baseline)
    
    # 1. Ambiguity Rule (Contra Proferentem)
    IF factors.is_ambiguous IS TRUE:
        risk += 20
        verdict += "AMBIGUOUS: Favors Plaintiff (Non-drafter)"
    ELSE:
        verdict += "CLEAR: No ambiguity"

    # 2. Exclusion Clause Validity
    IF factors.is_exclusion_clear IS FALSE:
        risk += 15
        verdict += "EXCLUSION FAILED: Strict Construction applies"

    # 3. Hierarchy of Norms
    IF factors.authority_is_mandatory IS TRUE:
        risk += 20
        verdict += "INVALID: Contract overrides Mandatory Law"

    # 4. Plausibility Baseline
    IF factors.plaintiff_plausible IS FALSE:
        risk -= 20
        verdict += "DISMISSAL: Argument implausible"

    RETURN CLIP(risk, 0, 100)
```

This ensures that **Risk is a causal function of specific legal defects**, not a random probability distribution.

---

## 5. Determinism & Stability Guarantees

BALE 2.1 adheres to the **Principle of Conditional Determinism**:
> *For any fixed input and fixed set of authorities, the system must yield the exact same Risk Score, provided the Neural Interpretation Slot yields stable Booleans.*

### Stability Benchmark
*   **Target**: 0.00% Standard Deviation on unambiguous "Control Clauses."
*   **Allowed Variance**: Variance is only permitted in the *Interpretation* phase (Argument generation), NEVER in the *Adjudication* phase (Scoring).

---

## 6. Known Limitations

1.  **Local Inference Dependency**: The system requires a running OpenAI-compatible server (vLLM, Ollama, etc.) at `localhost:8000`.
2.  **Jurisdictional Incompleteness**: Currently limited to general Commercial Contract principles.
3.  **Closed Universe**: The system does not conduct external web research.
