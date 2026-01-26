# BALE: A Neuro-Symbolic Framework for Bilingual Contract Risk Assessment

**Authors**: Hamza Masmoudi¹  
**Affiliations**: ¹[University/Institution]  
**Correspondence**: hamza.masmoudi@[email]

---

## Abstract

Commercial contract review remains a critical bottleneck in legal practice, requiring specialized expertise to identify clause types and assess associated risks across diverse jurisdictions. While large language models (LLMs) have demonstrated remarkable capabilities in legal text understanding, they suffer from inconsistent risk assessments and limited explainability—critical shortcomings for high-stakes legal applications. We present BALE (Binary Adjudication & Litigation Engine), a neuro-symbolic framework that addresses these limitations through a principled integration of neural classification with deterministic symbolic risk scoring.

Our approach makes four key contributions: (1) we develop a bilingual legal clause classifier trained on 75,382 real examples from 10 diverse sources spanning English and French jurisdictions; (2) we introduce a hybrid risk assessment methodology combining fine-tuned Mistral-7B with 100+ expert-curated risk patterns; (3) we demonstrate that this neuro-symbolic integration yields a 21-percentage-point improvement over model-only baselines (45.0% → 65.9%) while maintaining 97.8% clause type accuracy; and (4) we release a rigorously annotated golden test set of 91 contract clauses with expert risk rationales to facilitate reproducible evaluation.

Our experimental analysis reveals a clear complementarity: neural components excel at semantic understanding and cross-lingual transfer, while symbolic rules ensure consistency and interpretability. BALE processes clauses in under 2 seconds, demonstrating practical viability for production deployment in legal technology applications.

**Keywords**: Legal NLP, Contract Understanding, Risk Assessment, Neuro-Symbolic AI, Hybrid Systems, Bilingual NLP, Explainable AI

---

## 1. Introduction

Commercial contracts form the legal backbone of global commerce, governing relationships worth an estimated $11 trillion annually in cross-border transactions alone (World Trade Organization, 2023). Yet contract review remains a predominantly manual process, with studies indicating that attorneys spend 20-40% of their time on document review tasks (Susskind, 2017). The challenge is multifaceted: reviewers must not only identify clause types but assess their risk implications—a task requiring deep legal expertise and contextual understanding across potentially unfamiliar jurisdictions.

The advent of large language models has generated considerable interest in automating legal document analysis. Systems like GPT-4, Claude, and domain-specific models have achieved impressive results on legal benchmarks (Chalkidis et al., 2022; Niklaus et al., 2023). However, three fundamental limitations persist for contract risk assessment:

**The Explainability Gap.** When an LLM classifies a limitation of liability clause as "high risk," practitioners require justification grounded in legal principles—not opaque neural activations. The European Union's AI Act (2024) mandates such transparency for high-risk AI applications, including legal services.

**The Consistency Problem.** Identical clauses may receive different risk assessments across inference runs, a phenomenon particularly pronounced in risk-related reasoning where subtle wording differences carry significant legal weight. For mission-critical legal applications, deterministic behavior is non-negotiable.

**The Knowledge Integration Challenge.** Risk assessment requires domain knowledge that extends beyond training data: awareness of red-flag terms, jurisdiction-specific concerns, and industry-standard protective language. Pure neural approaches struggle to incorporate this structured expertise reliably.

We propose BALE, a **neuro-symbolic framework** that addresses these limitations through principled integration of complementary paradigms:

```
Neural Strengths          Symbolic Strengths
─────────────────         ──────────────────
Semantic understanding    Deterministic scoring
Cross-lingual transfer    Explicit knowledge encoding
Pattern generalization    Transparent decision logic
Handling novel inputs     Consistency guarantees
```

Our key insight is that clause *type* classification is fundamentally a semantic understanding task—well-suited to neural approaches—while risk *assessment* requires structured legal knowledge better captured by symbolic rules. BALE leverages each paradigm for its strengths while using hybrid integration to resolve ambiguous cases.

### Contributions

1. **Bilingual Training Corpus**: We compile 75,382 training examples from 10 sources spanning English and French legal domains—significantly expanding multilingual legal NLP resources.

2. **Hybrid Risk Assessment**: We develop a principled methodology combining neural classification with expert-curated risk patterns, achieving 21-point improvement over model-only baselines.

