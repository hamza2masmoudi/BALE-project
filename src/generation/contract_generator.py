"""
BALE Contract Generation Engine
Generate complete contracts from natural language requirements.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime
import json

from src.logger import setup_logger

logger = setup_logger("contract_generator")


class ContractStyle(str, Enum):
    FORMAL = "formal"
    PLAIN_ENGLISH = "plain_english"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    PROTECTIVE = "protective"


@dataclass
class GenerationRequest:
    """Request for contract generation."""
    contract_type: str
    description: str
    jurisdiction: str = "US"
    industry: str = "technology"
    
    party_a_name: str = "Party A"
    party_a_type: str = "corporation"
    party_b_name: str = "Party B"
    party_b_type: str = "corporation"
    
    your_position: str = "neutral"  # buyer, seller, neutral
    style: ContractStyle = ContractStyle.BALANCED
    
    # Optional specifications
    term_months: int = 12
    auto_renew: bool = True
    liability_cap_multiplier: float = 1.0  # Multiplier of annual fees
    include_clauses: List[str] = field(default_factory=list)
    exclude_clauses: List[str] = field(default_factory=list)
    special_requirements: str = ""


@dataclass
class GeneratedContract:
    """A generated contract."""
    contract_id: str
    contract_type: str
    title: str
    full_text: str
    
    sections: List[Dict[str, str]]
    metadata: Dict[str, Any]
    
    risk_score: int
    warnings: List[str]
    
    generated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Clause templates organized by type and section
CLAUSE_TEMPLATES = {
    "recitals": {
        "standard": """
RECITALS

WHEREAS, {party_a} is engaged in the business of {party_a_business}; and

WHEREAS, {party_b} desires to engage {party_a} to provide {service_description}; and

WHEREAS, the parties wish to set forth the terms and conditions of such engagement;

NOW, THEREFORE, in consideration of the mutual covenants and agreements hereinafter set forth and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the parties agree as follows:
""",
    },
    "definitions": {
        "standard": """
1. DEFINITIONS

1.1 "Affiliate" means any entity that directly or indirectly controls, is controlled by, or is under common control with a party.

1.2 "Confidential Information" means all non-public information disclosed by one party to the other that is designated as confidential or that reasonably should be understood to be confidential.

1.3 "Deliverables" means the work product, materials, and other items to be delivered by {provider} under this Agreement.

1.4 "Effective Date" means {effective_date}.

1.5 "Intellectual Property Rights" means all patents, copyrights, trademarks, trade secrets, and other intellectual property rights.

1.6 "Services" means the services to be provided by {provider} as described in this Agreement.

1.7 "Term" means the period during which this Agreement is in effect.
""",
    },
    "services": {
        "msa": """
2. SERVICES

2.1 Scope. {provider} shall provide the Services described in each Statement of Work ("SOW") executed by the parties. Each SOW shall reference this Agreement and shall be governed by its terms.

2.2 Performance. {provider} shall perform Services in a professional and workmanlike manner consistent with industry standards.

2.3 Personnel. {provider} shall assign qualified personnel to perform Services and may replace personnel with the prior consent of {customer}, which consent shall not be unreasonably withheld.

2.4 Changes. Either party may request changes to the scope of Services. Changes must be documented in a written change order signed by both parties.
""",
        "nda": """
2. PURPOSE

2.1 The parties wish to explore a potential business relationship concerning {purpose} (the "Purpose").

2.2 In connection with the Purpose, each party may disclose Confidential Information to the other.
""",
        "sla": """
2. SERVICE LEVELS

2.1 Availability. {provider} shall maintain {uptime_percentage}% availability for Production Services, measured monthly.

2.2 Response Times. {provider} shall respond to support requests according to the following schedule:
    - Critical (Service Down): {critical_response} hour(s)
    - High (Major Impact): {high_response} hours
    - Medium (Moderate Impact): {medium_response} hours
    - Low (Minor Issue): {low_response} business days

2.3 Exclusions. Service levels do not apply during scheduled maintenance or circumstances beyond {provider}'s reasonable control.
""",
    },
    "fees": {
        "standard": """
3. FEES AND PAYMENT

3.1 Fees. {customer} shall pay {provider} the fees set forth in each SOW or as otherwise agreed in writing.

