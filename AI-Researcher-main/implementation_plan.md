# Implementation Plan

[Overview]
Separate the frontend from the backend by removing the Gradio-based UI and introducing a clean FastAPI backend with well-defined REST/WebSocket interfaces, enabling a completely new, independent frontend to be built later.

This plan decouples presentation from core research logic. The backend will expose stable APIs for triggering research workflows (Level 1 and Level 2), paper generation, environment/config management, file operations (upload/download), and real-time log streaming. All UI-specific code and assets will be removed from the repository to enforce a strict separation of concerns. The system will become easier to test, deploy, and integrate with any modern frontend framework (React, Vue, Angular, Flutter, etc.).

[Types]  
Introduce explicit API schemas and internal service types using Pydantic models and enums.

Detailed type definitions:
- Enums:
  - ModeEnum: {"detailed_idea", "reference_based", "paper_generation"}

- Request Schemas (backend/app/models/schemas.py):
  - ResearchRequest:
    - mode: ModeEnum ("detailed_idea" | "reference_based")
    - input: str (the prompt/idea; required for detailed_idea)
    - references: list[str] (raw references text or IDs; required for reference_based)
    - category: str (e.g., "vq" | "gnn" | "diffu_flow" | "reasoning" | "recommendation")
    - instance_id: str
    - task_level: str ("task1" | "task2")
    - model: str (optional override)
    - container_name: str
    - workplace_name: str
    - cache_path: str
    - port: int
    - max_iter_times: int
  - PaperRequest:
    - research_field: str (e.g., "vq")
    - instance_id: str
  - ConfigSetRequest:
    - key: str
    - value: str
  - ConfigBulkSetRequest:
    - items: list[{ key: str, value: str }]

- Response Schemas:
  - JobResponse:
    - job_id: str
    - status: str ("queued" | "running" | "completed" | "error")
    - message: str
  - StatusResponse:
    - status: str
    - details: dict
  - FileResponse:
    - download_url: str
  - ConfigListResponse:
    - items: list[{ key: str, value: str, source: str }]

- Streaming Event Payload (WebSocket):
  - LogEvent:
    - type: "log" | "status" | "error"
    - timestamp: str (ISO)
    - message: str
    - tool?: str
    - job_id?: str


[Files]
Create a new backend service and remove Gradio UI and assets.

Detailed breakdown:
- New files to be created:
  - AI-Researcher-main/backend/app/main.py
    - Purpose: FastAPI application entrypoint; include lifespan handlers; mount routers; CORS.
  - AI-Researcher-main/backend/app/api/v1/research.py
    - Purpose: REST endpoints:
      - POST /api/v1/research/start (ResearchRequest) → JobResponse
      - GET /api/v1/research/{job_id}/status → StatusResponse
      - GET /api/v1/research/{job_id}/artifacts → list of downloadable paths
  - AI-Researcher-main/backend/app/api/v1/paper.py
    - Purpose: REST endpoints:
      - POST /api/v1/paper/start (PaperRequest) → JobResponse
      - GET /api/v1/paper/{job_id}/status → StatusResponse
      - GET /api/v1/paper/{job_id}/pdf → File download/URL
  - AI-Researcher-main/backend/app/api/v1/config.py
    - Purpose: REST endpoints for env/config:
      - GET /api/v1/config → ConfigListResponse
      - POST /api/v1/config/set (ConfigSetRequest)
      - POST /api/v1/config/bulk-set (ConfigBulkSetRequest)
  - AI-Researcher-main/backend/app/api/v1/logs.py
    - Purpose: WebSocket endpoint:
      - WS /api/v1/logs/{job_id} → live log streaming
  - AI-Researcher-main/backend/app/models/schemas.py
    - Purpose: Pydantic models: ModeEnum, ResearchRequest, PaperRequest, Config requests, responses.
  - AI-Researcher-main/backend/app/core/config.py
    - Purpose: Centralized settings using Pydantic BaseSettings (API_BASE_URL, PORT, COMPLETION_MODEL, etc.), .env loading.
  - AI-Researcher-main/backend/app/core/logging.py
    - Purpose: Structured logging configuration; integrate with existing logger if possible.
  - AI-Researcher-main/backend/app/services/research_service.py
    - Purpose: Service wrapper that calls refactored research execution; non-UI orchestration; background task mgmt; job registry.
  - AI-Researcher-main/backend/app/services/paper_service.py
    - Purpose: Service wrapper for paper generation; background task mgmt; job registry.
  - AI-Researcher-main/backend/app/services/log_service.py
    - Purpose: Log file tailing and emission to WebSocket; integrate with existing global_state.LOG_PATH where applicable.
  - AI-Researcher-main/backend/README_API.md
    - Purpose: API usage documentation and examples (curl/httpie).

- Existing files to be modified:
  - AI-Researcher-main/main_ai_researcher.py
    - Changes:
      - Extract and export pure functions:
        - run_research(input: str, reference: str, mode: str, args: argparse.Namespace|dict) -> dict
        - Avoid os.chdir side effects; use absolute/relative paths without changing global CWD.
        - Make it thread-safe for API server (no global mutable flips that cross-requests).
      - Do not directly read env inside function; accept a config object/args (injected by services).
  - AI-Researcher-main/global_state.py
    - Changes:
      - Remove UI-specific fields or make them optional.
      - Ensure no process-global flags break concurrent API requests (e.g., INIT_FLAG).
      - Consider replacing with per-job state tracked by services.
  - AI-Researcher-main/research_agent/constant.py
    - Changes:
      - Ensure configuration reads are compatible with API-injected settings (do not depend on Gradio).
      - Confirm DEFAULT_LOG/LOG_PATH interplay works headlessly.
  - AI-Researcher-main/README.md
    - Changes:
      - Remove Web GUI section and images; add new "Backend API" section with startup instructions (uvicorn) and sample requests.

