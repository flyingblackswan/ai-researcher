from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from ...models.schemas import PaperRequest, JobResponse, StatusResponse
from ...services.paper_service import start_paper_job, paper_job_registry

router = APIRouter()


@router.post("/start", response_model=JobResponse)
async def start_paper(req: PaperRequest) -> JobResponse:
    """
    Kick off a new paper generation job.
    """
    return await start_paper_job(req)


@router.get("/{job_id}/status", response_model=StatusResponse)
async def get_status(job_id: str) -> StatusResponse:
    """
    Check the current status of a paper generation job.
    """
    job = await paper_job_registry.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    details: Dict[str, Any] = {
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "log_path": job.log_path,
        "artifacts": job.artifacts,
        "error": job.error,
    }
    return StatusResponse(status=job.status, details=details)


@router.get("/{job_id}/pdf")
async def get_pdf(job_id: str) -> Dict[str, Any]:
    """
    Return the expected PDF path/url for a completed paper job.
    """
    job = await paper_job_registry.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    pdf = None
    if job.artifacts:
        pdf = job.artifacts.get("pdf")
    return {"status": job.status, "pdf": pdf, "artifacts": job.artifacts}
