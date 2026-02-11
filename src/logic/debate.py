"""
BALE Adversarial Debate Engine
Orchestrates a multi-turn dialectic between Plaintiff and Defense to explore legal nuances.
"""
import logging
from typing import List, Dict, Any
from src.agents import BaleAgents
from src.types import BaleState
logger = logging.getLogger("bale_debate")
class DebateEngine(BaleAgents):
"""
Extends BaleAgents to run a multi-turn adversarial debate.
"""
def __init__(self):
super().__init__()
def run_debate(self, clause_text: str, context: str = "", rounds: int = 2) -> Dict[str, Any]:
"""
Run a multi-round debate.
Returns the full transcript and the final fact extraction.
"""
transcript = []
history = [] # For LLM context
# Initial Context
intro = f"Dispute Context: {context}\nClause in Dispute: {clause_text}"
history.append(f"Judge: We are here to debate the following clause:\n{clause_text}")
logger.info(f"Starting {rounds}-round debate on clause: {clause_text[:50]}...")
for i in range(rounds):
round_num = i + 1
# --- PLAINTIFF TURN ---
p_prompt = f"""You are the Plaintiff's Counsel.
Round {round_num} of {rounds}.
Current Transcript:
{self._format_history(history)}
Your Goal: Argue WHY this clause should be interpreted against the drafter (Defense) or is invalid.
Focus on: Ambiguity, Unfairness, Statutory Violations.
If this is a rebuttal, address the Defense's last point directly.
Keep it sharp and under 100 words.
"""
p_arg = self._call_model([{"role": "user", "content": p_prompt}], temperature=0.7)
history.append(f"Plaintiff (Round {round_num}): {p_arg}")
transcript.append({"round": round_num, "speaker": "Plaintiff", "text": p_arg})
print(f"\n[Round {round_num} Plaintiff]: {p_arg}")
# --- DEFENSE TURN ---
d_prompt = f"""You are the Defense Counsel.
Round {round_num} of {rounds}.
Current Transcript:
{self._format_history(history)}
Your Goal: Argue WHY this clause is valid, clear, and enforceable.
Focus on: Freedom of Contract, Commercial Reality, Plain Meaning.
You MUST rebut the Plaintiff's specific argument from this round.
Keep it sharp and under 100 words.
"""
d_arg = self._call_model([{"role": "user", "content": d_prompt}], temperature=0.7)
history.append(f"Defense (Round {round_num}): {d_arg}")
transcript.append({"round": round_num, "speaker": "Defense", "text": d_arg})
print(f"[Round {round_num} Defense]: {d_arg}")
# --- JUDGE FACT EXTRACTION ---
print("\n[Judge] Extracting Facts from Debate...")
facts = self._extract_facts(history, clause_text)
return {
"transcript": transcript,
"facts": facts,
"full_text": "\n".join(history)
}
def _format_history(self, history: List[str]) -> str:
return "\n".join(history)
def _extract_facts(self, history: List[str], clause: str) -> Dict[str, Any]:
"""
Ask the LLM to act as a Clerk and extract boolean facts based on the debate.
These facts feed the Symbolic Engine.
"""
transcript_text = self._format_history(history)
prompt = f"""You are the Judicial Clerk.
Review the debate transcript below regarding a contract clause.
Clause: {clause}
TRANSCRIPT:
{transcript_text}
Your Job: Extract purely factual BOOLEAN attributes to feed the Logic Engine.
Be objective. If the Debate showed a fact was "proven" or "highly likely", mark True.
Return JSON ONLY:
{{
"is_ambiguous": boolean,
"is_external": boolean,
"is_unforeseeable": boolean,
"is_irresistible": boolean,
"is_economic_change": boolean,
"is_strike": boolean,
"is_internal_dispute": boolean,
"contract_date_post_2020": boolean
}}
"""
response = self._call_model([{"role": "user", "content": prompt}], temperature=0.1)
# Simple parsing (robustness would need json repair)
try:
import json
clean_resp = response.replace("```json", "").replace("```", "").strip()
return json.loads(clean_resp)
except Exception as e:
logger.error(f"Failed to parse Judge output: {e}")
return {}
# Export
__all__ = ["DebateEngine"]
