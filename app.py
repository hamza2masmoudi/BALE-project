import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

from src.ingestion import PDFProcessor
from src.vector_store import VectorEngine
from src.graph import compile_graph

st.set_page_config(page_title="BALE - Legal Disparity Engine", layout="wide")

# Custom Professional CSS
st.markdown("""
<style>
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    h1 {
        font-weight: 700 !important;
        color: #1E3A8A !important; /* Navy Blue */
    }
    h2, h3 {
        color: #374151 !important;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        color: #1E3A8A !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        color: #4B5563;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        border-bottom: 2px solid #1E3A8A;
        color: #1E3A8A;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #F3F4F6;
        border-radius: 4px;
        color: #1F2937;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ BALE: Bilingual Agentic Legal Engine")
st.markdown("### Asymmetric Legal Analysis: Common Law vs. Civil Law")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Model Status Check
    mistral_key = os.getenv("MISTRAL_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    st.subheader("Model Status")
    if mistral_key:
        st.success("Analyst (Mistral): Active")
    else:
        st.warning("Analyst (Mistral): MOCK MODE")
        
    if deepseek_key:
        st.success("Auditor (DeepSeek): Active")
    else:
        st.warning("Auditor (DeepSeek): MOCK MODE")

    st.divider()
    uploaded_file = st.file_uploader("Upload Legal Document (PDF)", type=["pdf"])

# Main Area
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    st.success("File uploaded successfully.")

    if st.button("Analyze Disparities", type="primary"):
        progress_bar = st.progress(0)
        
        with st.status("Processing Document...", expanded=True) as status:
            # 1. Ingestion
            st.write("📄 Ingesting and Parsing PDF...")
            processor = PDFProcessor()
            text = processor.extract_layout_aware_text(tmp_path)
            tag = processor.tag_text(text)
            chunks = processor.semantic_chunking(text, tag)
            progress_bar.progress(30)
            
            st.write(f"   - Detected System: **{tag}**")
            st.write(f"   - Extracted **{len(chunks)}** Legal Chunks")
            
            # 2. Vector Store
            st.write("💾 Indexing into Vector Space...")
            ve = VectorEngine() 
            ve.add_documents(chunks)
            progress_bar.progress(60)
            
            # 3. Agent Graph (Dialectic Engine)
            st.write("🤖 **Dialectic Consensus Engine** Running...")
            st.write("   - 🏛️ **Civilist Agent** (Napoleonic Code Analysis)")
            st.write("   - ⚖️ **Commonist Agent** (Case Law Analysis)")
            st.write("   - 🧠 **Synthesizer** (Measuring Interpretive Gap)")
            
            app = compile_graph()
            initial_state = {"content": text}
            result = app.invoke(initial_state)
            progress_bar.progress(100)
            status.update(label="Dialectic Analysis Complete!", state="complete", expanded=False)
            
        # Display Results
        report = result.get("final_report", {})
        
        st.divider()
        st.header("🧠 Dialectic Consensus Report")
        
        # Top-level metrics
        # Top-level metrics
        gap = report.get("gap", 0)
        risk = report.get("risk", 50)
        
        col_gap, col_risk = st.columns(2)
        
        with col_gap:
            st.metric("Interpretive Gap", f"{gap}%")
            if gap < 20:
                st.success("✅ **Consensus Reached**")
            elif gap < 60:
                st.warning("⚠️ **Divergence Detected**")
            else:
                st.error("🚨 **FUNDAMENTAL CONFLICT**")
                
        with col_risk:
            st.metric("Litigation Risk", f"{risk}%", help="Win Probability for Plaintiff against Defense")
            if risk < 30:
                 st.success("🛡️ **Low Risk**: Defense likely prevails.")
            elif risk < 70:
                 st.warning("⚖️ **Moderate Risk**: Outcome uncertain.")
            else:
                 st.error("🔥 **High Risk**: Plaintiff likely wins.")

        st.divider()
        transcript = report.get("transcript", "")
        if transcript:
            with st.expander("⚖️ View Adversarial Mock Trial (Plaintiff vs Defense)"):
                st.markdown(transcript)

        st.markdown("### 🏛️ The Legal Debate")
        col_civ, col_com = st.columns(2)
        
        with col_civ:
            st.info("**The Civilist Opinion** (Napoleonic Code)")
            st.markdown(report.get("civilist", "No opinion."))
        
        with col_com:
            st.info("**The Commonist Opinion** (Common Law)")
            st.markdown(report.get("commonist", "No opinion."))

        st.divider()
        st.markdown("### 🧠 Synthesis & Symbolic Logic")
        st.write(report.get("synthesis", "No synthesis."))
        
        logic = report.get("logic", "N/A")
        if logic and logic != "N/A":
            st.markdown(f"**Symbolic Representation:**")
            st.code(logic, language="prolog")
            
        # Phase 8: The Golden Clause
        golden = report.get("golden_clause")
        rationale = report.get("rationale")
        
        if golden and "N/A" not in golden:
            st.divider()
            st.markdown("### ✨ The Golden Clause (Automated Harmonization)")
            st.markdown("> **Strategist's Rationale**: " + str(rationale))
            
            st.text_area("Proposed Redraft", value=golden, height=150)
            st.caption("This clause has been drafted to satisfy both Civil Law good faith and Common Law commercial certainty.")
            
        st.divider()
        st.markdown("### 📚 Verified Citations")
        verified = report.get("verified", [])
        if verified:
            for v in verified:
                st.success(f"✅ **{v}** (Found in VectorDB)")
        else:
            st.caption("No specific citations were verified against the database.")

        # JSON View
        with st.expander("View Raw JSON Output"):
            st.json(result)

    # Cleanup
    os.remove(tmp_path)
else:
    st.info("Please upload a PDF to begin analysis.")
