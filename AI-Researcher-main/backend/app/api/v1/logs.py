from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...services.log_service import stream_logs

router = APIRouter()


@router.websocket("/{job_type}/{job_id}")
async def websocket_logs(websocket: WebSocket, job_type: str, job_id: str):
    """
    WebSocket endpoint for streaming logs in real-time.

    Connect example:
    ws://localhost:7039/api/v1/logs/research/{job_id}
    ws://localhost:7039/api/v1/logs/paper/{job_id}
    """
    await websocket.accept()
    try:
        async for event_json in stream_logs(job_type, job_id):
            await websocket.send_text(event_json)
    except WebSocketDisconnect:
        # Client disconnected; just exit gracefully
        return
    except Exception as e:
        # Attempt to notify client about server-side errors
        try:
            await websocket.send_text(f'{{"type":"error","message":"{str(e)}"}}')
        except Exception:
            pass
