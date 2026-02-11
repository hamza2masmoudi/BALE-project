"""
Force Majeure Logic Model (Article 1218 Civil Code)
Formalizes the 3 conditions of Force Majeure:
1. Exteriority (External to the debtor)
2. Unforeseeability (Could not be predicted at contract formation)
3. Irresistibility (Could not be avoided)
"""
from src.logic.engine import Rule
def get_force_majeure_rules() -> list[Rule]:
rules = []
# Rule 1: Valid Force Majeure requires all 3 conditions
rules.append(Rule(
name="Valid Force Majeure Definition",
conditions=[
{"name": "is_external", "value": True},
{"name": "is_unforeseeable", "value": True},
{"name": "is_irresistible", "value": True}
],
conclusion={"name": "is_valid_force_majeure", "value": True}
))
# Rule 2: Economic hardship is NEVER Force Majeure (Classic case law distinction)
rules.append(Rule(
name="Economic Hardship Exclusion",
conditions=[
{"name": "is_economic_change", "value": True}
],
conclusion={"name": "is_irresistible", "value": False}
))
# Rule 3: Strikes are only FM if they are general (not internal)
rules.append(Rule(
name="Internal Strike Exclusion",
conditions=[
{"name": "is_strike", "value": True},
{"name": "is_internal_dispute", "value": True}
],
conclusion={"name": "is_external", "value": False}
))
# Rule 4: Pandemics are foreseeable if contract signed after 2020
rules.append(Rule(
name="Covid Predictability",
conditions=[
{"name": "is_pandemic", "value": True},
{"name": "contract_date_post_2020", "value": True}
],
conclusion={"name": "is_unforeseeable", "value": False}
))
return rules