3.2 Invoicing. {provider} shall invoice {customer} {invoice_frequency}. Invoices shall include reasonable detail of Services performed.

3.3 Payment Terms. Payment is due within {payment_days} days of invoice date.

3.4 Late Payment. Late payments shall accrue interest at the lesser of {interest_rate}% per month or the maximum rate permitted by law.

3.5 Taxes. Fees are exclusive of taxes. {customer} is responsible for all applicable taxes except taxes based on {provider}'s income.

3.6 Expenses. {customer} shall reimburse {provider} for reasonable, pre-approved expenses with receipts.
""",
    },
    "term_termination": {
        "standard": """
4. TERM AND TERMINATION

4.1 Term. This Agreement shall commence on the Effective Date and continue for {term_months} months (the "Initial Term"){renewal_clause}.

4.2 Termination for Cause. Either party may terminate this Agreement upon {cure_days} days written notice if the other party materially breaches this Agreement and fails to cure such breach within the notice period.

4.3 Termination for Convenience. Either party may terminate this Agreement for convenience upon {convenience_days} days written notice.

4.4 Effect of Termination. Upon termination: (a) all rights granted hereunder shall terminate; (b) {customer} shall pay all amounts due through the termination date; (c) each party shall return or destroy the other's Confidential Information.

4.5 Survival. Sections {survival_sections} shall survive termination.
""",
        "auto_renew": ", and shall automatically renew for successive {renewal_period} periods unless either party provides written notice of non-renewal at least {renewal_notice} days prior to the end of the then-current term",
        "no_renew": "",
    },
    "ip": {
        "customer_owns": """
5. INTELLECTUAL PROPERTY

5.1 Pre-Existing IP. Each party retains all rights in its pre-existing intellectual property.

5.2 Work Product. All Deliverables developed specifically for {customer} under this Agreement shall be owned by {customer} as work made for hire. To the extent any Deliverable does not qualify as work made for hire, {provider} hereby assigns all rights therein to {customer}.

5.3 Provider Tools. {provider} retains rights in its pre-existing tools, methodologies, and know-how. {provider} grants {customer} a perpetual, non-exclusive license to use any {provider} materials incorporated in the Deliverables.
""",
        "provider_owns": """
5. INTELLECTUAL PROPERTY

5.1 Ownership. All intellectual property rights in the Services and Deliverables, including all improvements and modifications, shall be owned exclusively by {provider}.

5.2 License. {provider} grants {customer} a non-exclusive, non-transferable license to use the Deliverables during the Term for {customer}'s internal business purposes.

5.3 No Other Rights. Except as expressly granted herein, {customer} obtains no rights in {provider}'s intellectual property.
""",
        "balanced": """
5. INTELLECTUAL PROPERTY

5.1 Pre-Existing IP. Each party retains all rights in its pre-existing intellectual property.

5.2 Customer-Specific Deliverables. Work product developed specifically for {customer} and paid for by {customer} shall be owned by {customer}.

5.3 Provider's General IP. {provider} retains rights in its tools, methodologies, and general-purpose components developed in connection with Services. Any such materials incorporated in Deliverables are licensed to {customer} for internal use.

5.4 Improvements. General improvements to {provider}'s methodology shall be owned by {provider}.
""",
    },
    "confidentiality": {
        "mutual": """
6. CONFIDENTIALITY

6.1 Definition. "Confidential Information" means all non-public information disclosed by one party to the other that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and circumstances of disclosure.

6.2 Exclusions. Confidential Information does not include information that: (a) is or becomes publicly available through no fault of the receiving party; (b) was rightfully in the receiving party's possession prior to disclosure; (c) is rightfully obtained from a third party without restriction; or (d) is independently developed without use of Confidential Information.

6.3 Obligations. The receiving party shall: (a) use the same degree of care to protect the disclosing party's Confidential Information as it uses to protect its own, but no less than reasonable care; (b) use Confidential Information only for purposes of this Agreement; (c) not disclose Confidential Information to third parties except to employees and contractors who need to know.

6.4 Required Disclosure. If required by law to disclose Confidential Information, the receiving party shall provide prompt notice to the disclosing party and cooperate in seeking protective treatment.

6.5 Term. Confidentiality obligations shall survive termination for {confidentiality_years} years.
""",
    },
    "warranties": {
        "balanced": """
7. WARRANTIES

