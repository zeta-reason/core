/**
 * Component for selecting and configuring model(s) to evaluate
 */

import React, { useState, useEffect } from 'react';
import type { ModelConfig } from '../types/api';
import {
  loadPresets,
  savePresets,
  createPreset,
  deletePreset,
  type ModelPreset,
} from '../utils/modelPresets';
import {
  listProviders,
  listModels,
  getProviderInfo,
  getModelInfo,
  isProviderImplemented,
  type ProviderId,
} from '../config/modelRegistry';

interface ModelSelectorProps {
  onModelsChange: (models: ModelConfig[]) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({ onModelsChange }) => {
  const [models, setModels] = useState<ModelConfig[]>([
    {
      model_id: 'gpt-4o-mini',
      provider: 'openai',
      temperature: 0.7,
      max_tokens: 1000,
      use_cot: true,
      shots: 1,
    },
  ]);

  const [presets, setPresets] = useState<ModelPreset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('');

  // Load presets on mount
  useEffect(() => {
    const loaded = loadPresets();
    setPresets(loaded);
  }, []);

  const addModel = () => {
    const newModel: ModelConfig = {
      model_id: 'gpt-4o-mini',
      provider: 'openai',
      temperature: 0.7,
      max_tokens: 1000,
      use_cot: true,
      shots: 1,
    };
    const updated = [...models, newModel];
    setModels(updated);
    onModelsChange(updated);
  };

  const removeModel = (index: number) => {
    const updated = models.filter((_, i) => i !== index);
    setModels(updated);
    onModelsChange(updated);
  };

  const updateModel = (index: number, field: keyof ModelConfig, value: string | number | boolean) => {
    const updated = models.map((model, i) => {
      if (i === index) {
        const updatedModel = { ...model, [field]: value };

        // When provider changes, update to the first available model for that provider
        if (field === 'provider') {
          const providerModels = listModels(value as ProviderId);
          if (providerModels.length > 0) {
            const firstModel = providerModels[0];
            updatedModel.model_id = firstModel.modelId;
            updatedModel.max_tokens = firstModel.defaultMaxTokens || 1000;
            updatedModel.temperature = firstModel.defaultTemperature || 0.7;
          }
        }

        // When model_id changes, update defaults from registry
        if (field === 'model_id') {
          const modelInfo = getModelInfo(model.provider as ProviderId, value as string);
          if (modelInfo) {
            updatedModel.max_tokens = modelInfo.defaultMaxTokens || model.max_tokens;
            updatedModel.temperature = modelInfo.defaultTemperature || model.temperature;
          }
        }

        return updatedModel;
      }
      return model;
    });
    setModels(updated);
    onModelsChange(updated);
  };

  const handleSavePreset = () => {
    if (models.length === 0) {
      alert('No models configured. Please add at least one model before saving a preset.');
      return;
    }

    const name = prompt('Enter a name for this preset:');
    if (!name || name.trim() === '') {
      return; // User cancelled or entered empty name
    }

    const newPreset = createPreset(name, models);
    const updatedPresets = [...presets, newPreset];
    setPresets(updatedPresets);
    savePresets(updatedPresets);

    alert(`Preset "${name}" saved successfully!`);
  };

  const handleLoadPreset = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const presetId = e.target.value;

    if (!presetId) {
      setSelectedPresetId('');
      return; // Empty selection
    }

    const preset = presets.find((p) => p.id === presetId);
    if (!preset) {
      return;
    }

    // Convert ModelPresetModelConfig[] to ModelConfig[]
    const loadedModels: ModelConfig[] = preset.models.map((m) => ({
      provider: m.provider,
      model_id: m.model_id,
      temperature: m.temperature,
      max_tokens: m.max_tokens,
      use_cot: m.use_cot,
      shots: m.shots || 1, // Default to 1 for older presets without shots
    }));

    setModels(loadedModels);
    onModelsChange(loadedModels);

    // Keep selection to show which preset is loaded and enable delete
    setSelectedPresetId(presetId);
  };

  const handleDeletePreset = (presetId: string) => {
    if (!confirm('Are you sure you want to delete this preset?')) {
      return;
    }

    const updatedPresets = deletePreset(presetId);
    setPresets(updatedPresets);
    setSelectedPresetId('');
  };

