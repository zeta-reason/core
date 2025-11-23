/**
 * Utilities for saving and loading model configuration presets
 * Presets are stored in browser localStorage
 */

import type { ModelConfig } from '../types/api';

const STORAGE_KEY = 'zeta_reason_model_presets_v1';

// ============================================================================
// Types
// ============================================================================

/**
 * Single model configuration within a preset
 */
export interface ModelPresetModelConfig {
  provider: string;
  model_id: string;
  temperature: number;
  max_tokens: number;
  use_cot: boolean;
  shots?: number; // Optional for backward compatibility with v1.0 presets
}

/**
 * A saved preset containing one or more model configurations
 */
export interface ModelPreset {
  id: string;
  name: string;
  createdAt: string; // ISO timestamp
  models: ModelPresetModelConfig[];
}

// ============================================================================
// localStorage Functions
// ============================================================================

/**
 * Load all presets from localStorage
 * @returns Array of ModelPreset, empty if none found or localStorage unavailable
 */
export function loadPresets(): ModelPreset[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return [];
    }
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.warn('Failed to load presets from localStorage:', error);
    return [];
  }
}

/**
 * Save presets array to localStorage
 * @param presets - Array of ModelPreset to save
 */
export function savePresets(presets: ModelPreset[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(presets));
  } catch (error) {
    console.error('Failed to save presets to localStorage:', error);
  }
}

/**
 * Create a new preset from current model configurations
 * @param name - User-provided name for the preset
 * @param modelsConfig - Current array of ModelConfig
 * @returns New ModelPreset with generated ID and timestamp
 */
export function createPreset(name: string, modelsConfig: ModelConfig[]): ModelPreset {
  // Generate unique ID using timestamp
  const id = `preset_${Date.now()}`;

  // Convert ModelConfig[] to ModelPresetModelConfig[]
  const models: ModelPresetModelConfig[] = modelsConfig.map((model) => ({
    provider: model.provider,
    model_id: model.model_id,
    temperature: model.temperature,
    max_tokens: model.max_tokens,
    use_cot: model.use_cot,
    shots: model.shots,
  }));

  return {
    id,
    name: name.trim(),
    createdAt: new Date().toISOString(),
    models,
  };
}

/**
 * Delete a preset by ID
 * @param presetId - ID of preset to delete
 * @returns Updated array of presets
 */
export function deletePreset(presetId: string): ModelPreset[] {
  const presets = loadPresets();
  const updated = presets.filter((p) => p.id !== presetId);
  savePresets(updated);
  return updated;
}