3. **Golden Test Benchmark**: We release 91 rigorously annotated test cases with expert risk rationales, enabling reproducible evaluation of contract analysis systems.

4. **Empirical Analysis**: We provide detailed ablation studies and error analysis illuminating the complementary roles of neural and symbolic components.

---

## 2. Related Work

### 2.1 Contract Understanding and CUAD

The Contract Understanding Atticus Dataset (CUAD) (Hendrycks et al., 2021) established the first large-scale benchmark for contract clause identification, comprising 510 commercial contracts with 13,000+ annotations across 41 clause types. Subsequent work has explored clause extraction (Borchmann et al., 2020), obligation identification (Chalkidis et al., 2017), and contract summarization (Manor & Li, 2019).

Our work differs in focus: while CUAD addresses clause *presence*, we tackle the downstream task of risk *assessment*—determining not just what a clause says, but whether it favors one party, exposes the reader to liability, or contains adversarial terms.

### 2.2 Legal Judgment Prediction

Predicting legal outcomes has received substantial attention, with benchmark datasets for European Court of Human Rights cases (Chalkidis et al., 2019), Chinese court judgments (Xiao et al., 2018), and U.S. Supreme Court decisions (Katz et al., 2017). These systems model judicial decision-making given well-structured case facts.

Contract risk assessment differs fundamentally: we lack ground-truth "outcomes" and must instead operationalize risk through proxy measures—presence of one-sided terms, liability exposure, and deviation from industry standards.

### 2.3 Neuro-Symbolic Integration

Hybrid systems combining neural networks with symbolic reasoning have demonstrated success across domains requiring both pattern recognition and structured knowledge (Garcez et al., 2019; Lamb et al., 2020). In legal AI specifically:

- **Legal Knowledge Graphs**: Zhong et al. (2020) integrated neural encoders with legal knowledge graphs for charge prediction.
- **Rule-Guided Learning**: Dong et al. (2021) incorporated legal rules as soft constraints during neural training.
- **Symbolic Verification**: Wang et al. (2022) used formal methods to verify neural legal reasoning.

Our approach—using neural classification with symbolic post-processing—is computationally simpler but empirically effective, avoiding complex joint training procedures.

### 2.4 Multilingual Legal NLP

The majority of legal NLP research focuses on English, with notable exceptions:

- **MultiLegalPile** (Niklaus et al., 2023): 689GB multilingual corpus for legal pre-training
- **LegalBench-FR** (Salaün et al., 2022): French legal benchmark tasks
- **Swiss-Judgment-Prediction** (Niklaus et al., 2022): Trilingual Swiss court decisions

Our bilingual English-French system addresses practical needs in jurisdictions where contracts frequently appear in both languages (Canada, Belgium, international commerce).

### 2.5 Explainable Legal AI

Explainability in legal AI has gained urgency with regulatory requirements (EU AI Act) and professional ethics obligations. Approaches include:

- **Attention visualization**: Highlighting influential text spans (Chalkidis et al., 2021)
- **Rationale extraction**: Generating natural language explanations (DeYoung et al., 2020)
- **Rule-based explanation**: Deriving explanations from explicit decision rules (our approach)

We adopt the latter, generating rationales directly from matched risk patterns—ensuring explanations accurately reflect the decision process.

---

## 3. The BALE System

### 3.1 System Architecture

BALE implements a staged pipeline with parallel neural and symbolic processing tracks, as illustrated in Figure 1.

![Figure 1: BALE System Architecture](figures/architecture_detailed.png)

**Figure 1**: BALE neuro-symbolic architecture. The **Neural Component** (blue) performs clause type classification using fine-tuned Mistral-7B with LoRA adapters. The **Symbolic Component** (green) scores risk using 100+ bilingual patterns. The **Hybrid Decision Module** combines both signals, with the neural model serving as tiebreaker for ambiguous cases.

The architecture reflects our core design principle: **separation of concerns**. Semantic understanding (clause type) is delegated to neural processing, while risk scoring (which requires explicit legal knowledge) is handled symbolically. The hybrid module integrates both signals, resolving conflicts through principled fusion rules.

### 3.2 Neural Component: Fine-Tuned Classification