7.1 Mutual Warranties. Each party represents and warrants that: (a) it has the authority to enter into this Agreement; (b) its performance will not violate any applicable laws; and (c) it will comply with all applicable laws in performing its obligations.

7.2 {provider_capitalized} Warranties. {provider} warrants that: (a) Services will be performed in a professional manner consistent with industry standards; (b) Deliverables will conform to specifications for {warranty_days} days following delivery; and (c) Deliverables will not infringe third-party intellectual property rights.

7.3 Disclaimer. EXCEPT AS EXPRESSLY SET FORTH HEREIN, NEITHER PARTY MAKES ANY OTHER WARRANTIES, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
""",
    },
    "indemnification": {
        "mutual": """
8. INDEMNIFICATION

8.1 By {provider}. {provider} shall indemnify, defend, and hold harmless {customer} from third-party claims arising from: (a) {provider}'s gross negligence or willful misconduct; (b) {provider}'s breach of this Agreement; or (c) infringement of intellectual property rights by the Deliverables.

8.2 By {customer}. {customer} shall indemnify, defend, and hold harmless {provider} from third-party claims arising from: (a) {customer}'s use of Deliverables in violation of this Agreement; (b) {customer}'s data or content; or (c) {customer}'s gross negligence or willful misconduct.

8.3 Procedure. The indemnified party shall: (a) provide prompt written notice of any claim; (b) allow the indemnifying party to control the defense; and (c) provide reasonable cooperation.

8.4 Sole Remedy. This Section states the indemnifying party's sole liability and the indemnified party's sole remedy for third-party claims.
""",
    },
    "limitation_of_liability": {
        "balanced": """
9. LIMITATION OF LIABILITY

9.1 Exclusion of Damages. EXCEPT FOR INDEMNIFICATION OBLIGATIONS, GROSS NEGLIGENCE, WILLFUL MISCONDUCT, OR BREACH OF CONFIDENTIALITY, NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOST PROFITS OR DATA.

9.2 Cap on Liability. EXCEPT FOR INDEMNIFICATION OBLIGATIONS, GROSS NEGLIGENCE, OR WILLFUL MISCONDUCT, NEITHER PARTY'S TOTAL LIABILITY SHALL EXCEED {liability_cap}.

9.3 Applicability. The limitations in this Section apply regardless of the theory of liability (contract, tort, or otherwise) and even if a party has been advised of the possibility of such damages.
""",
        "uncapped_carveouts": """
9. LIMITATION OF LIABILITY

9.1 Exclusion of Damages. NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOST PROFITS OR DATA.

9.2 Cap on Liability. EACH PARTY'S TOTAL LIABILITY SHALL NOT EXCEED {liability_cap}, EXCEPT THAT THIS CAP SHALL NOT APPLY TO: (a) INDEMNIFICATION OBLIGATIONS; (b) BREACH OF CONFIDENTIALITY; (c) GROSS NEGLIGENCE OR WILLFUL MISCONDUCT; OR (d) {customer}'S PAYMENT OBLIGATIONS.

9.3 Applicability. The limitations in this Section apply regardless of the theory of liability and even if advised of the possibility of such damages.
""",
    },
    "force_majeure": {
        "standard": """
10. FORCE MAJEURE

Neither party shall be liable for delays or failures in performance caused by circumstances beyond its reasonable control, including natural disasters, acts of war or terrorism, government actions, pandemic, epidemics, labor disputes, or internet or telecommunications failures. The affected party shall provide prompt notice and use reasonable efforts to mitigate the impact.
""",
    },
    "dispute_resolution": {
        "arbitration": """
11. DISPUTE RESOLUTION

11.1 Negotiation. The parties shall first attempt to resolve any dispute through good-faith negotiation between executives with authority to settle.

11.2 Mediation. If negotiation fails within thirty (30) days, the parties shall attempt mediation before a mutually agreed mediator.

11.3 Arbitration. If mediation fails, any dispute shall be resolved by final and binding arbitration in {arbitration_location} under {arbitration_rules} rules. The arbitrator's decision shall be enforceable in any court of competent jurisdiction.

11.4 Costs. Each party shall bear its own costs, and the parties shall share arbitration fees equally.
""",
        "litigation": """
11. DISPUTE RESOLUTION

