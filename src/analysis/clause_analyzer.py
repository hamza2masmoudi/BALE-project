"""
BALE LLM-Powered Clause Analyzer
Real legal intelligence via structured LLM prompts.
"""
import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from src.logger import setup_logger

load_dotenv()
logger = setup_logger("clause_analyzer")


@dataclass
class ClauseRisk:
    """Risk assessment for a single clause."""
    clause_type: str
    clause_text: str
    risk_score: int  # 0-100
    risk_level: str  # low, medium, high, critical
    issues: List[str]
    recommendation: str
    who_benefits: str  # party_a, party_b, balanced
    enforceability: str  # strong, moderate, weak, questionable
    missing_protections: List[str]


@dataclass
class ContractAnalysis:
    """Complete contract analysis result."""
    contract_id: str
    overall_risk: int
    risk_level: str
    clauses_analyzed: int
    high_risk_clauses: List[ClauseRisk]
    medium_risk_clauses: List[ClauseRisk]
    low_risk_clauses: List[ClauseRisk]
    critical_issues: List[str]
    recommendations: List[str]
    power_balance: str  # balanced, favors_party_a, favors_party_b
    analysis_timestamp: str


# Clause extraction patterns
CLAUSE_PATTERNS = [
    (r'(?:^|\n)(\d+\.?\s*(?:INDEMNIF|Indemnif)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'indemnification'),
    (r'(?:^|\n)(\d+\.?\s*(?:LIABIL|Liabil)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'liability'),
    (r'(?:^|\n)(\d+\.?\s*(?:CONFIDEN|Confiden)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'confidentiality'),
    (r'(?:^|\n)(\d+\.?\s*(?:TERMINAT|Terminat)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'termination'),
    (r'(?:^|\n)(\d+\.?\s*(?:INTELLECTUAL|Intellectual|IP\s+)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'ip_ownership'),
    (r'(?:^|\n)(\d+\.?\s*(?:WARRANT|Warrant)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'warranties'),
    (r'(?:^|\n)(\d+\.?\s*(?:FORCE\s+MAJEURE|Force\s+Majeure)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'force_majeure'),
    (r'(?:^|\n)(\d+\.?\s*(?:DISPUTE|Dispute|ARBITRAT|Arbitrat|GOVERNING\s+LAW)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'dispute_resolution'),
    (r'(?:^|\n)(\d+\.?\s*(?:DATA\s+PROTECT|PRIVACY|GDPR|data\s+protection)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'data_protection'),
    (r'(?:^|\n)(\d+\.?\s*(?:NON-COMPETE|Non-Compete|RESTRICTIVE\s+COVENANT)[^\n]*\n(?:.*?\n)*?(?=\n\d+\.|\nARTICLE|\Z))', 'non_compete'),
]


class ClauseAnalyzer:
    """
    LLM-powered contract clause analyzer.
    Uses structured prompts for accurate legal risk assessment.
    """
    
    def __init__(self, mode: str = "auto"):
        """
        Initialize analyzer.
        mode: 'auto' (detect best), 'mistral', or 'local'
        """
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        self.local_endpoint = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:8000/v1/chat/completions")
        
        if mode == "auto":
            self.mode = "mistral" if self.mistral_key else "local"
        else:
            self.mode = mode
            
        logger.info(f"ClauseAnalyzer initialized in {self.mode} mode")
        
        # Training data collection
        self.training_data: List[Dict] = []
        self.save_training_data = True
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        """Call the LLM with structured prompts."""
        headers = {"Content-Type": "application/json"}
        
        if self.mode == "mistral":
            endpoint = "https://api.mistral.ai/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.mistral_key}"
            model = "mistral-large-latest"
        else:
            endpoint = self.local_endpoint
            model = os.getenv("LOCAL_LLM_MODEL", "qwen2.5-32b-instruct")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 2048
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        
        # Save for training data
        if self.save_training_data:
            self.training_data.append({
                "system": system_prompt,
                "user": user_prompt,
                "assistant": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return result

    def extract_clauses(self, contract_text: str) -> List[Tuple[str, str]]:
        """Extract clauses from contract text."""
        clauses = []
        
        for pattern, clause_type in CLAUSE_PATTERNS:
            matches = re.findall(pattern, contract_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.strip()) > 50:  # Minimum clause length
                    clauses.append((clause_type, match.strip()[:3000]))  # Cap at 3000 chars
        
        # If pattern matching failed, split by sections
        if not clauses:
            sections = re.split(r'\n(?=\d+\.|\n[A-Z][A-Z]+\s)', contract_text)
            for section in sections:
                if len(section.strip()) > 100:
                    clauses.append(("general", section.strip()[:3000]))
        
        logger.info(f"Extracted {len(clauses)} clauses from contract")
        return clauses

    def _get_clause_prompt(self, clause_type: str) -> Tuple[str, str]:
        """Get specialized prompts for each clause type."""
        
        base_system = """You are a senior legal analyst specializing in contract risk assessment. 
You must respond with valid JSON only, no other text.
Your analysis must be precise, actionable, and focused on real legal risks."""

        prompts = {
            "indemnification": (
                base_system + "\nYou specialize in indemnification and liability allocation.",
                """Analyze this indemnification clause for legal risks:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Key risk factors to analyze:
- Scope: Is it unlimited or capped?
- Carveouts: Are there exclusions for gross negligence, willful misconduct?
- Defense obligations: Who controls litigation?
- Third-party claims coverage
- Survival period after termination"""
            ),
            
            "liability": (
                base_system + "\nYou specialize in limitation of liability clauses.",
                """Analyze this limitation of liability clause:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Key risk factors:
- Liability cap amount (should be 12-24 months fees typically)
- Consequential damages exclusion scope
- Carveouts for data breach, IP infringement, confidentiality breach
- "Super cap" for certain claims
- Mutual vs one-sided limitation"""
            ),
            
            "confidentiality": (
                base_system + "\nYou specialize in confidentiality and NDA provisions.",
                """Analyze this confidentiality clause:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Key risk factors:
- Definition of confidential information (too broad or narrow?)
- Exclusions for public info, prior knowledge, independent development
- Permitted disclosures (legal compulsion procedure)
- Duration of obligation (survival period)
- Return/destruction requirements"""
            ),
            
            "termination": (
                base_system + "\nYou specialize in termination and exit provisions.",
                """Analyze this termination clause:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Key risk factors:
- Termination for convenience rights (mutual or one-sided?)
- Notice period requirements
- Cure periods for breach
- Termination for cause events
- Transition/wind-down obligations
- Effect on accrued rights"""
            ),
            
            "ip_ownership": (
                base_system + "\nYou specialize in intellectual property provisions.",
                """Analyze this IP ownership clause:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Key risk factors:
- Work-for-hire vs license model
- Pre-existing IP carveouts
- Joint development ownership
- Background IP protection
- License grants (exclusive vs non-exclusive, field restrictions)
- Source code escrow triggers"""
            ),
            
            "non_compete": (
                base_system + "\nYou specialize in restrictive covenants and non-competes.",
                """Analyze this non-compete/restrictive covenant:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Key risk factors:
- Geographic scope (reasonable or overly broad?)
- Duration (typically 1-2 years max for enforceability)
- Activity restrictions (narrowly tailored?)
- Consideration provided
- State/jurisdiction enforceability (California, North Dakota ban them)
- Non-solicit vs no-hire distinction"""
            ),
            
            "data_protection": (
                base_system + "\nYou specialize in data protection and privacy provisions.",
                """Analyze this data protection clause:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Key risk factors:
- GDPR compliance (if EU data involved)
- Data processing agreement requirements
- Sub-processor controls
- Cross-border transfer mechanisms
- Breach notification timelines
- Audit rights
- Data subject rights handling"""
            ),
        }
        
        # Default prompt for unrecognized clause types
        default = (
            base_system,
            """Analyze this contract clause for legal risks:

"{clause_text}"

Respond with this exact JSON structure:
{{
    "risk_score": <0-100 integer>,
    "risk_level": "<low|medium|high|critical>",
    "issues": ["<specific issue 1>", "<specific issue 2>"],
    "who_benefits": "<party_a|party_b|balanced>",
    "enforceability": "<strong|moderate|weak|questionable>",
    "missing_protections": ["<missing item 1>", "<missing item 2>"],
    "recommendation": "<one sentence recommendation>"
}}

Consider: risk allocation, enforceability, missing protections, and who benefits."""
        )
        
        return prompts.get(clause_type, default)

    def analyze_clause(self, clause_type: str, clause_text: str) -> ClauseRisk:
        """Analyze a single clause using LLM."""
        system_prompt, user_template = self._get_clause_prompt(clause_type)
        user_prompt = user_template.format(clause_text=clause_text)
        
        try:
            response = self._call_llm(system_prompt, user_prompt)
            
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                logger.warning(f"Could not parse JSON from LLM response for {clause_type}")
                result = {
                    "risk_score": 50,
                    "risk_level": "medium",
                    "issues": ["Could not parse LLM response"],
                    "who_benefits": "unknown",
                    "enforceability": "unknown",
                    "missing_protections": [],
                    "recommendation": "Review required"
                }
            
            return ClauseRisk(
                clause_type=clause_type,
                clause_text=clause_text[:500] + "..." if len(clause_text) > 500 else clause_text,
                risk_score=result.get("risk_score", 50),
                risk_level=result.get("risk_level", "medium"),
                issues=result.get("issues", []),
                recommendation=result.get("recommendation", ""),
                who_benefits=result.get("who_benefits", "unknown"),
                enforceability=result.get("enforceability", "unknown"),
                missing_protections=result.get("missing_protections", [])
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {clause_type}: {e}")
            return ClauseRisk(
                clause_type=clause_type,
                clause_text=clause_text[:200] + "...",
                risk_score=50,
                risk_level="medium",
                issues=[f"Analysis error: {str(e)}"],
                recommendation="Manual review required",
                who_benefits="unknown",
                enforceability="unknown",
                missing_protections=[]
            )

    def analyze_contract(self, contract_text: str, contract_id: Optional[str] = None) -> ContractAnalysis:
        """
        Analyze entire contract clause by clause.
        Uses parallel processing for speed.
        """
        if not contract_id:
            contract_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Extract clauses
        clauses = self.extract_clauses(contract_text)
        
        if not clauses:
            logger.warning("No clauses found in contract")
            return ContractAnalysis(
                contract_id=contract_id,
                overall_risk=30,
                risk_level="medium",
                clauses_analyzed=0,
                high_risk_clauses=[],
                medium_risk_clauses=[],
                low_risk_clauses=[],
                critical_issues=["Could not extract clauses from contract"],
                recommendations=["Ensure contract has standard section formatting"],
                power_balance="unknown",
                analysis_timestamp=datetime.utcnow().isoformat()
            )
        
        # Analyze clauses in parallel
        clause_results: List[ClauseRisk] = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.analyze_clause, clause_type, clause_text): clause_type
                for clause_type, clause_text in clauses
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    clause_results.append(result)
                    logger.info(f"Analyzed {result.clause_type}: risk={result.risk_score}")
                except Exception as e:
                    logger.error(f"Clause analysis failed: {e}")
        
        # Categorize by risk level
        high_risk = [c for c in clause_results if c.risk_score >= 60]
        medium_risk = [c for c in clause_results if 30 <= c.risk_score < 60]
        low_risk = [c for c in clause_results if c.risk_score < 30]
        
        # Calculate overall risk (weighted average with penalties)
        if clause_results:
            base_risk = sum(c.risk_score for c in clause_results) / len(clause_results)
            # Add penalty for high-risk clauses
            high_risk_penalty = len(high_risk) * 5
            overall_risk = min(100, base_risk + high_risk_penalty)
        else:
            overall_risk = 50
        
        # Determine risk level
        if overall_risk >= 70:
            risk_level = "critical"
        elif overall_risk >= 50:
            risk_level = "high"
        elif overall_risk >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Collect critical issues
        critical_issues = []
        for c in high_risk:
            critical_issues.extend([f"[{c.clause_type.upper()}] {issue}" for issue in c.issues[:2]])
        
        # Collect recommendations
        recommendations = [c.recommendation for c in high_risk if c.recommendation][:5]
        
        # Determine power balance
        party_a_favors = sum(1 for c in clause_results if c.who_benefits == "party_a")
        party_b_favors = sum(1 for c in clause_results if c.who_benefits == "party_b")
        
        if party_a_favors > party_b_favors + 2:
            power_balance = "favors_party_a"
        elif party_b_favors > party_a_favors + 2:
            power_balance = "favors_party_b"
        else:
            power_balance = "balanced"
        
        return ContractAnalysis(
            contract_id=contract_id,
            overall_risk=int(overall_risk),
            risk_level=risk_level,
            clauses_analyzed=len(clause_results),
            high_risk_clauses=high_risk,
            medium_risk_clauses=medium_risk,
            low_risk_clauses=low_risk,
            critical_issues=critical_issues[:10],
            recommendations=recommendations,
            power_balance=power_balance,
            analysis_timestamp=datetime.utcnow().isoformat()
        )
    
    def save_training_data_to_file(self, filepath: str = "training_data/clause_analysis.jsonl"):
        """Save collected training data for future finetuning."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "a") as f:
            for item in self.training_data:
                f.write(json.dumps(item) + "\n")
        
        logger.info(f"Saved {len(self.training_data)} training examples to {filepath}")
        self.training_data = []


# Singleton instance
clause_analyzer = ClauseAnalyzer()
