from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from ..models.schemas import ResearchRequest, JobResponse

# Import existing entry to leverage current orchestration
# We keep compatibility initially by controlling env vars instead of refactoring deeply.
import sys  # type: ignore
# Ensure project root (which contains main_ai_researcher.py) is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import main_ai_researcher as _mai  # type: ignore


@dataclass
class JobInfo:
    job_id: str
    status: str = "queued"  # queued | running | completed | error
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    log_path: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class JobRegistry:
    def __init__(self) -> None:
        self._jobs: Dict[str, JobInfo] = {}
        self._lock = asyncio.Lock()

    async def create(self) -> JobInfo:
        async with self._lock:
            job_id = uuid.uuid4().hex
            job = JobInfo(job_id=job_id)
            self._jobs[job_id] = job
            return job

    async def update(self, job_id: str, **kwargs) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for k, v in kwargs.items():
                setattr(job, k, v)
            job.updated_at = datetime.utcnow().isoformat()

    async def get(self, job_id: str) -> Optional[JobInfo]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def list(self) -> Dict[str, JobInfo]:
        async with self._lock:
            return dict(self._jobs)


job_registry = JobRegistry()


def _ensure_logs_dir() -> Path:
    root = Path(__file__).resolve().parents[3]  # repository root (AI-Researcher-main/)
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def _setup_job_logging(job: JobInfo) -> str:
    logs_dir = _ensure_logs_dir()
    log_file = logs_dir / f"research_{job.job_id}.log"

    # Configure root logger to append to this job's file (basic setup)
    # NOTE: Existing agent logger uses global_state.LOG_PATH; we set it below as well.
    for h in list(logging.getLogger().handlers):
        logging.getLogger().removeHandler(h)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )

    # Set global_state.LOG_PATH for existing logger machinery
    try:
        import global_state  # type: ignore
        global_state.LOG_PATH = str(log_file)
    except Exception:
        pass

    return str(log_file)


def _apply_request_env(req: ResearchRequest) -> None:
    """
    Bridge: set environment variables consumed by main_ai_researcher() paths.
    This maintains compatibility before full refactor.
    """
    if req.category:
        os.environ["CATEGORY"] = req.category
    if req.instance_id:
        os.environ["INSTANCE_ID"] = req.instance_id
    if req.task_level:
        os.environ["TASK_LEVEL"] = req.task_level
    if req.container_name:
        os.environ["CONTAINER_NAME"] = req.container_name
    if req.workplace_name:
        os.environ["WORKPLACE_NAME"] = req.workplace_name
    if req.cache_path:
        os.environ["CACHE_PATH"] = req.cache_path
    if req.port is not None:
        os.environ["PORT"] = str(req.port)
    if req.max_iter_times is not None:
        os.environ["MAX_ITER_TIMES"] = str(req.max_iter_times)
    if req.model:
        os.environ["COMPLETION_MODEL"] = req.model  # respected by research_agent.constant

    # Ensure required defaults if not provided via request or existing env
    # These mirror values present in .env.template to keep legacy code happy.
    os.environ.setdefault("PORT", os.getenv("PORT") or "7020")
    os.environ.setdefault("MAX_ITER_TIMES", os.getenv("MAX_ITER_TIMES") or "0")
    os.environ.setdefault("CONTAINER_NAME", os.getenv("CONTAINER_NAME") or "paper_eval")
    os.environ.setdefault("WORKPLACE_NAME", os.getenv("WORKPLACE_NAME") or "workplace")
    os.environ.setdefault("CACHE_PATH", os.getenv("CACHE_PATH") or "cache")


def _mode_to_backend(mode: str) -> str:
    if mode == "detailed_idea":
        return "Detailed Idea Description"
    if mode == "reference_based":
        return "Reference-Based Ideation"
    if mode == "paper_generation":
        return "Paper Generation Agent"
    return mode


async def run_research_bg(job_id: str, req: ResearchRequest) -> None:
    # Mark running, set up logging
    await job_registry.update(job_id, status="running")
    job = await job_registry.get(job_id)
    if not job:
        return
    log_path = _setup_job_logging(job)
    await job_registry.update(job_id, log_path=log_path)

    try:
        _apply_request_env(req)

        # Prepare arguments for main_ai_researcher
        mode = _mode_to_backend(req.mode.value)
        user_input = req.input or ""
        reference_text = ""
        if req.references:
            reference_text = "\n".join(req.references)

        logging.info(f"Starting research job {job_id} with mode={mode}")
        # Call existing entrypoint (blocking)
        result = _mai.main_ai_researcher(user_input, reference_text, mode)
        logging.info(f"Research job {job_id} finished")

        # Preserve structured artifacts if provided; otherwise, wrap result
        artifacts: Dict[str, Any]
        if isinstance(result, dict):
            artifacts = result
        elif result is None:
            artifacts = {"result": ""}
        else:
            artifacts = {"result": str(result)}

        await job_registry.update(job_id, status="completed", artifacts=artifacts)
    except Exception as e:
        logging.exception(f"Job {job_id} failed: {e}")
        await job_registry.update(job_id, status="error", error=str(e))


async def start_research_job(req: ResearchRequest) -> JobResponse:
    job = await job_registry.create()
    # Spawn background task
    asyncio.create_task(run_research_bg(job.job_id, req))
    return JobResponse(job_id=job.job_id, status="queued", message="Research job queued")
