from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from ...models.schemas import ResearchRequest, JobResponse, StatusResponse
from ...services.research_service import start_research_job, job_registry

router = APIRouter()


@router.post("/start", response_model=JobResponse)
async def start_research(req: ResearchRequest) -> JobResponse:
    """
    Kick off a new research job (Level 1 detailed_idea or Level 2 reference_based).
    """
    return await start_research_job(req)


@router.get("/{job_id}/status", response_model=StatusResponse)
async def get_status(job_id: str) -> StatusResponse:
    """
    Check the current status of a research job.
    """
    job = await job_registry.get(job_id)
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


@router.get("/{job_id}/artifacts")
async def get_artifacts(job_id: str) -> Dict[str, Any]:
    """
    Return produced artifacts for a research job (paths / results).
    """
    job = await job_registry.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status not in ("completed", "error"):
        # You may still expose partial artifacts, but keep simple for now
        return {"status": job.status, "artifacts": job.artifacts}
    return {"status": job.status, "artifacts": job.artifacts}