- Files to be deleted or moved:
  - Delete: AI-Researcher-main/web_ai_researcher.py (Gradio UI)
  - Delete: AI-Researcher-main/assets/webgui/ (all UI-only screenshots)
  - Delete: Any UI-specific CSS/JS embedded references (none detected besides assets)
  - Optional: keep generic assets used in docs (logo.png, framework diagram) if desired by docs; but remove pure webgui assets.

- Configuration file updates:
  - AI-Researcher-main/setup.cfg
    - Remove: gradio
    - Add/ensure: fastapi, uvicorn[standard], pydantic, pydantic-settings, websockets, python-multipart
  - AI-Researcher-main/.env.template
    - Add: API_PORT (e.g., 7039 or configurable), CORS_ORIGINS, LOG_DIR
  - AI-Researcher-main/docker/ (optional follow-up)
    - Provide a Dockerfile variant to run the API server and expose the port.


[Functions]
Add service-layer functions and refactor main entry functions to pure callables.

Detailed breakdown:
- New functions:
  - backend/app/services/research_service.py
    - def start_research_job(req: ResearchRequest) -> JobResponse
      - Creates a job_id, spawns background task, wires logging, calls run_research()
    - async def run_research_bg(job_id: str, req: ResearchRequest) -> None
      - Converts request to args/namespace expected by research agents; calls run_infer_plan/main or run_infer_idea.main based on mode; updates job registry and log stream
  - backend/app/services/paper_service.py
    - def start_paper_job(req: PaperRequest) -> JobResponse
    - async def run_paper_bg(job_id: str, req: PaperRequest) -> None
  - backend/app/services/log_service.py
    - def tail_log(job_id: str) -> AsyncIterator[LogEvent]
    - def emit(job_id: str, message: str, type: str = "log") -> None

- Modified functions:
  - AI-Researcher-main/main_ai_researcher.py
    - def main_ai_researcher(input, reference, mode): split into:
      - def run_research(input, reference, mode, args) -> dict
        - No os.chdir; use import paths, or compute subpaths (Path(__file__).parent / "research_agent")
        - Return structured result (status, artifacts paths), not only side-effects
  - Any direct UI-coupled getters in web_ai_researcher to be removed.

- Removed functions:
  - All Gradio UI-specific functions in web_ai_researcher.py:
    - create_ui(), process_with_live_logs(), env table UI handlers, etc.
  - Any log polling tailored to UI markup should be dropped. Logging should be plain text or structured events.


[Classes]
Introduce schemas and optional service registries; do not add heavy class hierarchies beyond necessity.

Detailed breakdown:
- New classes:
  - Pydantic models in backend/app/models/schemas.py (see [Types])
  - Optional: JobRegistry (simple class) in services to keep job statuses and artifact paths in-memory:
    - fields: { job_id -> { status, start_time, end_time, log_path, artifacts } }
    - thread-safe via asyncio locks

- Modified classes:
  - None required in existing code; ensure existing MetaChain logger can be used without UI.

- Removed classes:
  - None (web_ai_researcher had mostly functions, not classes).


[Dependencies]
Switch UI stack from Gradio to FastAPI; remove UI-only deps.

Details:
- Add (setup.cfg install_requires):
  - fastapi>=0.115.0
  - uvicorn[standard]>=0.30.0
  - pydantic>=2.6.0
  - pydantic-settings>=2.3.0
  - websockets>=12.0
  - python-multipart>=0.0.9  (for file uploads)
- Remove:
  - gradio
- Keep:
  - litellm==1.55.0 and existing core dependencies
- Optional:
  - httpx>=0.27.0 (for integration tests)
  - starlette>=0.37.0 (FastAPI base, usually pulled transitively)


[Testing]
Adopt API-first testing with pytest and httpx.

Test requirements:
- New tests:
  - tests/api/test_research.py
    - POST /api/v1/research/start (both modes), then poll status until finished
    - Validate artifacts listing
  - tests/api/test_paper.py
    - POST /api/v1/paper/start, poll, then download PDF
  - tests/api/test_config.py
    - GET/POST config endpoints lifecycle
  - tests/api/test_logs.py
    - WebSocket connect; assert receipt of log events

Existing test modifications:
- None mandatory, but remove or mark skip any UI-related tests.

Validation strategies:
- Use FastAPI TestClient / httpx.AsyncClient for endpoint tests
- Mock long-running jobs for unit speed; add an E2E profile to run a minimal sample instance


[Implementation Order]
Implement backend first, then remove frontend, then finalize dependencies and docs.

Numbered steps:
1. Scaffolding: Create backend/app structure (main.py, core, api, models, services).
2. Schemas: Implement Pydantic models (ModeEnum, ResearchRequest, PaperRequest, responses).
3. Services: Implement research_service and paper_service wrappers that call refactored run_research and paper writing.
4. Refactor main_ai_researcher.run_research: make it pure and safe (no os.chdir; return structured results).
5. WebSocket: Implement logs.py WS endpoint; wire log_service tailing of per-job logs.
6. API Routers: Implement research.py, paper.py, config.py; mount in main.py with CORS.
7. Dependency updates: setup.cfg update (remove gradio; add fastapi/uvicorn/etc.); .env.template additions.
8. Remove UI: Delete web_ai_researcher.py and assets/webgui/*; purge UI references from README.md.
9. Docs: Add backend/README_API.md and update top-level README with API usage and uvicorn run command.
10. Tests: Add tests/api/* and run CI locally.
11. Smoke test: Start server (uvicorn backend.app.main:app --reload --port 7039) and run a minimal job end-to-end.
