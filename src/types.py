from typing import TypedDict, List, Dict, Optional

class BaleState(TypedDict):
    content: str
    fr_civil_text: Optional[str]
    en_common_text: Optional[str]
    
    # Dialectic Outputs
    civilist_opinion: Optional[str]
    commonist_opinion: Optional[str]
    synthesizer_comparison: Optional[str]
    interpretive_gap: int # 0-100
    
    # Harmonizer Outputs (Phase 8)
    harmonized_clause: Optional[str]
    harmonization_rationale: Optional[str]
    
    # Phase 9: Adversarial Risk Engine
    litigation_risk: int # 0-100 (Probability of Defense Failure)
    mock_trial_transcript: Optional[str]
    
    # Deprecated/Aliases for compatibility
    analyst_output: Optional[str]
    auditor_feedback: Optional[str]
    
    verified_citations: List[str]
    conflict_score: int
    final_report: Dict
    reasoning_steps: List[str]
