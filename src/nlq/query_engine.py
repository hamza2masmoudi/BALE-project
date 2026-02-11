"""
BALE Natural Language Query Engine
Chat with your contracts using natural language.
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from datetime import datetime, timedelta
from src.corpus import corpus_storage
from src.frontier import analyze_contract_frontiers
from src.logger import setup_logger
logger = setup_logger("nlq_engine")
class QueryIntent(str, Enum):
"""Detected intent types for natural language queries."""
RISK_EXPOSURE = "risk_exposure"
CONTRACT_SEARCH = "contract_search"
CLAUSE_LOOKUP = "clause_lookup"
PORTFOLIO_STATS = "portfolio_stats"
RENEWAL_TIMELINE = "renewal_timeline"
PARTY_ANALYSIS = "party_analysis"
WHAT_IF = "what_if"
COMPARISON = "comparison"
EXPLANATION = "explanation"
GENERAL = "general"
@dataclass
class QueryResult:
"""Result from a natural language query."""
query: str
intent: QueryIntent
answer: str
confidence: float
data: Dict[str, Any]
sources: List[str]
follow_up_suggestions: List[str]
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["intent"] = self.intent.value
return d
class NLQueryEngine:
"""
Natural Language Query engine for BALE.
Enables conversational interaction with contract data.
"""
def __init__(self):
self.intent_patterns = self._build_intent_patterns()
self.context = {} # Conversation context
def _build_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
"""Build regex patterns for intent detection."""
return {
QueryIntent.RISK_EXPOSURE: [
r"(what|how much).*(risk|exposure|liability)",
r"(show|list|find).*(high risk|risky|dangerous)",
r"(bankruptcy|default|breach).*(happen|occurs|if)",
r"(total|aggregate|combined).*(risk|exposure)",
r"(unlimited|uncapped).*(liability|exposure)",
],
QueryIntent.CONTRACT_SEARCH: [
r"(find|show|list|get).*(contract|agreement|nda|msa)",
r"(which|what).*(contract|agreement).*(have|contain|include)",
r"(search|look for|locate).*",
r"contracts (with|from|by)",
],
QueryIntent.CLAUSE_LOOKUP: [
r"(what|show|find).*(clause|term|provision|section)",
r"(indemnif|liabilit|terminat|confidential)",
r"(non.?compete|force majeure|governing law)",
],
QueryIntent.PORTFOLIO_STATS: [
r"(how many|total number|count).*(contract|agreement)",
r"(summary|overview|statistics|stats)",
r"(portfolio|all contracts)",
r"(average|mean|median).*(risk|value)",
],
QueryIntent.RENEWAL_TIMELINE: [
r"(renew|expir|terminat).*(next|upcoming|soon|this)",
r"(when|what date).*(renew|expire|end)",
r"(30|60|90|180) days",
r"calendar|timeline|schedule",
],
QueryIntent.PARTY_ANALYSIS: [
r"(who|which).*(vendor|supplier|customer|partner|counterpart)",
r"(contract|agreement) with (.*)",
r"(company|entity|party|organization)",
r"(relationship|dealing|history) with",
],
QueryIntent.WHAT_IF: [
r"what (if|happens|would happen)",
r"(scenario|hypothetical|assume)",
r"(change|modify|remove|add).*(clause|term)",
],
QueryIntent.COMPARISON: [
r"(compare|versus|vs|difference|between)",
r"(better|worse|stronger|weaker) than",
r"(market|industry|standard|benchmark)",
],
QueryIntent.EXPLANATION: [
r"(explain|what does|what is|define|meaning)",
r"(why|how come|reason)",
r"(help|understand|clarify)",
],
}
def detect_intent(self, query: str) -> Tuple[QueryIntent, float]:
"""Detect the intent of a natural language query."""
query_lower = query.lower()
intent_scores = {}
for intent, patterns in self.intent_patterns.items():
score = 0
for pattern in patterns:
if re.search(pattern, query_lower):
score += 1
if score > 0:
intent_scores[intent] = score / len(patterns)
if not intent_scores:
return QueryIntent.GENERAL, 0.5
best_intent = max(intent_scores, key=intent_scores.get)
return best_intent, min(intent_scores[best_intent] + 0.3, 0.95)
def query(self, query: str, context: Dict[str, Any] = None) -> QueryResult:
"""
Process a natural language query.
"""
if context:
self.context.update(context)
intent, confidence = self.detect_intent(query)
logger.info(f"Query: '{query}' -> Intent: {intent.value} ({confidence:.2f})")
# Route to appropriate handler
handlers = {
QueryIntent.RISK_EXPOSURE: self._handle_risk_exposure,
QueryIntent.CONTRACT_SEARCH: self._handle_contract_search,
QueryIntent.PORTFOLIO_STATS: self._handle_portfolio_stats,
QueryIntent.RENEWAL_TIMELINE: self._handle_renewal_timeline,
QueryIntent.PARTY_ANALYSIS: self._handle_party_analysis,
QueryIntent.CLAUSE_LOOKUP: self._handle_clause_lookup,
QueryIntent.WHAT_IF: self._handle_what_if,
QueryIntent.COMPARISON: self._handle_comparison,
QueryIntent.EXPLANATION: self._handle_explanation,
QueryIntent.GENERAL: self._handle_general,
}
handler = handlers.get(intent, self._handle_general)
answer, data, sources = handler(query)
# Generate follow-up suggestions
follow_ups = self._generate_follow_ups(intent, data)
return QueryResult(
query=query,
intent=intent,
answer=answer,
confidence=confidence,
data=data,
sources=sources,
follow_up_suggestions=follow_ups
)
def _handle_risk_exposure(self, query: str) -> Tuple[str, Dict, List]:
"""Handle risk exposure queries."""
stats = corpus_storage.get_corpus_stats()
analyses = corpus_storage.list_analyses(limit=100)
if not analyses:
return (
"No contracts in the corpus yet. Upload contracts to analyze risk exposure.",
{"total": 0},
[]
)
# Calculate aggregate risk
high_risk = [a for a in analyses if a.risk_score >= 60]
medium_risk = [a for a in analyses if 30 <= a.risk_score < 60]
# Check for specific keywords
query_lower = query.lower()
if "unlimited" in query_lower or "uncapped" in query_lower:
# Find contracts with unlimited liability
unlimited = [a for a in analyses if a.risk_score > 50]
answer = f"Found **{len(unlimited)}** contracts with potential unlimited liability exposure. "
if unlimited:
answer += f"Highest risk: {unlimited[0].contract_name} ({unlimited[0].risk_score}%)"
return answer, {"contracts": [a.to_dict() for a in unlimited[:5]]}, [a.analysis_id for a in unlimited[:5]]
if "bankruptcy" in query_lower or "default" in query_lower:
answer = f"If a counterparty defaults: **{len(high_risk)}** contracts have high exposure. "
answer += f"Total high-risk contracts represent significant potential liability. "
answer += "Recommend reviewing force majeure and termination clauses."
return answer, {"high_risk_count": len(high_risk)}, []
# General risk summary
avg_risk = sum(a.risk_score for a in analyses) / len(analyses)
answer = f"**Portfolio Risk Summary:**\n"
answer += f"- Total contracts: {len(analyses)}\n"
answer += f"- High risk (60%+): {len(high_risk)}\n"
answer += f"- Medium risk (30-60%): {len(medium_risk)}\n"
answer += f"- Average risk score: {avg_risk:.1f}%"
return answer, stats, []
def _handle_contract_search(self, query: str) -> Tuple[str, Dict, List]:
"""Handle contract search queries."""
query_lower = query.lower()
# Extract search terms
contract_type = None
jurisdiction = None
for t in ["msa", "nda", "sla", "license", "employment", "vendor"]:
if t in query_lower:
contract_type = t
break
for j in ["us", "uk", "eu", "germany", "singapore"]:
if j in query_lower:
jurisdiction = j.upper()
break
analyses = corpus_storage.list_analyses(
limit=20,
contract_type=contract_type,
jurisdiction=jurisdiction
)
if not analyses:
return (
f"No contracts found matching your criteria.",
{"results": []},
[]
)
answer = f"Found **{len(analyses)}** contracts"
if contract_type:
answer += f" of type {contract_type.upper()}"
if jurisdiction:
answer += f" in {jurisdiction}"
answer += ":\n\n"
for a in analyses[:5]:
answer += f"- **{a.contract_name}** ({a.contract_type}) - Risk: {a.risk_score}%\n"
if len(analyses) > 5:
answer += f"\n...and {len(analyses) - 5} more"
return answer, {"results": [a.to_dict() for a in analyses]}, [a.analysis_id for a in analyses]
def _handle_portfolio_stats(self, query: str) -> Tuple[str, Dict, List]:
"""Handle portfolio statistics queries."""
stats = corpus_storage.get_corpus_stats()
answer = f"**Portfolio Overview:**\n\n"
answer += f" **Total Contracts:** {stats['total_analyses']}\n"
answer += f" **Entities Tracked:** {stats['total_entities']}\n"
answer += f" **Average Risk:** {stats['avg_risk_score']:.1f}%\n\n"
if stats['risk_distribution']:
answer += "**Risk Distribution:**\n"
for level, count in stats['risk_distribution'].items():
emoji = "" if level == "low" else "" if level == "medium" else ""
answer += f"{emoji} {level.title()}: {count} contracts\n"
if stats['type_distribution']:
answer += "\n**By Type:**\n"
for t, count in list(stats['type_distribution'].items())[:5]:
answer += f"- {t.upper()}: {count}\n"
return answer, stats, []
def _handle_renewal_timeline(self, query: str) -> Tuple[str, Dict, List]:
"""Handle renewal/expiration timeline queries."""
analyses = corpus_storage.list_analyses(limit=50)
# Simulate renewal data (in production, this would come from contract metadata)
answer = "**Upcoming Contract Events:**\n\n"
answer += " *Note: Renewal dates require contract metadata integration.*\n\n"
answer += "Based on analysis dates, contracts requiring attention:\n"
for a in analyses[:5]:
answer += f"- **{a.contract_name}** - Risk: {a.risk_score}%\n"
return answer, {"contracts": [a.to_dict() for a in analyses[:5]]}, []
def _handle_party_analysis(self, query: str) -> Tuple[str, Dict, List]:
"""Handle counterparty analysis queries."""
entities = corpus_storage.list_entities(limit=20)
if not entities:
return (
"No entity data available yet. Analyze contracts to build entity profiles.",
{"entities": []},
[]
)
answer = f"**Entity Analysis:**\n\n"
answer += f"Tracking **{len(entities)}** counterparties:\n\n"
for e in entities[:10]:
trend_emoji = "" if e.risk_trend == "increasing" else "" if e.risk_trend == "decreasing" else ""
answer += f"- **{e.entity_name}**: {e.total_contracts} contracts, "
answer += f"Avg Risk: {e.avg_risk_score:.0f}% {trend_emoji}\n"
return answer, {"entities": [e.__dict__ for e in entities]}, []
def _handle_clause_lookup(self, query: str) -> Tuple[str, Dict, List]:
"""Handle clause lookup queries."""
query_lower = query.lower()
clause_info = {
"indemnification": {
"description": "Protects against third-party claims. Critical for risk allocation.",
"typical_issues": ["One-sided obligations", "Uncapped exposure", "Missing notice requirements"],
"recommendation": "Ensure mutual indemnification with appropriate caps."
},
"limitation of liability": {
"description": "Caps potential damages. Essential for managing risk exposure.",
"typical_issues": ["No cap", "Cap too low for scope", "Missing carveouts"],
"recommendation": "Standard is 12-24 months of fees with carveouts for willful misconduct."
},
"termination": {
"description": "Defines how parties can exit the agreement.",
"typical_issues": ["Asymmetric rights", "No cure period", "Excessive notice requirements"],
"recommendation": "Ensure mutual termination rights with reasonable cure periods."
},
"confidentiality": {
"description": "Protects sensitive information disclosed between parties.",
"typical_issues": ["One-sided protection", "Perpetual obligations", "Broad definitions"],
"recommendation": "Mutual obligations with 3-5 year survival period."
},
"force majeure": {
"description": "Excuses performance for events beyond control.",
"typical_issues": ["Narrow definition", "No termination right", "Missing notice requirements"],
"recommendation": "Include pandemic, cyber-attacks, and government actions."
},
}
for clause_type, info in clause_info.items():
if clause_type.replace(" ", "") in query_lower.replace(" ", ""):
answer = f"**{clause_type.title()} Clause:**\n\n"
answer += f" **What it does:** {info['description']}\n\n"
answer += " **Common issues:**\n"
for issue in info['typical_issues']:
answer += f"- {issue}\n"
answer += f"\n **Recommendation:** {info['recommendation']}"
return answer, info, []
return (
"I can explain these clause types: indemnification, limitation of liability, termination, confidentiality, force majeure. Which would you like to know about?",
{"available_clauses": list(clause_info.keys())},
[]
)
def _handle_what_if(self, query: str) -> Tuple[str, Dict, List]:
"""Handle what-if scenario queries."""
answer = "**Scenario Analysis:**\n\n"
answer += "What-if analysis requires specifying:\n"
answer += "1. The contract(s) to analyze\n"
answer += "2. The change to simulate\n\n"
answer += "Examples:\n"
answer += "- 'What if we remove the liability cap from TechCorp MSA?'\n"
answer += "- 'What if the vendor increases prices by 20%?'\n"
answer += "- 'What happens if we terminate for convenience?'"
return answer, {}, []
def _handle_comparison(self, query: str) -> Tuple[str, Dict, List]:
"""Handle comparison queries."""
from src.negotiation import MARKET_BENCHMARKS
answer = "**Market Comparison:**\n\n"
answer += "Your contracts vs market benchmarks:\n\n"
for key, benchmark in list(MARKET_BENCHMARKS.items())[:3]:
clause = key.split(":")[0].replace("_", " ").title()
answer += f"**{clause}:**\n"
answer += f"- Market standard: {benchmark.standard_language[:80]}...\n"
answer += f"- Mutual rate: {benchmark.mutual_rate*100:.0f}%\n\n"
return answer, {"benchmarks_available": len(MARKET_BENCHMARKS)}, []
def _handle_explanation(self, query: str) -> Tuple[str, Dict, List]:
"""Handle explanation queries."""
return self._handle_clause_lookup(query)
def _handle_general(self, query: str) -> Tuple[str, Dict, List]:
"""Handle general queries."""
answer = "I can help you with:\n\n"
answer += " **Risk Analysis** - 'What is my total risk exposure?'\n"
answer += " **Contract Search** - 'Find all NDAs with UK jurisdiction'\n"
answer += " **Portfolio Stats** - 'Give me a portfolio summary'\n"
answer += " **Renewals** - 'What contracts renew in the next 90 days?'\n"
answer += " **Counterparties** - 'Show me contracts with TechCorp'\n"
answer += " **Clauses** - 'Explain the indemnification clause'\n"
answer += " **Comparisons** - 'How do my terms compare to market?'\n"
return answer, {}, []
def _generate_follow_ups(self, intent: QueryIntent, data: Dict) -> List[str]:
"""Generate follow-up suggestions."""
suggestions = {
QueryIntent.RISK_EXPOSURE: [
"Show me the highest risk contracts",
"What is my indemnification exposure?",
"Compare my risk to market benchmarks"
],
QueryIntent.CONTRACT_SEARCH: [
"What is the total value of these contracts?",
"Show risk breakdown for these contracts",
"When do these contracts expire?"
],
QueryIntent.PORTFOLIO_STATS: [
"Show me high-risk contracts",
"Which counterparties have the most contracts?",
"What types of contracts do we have the most?"
],
QueryIntent.PARTY_ANALYSIS: [
"What is our exposure to this counterparty?",
"Show contracts expiring with this party",
"Compare this party to others"
],
}
return suggestions.get(intent, [
"Show portfolio summary",
"What is my risk exposure?",
"Find high-risk contracts"
])
# Singleton
nlq_engine = NLQueryEngine()