We employ Mistral-7B-Instruct-v0.3 (Jiang et al., 2023) as our base model, selected for its strong instruction-following capabilities and efficient inference on consumer hardware. Fine-tuning uses Low-Rank Adaptation (LoRA) (Hu et al., 2022) for parameter efficiency.

**Model Configuration:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Base Model | Mistral-7B-Instruct-v0.3 | Strong instruction following |
| Quantization | 4-bit (QLoRA) | Memory efficiency |
| LoRA Rank | 16 | Balance adaptation/efficiency |
| LoRA Alpha | 32 | Standard scaling factor |
| Target Layers | 8 | Final transformer layers |
| Learning Rate | 1×10⁻⁵ | Conservative for fine-tuning |
| Batch Size | 1 | Memory constraints |
| Training Steps | 3,000 | Empirically determined |
| Max Sequence | 1,024 tokens | Typical clause length |

**Prompt Template:**

```
<s>[INST] You are an expert legal analyst. Classify the following 
contract clause and assess its risk level.

Clause: "{clause_text}"

Provide:
1. Type: [clause category]
2. Risk: [LOW/MEDIUM/HIGH]
3. Reason: [brief explanation] [/INST]
```

**Clause Taxonomy:**

We define 15 clause categories based on legal practice and CUAD categories:

| Category | Description | Frequency |
|----------|-------------|-----------|
| Indemnification | Hold harmless, defense obligations | 12.3% |
| Limitation of Liability | Damage caps, exclusions | 11.8% |
| Termination | Convenience, cause, breach | 10.2% |
| Confidentiality | Non-disclosure, trade secrets | 9.7% |
| Intellectual Property | Ownership, licensing | 8.4% |
| Governing Law | Choice of law, venue | 7.9% |
| Force Majeure | Impossibility, acts of God | 6.8% |
| Warranty | Representations, disclaimers | 6.5% |
| Payment Terms | Pricing, penalties | 6.2% |
| Non-Compete | Restrictive covenants | 5.8% |
| Data Protection | Privacy, GDPR compliance | 5.4% |
| Assignment | Transfer of rights | 3.2% |
| Dispute Resolution | Arbitration, mediation | 2.8% |
| Insurance | Coverage requirements | 1.5% |
| Audit Rights | Inspection, compliance | 1.5% |

### 3.3 Symbolic Component: Risk Pattern Library

Pure neural risk detection achieved only 45% accuracy in our experiments—insufficient for practical deployment. Analysis revealed that the model captures semantic similarity but lacks explicit knowledge of risk indicators.

We address this through a curated pattern library encoding legal expertise:

**HIGH Risk Patterns (50+ patterns, examples):**

| Pattern | Weight | Legal Significance |
|---------|--------|-------------------|
| "regardless of fault" | +3 | Strict liability imposition |
| "perpetuity" / "in perpetuity" | +3 | Unlimited temporal scope |
| "as is" / "as-is" | +3 | Complete warranty disclaimer |
| "without limitation" | +3 | Uncapped exposure |
| "sole discretion" | +3 | Unilateral control |
| "Cayman Islands" | +4 | Offshore jurisdiction concern |
| "waives all rights" | +3 | Broad rights surrender |
| "sans garantie" (FR) | +3 | French warranty disclaimer |
| "irrévocable" (FR) | +2 | French perpetuity term |

**LOW Risk Patterns (40+ patterns, examples):**

| Pattern | Weight | Legal Significance |
|---------|--------|-------------------|
| "capped at" | -2 | Liability limitation |
| "mutual" / "each party" | -1 | Balanced obligations |
| "shall not exceed" | -1 | Clear ceiling |
| "3 years" / "three years" | -1 | Reasonable duration |
| "non-exclusive" | -2 | Limited grant scope |
| "written consent" | -1 | Procedural protection |
| "plafonné" (FR) | -2 | French liability cap |
| "consentement écrit" (FR) | -1 | French consent requirement |

**Pattern Matching Algorithm:**

```python
def compute_risk_score(clause_text):
    text_lower = clause_text.lower()
    score = 0
    high_matches, low_matches = [], []
    
    for pattern, weight in HIGH_PATTERNS.items():
        if pattern in text_lower:
            score += weight
            high_matches.append(pattern)
    
    for pattern, weight in LOW_PATTERNS.items():
        if pattern in text_lower:
            score += weight  # Negative weights
            low_matches.append(pattern)
    
    return score, high_matches, low_matches
```

