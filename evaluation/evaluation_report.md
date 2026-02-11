# BALE Evaluation Report
**Date**: 2026-01-16T18:41:13.391108
**Contracts Evaluated**: 15
**Success Rate**: 15/15
**Overall Score**: 82.2%
## Aggregate Scores
| Metric | Score |
|:-------|:------|
| Risk Accuracy | 60.0% |
| Silence Detection | 90.0% |
| Power Analysis | 100.0% |
| Imagination Analysis | 100.0% |
| Strain Analysis | 100.0% |
| Temporal Analysis | 100.0% |
## Individual Results
### TechCorp MSA - Balanced Terms
- **Type**: MSA
- **Expected Risk**: low
- **Actual Risk**: 15.6%
- **Passed**: risk_level_alignment, silence_detection, power_analysis_ran
### CloudVendor MSA - Vendor Heavy
- **Type**: MSA
- **Expected Risk**: high
- **Actual Risk**: 10.8%
- **Passed**: silence_detection_attempted, power_analysis_ran
- **Failed**: risk_level_alignment (expected=high, actual=10.8)
### AI Solutions MSA - Novel AI Clauses
- **Type**: MSA
- **Expected Risk**: medium
- **Actual Risk**: 24.4%
- **Passed**: imagination_analysis_ran, strain_analysis_ran
- **Failed**: risk_level_alignment (expected=medium, actual=24.4)
### Mutual NDA - Standard
- **Type**: NDA
- **Expected Risk**: low
- **Actual Risk**: 12.1%
- **Passed**: risk_level_alignment, silence_detection, power_analysis_ran
### One-Sided NDA - Investor Disclosure
- **Type**: NDA
- **Expected Risk**: medium
- **Actual Risk**: 14.9%
- **Passed**: power_analysis_ran
- **Failed**: risk_level_alignment (expected=medium, actual=14.9)
### Cloud Services SLA
- **Type**: SLA
- **Expected Risk**: medium
- **Actual Risk**: 21.7%
- **Passed**: strain_analysis_ran
- **Failed**: risk_level_alignment (expected=medium, actual=21.7)
### Executive Employment with Non-Compete
- **Type**: Employment
- **Expected Risk**: high
- **Actual Risk**: 11.3%
- **Passed**: temporal_analysis_ran, strain_analysis_ran
- **Failed**: risk_level_alignment (expected=high, actual=11.3)
### MSA with Missing Clauses
- **Type**: MSA
- **Expected Risk**: high
- **Actual Risk**: 23.0%
- **Passed**: silence_detection_attempted
- **Failed**: risk_level_alignment (expected=high, actual=23.0)
### Outdated 2018 MSA
- **Type**: MSA
- **Expected Risk**: high
- **Actual Risk**: 27.4%
- **Passed**: temporal_analysis_ran, strain_analysis_ran
- **Failed**: risk_level_alignment (expected=high, actual=27.4)
### Vendor Agreement - Extreme Power Imbalance
- **Type**: Vendor
- **Expected Risk**: high
- **Actual Risk**: 10.3%
- **Passed**: power_analysis_ran
- **Failed**: risk_level_alignment (expected=high, actual=10.3)
### Highly Ambiguous MSA
- **Type**: MSA
- **Expected Risk**: medium
- **Actual Risk**: 39.4%
- **Passed**: risk_level_alignment
### EU Data Processing Agreement
- **Type**: DPA
- **Expected Risk**: medium
- **Actual Risk**: 10.1%
- **Passed**: strain_analysis_ran
- **Failed**: risk_level_alignment (expected=medium, actual=10.1)
### Commercial Lending Agreement
- **Type**: Loan
- **Expected Risk**: high
- **Actual Risk**: 12.4%
- **Passed**: power_analysis_ran
- **Failed**: risk_level_alignment (expected=high, actual=12.4)
### HIPAA Business Associate Agreement
- **Type**: BAA
- **Expected Risk**: medium
- **Actual Risk**: 10.0%
- **Passed**: strain_analysis_ran
- **Failed**: risk_level_alignment (expected=medium, actual=10.0)
### Web3 Platform Terms of Service
- **Type**: Terms
- **Expected Risk**: high
- **Actual Risk**: 17.9%
- **Passed**: imagination_analysis_ran, strain_analysis_ran
- **Failed**: risk_level_alignment (expected=high, actual=17.9)
