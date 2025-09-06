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
from research_agent.config import settings




paper_job_registry = JobRegistry()


from research_agent.logger_config import setup_logging

async def run_paper_bg(job_id: str, req: PaperRequest) -> None:
    await paper_job_registry.update(job_id, status="running")
    setup_logging(job_id)

    try:
        if req.research_field:
            settings.CATEGORY = req.research_field
        if req.instance_id:
            settings.INSTANCE_ID = req.instance_id

        mode = "Paper Generation Agent"
        logging.info(f"Starting paper job {job_id} for field={req.research_field}, instance={req.instance_id}")
        result = run_ai_researcher("", "", mode)
        logging.info(f"Paper job {job_id} finished with result: {result}")

        # Common paper path convention as used by web_ui:
        # PAPER_FILE = f'{category}/target_sections/{instance_id}/iclr2025_conference.pdf'
        category = settings.CATEGORY
        instance_id = settings.INSTANCE_ID
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
