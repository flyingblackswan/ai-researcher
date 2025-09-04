from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

from ..models.schemas import LogEvent, LogEventType
from .research_service import job_registry
from .paper_service import paper_job_registry


def _get_log_path(job_type: str, job_id: str) -> Optional[Path]:
    if job_type == "research":
        reg = job_registry
    elif job_type == "paper":
        reg = paper_job_registry
    else:
        return None

    # NOTE: job_registry.get is async
    # This is a small helper used only in async context in stream_logs
    raise NotImplementedError("Use stream_logs() which resolves log_path internally.")


async def stream_logs(job_type: str, job_id: str) -> AsyncIterator[str]:
    """
    Async generator that yields JSONL LogEvent strings for a job's log file.
    Sends existing file contents from current end (tail -f style), then streams new lines.
    """
    registry = job_registry if job_type == "research" else paper_job_registry if job_type == "paper" else None
    if registry is None:
        # yield error event
        yield json.dumps(
            LogEvent(
                type=LogEventType.error,
                timestamp=datetime.utcnow().isoformat(),
                message=f"Unknown job type: {job_type}",
                job_id=job_id,
            ).model_dump()
        )
        return

    job = await registry.get(job_id)
    if not job or not job.log_path:
        yield json.dumps(
            LogEvent(
                type=LogEventType.error,
                timestamp=datetime.utcnow().isoformat(),
                message="Job not found or log path unavailable",
                job_id=job_id,
            ).model_dump()
        )
        return

    log_path = Path(job.log_path)
    # Ensure file exists
    if not log_path.exists():
        # Wait a bit if just created
        for _ in range(10):
            await asyncio.sleep(0.2)
            if log_path.exists():
                break

    try:
        with log_path.open("r", encoding="utf-8", errors="ignore") as f:
            # Seek to end to provide live-only logs by default.
            # If you prefer to replay last N lines, implement a ring buffer or read tail().
            f.seek(0, os.SEEK_END)

            # Emit initial status event
            yield json.dumps(
                LogEvent(
                    type=LogEventType.status,
                    timestamp=datetime.utcnow().isoformat(),
                    message=f"Connected to {job_type} job {job_id} logs",
                    job_id=job_id,
                ).model_dump()
            )

            while True:
                line = f.readline()
                if line:
                    event = LogEvent(
                        type=LogEventType.log,
                        timestamp=datetime.utcnow().isoformat(),
                        message=line.rstrip("\n"),
                        job_id=job_id,
                    )
                    yield json.dumps(event.model_dump())
                else:
                    await asyncio.sleep(0.2)
    except Exception as e:
        yield json.dumps(
            LogEvent(
                type=LogEventType.error,
                timestamp=datetime.utcnow().isoformat(),
                message=f"Error reading log file: {e}",
                job_id=job_id,
            ).model_dump()
        )
