/**
 * TypeScript types for experiment history feature
 */

import type { EvaluationResult, ModelConfig } from './api';
import type { SamplingConfig } from '../components/DatasetUpload';

// ============================================================================
// Experiment Metadata
// ============================================================================

export interface ExperimentMetadata {
  id: string;                    // UUID
  name: string;                  // User-provided or auto-generated
  timestamp: string;             // ISO 8601 timestamp
  dataset_name: string;          // Original dataset filename
  dataset_size: number;          // Total tasks in original dataset
  tasks_evaluated: number;       // Number of tasks actually evaluated
  model_count: number;           // Number of models compared
  model_ids: string[];           // List of model IDs
  accuracy_range: [number, number]; // [min, max] accuracy across models
  tags: string[];                // User-defined tags
}

// ============================================================================
// Full Experiment Data
// ============================================================================

export interface ExperimentData {
  metadata: ExperimentMetadata;
  results: EvaluationResult[];
  sampling_config: SamplingConfig;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface ExperimentSaveRequest {
  name: string;
  dataset_name: string;
  dataset_size: number;
  results: EvaluationResult[];
  sampling_config: SamplingConfig;
  tags?: string[];
}

export interface ExperimentSaveResponse {
  experiment_id: string;
}

export interface StorageStats {
  total_experiments: number;
  total_size_bytes: number;
  total_size_mb: number;
}
