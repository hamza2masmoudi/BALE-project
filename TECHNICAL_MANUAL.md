# BALE 2.1: The Engineer's Manual
**A Deep Dive into Neuro-Symbolic Legal Architecture**
> *"To engineer justice, one must first engineer the judge."*
---
## 1. The Core Philosophy: Why Neuro-Symbolic?
### The Problem: Stochastic Justice
Large Language Models (LLMs) are **probabilistic engines**. They predict the next token based on statistical likelihood.
* **Input**: "Is this clause valid?"
* **LLM Output**: "Yes" (60% prob) or "No" (40% prob).
In Law, this is unacceptable. A judge cannot flip a coin. A judge must apply a **rule** to a **fact** to reach a **verdict**.
* **The Rule**: "If A and B, then C." (Logic)
* **The Fact**: "A happened." (Observation)
### The Solution: The Neuro-Symbolic Split
BALE (Binary Adjudication & Litigation Engine) splits the cognitive load into two distinct systems:
1. **Neural System (System 1)**: The "Eyes and Ears".
* **Role**: Interpretation, Reading, Argument Generation.
* **Tool**: Large Language Models (LLMs).
* **Why**: Logic cannot "read" fuzzy human text. You need a neural net to understand that "act of God" equals "Force Majeure".
2. **Symbolic System (System 2)**: The "Gavel".
* **Role**: Adjudication, Scoring, Rule Application.
* **Tool**: Python Code (Algorithmic Logic).
* **Why**: We need 100% determinism. If the inputs are the same, the verdict *must* be the same.
---
## 2. The Architecture: A Pipeline of Agents
BALE is not a chatbot. It is a **Directed Acyclic Graph (DAG)** of specialized agents.
### The Pipeline Flow
1. **Ingestion**: Raw PDF text enters.
2. **Gatekeeper (Ontology)**: The system grounds the text in specific legal authorities (Codes, Case Law).
3. **Dialectic (Thesis-Antithesis)**:
* *Civilist Agent*: Argues from the Code (Deductive).
* *Commonist Agent*: Argues from Precedent (Inductive).
4. **Synthesis**: Measurements of the "Interpretive Gap".
5. **Adjudication**:
* *Adversarial Simulation*: A mock trial generates arguments.
* *Fact Clerk*: Extracts Boolean facts (`True`/`False`) and problems (`"broad indemnification"`).
* *Verdict Builder*: Calculates risk score (Base 50 + Factors).
* *Risk Model*: Predicts litigation outcomes (Settlement vs Win).
---
## 3. Algorithms & Mechanisms
### A. The "Ontology-First" Design
Most RAG (Retrieval-Augmented Generation) systems just search for "similar text." BALE searches for **Binding Authority**.
We defined a `LegalNode` structure:
```python
class LegalNode:
authority_level: int # 100=Constitution, 90=Statute, 30=Contract
binding_status: str # MANDATORY vs DEFAULT
```
**Why?**
Because LLMs hallucinate hierarchy. By hardcoding weights (`authority_level`), we force the system to respect the *Hierachy of Norms*.
In **V8 (Open Weight)**, we optimized this into an in-memory `LEGAL_CITATIONS` dictionary for portability, replacing the heavy Neo4j dependency used in Enterprise versions. This enables the entire "Brain" to run on a single MacBook.
### B. The Dialectic Engine (Civilist vs. Commonist)
We don't ask one model for the "truth." We ask two models for "bias."
* **The Civilist**: Prompted to act like a French Napoleonic Judge. It values *Bonne Foi* (Good Faith) and statutory text above all.
* **The Commonist**: Prompted to act like an English Commercial Judge. It values *Party Autonomy* and literal interpretation.
* **The Synthesizer**: It doesn't write legal text; it computes the **Interpretive Gap** (0-100%).
* Gap > 60%: "Fundamental Conflict."
* Gap < 20%: "Consensus."
**Why?**
International contracts often crash because a clause is valid in London but void in Paris. A single LLM averages these views into a mushy middle. By forcing extreme personas, we expose the hidden risks.
### C. The Deterministic Judge (The Crown Jewel)
This is where BALE differs from 99% of AI legal tools.
The `Judge` agent does not decide the verdict.
* **LLM Role**: Validates *Facts* ("Is the clause ambiguous?").
* **Python Role**: Decides *Verdict*.
**The Algorithm (`src/explainability_v8.py`)**:
```python
def build_verdict(self):
risk_score = 50 # Base Risk
# 1. Clause Type Risk (e.g., Indemnity = High)
if self.clause_type.risk_level == "HIGH":
risk_score += 15
# 2. Detected Problems (from V8 Analyzer)
for problem in self.problems:
# e.g. "Overly broad indemnification scope"
risk_score += 5 return clip(risk_score, 0, 100)
```
**The Advanced Risk Model (`src/risk_model_v8.py`)**:
Separately, the system runs a probabilistic simulation to predict outcomes:
* *Plaintiff Win Probability*
* *Expected Legal Costs*
* *Settlement Likelihood*
**Why?**
This ensures **Auditability**. A score of 80% is 80% because it has 1 High Risk Clause (+15) and 3 specific defects (+5 each). It is not a hallucination.
---
## 4. BALE 2.1: The Move to "Open Weights"
In the final phase, we removed OpenAI/Anthropic dependencies.
**Why?**
1. **Privacy**: Legal data is sensitive. Processing it on `localhost` is safer.
2. **Science**: We treat the LLM as a "Scientific Instrument." If we use GPT-4, and OpenAI changes the model tomorrow, our benchmarks are broken. By using **Open Weights** (e.g., Qwen2.5-32B or DeepSeek-R1), we freeze the brain. The experiment is reproducible forever.
**How?**
We replaced high-level wrappers (LangChain) with raw HTTP requests.
* **Old**: `agent.invoke(prompt)` (Black box)
* **New**: `requests.post("localhost:8000", json={...})` (Transparent)
---
## 5. Summary for the Student
* **Don't trust LLMs with decisions.** Use them for perception (reading/writing). Use code for logic.
* **Structure your inputs.** Don't just dump text. Create an Ontology (a map of concepts).
* **Force conflict.** You learn more from two agents disagreeing than one agent agreeing with itself.
* **Own the brain.** Real engineering means controlling your dependencies. That’s why we moved to open-source models.
---
## 6. Validation & Benchmarks (Jan 2026)
We do not trust; we verify. BALE 2.1 was evaluated against a **Golden Set** of 91 bilingual clauses.
### A. Classification Accuracy
* **English**: 100.0%
* **French**: 97.5%
* **Overall**: **98.9%**
### B. Risk Assessment Consistency
* **Binary Risk (Safe/Risky)**: 78.5%
* **Granular Risk (High/Med/Low)**: 45.1%
* **Latency**: ~2.69s per clause (Local M3 Max)
This proves the **Bilingual Hypothesis**: A single fine-tuned model *can* master two legal systems simultaneously without cross-talk.
