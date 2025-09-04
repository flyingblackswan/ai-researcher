from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ModeEnum(str, Enum):
    detailed_idea = "detailed_idea"
    reference_based = "reference_based"
    paper_generation = "paper_generation"


class ResearchRequest(BaseModel):
    mode: ModeEnum = Field(..., description="Research mode: detailed_idea or reference_based")
    input: Optional[str] = Field(None, description="User prompt/idea (required for detailed_idea)")
    references: Optional[List[str]] = Field(None, description="List of references (required for reference_based)")
    category: Optional[str] = Field(None, description="Benchmark category, e.g., vq | gnn | diffu_flow | reasoning | recommendation")
    instance_id: Optional[str] = Field(None, description="Benchmark instance identifier")
    task_level: Optional[str] = Field(None, description="task1 | task2")
    model: Optional[str] = Field(None, description="LLM model override")
    container_name: Optional[str] = Field(None, description="Container name for experiments")
    workplace_name: Optional[str] = Field(None, description="Workspace name")
    cache_path: Optional[str] = Field(None, description="Cache directory path")
    port: Optional[int] = Field(None, description="Service port used by internal components")
    max_iter_times: Optional[int] = Field(None, description="Maximum iteration count for the agent")


class PaperRequest(BaseModel):
    research_field: str = Field(..., description="Domain e.g., vq")
    instance_id: str = Field(..., description="Instance id to generate paper for")


class ConfigItem(BaseModel):
    key: str
    value: str


class ConfigSetRequest(BaseModel):
    key: str
    value: str


class ConfigBulkSetRequest(BaseModel):
    items: List[ConfigItem]


class JobResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="queued | running | completed | error")
    message: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class FileResponse(BaseModel):
    download_url: str


class ConfigListedItem(BaseModel):
    key: str
    value: str
    source: str


class ConfigListResponse(BaseModel):
    items: List[ConfigListedItem] = Field(default_factory=list)


# WebSocket streaming payloads
class LogEventType(str, Enum):
    log = "log"
    status = "status"
    error = "error"


class LogEvent(BaseModel):
    type: LogEventType
    timestamp: str
    message: str
    tool: Optional[str] = None
    job_id: Optional[str] = None
