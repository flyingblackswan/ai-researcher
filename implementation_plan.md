# Implementation Plan

[Overview]
Design and deliver a Bauhaus 2.0-inspired, decoupled web frontend that consumes the existing FastAPI backend to provide psychologically minimalist, adaptive, and ethically persuasive UX for research and paper generation workflows.

This frontend will be a modern SPA focusing on cognitive sustainability: reducing decision fatigue, guiding attention with functional ornament, and enabling flow-state usage across devices. It consumes the established REST endpoints and WebSocket log streams, surfacing system reasoning and progress in a humane way. The visual and behavioral system will be composed from design tokens, variable typography, and responsive grids that adapt to user context and usage patterns. Micro-animations are applied strictly where they serve comprehension or feedback, not ornament for its own sake. The project retains the headless backend with CORS and environment-driven configuration to support seamless local development and production deployment.

[Types]  
Type-safe API and UI contracts using TypeScript, with Zod runtime validation for critical payloads.

- Enums and Unions
  - type ModeEnum = "detailed_idea" | "reference_based" | "paper_generation"
  - type JobStatus = "queued" | "running" | "completed" | "error"
  - type LogEventType = "log" | "status" | "error"

- Backend-aligned API Models (TypeScript)
  - interface ResearchRequest {
      mode: ModeEnum
      input?: string
      references?: string[]
      category?: string
      instance_id?: string
      task_level?: string
      model?: string
      container_name?: string
      workplace_name?: string
      cache_path?: string
      port?: number
      max_iter_times?: number
    }
  - interface PaperRequest {
      research_field: string
      instance_id: string
    }
  - interface JobResponse {
      job_id: string
      status: JobStatus
      message?: string
    }
  - interface StatusResponse {
      status: JobStatus
      details: {
        created_at?: string
        updated_at?: string
        log_path?: string
        artifacts?: Record<string, any>
        error?: string | null
      }
    }
  - interface FileResponse {
      download_url: string
    }
  - interface ConfigItem {
      key: string
      value: string
    }
  - interface ConfigListResponse {
      items: { key: string; value: string; source: string }[]
    }
  - interface LogEvent {
      type: LogEventType
      timestamp: string
      message: string
      tool?: string
      job_id?: string
    }

- UI/State Types
  - interface JobListItem { id: string; type: "research" | "paper"; status: JobStatus; created_at?: string; label?: string }
  - interface Toast { id: string; title: string; description?: string; variant?: "info" | "success" | "warning" | "error" }
  - interface ThemeTokens { color: Record<string, string>; radius: Record<string, string>; space: Record<string, string>; font: { body: string; mono: string }; motion: { duration: Record<string, number>; easing: Record<string, string> } }

- Zod schemas (for critical payloads, especially incoming WS events)
  - const ZLogEvent = z.object({
      type: z.enum(["log","status","error"]),
      timestamp: z.string(),
      message: z.string(),
      tool: z.string().optional(),
      job_id: z.string().optional()
    })
  - const ZJobResponse = z.object({ job_id: z.string(), status: z.enum(["queued","running","completed","error"]), message: z.string().optional() })
  - const ZStatusResponse = z.object({ status: z.enum(["queued","running","completed","error"]), details: z.record(z.any()).default({}) })

[Files]
Create a new frontend/ application and minimally adjust backend config for CORS and documentation.

