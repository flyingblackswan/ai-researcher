from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from ..models.schemas import PaperRequest, JobResponse
from .research_service import JobRegistry, JobInfo  # reuse same registry pattern and JobInfo
from orchestration import run_ai_researcher




paper_job_registry = JobRegistry()


def _ensure_logs_dir() -> Path:
    root = Path(__file__).resolve().parents[3]  # repository root (AI-Researcher-main/)
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def _setup_job_logging(job: JobInfo) -> str:
    logs_dir = _ensure_logs_dir()
    log_file = logs_dir / f"paper_{job.job_id}.log"

    # Basic logging setup per job
    for h in list(logging.getLogger().handlers):
        logging.getLogger().removeHandler(h)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )

    return str(log_file)


async def run_paper_bg(job_id: str, req: PaperRequest) -> None:
    await paper_job_registry.update(job_id, status="running")
    job = await paper_job_registry.get(job_id)
    if not job:
        return
    log_path = _setup_job_logging(job)
    await paper_job_registry.update(job_id, log_path=log_path)

    try:
        # Bridge to existing paper entry point in main_ai_researcher (Paper Generation Agent)
        # It reads env CATEGORY/INSTANCE_ID, so set them here.
        if req.research_field:
            os.environ["CATEGORY"] = req.research_field
        if req.instance_id:
            os.environ["INSTANCE_ID"] = req.instance_id


        mode = "Paper Generation Agent"
        logging.info(f"Starting paper job {job_id} for field={req.research_field}, instance={req.instance_id}")
        result = run_ai_researcher("", "", mode)
        logging.info(f"Paper job {job_id} finished with result: {result}")

        # Common paper path convention as used by web_ui:
        # PAPER_FILE = f'{category}/target_sections/{instance_id}/iclr2025_conference.pdf'
        category = os.getenv("CATEGORY", req.research_field)
        instance_id = os.getenv("INSTANCE_ID", req.instance_id)
        expected_pdf = f"{category}/target_sections/{instance_id}/iclr2025_conference.pdf"

        await paper_job_registry.update(job_id, status="completed", artifacts={
            "result": str(result or ""),
            "pdf": expected_pdf
        })
    except Exception as e:
        logging.exception(f"Paper job {job_id} failed: {e}")
        await paper_job_registry.update(job_id, status="error", error=str(e))


async def start_paper_job(req: PaperRequest) -> JobResponse:
    job = await paper_job_registry.create()
    asyncio.create_task(run_paper_bg(job.job_id, req))
    return JobResponse(job_id=job.job_id, status="queued", message="Paper job queued")
