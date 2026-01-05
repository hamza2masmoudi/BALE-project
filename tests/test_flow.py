import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import PDFProcessor
from src.vector_store import VectorEngine
from src.graph import compile_graph

def test_pipeline():
    print("=== BALE End-to-End Test ===")
    
    # 1. Mock Ingestion
    print("\n1. Testing Ingestion...")
    # Simulated text that looks like a contract mixed with code citations
    # Simulated text that looks like a contract mixed with code citations
    mock_text = """
    AGREEMENT
    
    Section 1.1: Definitions
    "Force Majeure" shall mean...
    
    Clause 2.3: Termination
    The contract may be terminated...

    Article 1218 (Code Civil)
    Il y a force majeure...
    
    Article L. 442-1
    Engage la responsabilité de son auteur...
    """
    
    processor = PDFProcessor()
    # Skip PDF reading, assume text is extracted
    tag = processor.tag_text(mock_text)
    print(f"Detected Tag: {tag}")
    
    chunks = processor.semantic_chunking(mock_text, tag)
    print(f"Extracted {len(chunks)} chunks.")
    for c in chunks:
        print(f" - Chunk ID: {c.chunk_id}")

    # 2. Vector Store
    print("\n2. Testing Vector Engine...")
    ve = VectorEngine(persist_path="./data/test_chroma_db")
    ve.add_documents(chunks)
    
    # Test Search
    results = ve.hybrid_search("Force Majeure", k=2)
    print(f"Search Results for 'Force Majeure': {len(results)} found.")
    
    # 3. Agent Graph
    print("\n3. Testing Agent Graph...")
    app = compile_graph()
    state = {"content": mock_text}
    output = app.invoke(state)
    
    report = output.get("final_report", {})
    print("\n--- Final Report ---")
    
    # Check if we are using real LLMs or fallback
    analyst_key = os.getenv("MISTRAL_API_KEY")
    if not analyst_key:
        print("[INFO] Running in Mock Mode (Missing Keys)")
    else:
        print("[INFO] Running with Real LLMs")

    print(f"Analysis: {report.get('analysis')}")
    print(f"Audit: {report.get('audit')}")
    print(f"Verified Citations: {report.get('verified')}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_pipeline()