- New files to be created
  - frontend/.gitignore
  - frontend/.env.example
    - VITE_API_BASE=http://127.0.0.1:7039
  - frontend/index.html
  - frontend/package.json
  - frontend/tsconfig.json
  - frontend/vite.config.ts
  - frontend/postcss.config.js
  - frontend/tailwind.config.ts
  - frontend/src/main.tsx
  - frontend/src/App.tsx
  - frontend/src/index.css (imports tailwind base/components/utilities)
  - frontend/src/styles/tokens.css (CSS variables for Bauhaus 2.0 tokens: colors, space, radius, motion)
  - frontend/src/theme/theme.ts (ThemeTokens, computed tokens, helpers)
  - frontend/src/router.tsx (React Router or TanStack Router setup)
  - frontend/src/api/client.ts (base fetch wrapper; injects API base; handles errors)
  - frontend/src/api/research.ts (startResearch, getResearchStatus, getResearchArtifacts)
  - frontend/src/api/paper.ts (startPaper, getPaperStatus, getPaperPdf)
  - frontend/src/api/config.ts (getConfig, setConfig, bulkSetConfig)
  - frontend/src/lib/ws.ts (connectLogs(jobType, jobId): WebSocket wrapper with reconnection and Zod validation)
  - frontend/src/store/appStore.ts (Zustand or Jotai store for toasts, theme, recent jobs)
  - frontend/src/components/JobStatusBadge.tsx
  - frontend/src/components/LogStream.tsx (virtualized list using auto-sizing; functional ornament for log feedback)
  - frontend/src/components/FormField.tsx, frontend/src/components/Toolbar.tsx, frontend/src/components/Toast.tsx
  - frontend/src/pages/Dashboard.tsx (cards to start flows; recent jobs; cognitive minimalism)
  - frontend/src/pages/ResearchStart.tsx (progressive disclosure between detailed_idea and reference_based)
  - frontend/src/pages/ResearchJob.tsx (status polling + WS log stream + artifacts)
  - frontend/src/pages/PaperStart.tsx
  - frontend/src/pages/PaperJob.tsx
  - frontend/src/pages/Config.tsx (masked values, edit interactions with confirmation)
  - frontend/src/assets/fonts/inter-variable.woff2 (or via @fontsource-variable/inter)
  - frontend/src/hooks/useFlowHints.ts (anti-addictive cues: break prompts, reduced-contrast nudge after long sessions)
  - frontend/src/hooks/useAdaptiveTypography.ts (variable font adjustments based on time of day and reading speed)
  - frontend/src/hooks/useProgressiveDisclosure.ts (contextual UI simplification)

