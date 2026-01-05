import os
import sys
import tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import PDFProcessor
from src.graph import compile_graph

def test_chaos():
    print("=== BALE Chaos Test ===")
    
    # 1. Test Empty PDF Handling
    print("\n1. Testing Empty PDF Resilience...")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        # Create an empty file (invalid PDF structure actually, but good for testing robustness)
        tmp.write(b"")
        tmp.seek(0)
        
        processor = PDFProcessor()
        text = processor.extract_layout_aware_text(tmp.name)
        
        if text == "":
            print("SUCCESS: System handled corrupted/empty PDF gracefully (returned empty string).")
        else:
            print(f"FAILURE: Unexpected output: {text}")

    # 2. Test Agent Graph with Nonsense Input
    print("\n2. Testing Agent Graph with Garbage Input...")
    nonsense_text = "asdf jkl; 1234 %%$#@"
    
    app = compile_graph()
    output = app.invoke({"content": nonsense_text})
    
    report = output.get("final_report", {})
    score = report.get("score")
    print(f"Garbage Input Score: {score}")
    
    if score is not None:
         print("SUCCESS: Agents returned a valid schema even for garbage input.")
    else:
         print("FAILURE: Agents crashed or returned invalid schema.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_chaos()