  return (
    <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '4px' }}>
      <h3>2. Configure Model(s)</h3>

      {/* Presets Bar */}
      <div
        style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '15px',
          padding: '10px',
          backgroundColor: '#f5f5f5',
          borderRadius: '4px',
          alignItems: 'center',
        }}
      >
        <div style={{ flex: 1, display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label htmlFor="preset-select" style={{ fontSize: '14px', fontWeight: '500' }}>
            Load preset:
          </label>
          <select
            id="preset-select"
            value={selectedPresetId}
            onChange={handleLoadPreset}
            style={{
              flex: 1,
              padding: '6px 8px',
              fontSize: '14px',
              border: '1px solid #ccc',
              borderRadius: '3px',
            }}
          >
            <option value="">-- Select a preset --</option>
            {presets.map((preset) => (
              <option key={preset.id} value={preset.id}>
                {preset.name} ({preset.models.length} model{preset.models.length !== 1 ? 's' : ''})
              </option>
            ))}
          </select>
          {selectedPresetId && (
            <button
              onClick={() => handleDeletePreset(selectedPresetId)}
              style={{
                padding: '6px 12px',
                fontSize: '13px',
                cursor: 'pointer',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
              }}
              title="Delete selected preset"
            >
              Delete
            </button>
          )}
        </div>
        <button
          onClick={handleSavePreset}
          style={{
            padding: '6px 12px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '3px',
            whiteSpace: 'nowrap',
          }}
        >
          Save as preset
        </button>
      </div>

      {models.map((model, index) => (
        <div
          key={index}
          style={{
            marginBottom: '15px',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: '#f9f9f9',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
            <strong>Model {index + 1}</strong>
            {models.length > 1 && (
              <button
                onClick={() => removeModel(index)}
                style={{
                  padding: '2px 8px',
                  fontSize: '12px',
                  cursor: 'pointer',
                  backgroundColor: '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '3px',
                }}
              >
                Remove
              </button>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>
                Provider:
              </label>
              <select
                value={model.provider}
                onChange={(e) => updateModel(index, 'provider', e.target.value)}
                style={{ width: '100%', padding: '4px' }}
              >
                {listProviders()
                  .filter((providerId) => isProviderImplemented(providerId) || providerId === 'dummy')
                  .map((providerId) => {
                    const providerInfo = getProviderInfo(providerId);
                    return (
                      <option key={providerId} value={providerId}>
                        {providerInfo.displayName}
                      </option>
                    );
                  })}
                <option value="dummy">Dummy (Testing)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>
                Model:
              </label>
              <select
                value={model.model_id}
                onChange={(e) => updateModel(index, 'model_id', e.target.value)}
                style={{ width: '100%', padding: '4px' }}
              >
                {model.provider === 'dummy' ? (
                  <option value="dummy-model">Dummy Model</option>
                ) : (
                  listModels(model.provider as ProviderId).map((modelInfo) => (
                    <option key={modelInfo.modelId} value={modelInfo.modelId}>
                      {modelInfo.displayName}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>
                Temperature: {model.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={model.temperature}
                onChange={(e) => updateModel(index, 'temperature', parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>
                Max Tokens:
              </label>
              <input
                type="number"
                value={model.max_tokens}
                onChange={(e) => updateModel(index, 'max_tokens', parseInt(e.target.value))}
                style={{ width: '100%', padding: '4px' }}
                min="100"
                max="4000"
                step="100"
              />
            </div>

            <div>
              <label style={{ display: 'flex', alignItems: 'center', fontSize: '12px' }}>
                <input
                  type="checkbox"
                  checked={model.use_cot}
                  onChange={(e) => updateModel(index, 'use_cot', e.target.checked)}
                  style={{ marginRight: '6px' }}
                />
                Use Chain-of-Thought
              </label>
            </div>
          </div>
        </div>
      ))}

      <button
        onClick={addModel}
        style={{
          padding: '8px 16px',
          cursor: 'pointer',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontSize: '14px',
        }}
      >
        + Add Another Model
      </button>
    </div>
  );
};
