"""
BALE Multi-Jurisdiction Agents
Specialized legal agents for different jurisdictions.
"""
import os
import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from src.types import BaleState
from src.logger import setup_logger
from src.jurisdiction import Jurisdiction, LegalFamily

logger = setup_logger("bale_multi_agents")


class MultiJurisdictionAgents:
    """
    Extended agent collection for multi-jurisdiction analysis.
    Complements the base BaleAgents with jurisdiction-specific expertise.
    """
    
    def __init__(self, base_agents):
        """
        Initialize with reference to base agents for LLM access.
        
        Args:
            base_agents: BaleAgents instance with _call_model method
        """
        self.base = base_agents
    
    # ==================== US COMMERCIAL LAW ====================
    
    def us_commercial_node(self, state: BaleState) -> Dict:
        """
        US Commercial Law Agent: UCC and Delaware Court expertise.
        """
        content = state.get("content", "")
        mode = state.get("execution_mode", "local")
        logger.info(f"[US Commercial] Interpreting via UCC and US Case Law ({mode})")
        
        sys_msg = """You are 'The Commercialist', an expert US commercial law attorney.
Interpret the contract through the lens of US law:

**Primary Sources**:
- Uniform Commercial Code (UCC) Articles 1-9
- Restatement (Second) of Contracts
- State law (assume Delaware/New York unless specified)

**Key Principles**:
1. **Freedom of Contract**: Parties may generally agree to any terms not unconscionable
2. **Good Faith**: UCC §1-304 requires good faith in performance (honesty + reasonable commercial standards)
3. **Course of Dealing**: Past conduct between parties informs interpretation
4. **Trade Usage**: Industry customs are incorporated unless excluded
5. **Implied Warranty of Merchantability**: UCC §2-314 for sale of goods

**Analysis Focus**:
- Is this a transaction in goods (UCC applies) or services (common law)?
- Are there unconscionability concerns under UCC §2-302?
- Do limitation of liability clauses meet UCC §2-719 requirements?
- Consider Delaware Chancery jurisprudence for corporate matters
"""
        try:
            output = self.base._call_model([
                SystemMessage(content=sys_msg),
                HumanMessage(content=f"Analyze under US law:\n{content}")
            ], temperature=0.1, mode=mode)
        except Exception as e:
            logger.error(f"Error US Commercial: {e}")
            output = f"Error: {e}"
        
        return {"us_commercial_opinion": output}
    
    # ==================== GERMAN CIVIL LAW ====================
    
    def germanist_node(self, state: BaleState) -> Dict:
        """
        German Civil Law Agent: BGB and HGB expertise.
        """
        content = state.get("content", "")
        mode = state.get("execution_mode", "local")
        logger.info(f"[Germanist] Interpreting via BGB ({mode})")
        
        sys_msg = """You are 'Der Zivilist', a German civil law expert (Rechtsanwalt).
Interpret the contract through German law:

**Primary Sources**:
- Bürgerliches Gesetzbuch (BGB) - Civil Code
- Handelsgesetzbuch (HGB) - Commercial Code  
- AGB-Recht (Standard Terms Regulation) §§305-310 BGB

**Key Principles**:
1. **Treu und Glauben (§242 BGB)**: Good faith governs all obligations
2. **AGB-Kontrolle**: Standard terms are strictly controlled:
   - Überraschende Klauseln (surprising clauses) are void
   - Unangemessene Benachteiligung (unreasonable disadvantage) test
3. **Vertragsauslegung (§§133, 157 BGB)**: Interpret by true intent, not literal words
4. **Höhere Gewalt**: Force majeure requires impossibility, not mere hardship
5. **Schadensersatz (§280 BGB)**: Damages require fault (Verschulden)

**Analysis Focus**:
- Are these AGB (standard terms)? If so, apply strict §305ff controls
- Does the clause violate mandatory law (zwingendes Recht)?
- Would a Bundesgerichtshof (BGH) uphold this clause?
- Consider transparency requirement (Transparenzgebot)
"""
        try:
            output = self.base._call_model([
                SystemMessage(content=sys_msg),
                HumanMessage(content=f"Analyze under German law (BGB/HGB):\n{content}")
            ], temperature=0.1, mode=mode)
        except Exception as e:
            logger.error(f"Error Germanist: {e}")
            output = f"Error: {e}"
        
        return {"germanist_opinion": output}
    
    # ==================== EU LAW ====================
    
    def eu_law_node(self, state: BaleState) -> Dict:
        """
        EU Law Agent: European regulations and directives.
        """
        content = state.get("content", "")
        mode = state.get("execution_mode", "local")
        logger.info(f"[EU Law] Analyzing EU regulatory compliance ({mode})")
        
        sys_msg = """You are 'The Europeanist', an EU law specialist.
Analyze the contract for EU law compliance:

**Primary Sources**:
- Rome I Regulation (Applicable Law)
- Brussels I (Jurisdiction)
- Unfair Contract Terms Directive 93/13/EEC
- Consumer Rights Directive 2011/83/EU
- GDPR (if personal data involved)
- Digital Services Act / Digital Markets Act (if platform)

**Key Principles**:
1. **Consumer Protection Primacy**: Consumer-facing terms scrutinized strictly
2. **Transparency Requirement**: Core terms must be in plain language
3. **Choice of Law Limits**: Cannot derogate from mandatory consumer protections
4. **Data Protection**: GDPR compliance is non-negotiable
5. **Unfair Terms Test**: 
   - Not individually negotiated?
   - Causes significant imbalance?
   - Contrary to good faith?

**Analysis Focus**:
- Is this B2B or B2C? (Different rules apply)
- Does choice of law clause comply with Rome I?
- Are there GDPR implications (data processing clauses)?
- Would ECJ case law invalidate any clauses?
"""
        try:
            output = self.base._call_model([
                SystemMessage(content=sys_msg),
                HumanMessage(content=f"Analyze for EU law compliance:\n{content}")
            ], temperature=0.1, mode=mode)
        except Exception as e:
            logger.error(f"Error EU Law: {e}")
            output = f"Error: {e}"
        
        return {"eu_law_opinion": output}
    
    # ==================== CROSS-BORDER CONFLICTS ====================
    
    def cross_border_node(self, state: BaleState) -> Dict:
        """
        Cross-Border Conflict Agent: Resolves multi-jurisdiction conflicts.
        """
        civilist = state.get("civilist_opinion", "")
        commonist = state.get("commonist_opinion", "")
        us_opinion = state.get("us_commercial_opinion", "")
        german_opinion = state.get("germanist_opinion", "")
        eu_opinion = state.get("eu_law_opinion", "")
        mode = state.get("execution_mode", "local")
        
        # Gather all available opinions
        opinions = []
        if civilist: opinions.append(f"**French Civil Law**: {civilist[:500]}")
        if commonist: opinions.append(f"**English Common Law**: {commonist[:500]}")
        if us_opinion: opinions.append(f"**US Commercial Law**: {us_opinion[:500]}")
        if german_opinion: opinions.append(f"**German Law (BGB)**: {german_opinion[:500]}")
        if eu_opinion: opinions.append(f"**EU Law**: {eu_opinion[:500]}")
        
        if len(opinions) < 2:
            return {"cross_border_analysis": "Insufficient multi-jurisdiction data for conflict analysis."}
        
        logger.info(f"[Cross-Border] Analyzing conflicts across {len(opinions)} jurisdictions ({mode})")
        
        sys_msg = """You are 'The Conflict Resolver', an expert in private international law.
Your task is to identify and resolve conflicts between different legal systems.

**Your Framework**:
1. **Identification**: What specific points do the jurisdictions disagree on?
2. **Characterization**: Is this a matter of substance, procedure, or public policy?
3. **Applicable Law**: Under conflict rules (Rome I, Restatement), which law governs?
4. **Harmonization**: Can conflicting requirements be satisfied simultaneously?

**Output JSON**:
{
    "conflicts_identified": [
        {"issue": "...", "systems_in_conflict": ["FR", "UK"], "severity": "HIGH/MEDIUM/LOW"}
    ],
    "primary_applicable_law": "...",
    "conflict_resolution_strategy": "...",
    "harmonization_possible": true/false,
    "risk_if_unresolved": 0-100,
    "recommended_choice_of_law": "..."
}
"""
        try:
            opinions_text = "\n\n".join(opinions)
            response = self.base._call_model([
                SystemMessage(content=sys_msg),
                HumanMessage(content=f"Analyze conflicts between these jurisdictional opinions:\n\n{opinions_text}")
            ], temperature=0.1, mode=mode)
            
            # Parse JSON
            content_str = response
            if "```json" in content_str:
                content_str = content_str.split("```json")[1].split("```")[0].strip()
            elif "```" in content_str:
                content_str = content_str.split("```")[1].split("```")[0].strip()
            
            try:
                data = json.loads(content_str, strict=False)
            except:
                data = {"raw_analysis": response}
            
        except Exception as e:
            logger.error(f"Error Cross-Border: {e}")
            data = {"error": str(e)}
        
        return {"cross_border_analysis": data}
    
    # ==================== SINGAPORE (FUTURE) ====================
    
    def singapore_node(self, state: BaleState) -> Dict:
        """
        Singapore Law Agent (placeholder for future expansion).
        """
        content = state.get("content", "")
        mode = state.get("execution_mode", "local")
        
        sys_msg = """You are a Singapore law expert.
Singapore follows English common law with local modifications.
Key statutes: Contracts Act, Sale of Goods Act, PDPA.
Consider SICC/SIAC for international commercial disputes.
"""
        try:
            output = self.base._call_model([
                SystemMessage(content=sys_msg),
                HumanMessage(content=f"Analyze under Singapore law:\n{content}")
            ], temperature=0.1, mode=mode)
        except Exception as e:
            output = f"Error: {e}"
        
        return {"singapore_opinion": output}


