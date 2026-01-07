import streamlit as st
import os
import tempfile
import json
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

from src.ingestion import PDFProcessor
from src.vector_store import VectorEngine
from src.graph import compile_graph

st.set_page_config(page_title="BALE 2.2 - Legal Engine", page_icon="///", layout="wide")

# Inject Custom CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/style.css")

# --- CHART HELPERS ---
def create_radar_chart(metrics):
    categories = [
        'Civil Alignment', 'Common Alignment', 
        'Certainty', 'Good Faith', 'Enforceability'
    ]
    
    # Map from metrics keys to friendly names
    values = [
        metrics.get("civil_law_alignment", 50),
        metrics.get("common_law_alignment", 50),
        metrics.get("contract_certainty", 50),
        metrics.get("good_faith_score", 50),
        metrics.get("enforceability_score", 50)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(15, 15, 15, 0.2)',
        line=dict(color='black', width=2),
        name='Contract Profile'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='rgba(0,0,0,0.2)'),
            angularaxis=dict(linecolor='black')
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(family="Space Grotesk, sans-serif", size=12, color="black")
    )
    return fig

def create_gauge(risk):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk,
        title = {'text': "LITIGATION RISK", 'font': {'size': 14, 'family': "Space Grotesk"}},
        number = {'font': {'size': 40, 'family': "Space Grotesk", 'color': "black"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "black"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "black",
            'steps': [
                {'range': [0, 30], 'color': "#E6E8EB"},
                {'range': [30, 70], 'color': "#D1D5DB"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family="Space Grotesk, sans-serif", color="black")
    )
    return fig

# --- HERO SECTION (Brutalist Top) ---
st.markdown("""
<div class="hero-container">
    <span class="hero-prefix">///</span>
    <span class="hero-title">Your Ultimate Legal<br>Document <span class="hero-highlight">> Platform_</span></span>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR (Minimalist Navigation) ---
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM")
    
    # Model Status
    local_endpoint = os.getenv("LOCAL_LLM_ENDPOINT")
    
    if local_endpoint:
         st.success(f"LOCAL_CORE: {os.getenv('LOCAL_LLM_MODEL', 'Unknown')}")
    else:
        st.error("CORE: OFFLINE")

    st.divider()
    
    uploaded_file = st.file_uploader("UPLOAD LEGAL_DOC", type=["pdf"])
    st.markdown("""
    <div style="margin-top: 20px;">
        <span class="ui-tag">01/ LEGAL</span>
        <span class="ui-tag">02/ AI</span>
        <span class="ui-tag">03/ SECURITY</span>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN DASHBOARD ---
if uploaded_file:
    # State Management
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
        st.session_state.report = {}

    # File Handling
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    # Grid Layout: Left (Stream), Right (Verdict)
    col_dash, col_log = st.columns([2, 1])

    with col_dash:
        st.markdown('<div class="section-header">/// LIVE INTELLIGENCE</div>', unsafe_allow_html=True)
        
        if st.button("RUN ANALYSIS >", type="primary", use_container_width=True):
            st.session_state.analyzing = True
        
        # Streaming Area
        stream_container = st.empty()
        
        # Dashboard Tabs (Visible after analysis)
        dash_tabs = st.empty()
        
        if st.session_state.get("analyzing"):
            
            # Init Message
            stream_html = '<div class="ui-card">'
            stream_html += '<div class="stream-item"><div class="stream-agent">SYSTEM</div><div class="stream-content">Ingesting PDF...</div></div>'
            stream_container.markdown(stream_html + '</div>', unsafe_allow_html=True)
            
            # Processing
            processor = PDFProcessor()
            text = processor.extract_layout_aware_text(tmp_path)
            chunks = processor.semantic_chunking(text, "COMMERCIAL_LAW")
            ve = VectorEngine()
            ve.add_documents(chunks)
            
            # Run Graph
            app = compile_graph()
            initial_state = {"content": text}
            
            simulated_result = {}
            
            for output in app.stream(initial_state):
                for node_name, node_content in output.items():
                    simulated_result.update(node_content)
                    
                    # Accumulate Streaming Log
                    if node_name == "civilist":
                        stream_html += '<div class="stream-item"><div class="stream-agent">01 / CIVILIST</div><div class="stream-content">Napoleonic Code Analysis: DONE</div></div>'
                    elif node_name == "commonist":
                        stream_html += '<div class="stream-item"><div class="stream-agent">02 / COMMONIST</div><div class="stream-content">Case Law Analysis: DONE</div></div>'
                    elif node_name == "ip_specialist":
                         ip_op = node_content.get("ip_opinion", "")
                         status = "SKIPPED (No IP Terms)" if "N/A" in ip_op else "WIPO Analysis: DONE"
                         stream_html += f'<div class="stream-item"><div class="stream-agent">03 / IP_NODE</div><div class="stream-content">{status}</div></div>'
                    elif node_name == "synthesizer":
                        gap = node_content.get("interpretive_gap", 0)
                        stream_html += f'<div class="stream-item"><div class="stream-agent">04 / SYNTHESIZER</div><div class="stream-content">Gap Detected: {gap}%</div></div>'
                    elif node_name == "simulation":
                         stream_html += '<div class="stream-item"><div class="stream-agent">05 / SIMULATION</div><div class="stream-content">Mock Trial: CONCLUDED</div></div>'
                    
                    stream_container.markdown(stream_html + '</div>', unsafe_allow_html=True)
            
            st.session_state.report = simulated_result.get("final_report", {})
            st.session_state.analysis_complete = True
            os.remove(tmp_path)

        # RENDER VISUALS IF COMPLETE
        if st.session_state.analysis_complete:
            with dash_tabs:
                st.markdown('<div class="section-header" style="margin-top: 20px;">/// BALE VITALS</div>', unsafe_allow_html=True)
                tab_v, tab_t = st.tabs(["VISUALS", "TRANSCRIPT"])
                
                with tab_v:
                     metrics = st.session_state.report.get("metrics", {})
                     # Default metrics if missing
                     if not metrics:
                         metrics = {"civil_law_alignment": 50, "common_law_alignment": 50, "contract_certainty": 50, "good_faith_score": 50, "enforceability_score": 50}
                     
                     st.plotly_chart(create_radar_chart(metrics), use_container_width=True)
                
                with tab_t:
                    st.markdown(st.session_state.report.get("transcript", "N/A"))


    # --- RESULT VIEW ---
    with col_log:
        if st.session_state.analysis_complete:
            report = st.session_state.report
            
            # 1. VERDICT CARD (Black)
            risk = report.get("risk", 50)
            gap = report.get("gap", 0)
            verdict_text = "PLAINTIFF FAVOR" if risk > 50 else "DEFENSE FAVOR"

            st.markdown(f"""
            <div class="verdict-card-black">
                <div class="verdict-title">> Create new report</div>
                
                <div class="risk-stat">{risk}%</div>
                <div class="risk-label">LITIGATION RISK PROBABILITY</div>
                
                <hr style="border-color: #333; margin: 20px 0;">
                
                <div style="font-family: 'Space Grotesk'; font-size: 1.2rem;">{verdict_text}</div>
                <div class="risk-label">INTERPRETIVE GAP: {gap}%</div>
                
                <div style="margin-top: 30px; text-align: right;">
                     <span class="ui-tag">EXPORT PDF</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. DETAILS (Tabs)
            st.markdown('<div class="section-header" style="margin-top: 30px;">/// DATA POINTS</div>', unsafe_allow_html=True)
            
            # GAUGE CHART HERE
            st.plotly_chart(create_gauge(risk), use_container_width=True)
            
            st.info(f"Civilist: {report.get('civilist', 'N/A')[:100]}...")
            st.success(f"Golden: {report.get('golden_clause', 'N/A')[:100]}...")

else:
    # Landing Page State (Empty State)
    st.markdown("""
    <div class="ui-card" style="text-align: center; padding: 60px;">
        <h3 style="margin-bottom: 20px;">READY FOR INTELLIGENCE</h3>
        <p style="color: #6B7280; margin-bottom: 30px;">Connect to Neural Core to begin processing.</p>
        <div>
           <span class="ui-tag">01/ UPLOAD PDF</span>
           <span class="ui-tag">02/ ANALYZE</span>
           <span class="ui-tag">03/ REPORT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
