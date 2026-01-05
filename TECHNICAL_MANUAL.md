# BALE 2.1: The Engineer's Manual
**A Deep Dive into Neuro-Symbolic Legal Architecture**

> *"To engineer justice, one must first engineer the judge."*

---

## 1. The Core Philosophy: Why Neuro-Symbolic?

### The Problem: Stochastic Justice
Large Language Models (LLMs) are **probabilistic engines**. They predict the next token based on statistical likelihood.
*   **Input**: "Is this clause valid?"
*   **LLM Output**: "Yes" (60% prob) or "No" (40% prob).

In Law, this is unacceptable. A judge cannot flip a coin. A judge must apply a **rule** to a **fact** to reach a **verdict**.
*   **The Rule**: "If A and B, then C." (Logic)
*   **The Fact**: "A happened." (Observation)

### The Solution: The Neuro-Symbolic Split
BALE (Binary Adjudication & Litigation Engine) splits the cognitive load into two distinct systems:

1.  **Neural System (System 1)**: The "Eyes and Ears".
    *   **Role**: Interpretation, Reading, Argument Generation.
    *   **Tool**: Large Language Models (LLMs).
    *   **Why**: Logic cannot "read" fuzzy human text. You need a neural net to understand that "act of God" equals "Force Majeure".

2.  **Symbolic System (System 2)**: The "Gavel".
    *   **Role**: Adjudication, Scoring, Rule Application.
    *   **Tool**: Python Code (Algorithmic Logic).
    *   **Why**: We need 100% determinism. If the inputs are the same, the verdict *must* be the same.

---

## 2. The Architecture: A Pipeline of Agents

BALE is not a chatbot. It is a **Directed Acyclic Graph (DAG)** of specialized agents.

### The Pipeline Flow
1.  **Ingestion**: Raw PDF text enters.
2.  **Gatekeeper (Ontology)**: The system grounds the text in specific legal authorities (Codes, Case Law).
3.  **Dialectic (Thesis-Antithesis)**:
    *   *Civilist Agent*: Argues from the Code (Deductive).
    *   *Commonist Agent*: Argues from Precedent (Inductive).
4.  **Synthesis**: Measurements of the "Interpretive Gap".
5.  **Adjudication**:
    *   *Adversarial Simulation*: A mock trial generates arguments.
    *   *Fact Clerk*: Extracts Boolean facts (`True`/`False`).
    *   *Symbolic Judge*: Calculates risk (`risk += 20`).

---

## 3. Algorithms & Mechanisms

### A. The "Ontology-First" Design
Most RAG (Retrieval-Augmented Generation) systems just search for "similar text." BALE searches for **Binding Authority**.

We defined a `LegalNode` structure:
```python
class LegalNode:
    authority_level: int  # 100=Constitution, 90=Statute, 30=Contract
    binding_status: str   # MANDATORY vs DEFAULT
```
**Why?**
Because LLMs hallucinate hierarchy. They might think a contract clause overrides a federal law. By hardcoding weights (`authority_level`), we force the system to respect the *Hierachy of Norms* (Kelsen's Pyramid).

### B. The Dialectic Engine (Civilist vs. Commonist)
We don't ask one model for the "truth." We ask two models for "bias."

*   **The Civilist**: Prompted to act like a French Napoleonic Judge. It values *Bonne Foi* (Good Faith) and statutory text above all.
*   **The Commonist**: Prompted to act like an English Commercial Judge. It values *Party Autonomy* and literal interpretation.
*   **The Synthesizer**: It doesn't write legal text; it computes the **Interpretive Gap** (0-100%).
    *   Gap > 60%: "Fundamental Conflict."
    *   Gap < 20%: "Consensus."

**Why?**
International contracts often crash because a clause is valid in London but void in Paris. A single LLM averages these views into a mushy middle. By forcing extreme personas, we expose the hidden risks.

### C. The Deterministic Judge (The Crown Jewel)
This is where BALE differs from 99% of AI legal tools.

The `Judge` agent does not decide the verdict.
*   **LLM Role**: Validates *Facts* ("Is the clause ambiguous?").
*   **Python Role**: Decides *Verdict*.

**The Algorithm (`src/adjudication.py`)**:
```python
def calculate_risk(factors):
    risk = 50
    if factors.is_ambiguous:
        risk += 20  # Contra Proferentem Rule: Ambiguity hurts the drafter.
    if factors.violates_mandatory_law:
        risk += 30  # Illegal clauses are void.
    return risk
```
**Why?**
This ensures **Auditability**. If the risk is 80%, we can point exactly to line 5 (`risk += 30`) and say "It's because you violated Mandatory Law." An LLM cannot provide that causal guarantee.

---

## 4. BALE 2.1: The Move to "Open Weights"

In the final phase, we removed OpenAI/Anthropic dependencies.

**Why?**
1.  **Privacy**: Legal data is sensitive. Processing it on `localhost` is safer.
2.  **Science**: We treat the LLM as a "Scientific Instrument." If we use GPT-4, and OpenAI changes the model tomorrow, our benchmarks are broken. By using **Open Weights** (e.g., Qwen2.5-32B or DeepSeek-R1), we freeze the brain. The experiment is reproducible forever.

**How?**
We replaced high-level wrappers (LangChain) with raw HTTP requests.
*   **Old**: `agent.invoke(prompt)` (Black box)
*   **New**: `requests.post("localhost:8000", json={...})` (Transparent)

---

## 5. Summary for the Student

*   **Don't trust LLMs with decisions.** Use them for perception (reading/writing). Use code for logic.
*   **Structure your inputs.** Don't just dump text. Create an Ontology (a map of concepts).
*   **Force conflict.** You learn more from two agents disagreeing than one agent agreeing with itself.
*   **Own the brain.** Real engineering means controlling your dependencies. That’s why we moved to open-source models.

You have built a system that doesn't just "chat"—it **thinks, debates, and judges** according to strict rules. That is true Computer Science.
