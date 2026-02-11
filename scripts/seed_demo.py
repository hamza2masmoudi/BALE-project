"""
BALE Demo Data Generator
Creates sample data for demonstration and testing.
"""
import uuid
import random
from datetime import datetime, timedelta
from typing import List
from api.analytics import analytics_engine
# Sample contract clauses for demonstration
SAMPLE_CLAUSES = [
{
"name": "Force Majeure",
"text": "Neither party shall be liable for any failure or delay in performance due to circumstances beyond its reasonable control, including acts of God, war, terrorism, or government actions.",
"risk": 45,
"jurisdiction": "UK"
},
{
"name": "Limitation of Liability", "text": "The Supplier's total liability under this Agreement shall not exceed the fees paid by the Customer in the twelve months preceding the claim.",
"risk": 62,
"jurisdiction": "US"
},
{
"name": "Indemnification",
"text": "The Licensor shall indemnify and hold harmless the Licensee from any claims arising from the Licensor's negligence or willful misconduct.",
"risk": 38,
"jurisdiction": "UK"
},
{
"name": "Termination for Convenience",
"text": "Either party may terminate this Agreement for any reason upon sixty (60) days prior written notice to the other party.",
"risk": 28,
"jurisdiction": "FRANCE"
},
{
"name": "Exclusion of Consequential Damages",
"text": "In no event shall either party be liable for any indirect, incidental, special, consequential, or punitive damages, including loss of profits.",
"risk": 78,
"jurisdiction": "US"
},
{
"name": "IP Assignment",
"text": "All intellectual property rights in work product created by Contractor shall vest in and be the sole property of the Company.",
"risk": 55,
"jurisdiction": "GERMANY"
},
{
"name": "Data Protection",
"text": "The Processor shall process personal data only in accordance with the Controller's documented instructions and applicable data protection law.",
"risk": 42,
"jurisdiction": "EU"
},
{
"name": "Non-Compete",
"text": "For a period of two years following termination, the Employee shall not engage in any business that competes with the Company.",
"risk": 71,
"jurisdiction": "US"
},
]
SAMPLE_CONTRACTS = [
{"name": "SaaS Master Agreement", "jurisdiction": "UK", "risk": 45, "clauses": 24},
{"name": "NDA - TechCorp", "jurisdiction": "US", "risk": 28, "clauses": 12},
{"name": "IP License Agreement", "jurisdiction": "FRANCE", "risk": 72, "clauses": 18},
{"name": "Employment Contract", "jurisdiction": "GERMANY", "risk": 35, "clauses": 32},
{"name": "Vendor Services Agreement", "jurisdiction": "UK", "risk": 51, "clauses": 28},
{"name": "Software License - Enterprise", "jurisdiction": "US", "risk": 44, "clauses": 21},
{"name": "Distribution Agreement", "jurisdiction": "EU", "risk": 58, "clauses": 26},
{"name": "Consulting Services MSA", "jurisdiction": "UK", "risk": 33, "clauses": 19},
]
def generate_demo_analytics(days: int = 30, analyses_per_day: int = 10):
"""
Generate demo analytics data.
Args:
days: Number of days of history to generate
analyses_per_day: Average analyses per day
"""
now = datetime.utcnow()
jurisdictions = ["UK", "US", "FRANCE", "GERMANY", "EU", "SINGAPORE"]
verdicts = ["PLAINTIFF_FAVOR", "DEFENSE_FAVOR", "AMBIGUOUS"]
for day_offset in range(days):
date = now - timedelta(days=day_offset)
num_analyses = random.randint(
max(1, analyses_per_day - 5),
analyses_per_day + 5
)
for _ in range(num_analyses):
# Vary risk by jurisdiction
jurisdiction = random.choice(jurisdictions)
base_risk = {
"UK": 40,
"US": 55,
"FRANCE": 45,
"GERMANY": 35,
"EU": 42,
"SINGAPORE": 38
}.get(jurisdiction, 45)
risk = max(10, min(95, base_risk + random.randint(-20, 25)))
if risk > 60:
verdict = "PLAINTIFF_FAVOR"
elif risk < 40:
verdict = "DEFENSE_FAVOR"
else:
verdict = random.choice(verdicts)
analytics_engine.record_analysis(
analysis_id=str(uuid.uuid4()),
user_id=f"user_{random.randint(1, 20)}",
jurisdiction=jurisdiction,
risk_score=risk,
verdict=verdict,
processing_time_ms=random.randint(800, 3500),
timestamp=date + timedelta(hours=random.randint(0, 23))
)
print(f" Generated {days * analyses_per_day} demo analyses")
def seed_demo_data():
"""Seed all demo data."""
print("\n Seeding BALE demo data...\n")
# Generate analytics
generate_demo_analytics(days=30, analyses_per_day=12)
print("\n Demo data seeding complete!\n")
if __name__ == "__main__":
seed_demo_data()
