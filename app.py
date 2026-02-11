import streamlit as st
import os
import tempfile
import json
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()
from src.ingestion import PDFProcessor
from src.v10.pipeline import V10Pipeline
st.set_page_config(page_title="BALE V10 - Contract Intelligence", page_icon="///", layout="wide")
def load_css(file_path):
with open(file_path) as f:
st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("assets/style.css")
# --- Chart Helpers ---
def create_risk_gauge(risk_score, risk_level):
color_map = {"HIGH": "#DC2626", "MEDIUM": "#F59E0B", "LOW": "#10B981"}
bar_color = color_map.get(risk_level, "#6B7280")
fig = go.Figure(go.Indicator(
mode="gauge+number",
value=risk_score,
title={"text": "CONTRACT RISK", "font": {"size": 14, "family": "Space Grotesk"}},
number={"font": {"size": 40, "family": "Space Grotesk", "color": "black"}},
gauge={
"axis": {"range": [None, 100], "tickwidth": 1, "tickcolor": "black"},
"bar": {"color": bar_color},
"bgcolor": "white",
"borderwidth": 2,
"bordercolor": "black",
"steps": [
{"range": [0, 30], "color": "#E6E8EB"},
{"range": [30, 70], "color": "#D1D5DB"},
],
"threshold": {
"line": {"color": "red", "width": 4},
"thickness": 0.75,
"value": 90,
},
},
))
fig.update_layout(
paper_bgcolor="rgba(0,0,0,0)",
height=250,
margin=dict(l=20, r=20, t=50, b=20),
font=dict(family="Space Grotesk, sans-serif", color="black"),
)
return fig
def create_power_bar(power_data):
parties = power_data.get("parties", [])
if len(parties) < 2:
return None
fig = go.Figure()
fig.add_trace(go.Bar(
name=parties[0]["name"],
x=["Obligations", "Protections", "Burden Score"],
y=[parties[0]["obligations"], parties[0]["protections"], parties[0]["burden_score"]],
marker_color="black",
))
fig.add_trace(go.Bar(
name=parties[1]["name"],
x=["Obligations", "Protections", "Burden Score"],
y=[parties[1]["obligations"], parties[1]["protections"], parties[1]["burden_score"]],
marker_color="#94A3B8",
))
fig.update_layout(
barmode="group",
paper_bgcolor="rgba(0,0,0,0)",
plot_bgcolor="rgba(0,0,0,0)",
height=280,
margin=dict(l=20, r=20, t=20, b=40),
font=dict(family="Space Grotesk, sans-serif", size=12, color="black"),
legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
return fig
def create_completeness_chart(graph_data):
completeness = graph_data.get("completeness_score", 0) * 100
fig = go.Figure(go.Indicator(
mode="gauge+number",
value=completeness,
title={"text": "COMPLETENESS", "font": {"size": 14, "family": "Space Grotesk"}},
number={"font": {"size": 36, "family": "Space Grotesk"}, "suffix": "%"},
gauge={
"axis": {"range": [0, 100]},
"bar": {"color": "#10B981" if completeness > 70 else "#F59E0B"},
"borderwidth": 2,
"bordercolor": "black",
},
))
fig.update_layout(
paper_bgcolor="rgba(0,0,0,0)",
height=200,
margin=dict(l=20, r=20, t=50, b=20),
)
return fig
# --- Hero Section ---
st.markdown("""
<div class="hero-container">
<span class="hero-prefix">///</span>
<span class="hero-title">Contract Intelligence<br>Engine <span class="hero-highlight">> V10_</span></span>
</div>
""", unsafe_allow_html=True)
# --- Sidebar ---
with st.sidebar:
st.markdown("### CONFIGURATION")
contract_type = st.selectbox("CONTRACT TYPE", [
"MSA", "NDA", "SLA", "Employment", "License", "Lease", "Supply",
])
st.divider()
uploaded_file = st.file_uploader("UPLOAD CONTRACT", type=["pdf"])
st.markdown("""
<div style="margin-top: 20px;">
<span class="ui-tag">01/ CLASSIFY</span>
<span class="ui-tag">02/ GRAPH</span>
<span class="ui-tag">03/ ANALYZE</span>
</div>
""", unsafe_allow_html=True)
# --- Main Dashboard ---
if uploaded_file:
if "analysis_complete" not in st.session_state:
st.session_state.analysis_complete = False
st.session_state.report = {}
st.session_state.v10_report = None
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
tmp_file.write(uploaded_file.getvalue())
tmp_path = tmp_file.name
col_dash, col_log = st.columns([2, 1])
with col_dash:
st.markdown('<div class="section-header">/// CONTRACT ANALYSIS</div>', unsafe_allow_html=True)
if st.button("RUN ANALYSIS >", type="primary", use_container_width=True):
st.session_state.analyzing = True
stream_container = st.empty()
dash_tabs = st.empty()
if st.session_state.get("analyzing"):
stream_html = '<div class="ui-card">'
stream_html += '<div class="stream-item"><div class="stream-agent">SYSTEM</div><div class="stream-content">Ingesting document...</div></div>'
stream_container.markdown(stream_html + "</div>", unsafe_allow_html=True)
# Step 1: Extract text
processor = PDFProcessor()
text = processor.extract_layout_aware_text(tmp_path)
stream_html += '<div class="stream-item"><div class="stream-agent">01 / CLASSIFIER</div><div class="stream-content">Embedding-based clause classification...</div></div>'
stream_container.markdown(stream_html + "</div>", unsafe_allow_html=True)
# Step 2: Run V10 pipeline
pipeline = V10Pipeline(multilingual=True)
report = pipeline.analyze(text, contract_type)
stream_html += f'<div class="stream-item"><div class="stream-agent">02 / GRAPH</div><div class="stream-content">Clause relationships mapped: {report.graph["conflict_count"]} conflicts, {report.graph["dependency_gap_count"]} gaps</div></div>'
stream_container.markdown(stream_html + "</div>", unsafe_allow_html=True)
stream_html += f'<div class="stream-item"><div class="stream-agent">03 / POWER</div><div class="stream-content">Asymmetry score: {report.power["power_score"]:.0f}/100</div></div>'
stream_container.markdown(stream_html + "</div>", unsafe_allow_html=True)
stream_html += f'<div class="stream-item"><div class="stream-agent">04 / DISPUTES</div><div class="stream-content">{len(report.disputes["hotspots"])} hotspots identified</div></div>'
stream_container.markdown(stream_html + "</div>", unsafe_allow_html=True)
stream_html += f'<div class="stream-item"><div class="stream-agent">VERDICT</div><div class="stream-content">Risk Level: {report.risk_level} ({report.overall_risk_score:.0f}/100) | {report.analysis_time_ms}ms</div></div>'
stream_container.markdown(stream_html + "</div>", unsafe_allow_html=True)
st.session_state.v10_report = report
st.session_state.report = report.to_dict()
st.session_state.analysis_complete = True
st.session_state.analyzing = False
os.remove(tmp_path)
# Render visuals after analysis
if st.session_state.analysis_complete and st.session_state.report:
data = st.session_state.report
with dash_tabs:
st.markdown('<div class="section-header" style="margin-top: 20px;">/// ANALYSIS RESULTS</div>', unsafe_allow_html=True)
tab_graph, tab_power, tab_disputes, tab_raw = st.tabs([
"GRAPH", "POWER", "DISPUTES", "RAW JSON",
])
with tab_graph:
graph = data.get("graph_analysis", {})
st.plotly_chart(create_completeness_chart(graph), use_container_width=True)
if graph.get("conflicts"):
st.markdown("**Conflicts Detected:**")
for c in graph["conflicts"]:
st.warning(f"{c['clause_a']} vs {c['clause_b']}: {c['description']}")
if graph.get("missing_dependencies"):
st.markdown("**Missing Dependencies:**")
for d in graph["missing_dependencies"]:
st.error(f"{d['clause_has']} requires {d['clause_needs']}: {d['description']}")
if graph.get("missing_expected"):
st.markdown("**Missing Expected Clauses:**")
for m in graph["missing_expected"][:5]:
st.info(f"{m['clause_type'].replace('_', ' ').title()} -- expected in {int(m['expected_prevalence'] * 100)}% of similar contracts")
with tab_power:
power = data.get("power_analysis", {})
power_fig = create_power_bar(power)
if power_fig:
st.plotly_chart(power_fig, use_container_width=True)
st.markdown(f"**{power.get('summary', '')}**")
with tab_disputes:
disputes = data.get("dispute_prediction", {})
st.markdown(f"**Predicted Dispute Volume:** {disputes.get('dispute_count_prediction', 'N/A')}")
for h in disputes.get("hotspots", [])[:8]:
severity = h["severity"]
color = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "blue"}.get(severity, "gray")
st.markdown(
f"<span style='color:{color}; font-weight:bold'>[{severity}]</span> "
f"**{h['clause_type'].replace('_', ' ').title()}** -- {h['dispute_probability']:.0%} probability",
unsafe_allow_html=True,
)
st.caption(h["reason"])
st.caption(f"Recommendation: {h['recommendation']}")
st.divider()
with tab_raw:
st.json(data)
# --- Result sidebar ---
with col_log:
if st.session_state.analysis_complete and st.session_state.report:
data = st.session_state.report
overall = data.get("overall", {})
risk = overall.get("risk_score", 50)
risk_level = overall.get("risk_level", "MEDIUM")
st.markdown(f"""
<div class="verdict-card-black">
<div class="verdict-title">> Contract Report</div>
<div class="risk-stat">{risk:.0f}%</div>
<div class="risk-label">CONTRACT RISK SCORE</div>
<hr style="border-color: #333; margin: 20px 0;">
<div style="font-family: 'Space Grotesk'; font-size: 1.2rem;">{risk_level} RISK</div>
<div class="risk-label">COMPLETENESS: {data.get('graph_analysis', {}).get('completeness_score', 0):.0%}</div>
<div style="margin-top: 30px; text-align: right;">
<span class="ui-tag">EXPORT JSON</span>
</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="section-header" style="margin-top: 30px;">/// RISK GAUGE</div>', unsafe_allow_html=True)
st.plotly_chart(create_risk_gauge(risk, risk_level), use_container_width=True)
st.markdown('<div class="section-header" style="margin-top: 20px;">/// SUMMARY</div>', unsafe_allow_html=True)
st.markdown(overall.get("executive_summary", ""))
# Classifications
st.markdown('<div class="section-header" style="margin-top: 20px;">/// CLASSIFICATIONS</div>', unsafe_allow_html=True)
for c in data.get("classifications", [])[:10]:
st.caption(f"{c['id']}: **{c['clause_type'].replace('_', ' ').title()}** ({c['confidence']:.0%})")
else:
st.markdown("""
<div class="ui-card" style="text-align: center; padding: 60px;">
<h3 style="margin-bottom: 20px;">READY FOR ANALYSIS</h3>
<p style="color: #6B7280; margin-bottom: 30px;">Upload a contract to begin V10 analysis.</p>
<div>
<span class="ui-tag">01/ CLASSIFY</span>
<span class="ui-tag">02/ GRAPH</span>
<span class="ui-tag">03/ ANALYZE</span>
</div>
</div>
""", unsafe_allow_html=True)
