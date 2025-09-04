# AI-Researcher Backend API

Headless FastAPI backend exposing stable endpoints for research workflows, paper generation, configuration, and real-time log streaming. The original Gradio frontend has been decoupled and removed. You can build any new frontend (React, Vue, Angular, mobile) against these APIs.

## Run the API

- Ensure dependencies are installed (see setup.cfg requirements for FastAPI/Uvicorn/etc.).
- Start the server:

```bash
uvicorn backend.app.main:app --reload --port 7039
```

Health check:
```bash
curl http://127.0.0.1:7039/health
```

## CORS

CORS is permissive by default for development. In production, set allowlisted origins via environment configuration and adjust main.py.

## API Overview

Base URL: http://127.0.0.1:7039

- Research jobs
  - POST /api/v1/research/start
  - GET  /api/v1/research/{job_id}/status
  - GET  /api/v1/research/{job_id}/artifacts
- Paper jobs
  - POST /api/v1/paper/start
  - GET  /api/v1/paper/{job_id}/status
  - GET  /api/v1/paper/{job_id}/pdf
- Config
  - GET  /api/v1/config
  - POST /api/v1/config/set
  - POST /api/v1/config/bulk-set
- Logs (WebSocket)
  - WS   /api/v1/logs/research/{job_id}
  - WS   /api/v1/logs/paper/{job_id}

## Schemas

### ResearchRequest (JSON)
```json
{
  "mode": "detailed_idea | reference_based",
  "input": "string (required for detailed_idea)",
  "references": ["string", "string"],
  "category": "vq | gnn | diffu_flow | reasoning | recommendation",
  "instance_id": "string",
  "task_level": "task1 | task2",
  "model": "string",
  "container_name": "string",
  "workplace_name": "string",
  "cache_path": "string",
  "port": 12345,
  "max_iter_times": 0
}
```

### PaperRequest (JSON)
```json
{
  "research_field": "vq",
  "instance_id": "one_layer_vq"
}
```

### JobResponse
```json
{
  "job_id": "abc123",
  "status": "queued",
  "message": "Research job queued"
}
```

### StatusResponse
```json
{
  "status": "queued | running | completed | error",
  "details": {
    "created_at": "...",
    "updated_at": "...",
    "log_path": "path/to/logfile",
    "artifacts": { "result": "..." },
    "error": "optional error text"
  }
}
```

## Usage Examples

### Submit Detailed Idea Research (Level 1)
```bash
curl -X POST http://127.0.0.1:7039/api/v1/research/start \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "detailed_idea",
    "input": "Design a rotated VQ-VAE improvement with better gradient flow.",
    "category": "vq",
    "instance_id": "one_layer_vq",
    "task_level": "task1",
    "container_name": "paper_eval",
    "workplace_name": "workplace",
    "cache_path": "cache",
    "port": 12372,
    "max_iter_times": 0
  }'
```

### Submit Reference-Based Research (Level 2)
```bash
curl -X POST http://127.0.0.1:7039/api/v1/research/start \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "reference_based",
    "references": [
      "Neural discrete representation learning",
      "Straightening out the straight-through estimator"
    ],
    "category": "vq",
    "instance_id": "one_layer_vq",
    "task_level": "task2"
  }'
```

### Check Job Status
```bash
curl http://127.0.0.1:7039/api/v1/research/{job_id}/status
```

### Get Artifacts
```bash
curl http://127.0.0.1:7039/api/v1/research/{job_id}/artifacts
```

### Start Paper Generation
```bash
curl -X POST http://127.0.0.1:7039/api/v1/paper/start \
  -H "Content-Type: application/json" \
  -d '{"research_field":"vq","instance_id":"one_layer_vq"}'
```

### Check Paper Status
```bash
curl http://127.0.0.1:7039/api/v1/paper/{job_id}/status
```

### Get Expected PDF Path
```bash
curl http://127.0.0.1:7039/api/v1/paper/{job_id}/pdf
```

## Log Streaming (WebSocket)

Connect with a WebSocket client:

- Research logs:
  - ws://127.0.0.1:7039/api/v1/logs/research/{job_id}
- Paper logs:
  - ws://127.0.0.1:7039/api/v1/logs/paper/{job_id}

Messages are JSONL with shape:
```json
{
  "type": "log | status | error",
  "timestamp": "ISO8601",
  "message": "text",
  "job_id": "{job_id}"
}
```

## Environment

You can manage environment variables via /api/v1/config endpoints or by editing .env directly. Consider these keys (existing template):
- CATEGORY, INSTANCE_ID, TASK_LEVEL, CONTAINER_NAME, WORKPLACE_NAME, CACHE_PATH, PORT, MAX_ITER_TIMES, COMPLETION_MODEL, GPUS, OPENROUTER_API_KEY, etc.

You may also introduce:
- API_PORT (backend port)
- CORS_ORIGINS (comma-separated)
- LOG_DIR (custom logs directory)

## Notes

- At this stage, the backend bridges to existing orchestration in `main_ai_researcher.py`. A future refactor will make `run_research()` a pure callable without `os.chdir` and with structured return values.
- The legacy Gradio UI (`web_ai_researcher.py`) and web GUI assets have been removed as part of decoupling.
