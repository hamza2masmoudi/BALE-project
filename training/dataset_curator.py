"""
BALE Legal Dataset Curator
Tools for creating and managing fine-tuning datasets.
"""
import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from src.logger import setup_logger

logger = setup_logger("bale_dataset")


@dataclass
class TrainingPair:
    """A single training example for fine-tuning."""
    id: str
    instruction: str
    input: str
    output: str
    
    # Metadata
    task_type: str  # interpretation, risk_assessment, harmonization, simulation
    domain: str  # commercial, ip, employment, real_estate
    jurisdiction: str  # FRANCE, UK, US, INTERNATIONAL
    difficulty: str  # easy, medium, hard
    
    # Quality
    source: str  # synthetic, expert, case_law
    is_validated: bool = False
    quality_score: Optional[float] = None
    
    def to_alpaca_format(self) -> Dict[str, str]:
        """Export to Alpaca/Stanford format."""
        return {
            "instruction": self.instruction,
            "input": self.input,
            "output": self.output
        }
    
    def to_chatml_format(self) -> List[Dict[str, str]]:
        """Export to ChatML/OpenAI format."""
        return [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": self.input},
            {"role": "assistant", "content": self.output}
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DatasetCurator:
    """
    Main tool for creating and managing legal fine-tuning datasets.
    """
    
    # Instruction templates for different task types
    INSTRUCTIONS = {
        "interpretation": """You are a legal expert analyzing contract clauses. 
Interpret the following clause from both Civil Law (French Code Civil) and Common Law (English Law) perspectives.
Identify any ambiguities, risks, or areas of legal conflict.""",

        "risk_assessment": """You are BALE, a legal risk assessment engine.
Analyze the following clause and provide:
1. Risk Score (0-100)
2. Key risk factors (as Boolean true/false)
3. Brief explanation of risks
Output as JSON.""",

        "harmonization": """You are an international legal drafting expert.
Given the following problematic clause, draft an improved 'Golden Clause' that:
1. Reduces litigation risk
2. Balances Civil Law and Common Law requirements
3. Maintains commercial intent
Provide the new clause and rationale.""",

        "simulation": """You are simulating a legal argument.
Role: {role}
Your goal: {goal}
Draft a persuasive legal argument based on the following context.""",

        "factor_extraction": """You are a judicial clerk extracting legal factors.
Analyze the following legal arguments and extract Boolean decision factors:
- is_ambiguous: Is the clause ambiguous?
- is_exclusion_clear: Is any exclusion clause valid?
- authority_is_mandatory: Does mandatory law apply?
- plaintiff_plausible: Is the plaintiff's claim plausible?
Respond with JSON only."""
    }
    
    # Clause templates for synthetic generation
    CLAUSE_TEMPLATES = {
        "liability_exclusion": [
            "The Supplier shall not be liable for any {damage_type} damages arising from {event}.",
            "Under no circumstances shall {party} be responsible for {damage_type} losses, including {examples}.",
            "Notwithstanding any other provision, liability is limited to {amount} except in cases of {exception}."
        ],
        "force_majeure": [
            "Neither party shall be liable for failure to perform due to {fm_events}.",
            "In the event of Force Majeure, defined as {definition}, obligations shall be suspended for {period}.",
            "This Agreement may be terminated if Force Majeure continues for more than {days} days."
        ],
        "termination": [
            "Either party may terminate this Agreement upon {notice_period} written notice.",
            "This Agreement shall automatically renew unless terminated {termination_window} prior to expiration.",
            "{party} may terminate immediately upon material breach by the other party."
        ],
        "intellectual_property": [
            "All IP created under this Agreement shall belong to {ip_owner}.",
            "{party} grants a {license_type} license to use the following IP: {ip_description}.",
            "Moral rights are {waived_status} to the extent permitted by applicable law."
        ],
        "confidentiality": [
            "Confidential Information shall be protected for {period} following termination.",
            "The receiving party shall use Confidential Information solely for {purpose}.",
            "Exceptions to confidentiality include: {exceptions}."
        ]
    }
    
    # Defect injection patterns
    DEFECTS = {
        "ambiguity": [
            ("damages", "losses or other impacts"),
            ("immediately", "promptly"),
            ("best efforts", "reasonable endeavors"),
            ("material breach", "significant non-compliance"),
            ("written notice", "notification")
        ],
        "missing_definition": [
            "Force Majeure", "Confidential Information", "Material Breach",
            "Affiliate", "Change of Control"
        ],
        "conflict_with_law": [
            ("waive all liability", "void under Art. 1170 CC"),
            ("exclude consequential damages", "may conflict with consumer protection"),
            ("limit liability to €100", "may be unenforceable if grossly negligent")
        ]
    }
    
    def __init__(self, output_dir: str = "training/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.examples: List[TrainingPair] = []
    
    def _generate_id(self, content: str) -> str:
        """Generate deterministic ID from content."""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def generate_interpretation_pair(
        self,
        clause_type: str = "liability_exclusion",
        inject_defect: bool = True
    ) -> TrainingPair:
        """Generate a clause interpretation training pair."""
        # Select random template
        templates = self.CLAUSE_TEMPLATES.get(clause_type, self.CLAUSE_TEMPLATES["liability_exclusion"])
        template = random.choice(templates)
        
        # Fill template
        clause = template.format(
            damage_type=random.choice(["indirect", "consequential", "incidental", "special"]),
            event=random.choice(["this Agreement", "the Services", "Product use", "any breach"]),
            party=random.choice(["Supplier", "Provider", "Contractor", "Seller"]),
            examples=random.choice(["lost profits, data loss, or business interruption", "punitive damages or penalties"]),
            amount=random.choice(["€10,000", "the fees paid", "direct damages only", "12 months of fees"]),
            exception=random.choice(["gross negligence", "willful misconduct", "fraud", "death or personal injury"]),
            fm_events=random.choice(["acts of God, war, or government action", "events beyond reasonable control"]),
            definition=random.choice(["circumstances beyond reasonable control", "unforeseeable events"]),
            period=random.choice(["the duration of such event", "a reasonable period", "up to 90 days"]),
            days=random.choice(["30", "60", "90", "180"]),
            notice_period=random.choice(["30 days", "60 days", "90 days", "written"]),
            termination_window=random.choice(["30 days", "60 days", "90 days"]),
            ip_owner=random.choice(["Client", "Provider", "jointly to both parties"]),
            license_type=random.choice(["non-exclusive", "exclusive", "worldwide", "perpetual"]),
            ip_description=random.choice(["the Software", "all deliverables", "background IP"]),
            waived_status=random.choice(["hereby waived", "preserved", "waived to the maximum extent"]),
            purpose=random.choice(["the purposes of this Agreement", "internal business use", "evaluating the Services"])
        )
        
        # Inject defect if requested
        if inject_defect:
            defect_type = random.choice(["ambiguity", "missing_definition"])
            if defect_type == "ambiguity":
                old, new = random.choice(self.DEFECTS["ambiguity"])
                clause = clause.replace(old, new) if old in clause.lower() else clause
        
        # Generate expected output
        jurisdiction = random.choice(["FRANCE", "UK", "INTERNATIONAL"])
        difficulty = "medium" if inject_defect else "easy"
        
        civil_analysis = self._generate_civil_analysis(clause, clause_type)
        common_analysis = self._generate_common_analysis(clause, clause_type)
        
        output = f"""## Civil Law Analysis (French Code Civil)
{civil_analysis}

## Common Law Analysis (English Law)
{common_analysis}

## Key Conflicts
- Interpretation of liability limitations differs between systems
- Good faith requirements (Art. 1104 CC) may override exclusion clauses
- Enforceability depends on jurisdictional rules
"""
        
        pair_id = self._generate_id(clause)
        
        return TrainingPair(
            id=pair_id,
            instruction=self.INSTRUCTIONS["interpretation"],
            input=f"Clause:\n{clause}",
            output=output,
            task_type="interpretation",
            domain=clause_type.replace("_", " "),
            jurisdiction=jurisdiction,
            difficulty=difficulty,
            source="synthetic"
        )
    
    def generate_risk_assessment_pair(self, clause: str = None) -> TrainingPair:
        """Generate a risk assessment training pair."""
        if clause is None:
            # Generate a clause
            interp_pair = self.generate_interpretation_pair()
            clause = interp_pair.input.replace("Clause:\n", "")
        
        # Randomly assign risk factors (for training diversity)
        is_ambiguous = random.choice([True, True, False])  # Bias toward ambiguous
        is_exclusion_clear = random.choice([True, False])
        authority_is_mandatory = random.choice([True, False, False])  # Less common
        plaintiff_plausible = random.choice([True, True, False])  # Usually plausible
        
        # Calculate risk based on factors
        risk = 50
        if is_ambiguous: risk += 20
        if not is_exclusion_clear: risk += 15
        if authority_is_mandatory: risk += 20
        if plaintiff_plausible: risk += 10
        else: risk -= 20
        risk = max(0, min(100, risk))
        
        output = json.dumps({
            "risk_score": risk,
            "verdict": "PLAINTIFF_FAVOR" if risk > 50 else "DEFENSE_FAVOR",
            "factors": {
                "is_ambiguous": is_ambiguous,
                "is_exclusion_clear": is_exclusion_clear,
                "authority_is_mandatory": authority_is_mandatory,
                "plaintiff_plausible": plaintiff_plausible
            },
            "explanation": self._generate_risk_explanation(risk, is_ambiguous, is_exclusion_clear)
        }, indent=2)
        
        return TrainingPair(
            id=self._generate_id(clause + "risk"),
            instruction=self.INSTRUCTIONS["risk_assessment"],
            input=clause,
            output=output,
            task_type="risk_assessment",
            domain="commercial",
            jurisdiction="INTERNATIONAL",
            difficulty="medium",
            source="synthetic"
        )
    
    def generate_harmonization_pair(self, clause: str = None, risk: int = 65) -> TrainingPair:
        """Generate a harmonization training pair."""
        if clause is None:
            interp_pair = self.generate_interpretation_pair(inject_defect=True)
            clause = interp_pair.input.replace("Clause:\n", "")
        
        # Generate improved clause
        golden_clause = self._generate_golden_clause(clause)
        
        output = f"""## Golden Clause (Improved)
{golden_clause}

## Rationale
- Added explicit definitions to reduce ambiguity
- Balanced Civil Law good faith requirements with Common Law freedom of contract
- Maintained commercial intent while reducing litigation exposure
- Estimated risk reduction: {max(10, risk - 35)}%
"""
        
        return TrainingPair(
            id=self._generate_id(clause + "harm"),
            instruction=self.INSTRUCTIONS["harmonization"],
            input=f"Problematic Clause:\n{clause}\n\nCurrent Risk Score: {risk}%",
            output=output,
            task_type="harmonization",
            domain="commercial",
            jurisdiction="INTERNATIONAL",
            difficulty="hard",
            source="synthetic"
        )
    
    def _generate_civil_analysis(self, clause: str, clause_type: str) -> str:
        """Generate Civil Law analysis (simplified for training)."""
        analyses = {
            "liability_exclusion": """Under French law, this clause faces scrutiny under Articles 1170 and 1231-3 of the Code Civil. Exclusion of liability for gross negligence (faute lourde) would be void. The clause must be interpreted in light of the obligation of good faith (Art. 1104). If drafted by the stronger party (e.g., supplier), contra proferentem applies.""",
            "force_majeure": """Article 1218 CC defines force majeure strictly: the event must be unforeseeable, irresistible, and external. Courts may refuse to recognize contractual definitions that are broader than the statutory standard. The clause should align with recent Cour de Cassation jurisprudence on commercial impossibility.""",
            "intellectual_property": """French law recognizes strong moral rights (droit moral) under the Intellectual Property Code (Art. L121-1). Any waiver of moral rights by the author is void under French law, even if contractually agreed. This creates a fundamental conflict with common law approaches."""
        }
        return analyses.get(clause_type, analyses["liability_exclusion"])
    
    def _generate_common_analysis(self, clause: str, clause_type: str) -> str:
        """Generate Common Law analysis (simplified for training)."""
        analyses = {
            "liability_exclusion": """Under English law, this clause would be tested against the Unfair Contract Terms Act 1977 (UCTA) for reasonableness. Photo Production Ltd v Securicor establishes that exclusion clauses are valid if clearly drafted, but strict construction applies. The clause must be unambiguous to exclude liability for negligence.""",
            "force_majeure": """Common law does not recognize force majeure as a standalone doctrine. The clause operates purely as a matter of contract. Courts will interpret force majeure clauses strictly (Metropolitan Water Board v Dick Kerr). Mere economic hardship is insufficient; physical impossibility or illegality is typically required.""",
            "intellectual_property": """English law allows broader waivers of moral rights under the CDPA 1988. Work-for-hire doctrines favor the commissioning party. This creates tension with civil law systems where moral rights are inalienable. The clause should specify applicable IP law to reduce conflict."""
        }
        return analyses.get(clause_type, analyses["liability_exclusion"])
    
    def _generate_risk_explanation(self, risk: int, is_ambiguous: bool, is_exclusion_clear: bool) -> str:
        """Generate explanation for risk score."""
        parts = []
        if risk > 70:
            parts.append("High risk due to multiple defects.")
        elif risk > 50:
            parts.append("Moderate risk favoring plaintiff.")
        else:
            parts.append("Lower risk, defense-favorable position.")
        
        if is_ambiguous:
            parts.append("Contra proferentem likely applies due to ambiguous language.")
        if not is_exclusion_clear:
            parts.append("Exclusion clause lacks required clarity for enforcement.")
        
        return " ".join(parts)
    
    def _generate_golden_clause(self, problematic_clause: str) -> str:
        """Generate an improved version of a problematic clause."""
        # Simple improvement patterns
        if "shall not be liable" in problematic_clause.lower():
            return """To the maximum extent permitted by applicable law, and except for liability arising from (a) gross negligence or willful misconduct, (b) death or personal injury caused by negligence, or (c) fraud, neither party shall be liable to the other for any indirect, incidental, special, or consequential damages. This limitation shall not apply where void under mandatory law. The total aggregate liability of either party shall not exceed the fees paid under this Agreement in the twelve (12) months preceding the claim."""
        
        return """[IMPROVED CLAUSE: All defined terms are explicitly stated. Liability limitations exclude cases of gross negligence, fraud, and personal injury. Good faith obligations are acknowledged. Dispute resolution mechanism specified.]"""
    
    def generate_batch(
        self,
        count: int = 100,
        task_types: List[str] = None
    ) -> List[TrainingPair]:
        """Generate a batch of training pairs."""
        task_types = task_types or ["interpretation", "risk_assessment", "harmonization"]
        clause_types = list(self.CLAUSE_TEMPLATES.keys())
        
        pairs = []
        for i in range(count):
            task = random.choice(task_types)
            clause_type = random.choice(clause_types)
            
            if task == "interpretation":
                pair = self.generate_interpretation_pair(clause_type)
            elif task == "risk_assessment":
                pair = self.generate_risk_assessment_pair()
            elif task == "harmonization":
                pair = self.generate_harmonization_pair()
            else:
                pair = self.generate_interpretation_pair(clause_type)
            
            pairs.append(pair)
            
            if (i + 1) % 100 == 0:
                logger.info(f"Generated {i + 1}/{count} pairs")
        
        self.examples.extend(pairs)
        return pairs
    
    def export_to_jsonl(self, filepath: str = None, format: str = "alpaca") -> str:
        """Export dataset to JSONL file."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.output_dir / f"bale_training_{format}_{timestamp}.jsonl"
        
        filepath = Path(filepath)
        
        with open(filepath, "w") as f:
            for pair in self.examples:
                if format == "alpaca":
                    data = pair.to_alpaca_format()
                elif format == "chatml":
                    data = {"messages": pair.to_chatml_format()}
                else:
                    data = pair.to_dict()
                
                f.write(json.dumps(data) + "\n")
        
        logger.info(f"Exported {len(self.examples)} pairs to {filepath}")
        return str(filepath)
    
    def export_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        task_counts = {}
        domain_counts = {}
        difficulty_counts = {}
        
        for pair in self.examples:
            task_counts[pair.task_type] = task_counts.get(pair.task_type, 0) + 1
            domain_counts[pair.domain] = domain_counts.get(pair.domain, 0) + 1
            difficulty_counts[pair.difficulty] = difficulty_counts.get(pair.difficulty, 0) + 1
        
        return {
            "total": len(self.examples),
            "by_task": task_counts,
            "by_domain": domain_counts,
            "by_difficulty": difficulty_counts,
            "validated": sum(1 for p in self.examples if p.is_validated)
        }


# ==================== CLI ENTRY POINT ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="BALE Dataset Curator")
    parser.add_argument("--count", type=int, default=1000, help="Number of examples to generate")
    parser.add_argument("--format", choices=["alpaca", "chatml", "full"], default="alpaca")
    parser.add_argument("--output", type=str, default=None)
    
    args = parser.parse_args()
    
    curator = DatasetCurator()
    curator.generate_batch(count=args.count)
    
    output_path = curator.export_to_jsonl(filepath=args.output, format=args.format)
    
    stats = curator.export_stats()
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total: {stats['total']}")
    print(f"   By Task: {stats['by_task']}")
    print(f"   Output: {output_path}")