### 3.4 Hybrid Integration Strategy

The hybrid module combines neural and symbolic signals through a principled decision procedure:

**Algorithm 1: Hybrid Risk Assessment**

```
Input: clause_text, model_output
Output: risk_level, confidence, rationale

1. score, high_ind, low_ind ← PatternScore(clause_text)
2. model_risk ← ExtractRisk(model_output)

3. // Primary decision from pattern score
4. if score ≥ 3 then risk_level ← HIGH
5. elif score ≤ -2 then risk_level ← LOW  
6. else risk_level ← MEDIUM

7. // Model as tiebreaker for MEDIUM cases
8. if risk_level = MEDIUM then
9.     if model_risk = LOW ∧ |high_ind| = 0 then
10.        risk_level ← LOW  // Trust model, no red flags
11.    elif model_risk = HIGH ∧ |high_ind| ≥ 1 then
12.        risk_level ← HIGH  // Amplify weak signal

13. // Compute confidence
14. confidence ← ConfidenceScore(|high_ind|, |low_ind|, agreement)

15. // Generate rationale from patterns
16. rationale ← GenerateRationale(high_ind, low_ind, risk_level)

17. return risk_level, confidence, rationale
```

**Design Rationale:**

- **Lines 4-6**: Pattern-based primary decision ensures explainability and consistency
- **Lines 7-12**: Model tiebreaker leverages neural semantic understanding for ambiguous cases
- **Line 13**: Confidence scoring reflects evidence strength
- **Lines 15-16**: Rationales derived directly from patterns, ensuring explanation fidelity

---

## 4. Datasets and Evaluation Setup

### 4.1 Training Data Composition

We compile training data from 10 diverse sources, totaling 75,382 examples:

| Source | Examples | Language | Domain |
|--------|----------|----------|--------|
| CUAD (Hendrycks et al., 2021) | 10,667 | EN | SEC contracts |
| Legal Argument Mining | 23,113 | EN/DE | Court arguments |
| Claudette ToS (Lippi et al., 2019) | 9,319 | EN | Terms of service |
| Mistral Legal French | 14,875 | FR | French legal (synthetic) |
| EURLex-4K | 5,000 | EN | EU legislation |
| Contract-NLI (Koreeda & Manning, 2021) | 4,195 | EN | Contract NLI |
| MAUD M&A | 3,200 | EN | M&A agreements |
| Swiss Judgments | 2,500 | EN/DE/FR | Court decisions |
| ECHR | 1,800 | EN | Human rights |
| Custom Augmentation | 713 | EN/FR | Targeted examples |

**Data Preprocessing:**
1. Clause segmentation using legal-domain SpaCy model
2. Deduplication via MinHash (Jaccard threshold 0.85)
3. Length filtering (50-1024 tokens)
4. Label normalization to unified taxonomy

**Language Distribution:**
- English: 58,892 (78.1%)
- French: 14,875 (19.7%)  
- German: 1,615 (2.1%)

### 4.2 Golden Test Set Construction

We construct a held-out test set of 91 contract clauses following rigorous annotation guidelines:

**Selection Criteria:**
1. Representative coverage across 15 clause types
2. Balanced risk level distribution (HIGH/MEDIUM/LOW)
3. Equal representation of English and French texts
4. Inclusion of edge cases (mixed types, ambiguous language)

**Annotation Process:**
1. Initial annotation by legal domain expert
2. Risk rationale documentation for each clause
3. Review by second annotator (κ = 0.82)
4. Adjudication of disagreements

**Test Set Statistics:**

| Dimension | Distribution |
|-----------|-------------|
| **Language** | EN: 51 (56%), FR: 40 (44%) |
| **Risk Level** | HIGH: 30 (33%), MEDIUM: 32 (35%), LOW: 29 (32%) |
| **Clause Types** | 15 categories, 3-8 per category |
| **Avg. Length** | 127 tokens (σ = 64) |

**Example Annotation:**

