/**
 * TypeScript types mirroring the Pydantic schemas from backend/zeta_reason/schemas.py
 */

// ============================================================================
// Dataset & Task Types
// ============================================================================

export interface Task {
  id: string;
  input: string;
  target: string;
}

// ============================================================================
// Model Configuration
// ============================================================================

export interface ModelConfig {
  model_id: string;
  provider: string;
  temperature: number;
  max_tokens: number;
  use_cot: boolean;
  shots: number; // Number of samples per task (for self-consistency). Fixed at 1 for v1.0.
  api_key?: string; // Optional API key (falls back to backend environment variable)
}

// ============================================================================
// Model Output
// ============================================================================

export interface ModelOutput {
  answer: string;
  cot_text: string;
  confidence: number | null;
  raw_response: string | null;
}

// ============================================================================
// Evaluation Results
// ============================================================================

export interface TaskResult {
  task_id: string;
  input: string;
  target: string;
  model_output: ModelOutput;
  correct: boolean;
  // Calibration fields
  prob_correct: number | null;
  // CoT shape/process fields
  cot_tokens: number | null;
  cot_chars: number | null;
  step_count: number | null;
  ra_ratio: number | null;
  self_correcting: boolean | null;
  // Efficiency fields
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
  latency_ms: number | null;
}

export interface MetricsSummary {
  // Answer-level metrics
  accuracy: number;
  brier: number | null;
  ece: number | null;
  sce: number | null;
  usr: number | null;
  // CoT shape metrics
  cot_tokens_mean: number | null;
  cot_chars_mean: number | null;
  step_count_mean: number | null;
  ra_ratio_mean: number | null;
  self_correction_rate: number | null;
  // Efficiency metrics
  prompt_tokens_mean: number | null;
  completion_tokens_mean: number | null;
  total_tokens_mean: number | null;
  latency_mean_ms: number | null;
  latency_p95_ms: number | null;
}

export interface EvaluationResult {
  model_configuration: ModelConfig;
  metrics: MetricsSummary;
  task_results: TaskResult[];
  total_tasks: number;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface EvaluateRequest {
  model_configuration: ModelConfig;
  tasks: Task[];
  run_id?: string;
}

export interface EvaluateResponse {
  result: EvaluationResult;
  run_id?: string | null;
}

export interface CompareRequest {
  model_configurations: ModelConfig[];
  tasks: Task[];
  run_id?: string;
}

export interface CompareResponse {
  results: EvaluationResult[];
  run_id?: string | null;
}

// ============================================================================
// UI State Types
// ============================================================================

export type EvaluationState =
  | { type: 'idle' }
  | { type: 'loading' }
  | { type: 'single'; result: EvaluationResult }
  | { type: 'compare'; results: EvaluationResult[] }
  | { type: 'error'; error: string };
