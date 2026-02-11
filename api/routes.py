"""
BALE API Routes - Extended Endpoints
Analytics, WebSocket, Jobs, Reports.
"""
import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from api.analytics import analytics_engine, report_generator, dashboard_provider, TimeRange
from api.realtime import websocket_handler, sse_generator, AnalysisProgressTracker, manager
from api.jobs import job_queue, run_background, JobStatus
from api.webhooks import emit_event_async, EventType
from api.cache import cache, analysis_cache_key
from src.logger import setup_logger
logger = setup_logger("bale_api_routes")
# ==================== ROUTERS ====================
analytics_router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])
realtime_router = APIRouter(tags=["Real-time"])
jobs_router = APIRouter(prefix="/v1/jobs", tags=["Jobs"])
reports_router = APIRouter(prefix="/v1/reports", tags=["Reports"])
metrics_router = APIRouter(tags=["Metrics"])
# ==================== ANALYTICS ENDPOINTS ====================
class DashboardDataResponse(BaseModel):
summary: dict
risk_trend: List[dict]
jurisdiction_breakdown: dict
recent_high_risk: List[dict]
@analytics_router.get("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard_data():
"""Get all dashboard data in one call."""
return dashboard_provider.get_dashboard_data()
@analytics_router.get("/summary")
async def get_analytics_summary(
time_range: str = Query("7d", description="Time range: 24h, 7d, 30d, 90d, all")
):
"""Get analytics summary for a time period."""
try:
tr = TimeRange(time_range)
except ValueError:
tr = TimeRange.LAST_7D
summary = analytics_engine.get_summary(tr)
return summary.to_dict()
@analytics_router.get("/risk-trend")
async def get_risk_trend(days: int = Query(30, ge=1, le=365)):
"""Get daily risk score trend."""
trend = analytics_engine.get_risk_trend(days=days)
return [{"date": d, "risk": r} for d, r in trend]
@analytics_router.get("/jurisdictions")
async def get_jurisdiction_breakdown():
"""Get breakdown by jurisdiction."""
return analytics_engine.get_jurisdiction_breakdown()
# ==================== REAL-TIME ENDPOINTS ====================
@realtime_router.websocket("/ws/{user_id}")
async def ws_endpoint(websocket: WebSocket, user_id: str):
"""WebSocket endpoint for real-time analysis updates."""
await websocket_handler(websocket, user_id)
@realtime_router.get("/v1/analyze/{analysis_id}/stream")
async def stream_analysis(analysis_id: str):
"""
Stream analysis progress via Server-Sent Events.
Connect to this endpoint after starting an analysis to receive
real-time progress updates.
"""
return StreamingResponse(
sse_generator(analysis_id),
media_type="text/event-stream",
headers={
"Cache-Control": "no-cache",
"Connection": "keep-alive",
"X-Accel-Buffering": "no"
}
)
# ==================== JOBS ENDPOINTS ====================
class JobResponse(BaseModel):
id: str
task_name: str
status: str
progress: int
created_at: str
completed_at: Optional[str]
result: Optional[dict]
error: Optional[str]
class BulkAnalysisRequest(BaseModel):
contract_id: str
clauses: List[str]
jurisdiction: str = "INTERNATIONAL"
@jobs_router.post("/bulk-analysis", response_model=JobResponse)
async def start_bulk_analysis(
request: BulkAnalysisRequest,
background_tasks: BackgroundTasks
):
"""
Start a bulk analysis job for multiple clauses.
Returns immediately with job ID for polling.
"""
# Start job queue if not running
if not job_queue._running:
background_tasks.add_task(job_queue.start)
job = await run_background(
"bulk_analysis",
request.contract_id,
request.clauses,
request.jurisdiction,
user_id="anonymous" # TODO: Get from auth
)
return JobResponse(
id=job.id,
task_name=job.task_name,
status=job.status.value,
progress=job.progress,
created_at=job.created_at,
completed_at=job.completed_at,
result=job.result,
error=job.error
)
@jobs_router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
"""Get the status of a background job."""
job = job_queue.get_job(job_id)
if not job:
raise HTTPException(404, "Job not found")
return JobResponse(
id=job.id,
task_name=job.task_name,
status=job.status.value,
progress=job.progress,
created_at=job.created_at,
completed_at=job.completed_at,
result=job.result,
error=job.error
)
@jobs_router.delete("/{job_id}")
async def cancel_job(job_id: str):
"""Cancel a pending job."""
if job_queue.cancel_job(job_id):
return {"status": "cancelled", "job_id": job_id}
raise HTTPException(400, "Cannot cancel job (not pending or not found)")
# ==================== REPORTS ENDPOINTS ====================
class ReportRequest(BaseModel):
format: str = "html" # html, json, markdown
time_range: str = "7d"
@reports_router.post("/generate")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
"""Generate an analytics report."""
try:
tr = TimeRange(request.time_range)
except ValueError:
tr = TimeRange.LAST_7D
summary = analytics_engine.get_summary(tr)
if request.format == "html":
html = report_generator.generate_html_report(summary)
return HTMLResponse(content=html)
elif request.format == "markdown":
md = report_generator.generate_markdown_report(summary)
return {"format": "markdown", "content": md}
else:
return {"format": "json", "data": summary.to_dict()}
@reports_router.get("/export/{analysis_id}")
async def export_analysis(analysis_id: str, format: str = "json"):
"""Export a single analysis result."""
# TODO: Fetch from database
return {"analysis_id": analysis_id, "format": format, "status": "not_implemented"}
# ==================== METRICS ENDPOINTS ====================
@metrics_router.get("/metrics")
async def prometheus_metrics():
"""
Prometheus-format metrics endpoint.
"""
# Get current stats
summary = analytics_engine.get_summary(TimeRange.LAST_24H)
metrics = []
# Analysis metrics
metrics.append(f"bale_analyses_total {summary.total_analyses}")
metrics.append(f"bale_avg_risk_score {summary.avg_risk_score:.2f}")
metrics.append(f"bale_high_risk_count {summary.high_risk_count}")
metrics.append(f"bale_low_risk_count {summary.low_risk_count}")
metrics.append(f"bale_avg_analysis_time_ms {summary.avg_analysis_time_ms:.2f}")
# Verdict counts
metrics.append(f"bale_verdicts{{outcome=\"plaintiff\"}} {summary.plaintiff_favor_count}")
metrics.append(f"bale_verdicts{{outcome=\"defense\"}} {summary.defense_favor_count}")
# By jurisdiction
for j, count in summary.by_jurisdiction.items():
metrics.append(f"bale_analyses_by_jurisdiction{{jurisdiction=\"{j}\"}} {count}")
# Cache stats
if cache.is_connected:
metrics.append("bale_cache_connected 1")
else:
metrics.append("bale_cache_connected 0")
# Active WebSocket connections
total_ws = sum(len(conns) for conns in manager.connections.values())
metrics.append(f"bale_websocket_connections {total_ws}")
return "\n".join(metrics) + "\n"
@metrics_router.get("/health/deep")
async def deep_health_check():
"""
Deep health check - verifies all components.
"""
checks = {}
healthy = True
# API
checks["api"] = {"status": "healthy"}
# Redis
try:
if cache.is_connected:
cache._client.ping()
checks["redis"] = {"status": "healthy"}
else:
checks["redis"] = {"status": "disconnected"}
healthy = False
except Exception as e:
checks["redis"] = {"status": "unhealthy", "error": str(e)}
healthy = False
# Database
try:
from database.config import check_connection
if check_connection():
checks["database"] = {"status": "healthy"}
else:
checks["database"] = {"status": "disconnected"}
except Exception as e:
checks["database"] = {"status": "error", "error": str(e)}
# LLM
local_endpoint = os.getenv("LOCAL_LLM_ENDPOINT")
if local_endpoint:
try:
import httpx
async with httpx.AsyncClient(timeout=5.0) as client:
resp = await client.get(local_endpoint.replace("/chat/completions", "/health"))
if resp.status_code < 400:
checks["llm_local"] = {"status": "healthy"}
else:
checks["llm_local"] = {"status": "unhealthy", "code": resp.status_code}
except Exception as e:
checks["llm_local"] = {"status": "unreachable", "error": str(e)}
else:
checks["llm_local"] = {"status": "not_configured"}
return {
"healthy": healthy,
"timestamp": datetime.utcnow().isoformat(),
"checks": checks
}
# ==================== EXPORT ALL ROUTERS ====================
def register_routes(app):
"""Register all additional routes with the main app."""
app.include_router(analytics_router)
app.include_router(realtime_router)
app.include_router(jobs_router)
app.include_router(reports_router)
app.include_router(metrics_router)
logger.info("Registered extended API routes")