def get_jurisdiction_prompts(jurisdiction: Jurisdiction) -> Dict[str, str]:
    """
    Get specialized prompts for a jurisdiction.
    Used by harmonizer to generate jurisdiction-appropriate solutions.
    """
    prompts = {
        Jurisdiction.FRANCE: {
            "harmonization_focus": "Ensure compliance with Art. 1104 CC (good faith) and ordre public",
            "risk_factors": "Unfair advantage clauses void under Art. 1171 CC"
        },
        Jurisdiction.UK: {
            "harmonization_focus": "Meet UCTA reasonableness test, ensure clear exclusions",
            "risk_factors": "Exclusion clauses must pass Photo Production scrutiny"
        },
        Jurisdiction.US: {
            "harmonization_focus": "Comply with UCC good faith, avoid unconscionability",
            "risk_factors": "State-specific rules may apply (esp. California, New York)"
        },
        Jurisdiction.GERMANY: {
            "harmonization_focus": "Pass AGB-Kontrolle, meet transparency requirements",
            "risk_factors": "Standard terms subject to §§305-310 BGB strict control"
        },
        Jurisdiction.EU: {
            "harmonization_focus": "Consumer protection primacy, GDPR compliance",
            "risk_factors": "Cannot contract out of mandatory EU consumer protections"
        },
        Jurisdiction.SINGAPORE: {
            "harmonization_focus": "Balance common law flexibility with PDPA compliance",
            "risk_factors": "Consider SICC jurisdiction for complex disputes"
        },
        Jurisdiction.INTERNATIONAL: {
            "harmonization_focus": "Align with CISG/UNIDROIT, clear choice of law",
            "risk_factors": "Ambiguous jurisdiction creates enforcement uncertainty"
        }
    }
    return prompts.get(jurisdiction, prompts[Jurisdiction.INTERNATIONAL])
