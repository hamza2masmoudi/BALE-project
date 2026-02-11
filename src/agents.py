import os
import requests
import json
import re
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from src.types import BaleState
from src.vector_store import VectorEngine
from dotenv import load_dotenv
from src.logger import setup_logger
from tenacity import retry, stop_after_attempt, wait_exponential
from src.adjudication import calculate_litigation_risk, DecisionFactors
load_dotenv()
logger = setup_logger("bale_agents")
class BaleAgents:
def __init__(self):
self.vector_engine = VectorEngine()
# BALE 2.1: Local Config
self.local_endpoint = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:8000/v1/chat/completions")
self.local_model = os.getenv("LOCAL_LLM_MODEL", "qwen2.5-32b-instruct")
# BALE 2.2: Cloud Config
self.mistral_key = os.getenv("MISTRAL_API_KEY")
self.mistral_model = "mistral-large-latest"
logger.info(f"BALE Agents Initialized. Local: {self.local_model}. Mistral Key Present: {bool(self.mistral_key)}")
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_model(self, messages, temperature=0.1, mode="local"):
"""
Unified Inference Caller.
mode: 'local' (Ollama/vLLM) or 'mistral' (Mistral API).
"""
headers = {"Content-Type": "application/json"}
formatted_messages = []
for m in messages:
if hasattr(m, "content"):
role = "user" if isinstance(m, HumanMessage) else "system"
formatted_messages.append({"role": role, "content": m.content})
else:
formatted_messages.append(m)
if mode == "mistral":
if not self.mistral_key:
raise ValueError("Mistral Mode selected but MISTRAL_API_KEY not found.")
endpoint = "https://api.mistral.ai/v1/chat/completions"
headers["Authorization"] = f"Bearer {self.mistral_key}"
model = self.mistral_model
else:
# Default to Local
endpoint = self.local_endpoint
model = self.local_model
payload = {
"model": model,
"messages": formatted_messages,
"temperature": temperature,
"max_tokens": 2048
}
try:
# logger.debug(f"Calling {mode} endpoint: {endpoint}")
response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
response.raise_for_status()
data = response.json()
return data["choices"][0]["message"]["content"]
except Exception as e:
logger.error(f"Inference Error ({mode}): {e}")
raise e
def civilist_node(self, state: BaleState) -> Dict:
"""
Civilist: Strict interpretation via Napoleonic Code.
"""
content = state.get("content", "")
mode = state.get("execution_mode", "local")
logger.info(f"[Civilist] Interpreting via Civil Law ({mode})")
sys_msg = """You are 'The Civilist', an orthodox French legal scholar. Interpret the text STRICTLY through the lens of the French Civil Code (Napoleonic Code).
- Focus on 'Good Faith' (Bonne Foi - Art. 1104).
- Focus on Statutory Limits (Ordre Public).
- Reject 'implied' terms not in the statute.
"""
try:
output = self._call_model([
SystemMessage(content=sys_msg),
HumanMessage(content=f"Interpret this text:\n{content}")
], temperature=0.1, mode=mode)
except Exception as e:
logger.error(f"Error Civilist: {e}")
output = f"Error: {e}"
return {"civilist_opinion": output}
def commonist_node(self, state: BaleState) -> Dict:
"""
Commonist: Pragmatic interpretation via Case Law.
"""
content = state.get("content", "")
mode = state.get("execution_mode", "local")
logger.info(f"[Commonist] Interpreting via Common Law ({mode})")
sys_msg = """You are 'The Commonist', a pragmatic English commercial judge.
Interpret the text through the lens of English Common Law.
- Focus on Freedom of Contract & Party Autonomy.
- Focus on 'Reasonableness' and Commercial Reality.
- Accept 'Economic Hardship' if successfully negotiated in the clause.
"""
try:
output = self._call_model([
SystemMessage(content=sys_msg),
HumanMessage(content=f"Interpret this text:\n{content}")
], temperature=0.1, mode=mode)
except Exception as e:
logger.error(f"Error Commonist: {e}")
output = f"Error: {e}"
return {"commonist_opinion": output}
def ip_specialist_node(self, state: BaleState) -> Dict:
"""
IP Specialist: Analysis via WIPO / Copyright / Patent Law.
"""
content = state.get("content", "")
mode = state.get("execution_mode", "local")
# Basic keyword check
is_ip_relevant = any(kw in content.lower() for kw in ["copyright", "patent", "intellectual property", "trademark", "license", "moral right", "royalty", "proprietary"])
if not is_ip_relevant:
logger.info("[IP Specialist] No IP terms found. Skipping.")
return {"ip_opinion": "N/A - No IP content detected."}
logger.info(f"[IP Specialist] Analyzing IP clauses ({mode})")
sys_msg = """You are 'The IP Specialist', an expert in International Intellectual Property Law (WIPO/Berne/TRIPS).
Analyze the text specifically for IP risks:
- Identify assignment vs license issues.
- Check for 'Moral Rights' waivers (valid in US, void in France/EU).
- Flag strict liability in IP indemnities.
"""
try:
output = self._call_model([
SystemMessage(content=sys_msg),
HumanMessage(content=f"Analyze IP risks in this text:\n{content}")
], temperature=0.1, mode=mode)
except Exception as e:
logger.error(f"Error IP Specialist: {e}")
output = f"Error: {e}"
return {"ip_opinion": output}
def synthesizer_node(self, state: BaleState) -> Dict:
"""
Synthesizer: Measures the Interpretive Gap.
"""
civilist = state.get("civilist_opinion", "")
commonist = state.get("commonist_opinion", "")
mode = state.get("execution_mode", "local")
logger.info(f"[Synthesizer] Measuring Interpretive Gap ({mode})")
sys_msg = """You are the Supreme Dialectic Judge. Compare the Civilist and Commonist opinions.
Return JSON:
- "synthesis": A summary of the conflict.
- "interpretive_gap": Integer 0-100 (0=Agreement, 100=Total Conflict).
- "symbolic_logic": A pseudo-code representation of the conflict (e.g. A != B).
- "metrics": {
"civil_law_alignment": 0-100,
"common_law_alignment": 0-100,
"contract_certainty": 0-100,
"good_faith_score": 0-100,
"enforceability_score": 0-100
}
"""
try:
response_content = self._call_model([
SystemMessage(content=sys_msg),
HumanMessage(content=f"Civilist: {civilist}\n\nCommonist: {commonist}")
], temperature=0.1, mode=mode)
content_str = response_content
if "```json" in content_str:
content_str = content_str.split("```json")[1].split("```")[0].strip()
elif "```" in content_str:
content_str = content_str.split("```")[1].split("```")[0].strip()
data = json.loads(content_str, strict=False)
synthesis = data.get("synthesis", "No synthesis.")
gap = data.get("interpretive_gap", 0)
logic = data.get("symbolic_logic", "N/A")
metrics = data.get("metrics", {
"civil_law_alignment": 50,
"common_law_alignment": 50,
"contract_certainty": 50,
"good_faith_score": 50,
"enforceability_score": 50
})
except Exception as e:
logger.error(f"Error Synthesizer: {e}")
synthesis = f"Error: {e}"
gap = 0
logic = "Error"
metrics = {}
return {
"synthesizer_comparison": synthesis,
"interpretive_gap": gap,
"metrics": metrics,
"reasoning_steps": [logic] }
def harmonizer_node(self, state: BaleState) -> Dict:
"""
Harmonizer: Drafts a 'Golden Clause' to resolve the conflict.
"""
gap = state.get("interpretive_gap", 0)
mode = state.get("execution_mode", "local")
logger.info(f"[Harmonizer] Gap is {gap}. Drafting solution ({mode}).")
if gap < 10:
return {
"harmonized_clause": "N/A - No significant conflict.",
"harmonization_rationale": "Consensus already exists."
}
civilist = state.get("civilist_opinion", "")
commonist = state.get("commonist_opinion", "")
synthesis = state.get("synthesizer_comparison", "")
sys_msg = """You are 'The Harmonizer', an elite international legal drafter.
Your goal is to draft a 'Golden Clause' that resolves the conflict between the Civilist and Commonist.
Return JSON:
- "golden_clause": The new, compromised legal text.
- "rationale": Explanation of how it satisfies both sides (e.g. 'Uses Good Faith to please Civilist, but allows Reasonable Endeavors for Commonist').
"""
try:
response_content = self._call_model([
SystemMessage(content=sys_msg),
HumanMessage(content=f"Civilist: {civilist}\nCommonist: {commonist}\nSynthesis: {synthesis}")
], temperature=0.1, mode=mode)
content_str = response_content
if "```json" in content_str:
content_str = content_str.split("```json")[1].split("```")[0].strip()
elif "```" in content_str:
content_str = content_str.split("```")[1].split("```")[0].strip()
data = json.loads(content_str, strict=False)
clause = data.get("golden_clause", "Drafting failed.")
if isinstance(clause, dict):
clause = str(clause)
rationale = data.get("rationale", "No rationale.")
except Exception as e:
logger.error(f"Error Harmonizer: {e}")
clause = "Error drafting clause."
rationale = str(e)
return {
"harmonized_clause": clause,
"harmonization_rationale": rationale
}
def simulation_node(self, state: BaleState) -> Dict:
"""
Adversarial Risk Engine: Runs a Mock Trial (Plaintiff vs Defense).
"""
clause = state.get("content", "")
synthesis = state.get("synthesizer_comparison", "")
mode = state.get("execution_mode", "local")
logger.info(f"[Simulation] Starting Adversarial Mock Trial ({mode})")
transcript = []
# 1. Plaintiff Agent
plaintiff_arg = "N/A"
try:
msg = f"""You are the Plaintiff's Counsel. Your goal is to interpret this clause to MAXIMIZE liability for the counterparty.
Clause: {clause}
Context: {synthesis}
Draft a brief, aggressive legal argument (1 paragraph)."""
resp_content = self._call_model([HumanMessage(content=msg)], temperature=0.7, mode=mode)
plaintiff_arg = resp_content
transcript.append(f" **Plaintiff**: {plaintiff_arg}")
except Exception as e:
logger.error(f"Plaintiff Error: {e}")
# 2. Defense Agent
defense_arg = "N/A"
try:
msg = f"""You are the Defense Counsel.
Your goal is to MINIMIZE liability and dismiss the Plaintiff's claim.
Clause: {clause}
Plaintiff Argument: {plaintiff_arg}
Draft a brief, defensive rebuttal (1 paragraph)."""
resp_content = self._call_model([HumanMessage(content=msg)], temperature=0.7, mode=mode)
defense_arg = resp_content
transcript.append(f" **Defense**: {defense_arg}")
except Exception as e:
logger.error(f"Defense Error: {e}")
# 3. Judge Agent
risk_score = 50
try:
msg = f"""You are the Fact-Finding Clerk for the Judge.
Analyze the arguments and extract the BOOLEAN FACTS required for the decision matrix.
Plaintiff Arg: {plaintiff_arg}
Defense Arg: {defense_arg}
Return JSON matching this schema:
{{
"is_ambiguous": boolean, "is_exclusion_clear": boolean, "authority_is_mandatory": boolean, "plaintiff_plausible": boolean }}
"""
resp_content = self._call_model([HumanMessage(content=msg)], temperature=0.1, mode=mode)
content_str = resp_content
if "```json" in content_str:
content_str = content_str.split("```json")[1].split("```")[0].strip()
elif "```" in content_str:
content_str = content_str.split("```")[1].split("```")[0].strip()
data = json.loads(content_str, strict=False)
# Neuro-Symbolic Step:
factors = DecisionFactors(**data)
risk_score, verdict = calculate_litigation_risk(factors)
checklist_str = str(data)
transcript.append(f" **Judicial Factors (Extracted)**:\n{checklist_str}")
transcript.append(f" **Calculated Verdict (Symbolic)**: {verdict}")
transcript.append(f"**Litigation Risk**: {risk_score}%")
except Exception as e:
logger.error(f"Judge Error: {e}")
transcript.append(f"Judge Error: {e}")
return {
"litigation_risk": risk_score,
"mock_trial_transcript": "\n\n".join(transcript)
}
def gatekeeper_node(self, state: BaleState) -> Dict:
"""
Gatekeeper: Verifies citations against VectorDB.
"""
synthesis = state.get("synthesizer_comparison", "")
# Gatekeeper uses embeddings, so uses self.vector_engine (Local Embeddings usually)
# We don't need to switch this since VectorEngine handles embedding model separately
# But if we wanted to log mode:
# logger.info("[Gatekeeper] Verifying Citations")
citations = re.findall(r"(?:Article|Section)\s+\w+", synthesis)
verified = []
for cit in citations:
results = self.vector_engine.hybrid_search(cit, k=1)
if results:
hit = results[0]
meta = hit.get("metadata", {})
auth_val = meta.get("authority_level", 30)
binding = meta.get("binding_status", "DEFAULT")
level_str = "CONTRACT"
if auth_val >= 90: level_str = "STATUTORY"
elif auth_val >= 70: level_str = "CASE LAW"
formatted_cit = f"{cit} [{level_str} - {binding}]"
verified.append(formatted_cit)
else:
pass
return {
"verified_citations": verified,
"final_report": {
"civilist": state.get("civilist_opinion"),
"commonist": state.get("commonist_opinion"),
"synthesis": synthesis,
"gap": state.get("interpretive_gap"),
"logic": state.get("reasoning_steps", [])[0] if state.get("reasoning_steps") else "N/A",
"metrics": state.get("metrics", {}),
"verified": verified,
"golden_clause": state.get("harmonized_clause"),
"rationale": state.get("harmonization_rationale"),
"risk": state.get("litigation_risk"),
"transcript": state.get("mock_trial_transcript")
}
}