11.1 Governing Law. This Agreement shall be governed by the laws of {governing_law_state}, without regard to conflict of laws principles.

11.2 Jurisdiction. The parties consent to exclusive jurisdiction and venue in the state and federal courts located in {court_location}.

11.3 Jury Waiver. THE PARTIES WAIVE THE RIGHT TO JURY TRIAL IN ANY PROCEEDING ARISING FROM THIS AGREEMENT.
""",
    },
    "general": {
        "standard": """
12. GENERAL PROVISIONS

12.1 Entire Agreement. This Agreement, including all SOWs and exhibits, constitutes the entire agreement and supersedes all prior agreements and understandings.

12.2 Amendments. Amendments must be in writing signed by authorized representatives of both parties.

12.3 Assignment. Neither party may assign this Agreement without prior written consent, except in connection with a merger, acquisition, or sale of all or substantially all of its assets.

12.4 Notices. Notices shall be in writing and deemed given when delivered by hand, overnight courier, or certified mail to the addresses set forth herein.

12.5 Severability. If any provision is held unenforceable, the remaining provisions shall continue in effect.

12.6 Waiver. Waiver of any breach shall not constitute waiver of subsequent breaches.

12.7 Independent Contractors. The parties are independent contractors. Nothing herein creates a partnership, joint venture, or agency relationship.

12.8 Counterparts. This Agreement may be executed in counterparts, each of which shall be deemed an original.
""",
    },
    "signature": {
        "standard": """
IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

{party_a_name_upper}

By: _________________________
Name: 
Title: 

{party_b_name_upper}

