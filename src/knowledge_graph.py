"""
BALE Knowledge Graph
Neo4j integration for legal precedent tracking and citation analysis.
"""
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from src.logger import setup_logger
from src.jurisdiction import Jurisdiction
logger = setup_logger("bale_knowledge_graph")
# ==================== DATA MODELS ====================
class RelationType(str, Enum):
"""Types of relationships in the legal knowledge graph."""
CITES = "CITES" # Case A cites Case B
OVERRULES = "OVERRULES" # Case A overrules Case B
DISTINGUISHES = "DISTINGUISHES" # Case A distinguishes Case B
FOLLOWS = "FOLLOWS" # Case A follows Case B
APPLIES = "APPLIES" # Case applies Statute
INTERPRETS = "INTERPRETS" # Case interprets Statute
AMENDS = "AMENDS" # Statute A amends Statute B
IMPLEMENTS = "IMPLEMENTS" # National law implements EU directive
EQUIVALENT_TO = "EQUIVALENT_TO" # Cross-jurisdiction equivalence
class NodeType(str, Enum):
"""Types of nodes in the legal knowledge graph."""
STATUTE = "STATUTE" # Legislative act
REGULATION = "REGULATION" # Executive regulation
CASE = "CASE" # Court decision
ARTICLE = "ARTICLE" # Individual article of statute
PRINCIPLE = "PRINCIPLE" # Legal doctrine/principle
CLAUSE_TYPE = "CLAUSE_TYPE" # Contract clause category
@dataclass
class LegalGraphNode:
"""Node in the legal knowledge graph."""
id: str
node_type: NodeType
name: str
jurisdiction: Jurisdiction
# Content
full_text: Optional[str] = None
summary: Optional[str] = None
# Authority
authority_level: int = 50 # 0-100
is_current: bool = True # False if overruled/repealed
# Dates
effective_date: Optional[datetime] = None
end_date: Optional[datetime] = None
# Metadata
citation: Optional[str] = None
court: Optional[str] = None
metadata: Optional[Dict[str, Any]] = None
@dataclass
class LegalGraphEdge:
"""Edge (relationship) in the legal knowledge graph."""
source_id: str
target_id: str
relation_type: RelationType
# Details
paragraph: Optional[str] = None # Specific paragraph of citation
confidence: float = 1.0
extracted_by: str = "manual" # manual, llm, parser
# Date
created_at: datetime = None
# ==================== NEO4J CLIENT ====================
class KnowledgeGraphClient:
"""
Neo4j client for the legal knowledge graph.
Handles connection, queries, and graph operations.
"""
def __init__(self, uri: str = None, user: str = None, password: str = None):
"""
Initialize Neo4j connection.
Falls back to environment variables if not provided.
"""
self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
self.user = user or os.getenv("NEO4J_USER", "neo4j")
self.password = password or os.getenv("NEO4J_PASSWORD", "bale_dev")
self.driver = None
self._connected = False
def connect(self) -> bool:
"""Establish connection to Neo4j."""
try:
from neo4j import GraphDatabase
self.driver = GraphDatabase.driver(
self.uri, auth=(self.user, self.password)
)
self.driver.verify_connectivity()
self._connected = True
logger.info(f"Connected to Neo4j at {self.uri}")
return True
except ImportError:
logger.warning("neo4j package not installed. Knowledge graph features disabled.")
return False
except Exception as e:
logger.error(f"Failed to connect to Neo4j: {e}")
return False
def close(self):
"""Close the connection."""
if self.driver:
self.driver.close()
self._connected = False
@property
def is_connected(self) -> bool:
return self._connected
# ==================== WRITE OPERATIONS ====================
def create_node(self, node: LegalGraphNode) -> bool:
"""Create or merge a node in the graph."""
if not self._connected:
return False
query = """
MERGE (n:{node_type} {{id: $id}})
SET n.name = $name,
n.jurisdiction = $jurisdiction,
n.authority_level = $authority_level,
n.is_current = $is_current,
n.citation = $citation,
n.summary = $summary,
n.updated_at = datetime()
RETURN n
""".format(node_type=node.node_type.value)
try:
with self.driver.session() as session:
session.run(query, {
"id": node.id,
"name": node.name,
"jurisdiction": node.jurisdiction.value,
"authority_level": node.authority_level,
"is_current": node.is_current,
"citation": node.citation,
"summary": node.summary
})
return True
except Exception as e:
logger.error(f"Failed to create node: {e}")
return False
def create_relationship(self, edge: LegalGraphEdge) -> bool:
"""Create a relationship between nodes."""
if not self._connected:
return False
query = """
MATCH (a {{id: $source_id}})
MATCH (b {{id: $target_id}})
MERGE (a)-[r:{rel_type}]->(b)
SET r.confidence = $confidence,
r.paragraph = $paragraph,
r.extracted_by = $extracted_by,
r.created_at = datetime()
RETURN r
""".format(rel_type=edge.relation_type.value)
try:
with self.driver.session() as session:
session.run(query, {
"source_id": edge.source_id,
"target_id": edge.target_id,
"confidence": edge.confidence,
"paragraph": edge.paragraph,
"extracted_by": edge.extracted_by
})
return True
except Exception as e:
logger.error(f"Failed to create relationship: {e}")
return False
# ==================== READ OPERATIONS ====================
def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
"""Get a node by ID."""
if not self._connected:
return None
query = """
MATCH (n {id: $id})
RETURN n
"""
try:
with self.driver.session() as session:
result = session.run(query, {"id": node_id})
record = result.single()
if record:
return dict(record["n"])
except Exception as e:
logger.error(f"Failed to get node: {e}")
return None
def find_citations(self, node_id: str, depth: int = 2) -> List[Dict[str, Any]]:
"""
Find all citations from/to a node up to given depth.
Returns citation chain for precedent analysis.
"""
if not self._connected:
return []
query = """
MATCH path = (source {id: $id})-[r:CITES|FOLLOWS|APPLIES*1..{depth}]->(target)
RETURN [n in nodes(path) | {id: n.id, name: n.name, type: labels(n)[0]}] as chain,
[rel in relationships(path) | type(rel)] as relations
LIMIT 50
""".format(depth=depth)
try:
with self.driver.session() as session:
result = session.run(query, {"id": node_id})
chains = []
for record in result:
chains.append({
"chain": record["chain"],
"relations": record["relations"]
})
return chains
except Exception as e:
logger.error(f"Failed to find citations: {e}")
return []
def check_overruled(self, node_id: str) -> Tuple[bool, Optional[str]]:
"""
Check if a case/statute has been overruled.
Returns (is_overruled, overruling_case_id).
"""
if not self._connected:
return (False, None)
query = """
MATCH (n {id: $id})<-[:OVERRULES]-(overruling)
RETURN overruling.id as overruling_id, overruling.name as overruling_name
LIMIT 1
"""
try:
with self.driver.session() as session:
result = session.run(query, {"id": node_id})
record = result.single()
if record:
return (True, record["overruling_id"])
except Exception as e:
logger.error(f"Failed to check overruled: {e}")
return (False, None)
def find_equivalent(
self, node_id: str, target_jurisdiction: Jurisdiction
) -> Optional[Dict[str, Any]]:
"""
Find equivalent legal concept in another jurisdiction.
E.g., Art. 1104 CC (FR) ≈ Good Faith duty (UK).
"""
if not self._connected:
return None
query = """
MATCH (source {id: $id})-[:EQUIVALENT_TO]-(target)
WHERE target.jurisdiction = $jurisdiction
RETURN target
LIMIT 1
"""
try:
with self.driver.session() as session:
result = session.run(query, {
"id": node_id,
"jurisdiction": target_jurisdiction.value
})
record = result.single()
if record:
return dict(record["target"])
except Exception as e:
logger.error(f"Failed to find equivalent: {e}")
return None
def get_precedent_strength(self, node_id: str) -> Dict[str, Any]:
"""
Calculate the strength of a precedent based on citation network.
More citations + followed = stronger precedent.
"""
if not self._connected:
return {"strength": 0, "details": "Graph not connected"}
query = """
MATCH (n {id: $id})
OPTIONAL MATCH (n)<-[:CITES]-(citing)
OPTIONAL MATCH (n)<-[:FOLLOWS]-(following)
OPTIONAL MATCH (n)<-[:OVERRULES]-(overruling)
RETURN n.authority_level as base_authority,
count(DISTINCT citing) as citation_count,
count(DISTINCT following) as follows_count,
count(DISTINCT overruling) as overruled_count
"""
try:
with self.driver.session() as session:
result = session.run(query, {"id": node_id})
record = result.single()
if record:
base = record["base_authority"] or 50
citations = record["citation_count"] or 0
follows = record["follows_count"] or 0
overruled = record["overruled_count"] or 0
# Calculate strength
if overruled > 0:
strength = 10 # Overruled cases have minimal strength
else:
strength = min(100, base + (citations * 2) + (follows * 5))
return {
"strength": strength,
"base_authority": base,
"citation_count": citations,
"follows_count": follows,
"is_overruled": overruled > 0
}
except Exception as e:
logger.error(f"Failed to get precedent strength: {e}")
return {"strength": 0, "details": "Error calculating strength"}
# ==================== ANALYTICS ====================
def get_jurisdiction_stats(self, jurisdiction: Jurisdiction) -> Dict[str, int]:
"""Get statistics for a jurisdiction."""
if not self._connected:
return {}
query = """
MATCH (n {jurisdiction: $jurisdiction})
RETURN labels(n)[0] as type, count(*) as count
"""
try:
with self.driver.session() as session:
result = session.run(query, {"jurisdiction": jurisdiction.value})
stats = {}
for record in result:
stats[record["type"]] = record["count"]
return stats
except Exception as e:
logger.error(f"Failed to get stats: {e}")
return {}
# ==================== INITIALIZATION ====================
def initialize_schema(self):
"""Create indexes and constraints."""
if not self._connected:
return
queries = [
"CREATE INDEX IF NOT EXISTS FOR (n:STATUTE) ON (n.id)",
"CREATE INDEX IF NOT EXISTS FOR (n:CASE) ON (n.id)",
"CREATE INDEX IF NOT EXISTS FOR (n:ARTICLE) ON (n.id)",
"CREATE INDEX IF NOT EXISTS FOR (n:PRINCIPLE) ON (n.id)",
"CREATE INDEX IF NOT EXISTS FOR (n:STATUTE) ON (n.jurisdiction)",
"CREATE INDEX IF NOT EXISTS FOR (n:CASE) ON (n.jurisdiction)",
]
try:
with self.driver.session() as session:
for query in queries:
session.run(query)
logger.info("Schema initialized")
except Exception as e:
logger.error(f"Failed to initialize schema: {e}")
def seed_foundational_data(self):
"""Seed basic legal nodes for common reference."""
foundational_nodes = [
# French Civil Code
LegalGraphNode(
id="fr_cc_1104",
node_type=NodeType.ARTICLE,
name="Article 1104 - Good Faith",
jurisdiction=Jurisdiction.FRANCE,
authority_level=90,
citation="Art. 1104 C. civ.",
summary="Contracts must be negotiated, formed and performed in good faith (Bonne Foi)."
),
LegalGraphNode(
id="fr_cc_1170",
node_type=NodeType.ARTICLE,
name="Article 1170 - Void Exclusions",
jurisdiction=Jurisdiction.FRANCE,
authority_level=90,
citation="Art. 1170 C. civ.",
summary="Any clause depriving the essential obligation of its substance is deemed unwritten."
),
# UK UCTA
LegalGraphNode(
id="uk_ucta_1977",
node_type=NodeType.STATUTE,
name="Unfair Contract Terms Act 1977",
jurisdiction=Jurisdiction.UK,
authority_level=90,
citation="UCTA 1977",
summary="Controls exclusion clauses; requires reasonableness test for B2B."
),
# US UCC
LegalGraphNode(
id="us_ucc_2_302",
node_type=NodeType.ARTICLE,
name="UCC § 2-302 - Unconscionability",
jurisdiction=Jurisdiction.US,
authority_level=85,
citation="UCC § 2-302",
summary="Court may refuse to enforce unconscionable contract or clause."
),
# German BGB
LegalGraphNode(
id="de_bgb_242",
node_type=NodeType.ARTICLE,
name="§ 242 BGB - Treu und Glauben",
jurisdiction=Jurisdiction.GERMANY,
authority_level=90,
citation="§ 242 BGB",
summary="Obligor must perform in accordance with good faith (Treu und Glauben)."
),
# EU GDPR
LegalGraphNode(
id="eu_gdpr_82",
node_type=NodeType.ARTICLE,
name="Article 82 GDPR - Right to Compensation",
jurisdiction=Jurisdiction.EU,
authority_level=95,
citation="Art. 82 GDPR",
summary="Any person who has suffered damage due to infringement has right to compensation."
),
]
# Cross-jurisdiction equivalences
equivalences = [
("fr_cc_1104", "de_bgb_242", "Good faith obligations"),
("uk_ucta_1977", "de_bgb_305", "Standard terms control"),
("us_ucc_2_302", "uk_ucta_1977", "Unconscionability/reasonableness"),
]
for node in foundational_nodes:
self.create_node(node)
for source, target, _ in equivalences:
self.create_relationship(LegalGraphEdge(
source_id=source,
target_id=target,
relation_type=RelationType.EQUIVALENT_TO,
confidence=0.85,
extracted_by="seed"
))
logger.info(f"Seeded {len(foundational_nodes)} foundational nodes")
# ==================== SINGLETON ====================
_client: Optional[KnowledgeGraphClient] = None
def get_knowledge_graph() -> KnowledgeGraphClient:
"""Get or create the knowledge graph client singleton."""
global _client
if _client is None:
_client = KnowledgeGraphClient()
_client.connect()
return _client
