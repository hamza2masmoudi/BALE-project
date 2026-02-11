"""
BALE Background Job Processing
Celery-style task queue for long-running operations.
"""
import os
import json
import uuid
import asyncio
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from src.logger import setup_logger
logger = setup_logger("bale_jobs")
# ==================== JOB STATUS ====================
class JobStatus(str, Enum):
PENDING = "pending"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
CANCELLED = "cancelled"
@dataclass
class Job:
"""Represents a background job."""
id: str
task_name: str
args: tuple
kwargs: Dict[str, Any]
status: JobStatus
# Timing
created_at: str
started_at: Optional[str] = None
completed_at: Optional[str] = None
# Results
result: Optional[Any] = None
error: Optional[str] = None
progress: int = 0
# Metadata
user_id: Optional[str] = None
priority: int = 0
def to_dict(self) -> Dict[str, Any]:
return {
"id": self.id,
"task_name": self.task_name,
"status": self.status.value,
"created_at": self.created_at,
"started_at": self.started_at,
"completed_at": self.completed_at,
"result": self.result,
"error": self.error,
"progress": self.progress,
"user_id": self.user_id
}
# ==================== TASK REGISTRY ====================
class TaskRegistry:
"""Registry for background tasks."""
def __init__(self):
self.tasks: Dict[str, Callable] = {}
def register(self, name: str = None):
"""Decorator to register a task."""
def decorator(func):
task_name = name or func.__name__
self.tasks[task_name] = func
logger.info(f"Registered task: {task_name}")
return func
return decorator
def get(self, name: str) -> Optional[Callable]:
return self.tasks.get(name)
registry = TaskRegistry()
# ==================== IN-MEMORY JOB QUEUE ====================
class JobQueue:
"""
Simple in-memory job queue.
In production, replace with Redis/Celery.
"""
def __init__(self, max_workers: int = 4):
self.jobs: Dict[str, Job] = {}
self.queue: asyncio.Queue = asyncio.Queue()
self.executor = ThreadPoolExecutor(max_workers=max_workers)
self._running = False
self._worker_task: Optional[asyncio.Task] = None
async def start(self):
"""Start the job processing worker."""
if self._running:
return
self._running = True
self._worker_task = asyncio.create_task(self._worker())
logger.info("Job queue started")
async def stop(self):
"""Stop the job processing worker."""
self._running = False
if self._worker_task:
self._worker_task.cancel()
try:
await self._worker_task
except asyncio.CancelledError:
pass
self.executor.shutdown(wait=True)
logger.info("Job queue stopped")
async def _worker(self):
"""Main worker loop."""
while self._running:
try:
job_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
job = self.jobs.get(job_id)
if job and job.status == JobStatus.PENDING:
await self._execute_job(job)
except asyncio.TimeoutError:
continue
except Exception as e:
logger.error(f"Worker error: {e}")
async def _execute_job(self, job: Job):
"""Execute a single job."""
job.status = JobStatus.RUNNING
job.started_at = datetime.utcnow().isoformat()
task_func = registry.get(job.task_name)
if not task_func:
job.status = JobStatus.FAILED
job.error = f"Unknown task: {job.task_name}"
return
try:
# Run in executor if sync, otherwise await
if asyncio.iscoroutinefunction(task_func):
result = await task_func(*job.args, **job.kwargs)
else:
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(
self.executor,
lambda: task_func(*job.args, **job.kwargs)
)
job.status = JobStatus.COMPLETED
job.result = result
job.progress = 100
logger.info(f"Job completed: {job.id}")
except Exception as e:
job.status = JobStatus.FAILED
job.error = str(e)
logger.error(f"Job failed: {job.id} - {e}")
finally:
job.completed_at = datetime.utcnow().isoformat()
async def enqueue(
self,
task_name: str,
*args,
user_id: str = None,
priority: int = 0,
**kwargs
) -> Job:
"""Add a job to the queue."""
job = Job(
id=str(uuid.uuid4()),
task_name=task_name,
args=args,
kwargs=kwargs,
status=JobStatus.PENDING,
created_at=datetime.utcnow().isoformat(),
user_id=user_id,
priority=priority
)
self.jobs[job.id] = job
await self.queue.put(job.id)
logger.info(f"Job enqueued: {job.id} ({task_name})")
return job
def get_job(self, job_id: str) -> Optional[Job]:
"""Get a job by ID."""
return self.jobs.get(job_id)
def update_progress(self, job_id: str, progress: int):
"""Update job progress."""
job = self.jobs.get(job_id)
if job:
job.progress = min(100, max(0, progress))
def cancel_job(self, job_id: str) -> bool:
"""Cancel a pending job."""
job = self.jobs.get(job_id)
if job and job.status == JobStatus.PENDING:
job.status = JobStatus.CANCELLED
return True
return False
def get_user_jobs(self, user_id: str, limit: int = 20) -> list:
"""Get recent jobs for a user."""
user_jobs = [
j for j in self.jobs.values()
if j.user_id == user_id
]
return sorted(
user_jobs,
key=lambda j: j.created_at,
reverse=True
)[:limit]
# Global queue instance
job_queue = JobQueue()
# ==================== TASK DEFINITIONS ====================
@registry.register("bulk_analysis")
async def bulk_analysis_task(
contract_id: str,
clauses: list,
jurisdiction: str = "INTERNATIONAL"
) -> Dict[str, Any]:
"""
Analyze multiple clauses in bulk.
"""
from src.graph import compile_graph
results = []
app = compile_graph()
for i, clause in enumerate(clauses):
try:
state = {
"content": clause,
"jurisdiction": jurisdiction,
"execution_mode": "local"
}
result = app.invoke(state)
results.append({
"index": i,
"clause": clause[:100],
"risk_score": result.get("risk_score", 0),
"verdict": result.get("verdict", "UNKNOWN")
})
except Exception as e:
results.append({
"index": i,
"clause": clause[:100],
"error": str(e)
})
return {
"contract_id": contract_id,
"total_clauses": len(clauses),
"results": results,
"avg_risk": sum(r.get("risk_score", 0) for r in results) / len(results) if results else 0
}
@registry.register("generate_report")
async def generate_report_task(
analysis_id: str,
format: str = "pdf"
) -> Dict[str, Any]:
"""
Generate a detailed analysis report.
"""
# In production, this would generate actual reports
await asyncio.sleep(2) # Simulate work
return {
"analysis_id": analysis_id,
"format": format,
"url": f"/reports/{analysis_id}.{format}",
"generated_at": datetime.utcnow().isoformat()
}
@registry.register("export_data")
async def export_data_task(
user_id: str,
data_type: str,
format: str = "json"
) -> Dict[str, Any]:
"""
Export user data.
"""
await asyncio.sleep(1) # Simulate work
return {
"user_id": user_id,
"data_type": data_type,
"format": format,
"download_url": f"/exports/{user_id}_{data_type}.{format}",
"expires_at": datetime.utcnow().isoformat()
}
# ==================== CONVENIENCE FUNCTIONS ====================
async def run_background(
task_name: str,
*args,
user_id: str = None,
**kwargs
) -> Job:
"""
Convenience function to enqueue a background job.
Usage:
job = await run_background("bulk_analysis", contract_id, clauses)
print(f"Job ID: {job.id}")
"""
return await job_queue.enqueue(task_name, *args, user_id=user_id, **kwargs)
async def wait_for_job(job_id: str, timeout: int = 300) -> Optional[Job]:
"""
Wait for a job to complete.
Usage:
job = await wait_for_job(job_id, timeout=60)
if job.status == JobStatus.COMPLETED:
print(job.result)
"""
start = asyncio.get_event_loop().time()
while True:
job = job_queue.get_job(job_id)
if not job:
return None
if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
return job
if asyncio.get_event_loop().time() - start > timeout:
return job
await asyncio.sleep(0.5)
