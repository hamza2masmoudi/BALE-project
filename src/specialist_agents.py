"""
BALE V8 Specialist Agents
Domain-specific legal analysis agents for enhanced coverage.
"""
import os
import requests
import json
from typing import Dict, Any, Optional
from src.types import BaleState
from src.logger import setup_logger
from tenacity import retry, stop_after_attempt, wait_exponential
logger = setup_logger("bale_specialist_agents")
class BaseSpecialistAgent:
"""Base class for specialist agents."""
def __init__(self):
self.local_endpoint = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:8000/v1/chat/completions")
self.local_model = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:32b")
self.mistral_key = os.getenv("MISTRAL_API_KEY")
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_model(self, messages: list, temperature: float = 0.1, mode: str = "local") -> str:
"""Unified model caller."""
if mode == "mistral" and self.mistral_key:
return self._call_mistral(messages, temperature)
return self._call_local(messages, temperature)
def _call_local(self, messages: list, temperature: float) -> str:
"""Call local LLM endpoint."""
try:
response = requests.post(
self.local_endpoint,
json={
"model": self.local_model,
"messages": messages,
"temperature": temperature,
"max_tokens": 2000
},
timeout=120
)
response.raise_for_status()
return response.json()["choices"][0]["message"]["content"]
except Exception as e:
logger.error(f"Local LLM error: {e}")
return f"ERROR: {str(e)}"
def _call_mistral(self, messages: list, temperature: float) -> str:
"""Call Mistral API."""
try:
response = requests.post(
"https://api.mistral.ai/v1/chat/completions",
headers={
"Authorization": f"Bearer {self.mistral_key}",
"Content-Type": "application/json"
},
json={
"model": "mistral-large-latest",
"messages": messages,
"temperature": temperature,
"max_tokens": 2000
},
timeout=120
)
response.raise_for_status()
return response.json()["choices"][0]["message"]["content"]
except Exception as e:
logger.error(f"Mistral API error: {e}")
return f"ERROR: {str(e)}"
class MAExpertAgent(BaseSpecialistAgent):
"""
M&A Expert Agent
Analyzes mergers & acquisitions specific provisions:
- Representations & Warranties
- Material Adverse Change (MAC) clauses
- Earnout provisions
- Closing conditions
- Purchase price adjustments
"""
SYSTEM_PROMPT = """You are an expert M&A (Mergers & Acquisitions) attorney with deep expertise in:
- Representations and Warranties analysis
- Material Adverse Change (MAC/MAE) clause interpretation
- Earnout and contingent consideration provisions
- Closing conditions and bring-down requirements
- Purchase price adjustments (working capital, net debt)
- Indemnification and escrow mechanisms
- Deal protection devices (no-shop, break fees)
Jurisdiction expertise: UK law and French law (cross-border M&A).
When analyzing clauses, consider:
1. Market standard vs. non-standard provisions
2. Seller-friendly vs. Buyer-friendly language
3. Enforceability in UK/French courts
4. Risk allocation between parties
5. Practical deal implications
Provide structured analysis with specific legal references where applicable."""
def analyze(self, state: BaleState) -> BaleState:
"""Analyze M&A provisions in the contract."""
clause = state.get("raw_clause", "")
messages = [
{"role": "system", "content": self.SYSTEM_PROMPT},
{"role": "user", "content": f"""Analyze this M&A provision:
CLAUSE:
{clause}
Provide analysis covering:
1. PROVISION TYPE: (Rep/Warranty, MAC, Earnout, Closing Condition, etc.)
2. PARTY BIAS: (Buyer-friendly, Seller-friendly, Balanced)
3. MARKET STANDARD: (Standard, Non-standard, Aggressive)
4. KEY RISKS: (List specific risks for each party)
5. RECOMMENDED REVISIONS: (If any)
6. LEGAL REFERENCES: (Relevant UK/French law or precedents)"""}
]
mode = state.get("inference_mode", "local")
analysis = self._call_model(messages, temperature=0.1, mode=mode)
state["ma_analysis"] = analysis
logger.info("M&A Expert analysis completed")
return state
class DataPrivacyAgent(BaseSpecialistAgent):
"""
Data Privacy Expert Agent
Analyzes GDPR and data protection provisions:
- Controller/Processor determinations
- Data Processing Agreements (Art. 28)
- International data transfers (SCCs)
- Data subject rights
- Security measures
- Breach notification
"""
SYSTEM_PROMPT = """You are a Data Protection specialist with expertise in:
- GDPR (General Data Protection Regulation)
- UK Data Protection Act 2018 and UK GDPR
- French Data Protection Law (Loi Informatique et Libertés)
- Standard Contractual Clauses (2021 SCCs)
- Data Processing Agreements (Art. 28 GDPR)
- International data transfers and Schrems II implications
- Data breach notification requirements
- Data subject rights (access, erasure, portability)
When analyzing data protection clauses, consider:
1. Controller vs. Processor determination
2. GDPR Art. 28 mandatory requirements
3. International transfer mechanisms
4. Technical and organizational measures
5. Sub-processor obligations
6. Liability allocation
Provide practical guidance citing specific GDPR articles and regulatory guidance."""
def analyze(self, state: BaleState) -> BaleState:
"""Analyze data protection provisions."""
clause = state.get("raw_clause", "")
messages = [
{"role": "system", "content": self.SYSTEM_PROMPT},
{"role": "user", "content": f"""Analyze this data protection provision:
CLAUSE:
{clause}
Provide analysis covering:
1. PROVISION TYPE: (DPA, SCC, Controller Agreement, etc.)
2. GDPR COMPLIANCE: (Compliant, Partially Compliant, Non-Compliant)
3. MISSING REQUIREMENTS: (List any missing Art. 28 requirements)
4. TRANSFER MECHANISM: (If applicable - SCCs, BCRs, adequacy)
5. SECURITY MEASURES: (Assessment of TOMs)
6. RISK ASSESSMENT: (High/Medium/Low with justification)
7. RECOMMENDED CHANGES: (Specific revisions needed)
8. LEGAL REFERENCES: (GDPR articles, CNIL/ICO guidance)"""}
]
mode = state.get("inference_mode", "local")
analysis = self._call_model(messages, temperature=0.1, mode=mode)
state["data_privacy_analysis"] = analysis
logger.info("Data Privacy analysis completed")
return state
class EmploymentLawAgent(BaseSpecialistAgent):
"""
Employment Law Expert Agent
Analyzes employment and restrictive covenants:
- Non-compete clauses
- Non-solicitation provisions
- Garden leave
- IP assignment
- Severance
"""
SYSTEM_PROMPT = """You are an Employment Law specialist with expertise in:
- UK employment law (Employment Rights Act 1996, common law restraints)
- French employment law (Code du Travail, Cour de Cassation jurisprudence)
- Restrictive covenants (non-compete, non-solicitation, non-dealing)
- Garden leave provisions
- IP and invention assignment
- Severance and termination payments
- Post-termination restrictions
Key differences between UK and French law:
- UK: Restraint of trade doctrine, reasonableness test, blue-pencil rule
- FR: Clause de non-concurrence must have financial compensation (contrepartie financière)
- FR: Article L.1121-1 Code du Travail - proportionality requirement
When analyzing, consider:
1. Geographic and temporal scope
2. Financial compensation (mandatory in France)
3. Legitimate business interest
4. Proportionality and reasonableness
5. Enforceability likelihood"""
def analyze(self, state: BaleState) -> BaleState:
"""Analyze employment law provisions."""
clause = state.get("raw_clause", "")
messages = [
{"role": "system", "content": self.SYSTEM_PROMPT},
{"role": "user", "content": f"""Analyze this employment provision:
CLAUSE:
{clause}
Provide analysis covering:
1. PROVISION TYPE: (Non-compete, Non-solicitation, Garden Leave, etc.)
2. SCOPE: (Duration, Geography, Activities restricted)
3. UK ENFORCEABILITY: (Likely enforceable, Questionable, Unenforceable)
4. FRENCH ENFORCEABILITY: (Likely enforceable, Questionable, Unenforceable)
5. MISSING ELEMENTS: (e.g., financial compensation for FR)
6. RECOMMENDED REVISIONS: (For each jurisdiction)
7. LEGAL REFERENCES: (Cases, statutes, Code du Travail articles)"""}
]
mode = state.get("inference_mode", "local")
analysis = self._call_model(messages, temperature=0.1, mode=mode)
state["employment_analysis"] = analysis
logger.info("Employment Law analysis completed")
return state
class DisputeResolutionAgent(BaseSpecialistAgent):
"""
Dispute Resolution Expert Agent
Analyzes jurisdiction and dispute resolution clauses:
- Governing law
- Jurisdiction (exclusive/non-exclusive)
- Arbitration clauses (ICC, LCIA)
- Mediation requirements
- Forum selection
"""
SYSTEM_PROMPT = """You are a Dispute Resolution specialist with expertise in:
- Governing law clauses (Rome I Regulation, choice of law)
- Jurisdiction clauses (Brussels Regulation recast, Hague Convention)
- International arbitration (ICC, LCIA, UNCITRAL)
- Enforcement of judgments and awards
- Mediation and ADR mechanisms
- Forum selection and asymmetric clauses
Key considerations:
- UK post-Brexit: No longer subject to Brussels Regulation
- French courts: Strong enforcement of arbitration clauses
- Asymmetric clauses: Valid in most jurisdictions
- Mandatory consumer protection rules
Provide practical advice on:
1. Clause validity and enforceability
2. Strategic advantages of forum choice
3. Enforcement considerations
4. Cost and timing implications"""
def analyze(self, state: BaleState) -> BaleState:
"""Analyze dispute resolution provisions."""
clause = state.get("raw_clause", "")
messages = [
{"role": "system", "content": self.SYSTEM_PROMPT},
{"role": "user", "content": f"""Analyze this dispute resolution provision:
CLAUSE:
{clause}
Provide analysis covering:
1. MECHANISM: (Litigation, Arbitration, Mediation, Hybrid)
2. GOVERNING LAW: (If specified)
3. FORUM/SEAT: (Jurisdiction or arbitral seat)
4. VALIDITY: (Valid, Potentially invalid, Invalid - with reasons)
5. ENFORCEMENT: (Assessment of enforceability across UK/FR/EU)
6. STRATEGIC ASSESSMENT: (Party favored, practical implications)
7. RECOMMENDED IMPROVEMENTS: (If any)
8. LEGAL REFERENCES: (Conventions, regulations, case law)"""}
]
mode = state.get("inference_mode", "local")
analysis = self._call_model(messages, temperature=0.1, mode=mode)
state["dispute_resolution_analysis"] = analysis
logger.info("Dispute Resolution analysis completed")
return state
# ==================== SPECIALIST ROUTER ====================
class SpecialistRouter:
"""Routes clauses to appropriate specialist agents based on content."""
def __init__(self):
self.ma_agent = MAExpertAgent()
self.data_privacy_agent = DataPrivacyAgent()
self.employment_agent = EmploymentLawAgent()
self.dispute_agent = DisputeResolutionAgent()
# Keywords for routing
self.ma_keywords = [
"representation", "warranty", "material adverse", "mac", "mae",
"earnout", "earn-out", "closing condition", "purchase price",
"indemnification basket", "escrow", "holdback", "bring-down",
"reps", "warranties", "disclosure schedule"
]
self.data_keywords = [
"personal data", "données personnelles", "gdpr", "rgpd",
"data processor", "sous-traitant", "data controller",
"responsable du traitement", "standard contractual clauses",
"scc", "data transfer", "transfert de données", "data breach",
"article 28", "data subject", "personne concernée"
]
self.employment_keywords = [
"non-compete", "non-competition", "clause de non-concurrence",
"non-solicitation", "non-sollicitation", "garden leave",
"restrictive covenant", "employee", "salarié", "employé",
"termination of employment", "severance", "indemnité"
]
self.dispute_keywords = [
"governing law", "loi applicable", "jurisdiction", "compétence",
"arbitration", "arbitrage", "mediation", "médiation",
"exclusive jurisdiction", "compétence exclusive", "icc", "lcia",
"dispute resolution", "règlement des litiges"
]
def route(self, clause: str) -> list:
"""Determine which specialist agents should analyze this clause."""
clause_lower = clause.lower()
agents = []
if any(kw in clause_lower for kw in self.ma_keywords):
agents.append("ma")
if any(kw in clause_lower for kw in self.data_keywords):
agents.append("data_privacy")
if any(kw in clause_lower for kw in self.employment_keywords):
agents.append("employment")
if any(kw in clause_lower for kw in self.dispute_keywords):
agents.append("dispute")
return agents if agents else ["general"]
def analyze(self, state: BaleState) -> BaleState:
"""Run appropriate specialist analyses."""
clause = state.get("raw_clause", "")
agents_to_run = self.route(clause)
specialist_results = {}
for agent_type in agents_to_run:
if agent_type == "ma":
state = self.ma_agent.analyze(state)
specialist_results["ma"] = state.get("ma_analysis", "")
elif agent_type == "data_privacy":
state = self.data_privacy_agent.analyze(state)
specialist_results["data_privacy"] = state.get("data_privacy_analysis", "")
elif agent_type == "employment":
state = self.employment_agent.analyze(state)
specialist_results["employment"] = state.get("employment_analysis", "")
elif agent_type == "dispute":
state = self.dispute_agent.analyze(state)
specialist_results["dispute"] = state.get("dispute_resolution_analysis", "")
state["specialist_analyses"] = specialist_results
state["specialists_used"] = agents_to_run
return state
# Export
__all__ = [
"MAExpertAgent",
"DataPrivacyAgent", "EmploymentLawAgent",
"DisputeResolutionAgent",
"SpecialistRouter"
]
