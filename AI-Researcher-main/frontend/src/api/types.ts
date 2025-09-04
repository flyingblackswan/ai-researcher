export type ModeEnum = "detailed_idea" | "reference_based" | "paper_generation";
export type JobStatus = "queued" | "running" | "completed" | "error";
export type LogEventType = "log" | "status" | "error";

export interface ResearchRequest {
  mode: ModeEnum;
  input?: string;
  references?: string[];
  category?: string;
  instance_id?: string;
  task_level?: string;
  model?: string;
  container_name?: string;
  workplace_name?: string;
  cache_path?: string;
  port?: number;
  max_iter_times?: number;
}

export interface PaperRequest {
  research_field: string;
  instance_id: string;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  message?: string;
}

export interface StatusResponse {
  status: JobStatus;
  details: {
    created_at?: string;
    updated_at?: string;
    log_path?: string;
    artifacts?: Record<string, any>;
    error?: string | null;
  };
}

export interface FileResponse {
  download_url: string;
}

export interface ConfigItem {
  key: string;
  value: string;
}

export interface ConfigListedItem {
  key: string;
  value: string;
  source: string;
}

export interface ConfigListResponse {
  items: ConfigListedItem[];
}

export interface LogEvent {
  type: LogEventType;
  timestamp: string;
  message: string;
  tool?: string;
  job_id?: string;
}
