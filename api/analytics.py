"""
BALE Analytics & Reporting Service
Aggregation, metrics, and report generation.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum

from src.logger import setup_logger

logger = setup_logger("bale_analytics")


# ==================== DATA MODELS ====================

class TimeRange(str, Enum):
    LAST_24H = "24h"
    LAST_7D = "7d"
    LAST_30D = "30d"
    LAST_90D = "90d"
    ALL_TIME = "all"


@dataclass
class AnalyticsSummary:
    """Summary statistics for a time period."""
    period: str
    start_date: str
    end_date: str
    
    # Volume
    total_analyses: int = 0
    total_contracts: int = 0
    total_users: int = 0
    
    # Risk
    avg_risk_score: float = 0.0
    high_risk_count: int = 0
    low_risk_count: int = 0
    
    # Verdicts
    plaintiff_favor_count: int = 0
    defense_favor_count: int = 0
    
    # Performance
    avg_analysis_time_ms: float = 0.0
    p95_analysis_time_ms: float = 0.0
    
    # By Jurisdiction
    by_jurisdiction: Dict[str, int] = None
    
    def __post_init__(self):
        if self.by_jurisdiction is None:
            self.by_jurisdiction = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UsageMetrics:
    """API usage metrics."""
    date: str
    
    # Requests
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # By endpoint
    analyze_calls: int = 0
    simulate_calls: int = 0
    contract_calls: int = 0
    
    # By user
    unique_users: int = 0
    api_key_users: int = 0
    jwt_users: int = 0
    
    # Performance
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0


# ==================== ANALYTICS ENGINE ====================

class AnalyticsEngine:
    """
    Aggregates and computes analytics from analysis results.
    """
    
    def __init__(self):
        # In-memory storage (replace with DB in production)
        self.analyses: List[Dict] = []
        self.usage_logs: List[Dict] = []
    
    def record_analysis(
        self,
        analysis_id: str,
        user_id: str,
        jurisdiction: str,
        risk_score: int,
        verdict: str,
        processing_time_ms: int,
        timestamp: datetime = None
    ):
        """Record an analysis result for aggregation."""
        self.analyses.append({
            "id": analysis_id,
            "user_id": user_id,
            "jurisdiction": jurisdiction,
            "risk_score": risk_score,
            "verdict": verdict,
            "processing_time_ms": processing_time_ms,
            "timestamp": (timestamp or datetime.utcnow()).isoformat()
        })
    
    def record_request(
        self,
        endpoint: str,
        user_id: str,
        auth_method: str,
        status_code: int,
        latency_ms: float,
        timestamp: datetime = None
    ):
        """Record an API request for usage tracking."""
        self.usage_logs.append({
            "endpoint": endpoint,
            "user_id": user_id,
            "auth_method": auth_method,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "timestamp": (timestamp or datetime.utcnow()).isoformat()
        })
    
    def get_summary(self, time_range: TimeRange = TimeRange.LAST_7D) -> AnalyticsSummary:
        """Get analytics summary for a time period."""
        now = datetime.utcnow()
        
        # Calculate date range
        if time_range == TimeRange.LAST_24H:
            start = now - timedelta(hours=24)
        elif time_range == TimeRange.LAST_7D:
            start = now - timedelta(days=7)
        elif time_range == TimeRange.LAST_30D:
            start = now - timedelta(days=30)
        elif time_range == TimeRange.LAST_90D:
            start = now - timedelta(days=90)
        else:
            start = datetime.min
        
        # Filter analyses
        filtered = [
            a for a in self.analyses
            if datetime.fromisoformat(a["timestamp"]) >= start
        ]
        
        if not filtered:
            return AnalyticsSummary(
                period=time_range.value,
                start_date=start.isoformat(),
                end_date=now.isoformat()
            )
        
        # Compute metrics
        risk_scores = [a["risk_score"] for a in filtered]
        processing_times = [a["processing_time_ms"] for a in filtered]
        
        by_jurisdiction = defaultdict(int)
        for a in filtered:
            by_jurisdiction[a["jurisdiction"]] += 1
        
        return AnalyticsSummary(
            period=time_range.value,
            start_date=start.isoformat(),
            end_date=now.isoformat(),
            total_analyses=len(filtered),
            total_contracts=len(set(a.get("contract_id", a["id"]) for a in filtered)),
            total_users=len(set(a["user_id"] for a in filtered)),
            avg_risk_score=sum(risk_scores) / len(risk_scores),
            high_risk_count=sum(1 for r in risk_scores if r > 70),
            low_risk_count=sum(1 for r in risk_scores if r <= 40),
            plaintiff_favor_count=sum(1 for a in filtered if "PLAINTIFF" in a["verdict"]),
            defense_favor_count=sum(1 for a in filtered if "DEFENSE" in a["verdict"]),
            avg_analysis_time_ms=sum(processing_times) / len(processing_times),
            p95_analysis_time_ms=sorted(processing_times)[int(len(processing_times) * 0.95)] if processing_times else 0,
            by_jurisdiction=dict(by_jurisdiction)
        )
    
    def get_risk_trend(
        self, 
        days: int = 30
    ) -> List[Tuple[str, float]]:
        """Get daily average risk score trend."""
        now = datetime.utcnow()
        start = now - timedelta(days=days)
        
        # Group by date
        by_date = defaultdict(list)
        for a in self.analyses:
            ts = datetime.fromisoformat(a["timestamp"])
            if ts >= start:
                date_str = ts.strftime("%Y-%m-%d")
                by_date[date_str].append(a["risk_score"])
        
        # Compute daily averages
        trend = []
        for date_str in sorted(by_date.keys()):
            scores = by_date[date_str]
            avg = sum(scores) / len(scores)
            trend.append((date_str, avg))
        
        return trend
    
    def get_jurisdiction_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get breakdown by jurisdiction."""
        by_j = defaultdict(lambda: {"count": 0, "total_risk": 0, "verdicts": defaultdict(int)})
        
        for a in self.analyses:
            j = a["jurisdiction"]
            by_j[j]["count"] += 1
            by_j[j]["total_risk"] += a["risk_score"]
            by_j[j]["verdicts"][a["verdict"]] += 1
        
        result = {}
        for j, data in by_j.items():
            result[j] = {
                "count": data["count"],
                "avg_risk": data["total_risk"] / data["count"],
                "verdicts": dict(data["verdicts"])
            }
        
        return result


