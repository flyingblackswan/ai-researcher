from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
import os

from dotenv import load_dotenv, find_dotenv, set_key, unset_key
from ...models.schemas import (
    ConfigListResponse,
    ConfigListedItem,
    ConfigSetRequest,
    ConfigBulkSetRequest,
)

router = APIRouter()


def _load_all_env() -> Dict[str, str]:
    """
    Load env vars with precedence:
    1) .env (explicitly loaded)
    2) Process environment
    """
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)

    # Build merged map: start from OS, then overlay with .env file entries to mark source
    env_map: Dict[str, str] = {}
    env_map.update(os.environ)
    return env_map


@router.get("", response_model=ConfigListResponse)
async def list_config() -> ConfigListResponse:
    """
    List environment variables useful to the system.
    Note: This currently returns all variables; a future refinement could filter to a known allowlist.
    """
    items: List[ConfigListedItem] = []
    env_map = _load_all_env()

    for k, v in env_map.items():
        # Mask obvious secrets minimally (display only length)
        display_v = v
        if any(s in k.lower() for s in ["key", "token", "secret", "password"]):
            if v:
                display_v = f"<hidden:len={len(v)}>"

        items.append(ConfigListedItem(key=k, value=display_v, source="process/.env"))
    return ConfigListResponse(items=items)


@router.post("/set")
async def set_config(req: ConfigSetRequest) -> Dict[str, Any]:
    """
    Set a single key in .env file and process env.
    """
    if not req.key:
        raise HTTPException(status_code=400, detail="key is required")

    dotenv_path = find_dotenv(usecwd=True)
    if not dotenv_path:
        # Create a new .env in project root
        dotenv_path = os.path.join(os.getcwd(), ".env")
        open(dotenv_path, "a", encoding="utf-8").close()

    set_key(dotenv_path, req.key, req.value or "")
    os.environ[req.key] = req.value or ""
    return {"status": "ok", "message": f"Set {req.key}"}


@router.post("/bulk-set")
async def bulk_set_config(req: ConfigBulkSetRequest) -> Dict[str, Any]:
    """
    Set multiple keys in .env file and process env.
    """
    dotenv_path = find_dotenv(usecwd=True)
    if not dotenv_path:
        dotenv_path = os.path.join(os.getcwd(), ".env")
        open(dotenv_path, "a", encoding="utf-8").close()

    for item in req.items:
        if item.key:
            set_key(dotenv_path, item.key, item.value or "")
            os.environ[item.key] = item.value or ""
    return {"status": "ok", "message": f"Set {len(req.items)} keys"}