- Existing files to be modified
  - backend/app/main.py
    - Parse CORS_ORIGINS from env (comma-separated) and configure allow_origins accordingly instead of "*".
  - .env.template
    - Document frontend dev URL examples for CORS_ORIGINS (e.g., http://localhost:5173,http://127.0.0.1:5173).
  - backend/README_API.md
    - Add “Frontend Integration” section describing expected VITE_API_BASE and WS base.

- Files to be deleted or moved
  - None (legacy frontend already removed).

- Configuration file updates
  - Add Tailwind, PostCSS, ESLint/Prettier configuration in frontend/.
  - Optionally add GitHub Actions workflow for frontend build.

[Functions]
Add typed API wrappers, WebSocket utilities, UX hooks, and UI composition functions; adjust backend CORS creation.

- New functions
  - src/api/client.ts
    - function apiFetch<T>(path: string, init?: RequestInit): Promise<T>
  - src/api/research.ts
    - async function startResearch(payload: ResearchRequest): Promise<JobResponse>
    - async function getResearchStatus(jobId: string): Promise<StatusResponse>
    - async function getResearchArtifacts(jobId: string): Promise<{ status: JobStatus; artifacts: Record<string,any> }>
  - src/api/paper.ts
    - async function startPaper(payload: PaperRequest): Promise<JobResponse>
    - async function getPaperStatus(jobId: string): Promise<StatusResponse>
    - async function getPaperPdf(jobId: string): Promise<{ status: JobStatus; pdf?: string; artifacts?: Record<string,any> }>
  - src/api/config.ts
    - async function getConfig(): Promise<ConfigListResponse>
    - async function setConfig(item: ConfigItem): Promise<{ ok: boolean }>
    - async function bulkSetConfig(items: ConfigItem[]): Promise<{ ok: boolean }>
  - src/lib/ws.ts
    - function connectLogs(jobType: "research" | "paper", jobId: string, onEvent: (e: LogEvent) => void): { close(): void }
  - src/hooks/useFlowHints.ts
    - function useFlowHints(): { shouldPromptBreak: boolean; consume(): void }
  - src/hooks/useAdaptiveTypography.ts
    - function useAdaptiveTypography(): { fontVariationSettings: React.CSSProperties; apply(node: HTMLElement): void }
  - src/hooks/useProgressiveDisclosure.ts
    - function useProgressiveDisclosure(context: any): { hiddenSections: string[]; reveal(sectionId: string): void }

- Modified functions
  - backend/app/main.py
    - def create_app(): FastAPI — replace allow_origins=["*"] with env-driven list

- Removed functions
  - None.

[Classes]
Primarily functional React; small utility classes for buffering and formatting.

- New classes
  - src/lib/LogRingBuffer.ts
    - class LogRingBuffer<T> { constructor(size: number); push(item: T): void; toArray(): T[] }
    - Purpose: Cap memory usage for WS logs; supports virtualized rendering.
  - src/lib/Stopwatch.ts
    - class Stopwatch { start(): void; stop(): number; elapsed(): number }
    - Purpose: Track session time to drive ethical persuasion cues.

- Modified classes
  - None.

- Removed classes
  - None.

[Dependencies]
Add a lean, accessible, and performant stack aligned to Bauhaus 2.0.

- Core
  - react, react-dom, typescript, vite
  - react-router-dom (or @tanstack/router) — choose react-router-dom for familiarity
  - @tanstack/react-query — data fetching, caching, retry
  - zod — runtime validation for API/WS payloads
  - zustand (or jotai) — global state; choose zustand for simplicity
- Design System
  - tailwindcss, postcss, autoprefixer — utility-first styling with design tokens
  - framer-motion — micro-animations as functional ornament
  - @radix-ui/react-* (dialog, tooltip, toast, slider) — accessible primitives
  - @fontsource-variable/inter (or locally hosted Inter Variable) — variable typography
  - clsx, tailwind-merge — class composition
- Tooling/Quality
  - eslint, @typescript-eslint/eslint-plugin, @typescript-eslint/parser, prettier, eslint-config-prettier
  - vite-plugin-svgr (optional)
- Testing
  - vitest, @testing-library/react, @testing-library/user-event, jsdom
  - playwright (optional e2e)

[Testing]
Use Vitest + RTL for component behavior and TanStack Query hooks; optional Playwright E2E for flows.

- Unit/Component
  - Test API clients (mock fetch) to ensure correct error handling.
  - Test LogStream rendering and virtualization under bursty WS input.
  - Test adaptive typography hook behavior at different “times of day”.
  - Test progressive disclosure logic reduces visible complexity by default.
- Integration
  - Simulate startResearch and poll status flow with MSW (Mock Service Worker).
- E2E (optional)
  - Start Research → live logs → artifacts; start Paper → PDF.
  - Config fetch and masked editing with confirmation flows.
- Accessibility checks
  - Axe or @storybook/addon-a11y (if Storybook added later).

[Implementation Order]
Scaffold, wire API and routes, implement flows, layer in design tokens and micro-animations, then polish and test.

1. Backend CORS tightening: parse CORS_ORIGINS from env and document usage in .env.template and backend/README_API.md.
2. Scaffold frontend with React + Vite + TypeScript; add Tailwind and base tokens.
3. Implement API client layer (client.ts and per-domain modules) with Zod validation.
4. Implement router and pages shell: Dashboard, ResearchStart, ResearchJob, PaperStart, PaperJob, Config.
5. Implement WS log streaming and virtualized LogStream with ring buffer and functional feedback animations.
6. Implement progressive disclosure and form UX (mode switch, contextual fields, defaults).
7. Implement status polling and artifacts/pdf retrieval; add JobStatusBadge and Toasts.
8. Add adaptive typography and ethical persuasion hooks; ensure features are subtle, user-first, and opt-out ready.
9. Polish: responsive grid, keyboard navigation, focus management, reduced motion support.
10. Add tests: unit, component, integration; optional Playwright e2e.
11. Production build config, CORS verification, deployment notes (serve frontend separately, configure API base/WS).
