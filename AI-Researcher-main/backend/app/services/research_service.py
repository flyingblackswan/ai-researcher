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

from orchestration import run_ai_researcher


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


from research_agent.config import settings

def _update_settings(req: ResearchRequest):
    """Update settings from the request."""
    if req.category:
        settings.CATEGORY = req.category
    if req.instance_id:
        settings.INSTANCE_ID = req.instance_id
    if req.task_level:
        settings.TASK_LEVEL = req.task_level
    if req.container_name:
        settings.CONTAINER_NAME = req.container_name
    if req.workplace_name:
        settings.WORKPLACE_NAME = req.workplace_name
    if req.cache_path:
        settings.CACHE_PATH = req.cache_path
    if req.port is not None:
        settings.PORT = req.port
    if req.max_iter_times is not None:
        settings.MAX_ITER_TIMES = req.max_iter_times
    if req.model:
        settings.COMPLETION_MODEL = req.model


def _mode_to_backend(mode: str) -> str:
    if mode == "detailed_idea":
        return "Detailed Idea Description"
    if mode == "reference_based":
        return "Reference-Based Ideation"
    if mode == "paper_generation":
        return "Paper Generation Agent"
    return mode


from research_agent.logger_config import setup_logging

async def run_research_bg(job_id: str, req: ResearchRequest) -> None:
    # Mark running
    await job_registry.update(job_id, status="running")
    setup_logging(job_id)

    try:
        _update_settings(req)

        # Prepare arguments for main_ai_researcher
        mode = _mode_to_backend(req.mode.value)
        user_input = req.input or ""
        reference_text = ""
        if req.references:
            reference_text = "\n".join(req.references)

        logging.info(f"Starting research job {job_id} with mode={mode}")
        # Call existing entrypoint (blocking)
        result = run_ai_researcher(user_input, reference_text, mode)
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