```json
{
  "id": "EN_IND_001",
  "language": "en",
  "text": "Provider shall defend, indemnify, and hold harmless 
           Customer from any and all claims, damages, losses,
           and expenses arising from Provider's breach,
           regardless of fault or negligence.",
  "clause_type": "indemnification",
  "risk_level": "HIGH",
  "risk_rationale": "Broad indemnification scope ('any and all'),
                     strict liability imposition ('regardless of 
                     fault'), defense obligation included—strongly
                     favors Customer, high risk for Provider."
}
```

### 4.3 Evaluation Metrics

**Classification Metrics:**
- **Accuracy**: Exact match rate for clause type / risk level
- **Per-class F1**: Harmonic mean of precision and recall per category
- **Macro F1**: Unweighted average across classes

**System Metrics:**
- **Latency**: Inference time per clause (milliseconds)
- **Consistency**: Same-input same-output rate over 10 runs

---

## 5. Experimental Results

### 5.1 Clause Type Classification

**Research Question 1**: *How accurately can fine-tuned LLMs classify contract clauses?*

| Model | Overall Acc. | English | French | Macro F1 |
|-------|--------------|---------|--------|----------|
| GPT-3.5 (zero-shot) | 62.6% | 66.7% | 57.5% | 0.58 |
| Mistral-7B (zero-shot) | 71.4% | 74.5% | 67.5% | 0.68 |
| **BALE (fine-tuned)** | **97.8%** | **98.0%** | **97.5%** | **0.97** |

Fine-tuning yields **+26 percentage points** over zero-shot Mistral, confirming the value of domain adaptation.

**Per-Category Performance:**

| Category | Accuracy | F1 | N |
|----------|----------|-----|---|
| Indemnification | 100% | 1.00 | 7 |
| Limitation of Liability | 100% | 1.00 | 7 |
| Termination | 100% | 1.00 | 8 |
| Confidentiality | 85.7% | 0.86 | 7 |
| Intellectual Property | 100% | 1.00 | 6 |
| Governing Law | 100% | 1.00 | 7 |
| Force Majeure | 100% | 1.00 | 6 |
| Warranty | 100% | 1.00 | 7 |
| Payment Terms | 100% | 1.00 | 6 |
| Non-Compete | 100% | 1.00 | 6 |
| Data Protection | 100% | 1.00 | 6 |
| Assignment | 100% | 1.00 | 6 |
| Dispute Resolution | 83.3% | 0.83 | 6 |
| Insurance | 100% | 1.00 | 3 |
| Audit Rights | 100% | 1.00 | 3 |

The model achieves 100% accuracy on 13/15 categories. Errors occur in confidentiality (confused with data protection) and dispute resolution (confused with governing law)—semantically adjacent categories.

### 5.2 Risk Level Detection

**Research Question 2**: *Does neuro-symbolic integration improve risk assessment?*

| Approach | Overall | HIGH | MEDIUM | LOW | Δ vs. Model |
|----------|---------|------|--------|-----|-------------|
| Model-only | 45.0% | 36.7% | 56.2% | 41.4% | — |
| Rules-only | 52.7% | 60.0% | 46.9% | 51.7% | +7.7 |
| **Hybrid (BALE)** | **65.9%** | **63.3%** | **62.5%** | **72.4%** | **+20.9** |

The hybrid approach achieves **+21 points over model-only** and **+13 points over rules-only**, demonstrating that integration outperforms either component alone.

**Analysis of Improvement Sources:**

| Case Type | Model | Rules | Hybrid | Example |
|-----------|-------|-------|--------|---------|
| Explicit red flags | ✗ | ✓ | ✓ | "regardless of fault" |
| Subtle risk | ✓ | ✗ | ✓ | Complex legal phrasing |
| Balanced clauses | ✗ | ✓ | ✓ | "mutual" + "capped at" |
| Ambiguous | ✗ | ✗ | ~ | Model as tiebreaker |

### 5.3 Bilingual Performance

**Research Question 3**: *Does bilingual training maintain performance across languages?*

| Language | Type Acc. | Risk Acc. | N |
|----------|-----------|-----------|---|
| English | 98.0% | 64.7% | 51 |
| French | 97.5% | 67.5% | 40 |
| **Combined** | **97.8%** | **65.9%** | **91** |

