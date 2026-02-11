"""
BALE Clause Negotiation System
AI-powered negotiation suggestions with market benchmarks.
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import re
from src.logger import setup_logger
logger = setup_logger("clause_negotiation")
class NegotiationStance(str, Enum):
AGGRESSIVE = "aggressive"
BALANCED = "balanced"
PROTECTIVE = "protective"
MARKET_STANDARD = "market_standard"
class RiskMitigation(str, Enum):
CAP_LIABILITY = "cap_liability"
ADD_CARVEOUT = "add_carveout"
NARROW_SCOPE = "narrow_scope"
ADD_NOTICE = "add_notice"
MUTUAL_OBLIGATION = "mutual_obligation"
SUNSET_CLAUSE = "sunset_clause"
@dataclass
class MarketBenchmark:
"""Market benchmark for a specific clause type."""
clause_type: str
jurisdiction: str
industry: str
# Market norms
typical_cap_multiplier: float # e.g., 1.0 = 1x annual fees
typical_duration_months: int
typical_notice_days: int
mutual_rate: float # How often this clause is mutual (0-1)
carveout_rate: float # How often carveouts exist (0-1)
# Market language
standard_language: str
aggressive_language: str
protective_language: str
@dataclass
class NegotiationSuggestion:
"""A specific negotiation suggestion."""
clause_type: str
current_text: str
suggested_text: str
mitigation_type: RiskMitigation
rationale: str
market_comparison: str
risk_reduction: int # Estimated risk score reduction
negotiation_difficulty: str # "easy", "moderate", "hard"
priority: str # "must-have", "should-have", "nice-to-have"
def to_dict(self) -> Dict[str, Any]:
d = asdict(self)
d["mitigation_type"] = self.mitigation_type.value
return d
@dataclass
class NegotiationPlaybook:
"""Complete negotiation playbook for a contract."""
contract_id: str
your_position: str # "buyer", "seller", "licensor", etc.
counterparty_power: float # -1 to 1, negative = you have power
# Overall stance recommendation
recommended_stance: NegotiationStance
# Priority-ordered suggestions
must_have: List[NegotiationSuggestion]
should_have: List[NegotiationSuggestion]
nice_to_have: List[NegotiationSuggestion]
# Deal breakers
walk_away_triggers: List[str]
# Concession strategy
concession_order: List[str] # What to give up first if needed
# Summary
total_risk_reduction: int
estimated_difficulty: str
def to_dict(self) -> Dict[str, Any]:
d = {
"contract_id": self.contract_id,
"your_position": self.your_position,
"counterparty_power": self.counterparty_power,
"recommended_stance": self.recommended_stance.value,
"must_have": [s.to_dict() for s in self.must_have],
"should_have": [s.to_dict() for s in self.should_have],
"nice_to_have": [s.to_dict() for s in self.nice_to_have],
"walk_away_triggers": self.walk_away_triggers,
"concession_order": self.concession_order,
"total_risk_reduction": self.total_risk_reduction,
"estimated_difficulty": self.estimated_difficulty,
}
return d
# Market benchmarks database
MARKET_BENCHMARKS: Dict[str, MarketBenchmark] = {
"liability_cap:US:technology": MarketBenchmark(
clause_type="liability_cap",
jurisdiction="US",
industry="technology",
typical_cap_multiplier=1.0,
typical_duration_months=12,
typical_notice_days=0,
mutual_rate=0.7,
carveout_rate=0.85,
standard_language="Liability shall not exceed fees paid in the 12 months preceding the claim.",
aggressive_language="IN NO EVENT SHALL [PARTY]'S LIABILITY EXCEED THE FEES PAID HEREUNDER.",
protective_language="Liability shall not exceed fees paid in the 12 months preceding the claim, except for (i) indemnification obligations, (ii) gross negligence or willful misconduct, and (iii) breach of confidentiality."
),
"indemnification:US:technology": MarketBenchmark(
clause_type="indemnification",
jurisdiction="US",
industry="technology",
typical_cap_multiplier=0, # Usually uncapped
typical_duration_months=36,
typical_notice_days=30,
mutual_rate=0.6,
carveout_rate=0.4,
standard_language="Each party shall indemnify the other from third-party claims arising from its breach of this Agreement.",
aggressive_language="Customer shall indemnify Provider from any and all claims arising from Customer's use of the Services.",
protective_language="Provider shall indemnify Customer from third-party IP infringement claims. Customer's indemnification limited to claims arising from Customer's data or willful misconduct."
),
"termination:US:technology": MarketBenchmark(
clause_type="termination",
jurisdiction="US",
industry="technology",
typical_cap_multiplier=0,
typical_duration_months=0,
typical_notice_days=30,
mutual_rate=0.9,
carveout_rate=0.5,
standard_language="Either party may terminate for convenience upon 30 days written notice.",
aggressive_language="Provider may terminate immediately upon Customer's breach. Customer may terminate only upon 90 days notice.",
protective_language="Either party may terminate for convenience upon 30 days notice. Either party may terminate immediately if the other materially breaches and fails to cure within 30 days."
),
"ip_ownership:US:technology": MarketBenchmark(
clause_type="ip_ownership",
jurisdiction="US",
industry="technology",
typical_cap_multiplier=0,
typical_duration_months=0,
typical_notice_days=0,
mutual_rate=0.2,
carveout_rate=0.7,
standard_language="Pre-existing IP remains with originating party. Work product jointly owned or licensed.",
aggressive_language="All work product, including derivative works, shall be owned exclusively by [PARTY].",
protective_language="Pre-existing IP remains with originating party. Customer-specific deliverables owned by Customer. Provider retains rights to general knowledge and pre-existing tools."
),
"data_protection:EU:technology": MarketBenchmark(
clause_type="data_protection",
jurisdiction="EU",
industry="technology",
typical_cap_multiplier=2.0,
typical_duration_months=0,
typical_notice_days=72,
mutual_rate=0.3,
carveout_rate=0.9,
standard_language="Processor shall process personal data in accordance with GDPR and Controller's instructions.",
aggressive_language="Customer bears all responsibility for data protection compliance.",
protective_language="Processor shall implement appropriate technical and organizational measures. Processor shall notify Controller within 72 hours of any personal data breach. Sub-processors require prior written consent."
),
}
class ClauseNegotiator:
"""
AI-powered clause negotiation engine.
Compares clauses to market benchmarks and suggests improvements.
"""
def __init__(self):
self.benchmarks = MARKET_BENCHMARKS
def analyze_clause(
self,
clause_text: str,
clause_type: str,
jurisdiction: str,
industry: str,
your_position: str
) -> List[NegotiationSuggestion]:
"""
Analyze a clause and generate negotiation suggestions.
"""
suggestions = []
# Get benchmark
benchmark_key = f"{clause_type}:{jurisdiction}:{industry}"
benchmark = self.benchmarks.get(
benchmark_key,
self.benchmarks.get(f"{clause_type}:US:technology")
)
if not benchmark:
return suggestions
text_lower = clause_text.lower()
# Check for common issues
# 1. Liability cap analysis
if clause_type == "liability_cap":
suggestions.extend(self._analyze_liability_cap(clause_text, benchmark, your_position))
# 2. Indemnification analysis
elif clause_type == "indemnification":
suggestions.extend(self._analyze_indemnification(clause_text, benchmark, your_position))
# 3. Termination analysis
elif clause_type == "termination":
suggestions.extend(self._analyze_termination(clause_text, benchmark, your_position))
# 4. IP ownership analysis
elif clause_type == "ip_ownership":
suggestions.extend(self._analyze_ip_ownership(clause_text, benchmark, your_position))
# Generic checks for any clause
suggestions.extend(self._generic_improvements(clause_text, clause_type, benchmark))
return suggestions
def _analyze_liability_cap(
self, text: str, benchmark: MarketBenchmark,
position: str
) -> List[NegotiationSuggestion]:
suggestions = []
text_lower = text.lower()
# Check if uncapped
if "unlimited" in text_lower or not re.search(r"not exceed|cap|limit", text_lower):
suggestions.append(NegotiationSuggestion(
clause_type="liability_cap",
current_text=text[:200],
suggested_text=benchmark.protective_language,
mitigation_type=RiskMitigation.CAP_LIABILITY,
rationale="Liability appears uncapped, which exposes you to unlimited risk.",
market_comparison=f"Market standard is {benchmark.typical_cap_multiplier}x annual fees.",
risk_reduction=25,
negotiation_difficulty="moderate",
priority="must-have"
))
# Check for carveouts
if benchmark.carveout_rate > 0.5 and not re.search(r"except|carve.?out|exclude", text_lower):
suggestions.append(NegotiationSuggestion(
clause_type="liability_cap",
current_text=text[:200],
suggested_text="Add: 'except for (i) indemnification obligations, (ii) gross negligence or willful misconduct, (iii) breach of confidentiality, and (iv) IP infringement'",
mitigation_type=RiskMitigation.ADD_CARVEOUT,
rationale=f"{int(benchmark.carveout_rate*100)}% of market contracts include carveouts for serious breaches.",
market_comparison="Standard practice to exclude willful misconduct and IP from caps.",
risk_reduction=15,
negotiation_difficulty="easy",
priority="should-have"
))
return suggestions
def _analyze_indemnification(
self,
text: str,
benchmark: MarketBenchmark,
position: str
) -> List[NegotiationSuggestion]:
suggestions = []
text_lower = text.lower()
# Check if one-sided
mutual_indicators = ["each party", "mutual", "reciprocal", "both parties"]
is_mutual = any(ind in text_lower for ind in mutual_indicators)
if not is_mutual and benchmark.mutual_rate > 0.5:
suggestions.append(NegotiationSuggestion(
clause_type="indemnification",
current_text=text[:200],
suggested_text=benchmark.standard_language,
mitigation_type=RiskMitigation.MUTUAL_OBLIGATION,
rationale="Indemnification is one-sided. Market standard is mutual.",
market_comparison=f"{int(benchmark.mutual_rate*100)}% of market contracts have mutual indemnification.",
risk_reduction=20,
negotiation_difficulty="moderate",
priority="must-have"
))
# Check for notice period
if "notice" not in text_lower and benchmark.typical_notice_days > 0:
suggestions.append(NegotiationSuggestion(
clause_type="indemnification",
current_text=text[:200],
suggested_text=f"Add: 'The indemnifying party shall be notified within {benchmark.typical_notice_days} days of any claim.'",
mitigation_type=RiskMitigation.ADD_NOTICE,
rationale="No notice requirement for claims reduces your ability to respond.",
market_comparison=f"Standard is {benchmark.typical_notice_days}-day notice requirement.",
risk_reduction=10,
negotiation_difficulty="easy",
priority="should-have"
))
return suggestions
def _analyze_termination(
self,
text: str,
benchmark: MarketBenchmark,
position: str
) -> List[NegotiationSuggestion]:
suggestions = []
text_lower = text.lower()
# Check for cure period
if "cure" not in text_lower and "remedy" not in text_lower:
suggestions.append(NegotiationSuggestion(
clause_type="termination",
current_text=text[:200],
suggested_text="Add: 'and fails to cure within 30 days of written notice'",
mitigation_type=RiskMitigation.ADD_NOTICE,
rationale="No cure period means immediate termination on any breach.",
market_comparison="Standard practice is 30-day cure period for material breaches.",
risk_reduction=15,
negotiation_difficulty="easy",
priority="must-have"
))
# Check for asymmetric termination
if "provider may terminate" in text_lower and "customer may terminate" not in text_lower:
suggestions.append(NegotiationSuggestion(
clause_type="termination",
current_text=text[:200],
suggested_text=benchmark.protective_language,
mitigation_type=RiskMitigation.MUTUAL_OBLIGATION,
rationale="Termination rights are asymmetric - only provider can terminate.",
market_comparison=f"{int(benchmark.mutual_rate*100)}% of contracts have symmetric termination.",
risk_reduction=20,
negotiation_difficulty="moderate",
priority="must-have"
))
return suggestions
def _analyze_ip_ownership(
self,
text: str,
benchmark: MarketBenchmark,
position: str
) -> List[NegotiationSuggestion]:
suggestions = []
text_lower = text.lower()
# Check for total assignment
if "exclusively" in text_lower or "all rights" in text_lower:
suggestions.append(NegotiationSuggestion(
clause_type="ip_ownership",
current_text=text[:200],
suggested_text=benchmark.protective_language,
mitigation_type=RiskMitigation.NARROW_SCOPE,
rationale="Broad IP assignment may include your pre-existing IP.",
market_comparison="Standard: Pre-existing IP remains with originating party.",
risk_reduction=20,
negotiation_difficulty="moderate",
priority="must-have"
))
return suggestions
def _generic_improvements(
self,
text: str,
clause_type: str,
benchmark: MarketBenchmark
) -> List[NegotiationSuggestion]:
suggestions = []
text_lower = text.lower()
# Check for "sole discretion"
if "sole discretion" in text_lower:
suggestions.append(NegotiationSuggestion(
clause_type=clause_type,
current_text=text[:200],
suggested_text="Replace 'sole discretion' with 'reasonable discretion'",
mitigation_type=RiskMitigation.NARROW_SCOPE,
rationale="'Sole discretion' allows arbitrary decisions without recourse.",
market_comparison="Best practice: 'reasonable discretion' or specific criteria.",
risk_reduction=10,
negotiation_difficulty="easy",
priority="should-have"
))
# Check for perpetual terms
if "perpetual" in text_lower or "forever" in text_lower:
suggestions.append(NegotiationSuggestion(
clause_type=clause_type,
current_text=text[:200],
suggested_text=f"Add sunset clause: 'This obligation shall survive for {benchmark.typical_duration_months} months following termination.'",
mitigation_type=RiskMitigation.SUNSET_CLAUSE,
rationale="Perpetual obligations create indefinite exposure.",
market_comparison=f"Market standard survival is {benchmark.typical_duration_months} months.",
risk_reduction=10,
negotiation_difficulty="moderate",
priority="nice-to-have"
))
return suggestions
def generate_playbook(
self,
contract_text: str,
contract_id: str,
jurisdiction: str,
industry: str,
your_position: str,
frontier_analysis: Dict[str, Any] = None
) -> NegotiationPlaybook:
"""
Generate a complete negotiation playbook for a contract.
"""
# Extract clauses
clauses = self._extract_clauses_for_negotiation(contract_text)
# Analyze each clause
all_suggestions = []
for clause_type, clause_text in clauses.items():
suggestions = self.analyze_clause(
clause_text,
clause_type,
jurisdiction,
industry,
your_position
)
all_suggestions.extend(suggestions)
# Categorize by priority
must_have = [s for s in all_suggestions if s.priority == "must-have"]
should_have = [s for s in all_suggestions if s.priority == "should-have"]
nice_to_have = [s for s in all_suggestions if s.priority == "nice-to-have"]
# Determine counterparty power from frontier analysis
counterparty_power = 0
if frontier_analysis and "social" in frontier_analysis:
counterparty_power = frontier_analysis["social"].get("asymmetry", 0)
# Recommend stance
if counterparty_power > 0.5:
stance = NegotiationStance.PROTECTIVE
elif counterparty_power < -0.5:
stance = NegotiationStance.AGGRESSIVE
else:
stance = NegotiationStance.BALANCED
# Calculate total risk reduction
total_reduction = sum(s.risk_reduction for s in all_suggestions)
# Define walk-away triggers
walk_away = []
if any(s.clause_type == "liability_cap" and s.priority == "must-have" for s in must_have):
walk_away.append("Refusal to add any liability cap")
if any(s.clause_type == "indemnification" and "one-sided" in s.rationale.lower() for s in must_have):
walk_away.append("Completely one-sided indemnification with no reciprocity")
# Define concession order (give up nice-to-have first)
concession_order = [
s.clause_type for s in nice_to_have
] + [
s.clause_type for s in should_have
]
# Estimate difficulty
if len(must_have) > 5:
difficulty = "hard"
elif len(must_have) > 2:
difficulty = "moderate"
else:
difficulty = "easy"
return NegotiationPlaybook(
contract_id=contract_id,
your_position=your_position,
counterparty_power=counterparty_power,
recommended_stance=stance,
must_have=must_have,
should_have=should_have,
nice_to_have=nice_to_have,
walk_away_triggers=walk_away,
concession_order=concession_order[:5], # Top 5
total_risk_reduction=total_reduction,
estimated_difficulty=difficulty
)
def _extract_clauses_for_negotiation(self, text: str) -> Dict[str, str]:
"""Extract clauses relevant for negotiation."""
clauses = {}
text_lower = text.lower()
# Simple section extraction
sections = re.split(r'\n\s*\d+[\.\)]\s+|\n\n+(?=[A-Z])', text)
for section in sections:
section_lower = section.lower()
if "liability" in section_lower and "limit" in section_lower:
clauses["liability_cap"] = section[:1000]
elif "indemnif" in section_lower:
clauses["indemnification"] = section[:1000]
elif "terminat" in section_lower:
clauses["termination"] = section[:1000]
elif "intellectual property" in section_lower or "work product" in section_lower:
clauses["ip_ownership"] = section[:1000]
elif "data protection" in section_lower or "personal data" in section_lower:
clauses["data_protection"] = section[:1000]
return clauses
# Singleton
clause_negotiator = ClauseNegotiator()
