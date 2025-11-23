/**
 * Component for uploading a JSONL dataset file
 */

import React, { useState } from 'react';
import type { Task } from '../types/api';

export type SamplingMode = 'all' | 'random';

export interface SamplingConfig {
  mode: SamplingMode;
  sampleSize: number;
}

interface DatasetUploadProps {
  onDatasetLoad: (tasks: Task[], fileName: string) => void;
  onSamplingConfigChange?: (config: SamplingConfig) => void;
}

export const DatasetUpload: React.FC<DatasetUploadProps> = ({
  onDatasetLoad,
  onSamplingConfigChange,
}) => {
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [totalTasks, setTotalTasks] = useState<number>(0);
  const [samplingMode, setSamplingMode] = useState<SamplingMode>('all');
  const [sampleSize, setSampleSize] = useState<number>(50);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setError(null);

    try {
      const text = await file.text();
      const lines = text.split('\n').filter((line) => line.trim());
      const tasks: Task[] = [];

      for (let i = 0; i < lines.length; i++) {
        try {
          const task = JSON.parse(lines[i]) as Task;

          // Validate task structure
          if (!task.id || !task.input || !task.target) {
            throw new Error(`Missing required fields in task on line ${i + 1}`);
          }

          tasks.push(task);
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Unknown error';
          throw new Error(`Failed to parse line ${i + 1}: ${message}`);
        }
      }

      if (tasks.length === 0) {
        throw new Error('No valid tasks found in file');
      }

      setTotalTasks(tasks.length);
      onDatasetLoad(tasks, file.name);

      // Notify parent of sampling config
      if (onSamplingConfigChange) {
        onSamplingConfigChange({ mode: samplingMode, sampleSize });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load dataset';
      setError(message);
      setFileName(null);
      setTotalTasks(0);
    }
  };

  const handleSamplingModeChange = (mode: SamplingMode) => {
    setSamplingMode(mode);
    if (onSamplingConfigChange) {
      onSamplingConfigChange({ mode, sampleSize });
    }
  };

  const handleSampleSizeChange = (size: number) => {
    setSampleSize(size);
    if (onSamplingConfigChange) {
      onSamplingConfigChange({ mode: samplingMode, sampleSize: size });
    }
  };

  return (
    <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '4px' }}>
      <h3>1. Upload Dataset</h3>
      <p style={{ fontSize: '14px', color: '#666' }}>
        Upload a JSONL file with tasks. Each line should be a JSON object with{' '}
        <code>id</code>, <code>input</code>, and <code>target</code> fields.
      </p>

      <input
        type="file"
        accept=".jsonl,.json"
        onChange={handleFileChange}
        style={{ marginBottom: '10px' }}
      />

      {fileName && (
        <div style={{ color: '#28a745', fontSize: '14px', marginBottom: '15px' }}>
          ✓ Loaded: {fileName} ({totalTasks} tasks)
        </div>
      )}

      {error && (
        <div style={{ color: '#dc3545', fontSize: '14px', marginTop: '10px' }}>
          Error: {error}
        </div>
      )}

      {/* Sampling Controls */}
      {totalTasks > 0 && (
        <div
          style={{
            marginTop: '15px',
            padding: '12px',
            backgroundColor: '#f5f5f5',
            borderRadius: '4px',
            border: '1px solid #ddd',
          }}
        >
          <div style={{ marginBottom: '10px', fontWeight: '500', fontSize: '14px' }}>
            Sampling:
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {/* Option 1: All tasks */}
            <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="sampling-mode"
                value="all"
                checked={samplingMode === 'all'}
                onChange={() => handleSamplingModeChange('all')}
                style={{ marginRight: '8px' }}
              />
              Use all tasks ({totalTasks} tasks)
            </label>

            {/* Option 2: Random sample */}
            <div>
              <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="sampling-mode"
                  value="random"
                  checked={samplingMode === 'random'}
                  onChange={() => handleSamplingModeChange('random')}
                  style={{ marginRight: '8px' }}
                />
                Random sample of
                <input
                  type="number"
                  value={sampleSize}
                  onChange={(e) => handleSampleSizeChange(parseInt(e.target.value) || 1)}
                  min="1"
                  max={totalTasks}
                  disabled={samplingMode !== 'random'}
                  style={{
                    marginLeft: '8px',
                    marginRight: '8px',
                    width: '80px',
                    padding: '4px 6px',
                    fontSize: '14px',
                    border: '1px solid #ccc',
                    borderRadius: '3px',
                    backgroundColor: samplingMode !== 'random' ? '#eee' : 'white',
                  }}
                />
                tasks
              </label>
              {samplingMode === 'random' && sampleSize > totalTasks && (
                <div style={{ fontSize: '12px', color: '#dc3545', marginTop: '4px', marginLeft: '24px' }}>
                  Sample size cannot exceed total tasks ({totalTasks})
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