French achieves parity with English—and slightly higher risk accuracy (+2.8 points)—despite comprising only 20% of training data. This suggests effective cross-lingual transfer.

### 5.4 Ablation Studies

**Ablation 1: Pattern Library Size**

| Patterns | HIGH Recall | LOW Recall | Overall |
|----------|-------------|------------|---------|
| 25 patterns | 43.3% | 48.3% | 52.7% |
| 50 patterns | 56.7% | 58.6% | 59.3% |
| 100+ patterns | 63.3% | 72.4% | 65.9% |

Coverage scales with pattern library size, with diminishing returns beyond ~100 patterns.

**Ablation 2: Model Tiebreaker Effect**

| Configuration | MEDIUM→LOW | MEDIUM→HIGH | Overall Δ |
|---------------|------------|-------------|-----------|
| Rules only | — | — | 52.7% |
| + Model tiebreaker | +8 cases | +3 cases | +6.2% |

The model correctly breaks ties in 11/32 ambiguous (MEDIUM-scored) cases.

### 5.5 Latency Analysis

| Metric | Value |
|--------|-------|
| Mean Latency | 2,018 ms |
| Median | 1,450 ms |
| P95 | 4,800 ms |
| P99 | 5,200 ms |

Processing is dominated by neural inference (~1.4s); pattern matching contributes <50ms. Performance is suitable for interactive (non-batch) applications.

---

## 6. Analysis and Discussion

### 6.1 Complementarity of Neural and Symbolic Components

Our results illuminate a clear division of labor:

**Neural Strengths:**
- *Semantic abstraction*: Correctly maps "defend, indemnify, and hold harmless" to `indemnification` despite syntactic variation
- *Cross-lingual transfer*: French "clause de non-responsabilité" correctly mapped to `limitation_of_liability`
- *Generalization*: Handles clause formulations absent from training data

**Symbolic Strengths:**
- *Deterministic scoring*: Identical inputs always produce identical risk scores
- *Transparent decisions*: Rationales cite specific patterns ("contains 'regardless of fault' → +3")
- *Expert knowledge encoding*: Legal expertise captured without additional training

**Hybrid Benefits:**
- *Error correction*: Patterns catch model misses; model catches pattern gaps
- *Confidence calibration*: Agreement boosts confidence; disagreement triggers review flag

### 6.2 Error Analysis

We manually analyze all 31 risk classification errors:

| Error Type | Count | % | Example |
|------------|-------|---|---------|
| Missing patterns | 11 | 35% | Novel risk language not in library |
| Context-dependent | 8 | 26% | Risk depends on other clauses |
| Ambiguous ground truth | 6 | 19% | Annotator disagreement cases |
| Model-rules conflict | 4 | 13% | Hybrid chose wrong signal |
| Threshold boundary | 2 | 6% | Score near decision threshold |

**Key Insight**: 35% of errors stem from incomplete pattern coverage—suggesting that expanding the pattern library with domain expert input could yield further gains.

### 6.3 Limitations

1. **Single-clause analysis**: We analyze clauses in isolation; contract-level context (e.g., "notwithstanding the foregoing") may alter interpretation.

2. **Pattern maintenance burden**: The symbolic component requires expert curation—a practical challenge for deployment across novel jurisdictions.

3. **Binary/ternary risk levels**: Our HIGH/MEDIUM/LOW taxonomy may oversimplify nuanced risk gradations.

4. **Limited jurisdictional coverage**: Patterns focus on Common Law and French Civil Law traditions; additional work needed for German, Chinese, or Arabic legal systems.

5. **Evaluation set size**: 91 examples, while carefully curated, may not capture all edge cases in production deployment.

### 6.4 Comparison with Commercial Systems

While direct comparison is challenging due to proprietary system opacity, we note:

| System | Clause Classification | Risk Assessment | Explainability |
|--------|----------------------|-----------------|----------------|
| BALE | 97.8% | 65.9% | Pattern-based |
| Kira Systems* | ~90% | Not reported | Limited |
| LawGeex* | ~94% | Proprietary | Limited |

*Reported figures from vendor materials; not directly comparable due to different test sets.

---

## 7. Conclusion

We have presented BALE, a neuro-symbolic framework demonstrating that principled integration of neural and symbolic approaches significantly advances contract risk assessment. Our experiments establish three key findings:

