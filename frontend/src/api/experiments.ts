/**
 * API client for experiment history operations
 */

import type {
  ExperimentMetadata,
  ExperimentData,
  ExperimentSaveRequest,
  ExperimentSaveResponse,
  StorageStats,
} from '../types/experiments';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/experiments`;

/**
 * Save a new experiment
 */
export async function saveExperiment(
  request: ExperimentSaveRequest
): Promise<string> {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to save experiment');
  }

  const data: ExperimentSaveResponse = await response.json();
  return data.experiment_id;
}

/**
 * List all experiment metadata
 */
export async function listExperiments(): Promise<ExperimentMetadata[]> {
  const response = await fetch(API_BASE);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to list experiments');
  }

  return response.json();
}

/**
 * Get full experiment data by ID
 */
export async function getExperiment(experimentId: string): Promise<ExperimentData> {
  const response = await fetch(`${API_BASE}/${experimentId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to load experiment');
  }

  return response.json();
}

/**
 * Delete an experiment by ID
 */
export async function deleteExperiment(experimentId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/${experimentId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to delete experiment');
  }
}

/**
 * Get storage statistics
 */
export async function getStorageStats(): Promise<StorageStats> {
  const response = await fetch(`${API_BASE}/stats/storage`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get storage stats');
  }

  return response.json();
}

/**
 * Generate auto-name for experiment
 */
export function generateExperimentName(config: {
  models: Array<{ model_id: string }>;
  dataset_name: string;
}): string {
  const modelNames = config.models
    .map((m) => m.model_id)
    .join(' vs ');

  const datasetName = config.dataset_name.replace('.jsonl', '').replace('.json', '');
  const date = new Date().toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return `${modelNames} on ${datasetName} - ${date}`;
}