# ==================== REPORT GENERATOR ====================

class ReportGenerator:
    """Generate formatted reports from analytics."""
    
    def __init__(self, analytics: AnalyticsEngine):
        self.analytics = analytics
    
    def generate_html_report(
        self,
        summary: AnalyticsSummary,
        title: str = "BALE Analytics Report"
    ) -> str:
        """Generate an HTML report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; background: #0a0a0a; color: #fff; }}
        h1 {{ color: #fff; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #111; border: 1px solid #222; border-radius: 12px; padding: 20px; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ color: #888; font-size: 0.9em; }}
        .risk-high {{ color: #ef4444; }}
        .risk-low {{ color: #10b981; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #222; }}
        th {{ background: #111; }}
    </style>
</head>
<body>
    <h1>📊 {title}</h1>
    <p style="color: #888;">Period: {summary.start_date[:10]} to {summary.end_date[:10]}</p>
    
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-value">{summary.total_analyses}</div>
            <div class="stat-label">Total Analyses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary.avg_risk_score:.1f}%</div>
            <div class="stat-label">Average Risk</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary.total_users}</div>
            <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-value risk-high">{summary.high_risk_count}</div>
            <div class="stat-label">High Risk Clauses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value risk-low">{summary.low_risk_count}</div>
            <div class="stat-label">Low Risk Clauses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{summary.avg_analysis_time_ms:.0f}ms</div>
            <div class="stat-label">Avg Analysis Time</div>
        </div>
    </div>
    
    <h2>By Jurisdiction</h2>
    <table>
        <tr><th>Jurisdiction</th><th>Analyses</th><th>%</th></tr>
        {"".join(f'<tr><td>{j}</td><td>{c}</td><td>{c/summary.total_analyses*100:.1f}%</td></tr>' for j, c in summary.by_jurisdiction.items())}
    </table>
    
    <h2>Verdicts</h2>
    <table>
        <tr><th>Outcome</th><th>Count</th></tr>
        <tr><td>Plaintiff Favor</td><td class="risk-high">{summary.plaintiff_favor_count}</td></tr>
        <tr><td>Defense Favor</td><td class="risk-low">{summary.defense_favor_count}</td></tr>
    </table>
    
    <footer style="margin-top: 40px; color: #666; font-size: 0.8em;">
        Generated by BALE Analytics • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
    </footer>
</body>
</html>
        """
        return html
    
    def generate_json_report(self, summary: AnalyticsSummary) -> str:
        """Generate a JSON report."""
        return json.dumps(summary.to_dict(), indent=2)
    
    def generate_markdown_report(self, summary: AnalyticsSummary) -> str:
        """Generate a Markdown report."""
        md = f"""# BALE Analytics Report

**Period**: {summary.start_date[:10]} to {summary.end_date[:10]}

## Summary

| Metric | Value |
|:-------|------:|
| Total Analyses | {summary.total_analyses} |
| Average Risk | {summary.avg_risk_score:.1f}% |
| Active Users | {summary.total_users} |
| High Risk Clauses | {summary.high_risk_count} |
| Low Risk Clauses | {summary.low_risk_count} |
| Avg Analysis Time | {summary.avg_analysis_time_ms:.0f}ms |

## By Jurisdiction

| Jurisdiction | Analyses |
|:-------------|:---------|
""" + "\n".join(f"| {j} | {c} |" for j, c in summary.by_jurisdiction.items())
        
        return md


# ==================== DASHBOARD DATA ====================

class DashboardDataProvider:
    """Provide data for the React dashboard."""
    
    def __init__(self, analytics: AnalyticsEngine):
        self.analytics = analytics
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard data in one call."""
        summary = self.analytics.get_summary(TimeRange.LAST_7D)
        trend = self.analytics.get_risk_trend(days=14)
        breakdown = self.analytics.get_jurisdiction_breakdown()
        
        return {
            "summary": summary.to_dict(),
            "risk_trend": [{"date": d, "risk": r} for d, r in trend],
            "jurisdiction_breakdown": breakdown,
            "recent_high_risk": self._get_recent_high_risk(5)
        }
    
    def _get_recent_high_risk(self, limit: int) -> List[Dict]:
        """Get recent high-risk analyses."""
        high_risk = [
            a for a in self.analytics.analyses
            if a["risk_score"] > 70
        ]
        return sorted(
            high_risk,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]


# ==================== GLOBAL INSTANCE ====================

analytics_engine = AnalyticsEngine()
report_generator = ReportGenerator(analytics_engine)
dashboard_provider = DashboardDataProvider(analytics_engine)