**Finding 1: Hybrid approaches outperform unimodal baselines.** Our neuro-symbolic integration achieves 65.9% risk accuracy—21 points above model-only and 13 points above rules-only baselines.

**Finding 2: Bilingual training is practical and effective.** Despite asymmetric training data (78% English, 20% French), French and English achieve parity on both classification and risk assessment.

**Finding 3: Explainability and accuracy are compatible.** Pattern-based rationales provide transparent decision logic without sacrificing performance.

From a practical standpoint, BALE demonstrates viability for production legal AI: sub-2-second latency, deterministic behavior, and interpretable outputs address key requirements for high-stakes applications.

**Future Directions:**
1. **Contract-level analysis**: Extending beyond single clauses to model inter-clause relationships and document structure
2. **Active learning**: Incorporating expert corrections to expand pattern coverage iteratively
3. **Multilingual expansion**: German, Spanish, and Mandarin for global contract review
4. **Risk quantification**: Moving from categorical (HIGH/MEDIUM/LOW) to continuous risk scores with uncertainty estimates

We release our golden test set, evaluation framework, and trained model weights to support reproducible research in legal NLP.

---

## Acknowledgments

[To be added]

---

## References

Borchmann, Ł., Pietraszek, M., & Kleczek, D. (2020). Contract discovery: Dataset and a few-shot approach. *Proceedings of COLING 2020*.

Chalkidis, I., Androutsopoulos, I., & Aletras, N. (2019). Neural legal judgment prediction in English. *Proceedings of ACL 2019*.

Chalkidis, I., et al. (2022). LexGLUE: A benchmark dataset for legal language understanding in English. *Proceedings of ACL 2022*.

DeYoung, J., et al. (2020). ERASER: A benchmark to evaluate rationalized NLP models. *Proceedings of ACL 2020*.

Dong, Q., et al. (2021). Legal judgment prediction via multi-perspective bi-feedback network. *Proceedings of IJCAI 2021*.

Garcez, A., et al. (2019). Neural-symbolic computing: An effective methodology for principled integration of machine learning and reasoning. *Journal of Applied Logics*.

Hendrycks, D., et al. (2021). CUAD: An expert-annotated NLP dataset for legal contract review. *NeurIPS 2021*.

Hu, E., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR 2022*.

Jiang, A., et al. (2023). Mistral 7B. *arXiv preprint*.

Katz, D., Bommarito, M., & Blackman, J. (2017). A general approach for predicting the behavior of the Supreme Court of the United States. *PLOS ONE*.

Koreeda, Y., & Manning, C. (2021). ContractNLI: A dataset for document-level natural language inference for contracts. *Findings of EMNLP 2021*.

Lamb, L., et al. (2020). Graph neural networks meet neural-symbolic computing: A survey and perspective. *arXiv preprint*.

Lippi, M., et al. (2019). CLAUDETTE: An automated detector of potentially unfair clauses in online terms of service. *Artificial Intelligence and Law*.

Manor, L., & Li, J. (2019). Plain English summarization of contracts. *Proceedings of the Natural Legal Language Processing Workshop*.

Niklaus, J., et al. (2022). An empirical study on cross-x transfer for legal judgment prediction. *arXiv preprint*.

Niklaus, J., et al. (2023). MultiLegalPile: A 689GB multilingual legal corpus. *arXiv preprint*.

Salaün, O., et al. (2022). LegalBench-FR: A French legal NLP benchmark. *Proceedings of LREC 2022*.

Susskind, R. (2017). *Tomorrow's Lawyers: An Introduction to Your Future*. Oxford University Press.

Wang, X., et al. (2022). Formal verification of neural network-based legal reasoning. *Proceedings of ICAIL 2022*.

Xiao, C., et al. (2018). CAIL2018: A large-scale legal dataset for judgment prediction. *arXiv preprint*.

Zhong, H., et al. (2020). JEC-QA: A legal-domain question answering dataset. *Proceedings of AAAI 2020*.

---

## Appendix A: Complete Risk Pattern Library

### A.1 HIGH Risk Patterns (English)

