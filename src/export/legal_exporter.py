"""
BALE Legal Export System
Generate professional legal documents from analysis.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from src.logger import setup_logger

logger = setup_logger("legal_export")


@dataclass
class ExportConfig:
    """Configuration for document export."""
    format: str  # "pdf", "html", "markdown", "json"
    include_executive_summary: bool = True
    include_risk_analysis: bool = True
    include_frontier_insights: bool = True
    include_negotiation_playbook: bool = True
    include_clause_annotations: bool = True
    redact_sensitive: bool = False
    branding: Dict[str, str] = None  # logo_url, company_name, etc.


class LegalExporter:
    """
    Export analysis results to professional legal documents.
    """
    
    def __init__(self):
        self.templates = {}
    
    def generate_memo(
        self,
        analysis_result: Dict[str, Any],
        frontier_result: Dict[str, Any] = None,
        negotiation_playbook: Dict[str, Any] = None,
        config: ExportConfig = None
    ) -> str:
        """Generate a legal memo in requested format."""
        
        if config is None:
            config = ExportConfig(format="markdown")
        
        if config.format == "markdown":
            return self._generate_markdown_memo(
                analysis_result, frontier_result, negotiation_playbook, config
            )
        elif config.format == "html":
            return self._generate_html_memo(
                analysis_result, frontier_result, negotiation_playbook, config
            )
        elif config.format == "json":
            return self._generate_json_export(
                analysis_result, frontier_result, negotiation_playbook
            )
        else:
            raise ValueError(f"Unsupported format: {config.format}")
    
    def _generate_markdown_memo(
        self,
        analysis: Dict[str, Any],
        frontier: Dict[str, Any],
        playbook: Dict[str, Any],
        config: ExportConfig
    ) -> str:
        """Generate markdown format memo."""
        
        lines = []
        
        # Header
        lines.append("# BALE Legal Analysis Memo")
        lines.append("")
        lines.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        lines.append(f"**Contract:** {analysis.get('contract_name', 'Unknown')}")
        lines.append(f"**Jurisdiction:** {analysis.get('jurisdiction', 'N/A')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        if config.include_executive_summary:
            lines.append("## Executive Summary")
            lines.append("")
            risk_score = analysis.get('risk_score', 0)
            risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 60 else "High"
            lines.append(f"**Overall Risk Assessment:** {risk_level} ({risk_score}%)")
            lines.append("")
            
            if frontier:
                frontier_risk = frontier.get('overall_frontier_risk', 0)
                lines.append(f"**Frontier Risk Index:** {frontier_risk}%")
                lines.append("")
                
                findings = frontier.get('critical_findings', [])
                if findings:
                    lines.append("### Key Findings")
                    lines.append("")
                    for finding in findings[:5]:
                        lines.append(f"- ⚠️ {finding}")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Risk Analysis
        if config.include_risk_analysis:
            lines.append("## Risk Analysis")
            lines.append("")
            
            verdict = analysis.get('verdict', {})
            if verdict:
                lines.append(f"**Primary Verdict:** {verdict.get('summary', 'N/A')}")
                lines.append("")
                
                factors = verdict.get('decision_factors', [])
                if factors:
                    lines.append("### Decision Factors")
                    lines.append("")
                    lines.append("| Factor | Impact | Reasoning |")
                    lines.append("|:-------|:-------|:----------|")
                    for f in factors[:10]:
                        lines.append(f"| {f.get('name', '')} | {f.get('impact', '')} | {f.get('reasoning', '')[:50]}... |")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Frontier Insights
        if config.include_frontier_insights and frontier:
            lines.append("## Frontier Intelligence")
            lines.append("")
            lines.append("*Second-order legal analysis capabilities*")
            lines.append("")
            
            # Silence
            if 'silence' in frontier:
                silence = frontier['silence']
                lines.append(f"### I. Silence Analysis")
                lines.append(f"- Silence Score: {silence.get('score', 0)}%")
                lines.append(f"- Missing Clauses: {len(silence.get('missing', []))}")
                lines.append("")
            
            # Temporal
            if 'temporal' in frontier:
                temporal = frontier['temporal']
                lines.append(f"### III. Temporal Decay")
                lines.append(f"- Stability Index: {temporal.get('stability', 0)*100:.0f}%")
                lines.append(f"- Review Urgency: {temporal.get('urgency', 'N/A').upper()}")
                lines.append("")
            
            # Social
            if 'social' in frontier:
                social = frontier['social']
                lines.append(f"### VI. Power Dynamics")
                lines.append(f"- Dominant Party: {social.get('dominant', 'N/A')}")
                lines.append(f"- Asymmetry Score: {social.get('asymmetry', 0):+.2f}")
                lines.append("")
            
            # Dispute
            if 'dispute' in frontier:
                dispute = frontier['dispute']
                lines.append(f"### VIII. Dispute Probability")
                lines.append(f"- Overall Probability: {dispute.get('probability', 0)*100:.1f}%")
                lines.append(f"- High-Risk Clauses: {dispute.get('high_risk', 0)}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Negotiation Playbook
        if config.include_negotiation_playbook and playbook:
            lines.append("## Negotiation Playbook")
            lines.append("")
            lines.append(f"**Recommended Stance:** {playbook.get('recommended_stance', 'balanced').upper()}")
            lines.append(f"**Estimated Difficulty:** {playbook.get('estimated_difficulty', 'moderate')}")
            lines.append(f"**Potential Risk Reduction:** {playbook.get('total_risk_reduction', 0)} points")
            lines.append("")
            
            must_have = playbook.get('must_have', [])
            if must_have:
                lines.append("### Must-Have Changes")
                lines.append("")
                for s in must_have:
                    lines.append(f"**{s.get('clause_type', '').replace('_', ' ').title()}**")
                    lines.append(f"- Issue: {s.get('rationale', '')}")
                    lines.append(f"- Market: {s.get('market_comparison', '')}")
                    lines.append(f"- Suggested: {s.get('suggested_text', '')[:200]}")
                    lines.append("")
            
            should_have = playbook.get('should_have', [])
            if should_have:
                lines.append("### Should-Have Changes")
                lines.append("")
                for s in should_have[:3]:
                    lines.append(f"- **{s.get('clause_type', '').replace('_', ' ').title()}**: {s.get('rationale', '')[:100]}")
                lines.append("")
            
            walk_away = playbook.get('walk_away_triggers', [])
            if walk_away:
                lines.append("### Walk-Away Triggers")
                lines.append("")
                for trigger in walk_away:
                    lines.append(f"- 🚫 {trigger}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Recommendations
        if frontier:
            actions = frontier.get('recommended_actions', [])
            if actions:
                lines.append("## Recommended Actions")
                lines.append("")
                for i, action in enumerate(actions, 1):
                    lines.append(f"{i}. {action}")
                lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This analysis was generated by BALE - Business Agreement Legal Evaluator*")
        lines.append(f"*Analysis ID: {analysis.get('contract_id', 'N/A')}*")
        lines.append(f"*Generated: {datetime.now().isoformat()}*")
        
        return "\n".join(lines)
    
    def _generate_html_memo(
        self,
        analysis: Dict[str, Any],
        frontier: Dict[str, Any],
        playbook: Dict[str, Any],
        config: ExportConfig
    ) -> str:
        """Generate HTML format memo."""
        
        markdown_content = self._generate_markdown_memo(analysis, frontier, playbook, config)
        
        # Wrap in HTML template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BALE Legal Analysis - {analysis.get('contract_name', 'Contract')}</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 0.5rem; }}
        h2 {{ color: #16213e; margin-top: 2rem; }}
        h3 {{ color: #0f3460; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
        th {{ background: #f5f5f5; }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 2rem 0; }}
        code {{ background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 3px; }}
        .risk-low {{ color: #10b981; }}
        .risk-medium {{ color: #f59e0b; }}
        .risk-high {{ color: #ef4444; }}
        @media print {{
            body {{ font-size: 11pt; }}
            h1 {{ font-size: 18pt; }}
            h2 {{ font-size: 14pt; }}
        }}
    </style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">
{markdown_content}
</pre>
</body>
</html>"""
        
        return html
    
    def _generate_json_export(
        self,
        analysis: Dict[str, Any],
        frontier: Dict[str, Any],
        playbook: Dict[str, Any]
    ) -> str:
        """Generate JSON format export."""
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "version": "BALE 2.2",
            "analysis": analysis,
            "frontier": frontier,
            "negotiation_playbook": playbook,
        }
        
        return json.dumps(export_data, indent=2, default=str)


# Singleton
legal_exporter = LegalExporter()