By: _________________________
Name: 
Title: 
"""
    },
}


class ContractGenerator:
    """
    AI-powered contract generation engine.
    Generates complete, jurisdiction-aware contracts from requirements.
    """
    
    def __init__(self):
        self.templates = CLAUSE_TEMPLATES
    
    def generate(self, request: GenerationRequest) -> GeneratedContract:
        """
        Generate a complete contract from requirements.
        """
        logger.info(f"Generating {request.contract_type} contract")
        
        import uuid
        contract_id = str(uuid.uuid4())[:8]
        
        # Build contract title
        title = self._generate_title(request)
        
        # Generate sections
        sections = self._generate_sections(request)
        
        # Assemble full text
        full_text = self._assemble_contract(request, sections)
        
        # Calculate risk score
        risk_score, warnings = self._assess_risk(request, full_text)
        
        return GeneratedContract(
            contract_id=contract_id,
            contract_type=request.contract_type,
            title=title,
            full_text=full_text,
            sections=sections,
            metadata={
                "jurisdiction": request.jurisdiction,
                "industry": request.industry,
                "style": request.style.value,
                "term_months": request.term_months,
                "parties": [request.party_a_name, request.party_b_name],
            },
            risk_score=risk_score,
            warnings=warnings,
            generated_at=datetime.utcnow().isoformat()
        )
    
    def _generate_title(self, req: GenerationRequest) -> str:
        """Generate contract title."""
        type_names = {
            "msa": "MASTER SERVICES AGREEMENT",
            "nda": "NON-DISCLOSURE AGREEMENT",
            "sla": "SERVICE LEVEL AGREEMENT",
            "license": "SOFTWARE LICENSE AGREEMENT",
            "employment": "EMPLOYMENT AGREEMENT",
            "consulting": "CONSULTING AGREEMENT",
            "vendor": "VENDOR AGREEMENT",
            "partnership": "PARTNERSHIP AGREEMENT",
        }
        return type_names.get(req.contract_type.lower(), "AGREEMENT")
    
    def _generate_sections(self, req: GenerationRequest) -> List[Dict[str, str]]:
        """Generate all sections for the contract."""
        sections = []
        
        # Substitution variables
        vars = {
            "party_a": req.party_a_name,
            "party_b": req.party_b_name,
            "party_a_name_upper": req.party_a_name.upper(),
            "party_b_name_upper": req.party_b_name.upper(),
            "provider": req.party_a_name if req.your_position == "seller" else req.party_b_name,
            "customer": req.party_b_name if req.your_position == "seller" else req.party_a_name,
            "provider_capitalized": (req.party_a_name if req.your_position == "seller" else req.party_b_name).split()[0],
            "effective_date": datetime.now().strftime("%B %d, %Y"),
            "party_a_business": req.industry + " services",
            "service_description": req.description,
            "term_months": str(req.term_months),
            "invoice_frequency": "monthly in arrears",
            "payment_days": "30",
            "interest_rate": "1.5",
            "cure_days": "30",
            "convenience_days": "90",
            "renewal_clause": self.templates["term_termination"]["auto_renew" if req.auto_renew else "no_renew"].format(
                renewal_period="one (1) year",
                renewal_notice="60"
            ),
            "renewal_period": "one (1) year",
            "renewal_notice": "60",
            "survival_sections": "5, 6, 8, 9, and 11",
            "confidentiality_years": "5",
            "warranty_days": "90",
            "liability_cap": f"the fees paid in the twelve (12) months preceding the claim" if req.liability_cap_multiplier == 1.0 else f"{req.liability_cap_multiplier}x the annual fees",
            "arbitration_location": self._get_arbitration_location(req.jurisdiction),
            "arbitration_rules": "AAA Commercial Arbitration" if req.jurisdiction == "US" else "ICC",
            "governing_law_state": self._get_governing_law(req.jurisdiction),
            "court_location": self._get_court_location(req.jurisdiction),
            "uptime_percentage": "99.9",
            "critical_response": "1",
            "high_response": "4",
            "medium_response": "8",
            "low_response": "2",
            "purpose": req.description,
        }
        
        # Build sections based on contract type
        section_order = self._get_section_order(req.contract_type)
        
        for section_name in section_order:
            if section_name in req.exclude_clauses:
                continue
            
            template = self._get_template(section_name, req)
            if template:
                rendered = template
                for key, value in vars.items():
                    rendered = rendered.replace("{" + key + "}", str(value))
                
                sections.append({
                    "name": section_name,
                    "content": rendered.strip()
                })
        
        return sections
    
    def _get_section_order(self, contract_type: str) -> List[str]:
        """Get section order for contract type."""
        base = ["recitals", "definitions", "services", "fees", "term_termination", 
                "ip", "confidentiality", "warranties", "indemnification", 
                "limitation_of_liability", "force_majeure", "dispute_resolution", 
                "general", "signature"]
        
        if contract_type.lower() == "nda":
            return ["recitals", "definitions", "services", "confidentiality", 
                    "term_termination", "general", "signature"]
        elif contract_type.lower() == "sla":
            return ["recitals", "services", "term_termination", "limitation_of_liability", 
                    "general", "signature"]
        
        return base
    
    def _get_template(self, section: str, req: GenerationRequest) -> Optional[str]:
        """Get appropriate template for section."""
        section_templates = self.templates.get(section, {})
        
        if not section_templates:
            return None
        
        # Choose variant based on style/type
        if section == "ip":
            if req.your_position == "buyer":
                return section_templates.get("customer_owns", section_templates.get("balanced"))
            elif req.your_position == "seller":
                return section_templates.get("provider_owns", section_templates.get("balanced"))
            return section_templates.get("balanced")
        
        if section == "services":
            return section_templates.get(req.contract_type.lower(), section_templates.get("msa"))
        
        if section == "limitation_of_liability":
            if req.style == ContractStyle.PROTECTIVE:
                return section_templates.get("uncapped_carveouts", section_templates.get("balanced"))
            return section_templates.get("balanced")
        
        if section == "dispute_resolution":
            if req.jurisdiction in ["US", "UK"]:
                return section_templates.get("litigation", section_templates.get("arbitration"))
            return section_templates.get("arbitration")
        
        return section_templates.get("standard") or section_templates.get("mutual") or section_templates.get("balanced")
    
    def _get_governing_law(self, jurisdiction: str) -> str:
        """Get governing law state/country."""
        laws = {
            "US": "the State of Delaware",
            "UK": "England and Wales",
            "EU": "the Netherlands",
            "GERMANY": "the Federal Republic of Germany",
            "SINGAPORE": "the Republic of Singapore",
        }
        return laws.get(jurisdiction, "the State of New York")
    
    def _get_arbitration_location(self, jurisdiction: str) -> str:
        """Get arbitration location."""
        locations = {
            "US": "New York, New York",
            "UK": "London, England",
            "EU": "Amsterdam, Netherlands",
            "GERMANY": "Frankfurt, Germany",
            "SINGAPORE": "Singapore",
        }
        return locations.get(jurisdiction, "New York, New York")
    
    def _get_court_location(self, jurisdiction: str) -> str:
        """Get court location."""
        return self._get_arbitration_location(jurisdiction)
    
    def _assemble_contract(self, req: GenerationRequest, sections: List[Dict]) -> str:
        """Assemble full contract text."""
        lines = []
        
        # Title
        lines.append(self._generate_title(req))
        lines.append("")
        lines.append(f"This {self._generate_title(req)} (\"Agreement\") is entered into as of {datetime.now().strftime('%B %d, %Y')} (\"Effective Date\") by and between:")
        lines.append("")
        lines.append(f"**{req.party_a_name}**, a {req.party_a_type} (\"{req.party_a_name.split()[0] if ' ' in req.party_a_name else 'Party A'}\"), and")
        lines.append("")
        lines.append(f"**{req.party_b_name}**, a {req.party_b_type} (\"{req.party_b_name.split()[0] if ' ' in req.party_b_name else 'Party B'}\").")
        lines.append("")
        
        # Sections
        for section in sections:
            lines.append(section["content"])
            lines.append("")
        
        return "\n".join(lines)
    
    def _assess_risk(self, req: GenerationRequest, text: str) -> tuple:
        """Assess risk of generated contract."""
        warnings = []
        risk = 25  # Base risk
        
        # Check for protective features
        if req.style == ContractStyle.AGGRESSIVE:
            risk += 15
            warnings.append("Aggressive terms may be difficult to negotiate")
        
        if req.liability_cap_multiplier < 1:
            risk += 10
            warnings.append("Low liability cap may not cover potential damages")
        
        if not req.auto_renew:
            warnings.append("No auto-renewal - ensure timely renewal tracking")
        
        # Check jurisdiction complexity
        if req.jurisdiction in ["EU", "GERMANY"]:
            warnings.append("EU/GDPR compliance requirements may apply")
        
        return min(risk, 50), warnings
    
    def generate_from_prompt(self, prompt: str) -> GeneratedContract:
        """Generate contract from natural language prompt."""
        # Parse the prompt to extract requirements
        request = self._parse_prompt(prompt)
        return self.generate(request)
    
    def _parse_prompt(self, prompt: str) -> GenerationRequest:
        """Parse natural language prompt into generation request."""
        prompt_lower = prompt.lower()
        
        # Detect contract type
        contract_type = "msa"
        type_patterns = {
            "nda": ["nda", "non-disclosure", "confidentiality agreement"],
            "msa": ["msa", "master service", "services agreement"],
            "sla": ["sla", "service level", "uptime"],
            "license": ["license", "software license", "saas"],
            "employment": ["employment", "hire", "employee"],
            "consulting": ["consulting", "consultant"],
            "vendor": ["vendor", "supplier", "procurement"],
            "partnership": ["partnership", "partner", "joint venture"],
        }
        
        for ct, patterns in type_patterns.items():
            if any(p in prompt_lower for p in patterns):
                contract_type = ct
                break
        
        # Detect jurisdiction
        jurisdiction = "US"
        jur_patterns = {
            "UK": ["uk", "united kingdom", "british", "english"],
            "EU": ["eu", "european", "gdpr"],
            "GERMANY": ["germany", "german"],
            "SINGAPORE": ["singapore", "singaporean"],
        }
        
        for jur, patterns in jur_patterns.items():
            if any(p in prompt_lower for p in patterns):
                jurisdiction = jur
                break
        
        # Detect position
        position = "neutral"
        if any(w in prompt_lower for w in ["we are selling", "we provide", "we offer", "as a vendor"]):
            position = "seller"
        elif any(w in prompt_lower for w in ["we are buying", "we need", "hiring", "engaging", "as a customer"]):
            position = "buyer"
        
        # Detect style
        style = ContractStyle.BALANCED
        if any(w in prompt_lower for w in ["aggressive", "favor us", "protect us strongly"]):
            style = ContractStyle.PROTECTIVE
        elif any(w in prompt_lower for w in ["fair", "balanced", "reasonable"]):
            style = ContractStyle.BALANCED
        
        return GenerationRequest(
            contract_type=contract_type,
            description=prompt,
            jurisdiction=jurisdiction,
            your_position=position,
            style=style,
        )


# Singleton
contract_generator = ContractGenerator()