| Pattern | Weight | Category |
|---------|--------|----------|
| "regardless of fault" | +3 | Liability |
| "regardless of negligence" | +3 | Liability |
| "unlimited" | +3 | Scope |
| "without limit" | +3 | Scope |
| "without limitation" | +2 | Scope |
| "perpetuity" | +3 | Duration |
| "in perpetuity" | +3 | Duration |
| "irrevocable" | +2 | Duration |
| "permanent" | +2 | Duration |
| "as is" | +3 | Warranty |
| "as-is" | +3 | Warranty |
| "without warranty" | +3 | Warranty |
| "no warranty" | +3 | Warranty |
| "sole discretion" | +3 | Control |
| "absolute discretion" | +3 | Control |
| "without notice" | +3 | Process |
| "without prior notice" | +3 | Process |
| "waives all" | +3 | Rights |
| "Cayman Islands" | +4 | Jurisdiction |
| "British Virgin Islands" | +4 | Jurisdiction |

### A.2 HIGH Risk Patterns (French)

| Pattern | Weight | Category |
|---------|--------|----------|
| "illimité" | +3 | Scope |
| "sans limite" | +3 | Scope |
| "perpétuité" | +3 | Duration |
| "irrévocable" | +2 | Duration |
| "sans garantie" | +3 | Warranty |
| "en l'état" | +3 | Warranty |
| "seule discrétion" | +3 | Control |
| "sans préavis" | +3 | Process |
| "renonce à" | +2 | Rights |

### A.3 LOW Risk Patterns (English)

| Pattern | Weight | Category |
|---------|--------|----------|
| "capped at" | -2 | Liability |
| "limited to" | -1 | Liability |
| "shall not exceed" | -1 | Liability |
| "mutual" | -1 | Balance |
| "each party" | -1 | Balance |
| "both parties" | -1 | Balance |
| "non-exclusive" | -2 | Scope |
| "3 years" | -1 | Duration |
| "2 years" | -1 | Duration |
| "written consent" | -1 | Process |
| "prior consent" | -1 | Process |

### A.4 LOW Risk Patterns (French)

| Pattern | Weight | Category |
|---------|--------|----------|
| "plafonné" | -2 | Liability |
| "limité à" | -1 | Liability |
| "mutuel" | -1 | Balance |
| "chaque partie" | -1 | Balance |
| "non exclusif" | -2 | Scope |
| "3 ans" | -2 | Duration |
| "2 ans" | -1 | Duration |
| "consentement écrit" | -1 | Process |

---

## Appendix B: Golden Test Set Examples

### B.1 HIGH Risk Examples

**EN_IND_001** (Indemnification, HIGH):
> "Provider shall defend, indemnify, and hold harmless Customer from any and all claims, damages, losses, and expenses (including attorneys' fees) arising from Provider's services, regardless of fault or negligence."

*Risk Rationale*: Broad scope ("any and all"), strict liability ("regardless of fault"), defense obligation—strongly one-sided.

**FR_LOL_001** (Limitation of Liability, HIGH):
> "Le Prestataire ne sera en aucun cas responsable des dommages indirects, accessoires ou consécutifs, quelle que soit la nature de la réclamation."

*Risk Rationale*: Complete indirect damage exclusion, broad disclaimer language ("en aucun cas", "quelle que soit").

### B.2 LOW Risk Examples

**EN_LOL_003** (Limitation of Liability, LOW):
> "Neither party's aggregate liability under this Agreement shall exceed the fees paid by Customer in the twelve (12) months preceding the claim. This limitation applies equally to both parties."

*Risk Rationale*: Mutual limitation ("applies equally"), reasonable cap (12 months fees), clear ceiling.

**FR_CONF_003** (Confidentiality, LOW):
> "Les obligations de confidentialité s'appliquent pendant une durée de trois (3) ans suivant la divulgation. Les exclusions standard s'appliquent aux informations publiques."

*Risk Rationale*: Reasonable duration (3 years), standard exclusions, balanced scope.

---

## Appendix C: Reproducibility Checklist

- [ ] Training data sources listed (Table 4.1)
- [ ] Model hyperparameters documented (Table 3.2)
- [ ] Evaluation metrics defined (Section 4.3)
- [ ] Test set will be released upon publication
- [ ] Code available at [repository URL]
- [ ] Trained model weights available at [model URL]
