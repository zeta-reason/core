/**
 * Component for viewing chain-of-thought reasoning for individual tasks
 */

import React, { useState } from 'react';
import type { EvaluationResult } from '../types/api';

interface CotViewerProps {
  results: EvaluationResult[];
}

export const CotViewer: React.FC<CotViewerProps> = ({ results }) => {
  const [selectedModelIndex, setSelectedModelIndex] = useState(0);
  const [selectedTaskIndex, setSelectedTaskIndex] = useState(0);

  if (results.length === 0) {
    return null;
  }

  const currentResult = results[selectedModelIndex];
  const currentTask = currentResult.task_results[selectedTaskIndex];

  if (!currentTask) {
    return null;
  }

  return (
    <div style={{ marginBottom: '20px' }}>
      <h3>Chain-of-Thought Viewer</h3>

      <div style={{ marginBottom: '15px', display: 'flex', gap: '15px' }}>
        {/* Model selector */}
        {results.length > 1 && (
          <div>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>
              Model:
            </label>
            <select
              value={selectedModelIndex}
              onChange={(e) => setSelectedModelIndex(parseInt(e.target.value))}
              style={{ padding: '6px', fontSize: '14px' }}
            >
              {results.map((result, index) => (
                <option key={index} value={index}>
                  {result.model_configuration.model_id} ({result.model_configuration.provider})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Task selector */}
        <div>
          <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Task:</label>
          <select
            value={selectedTaskIndex}
            onChange={(e) => setSelectedTaskIndex(parseInt(e.target.value))}
            style={{ padding: '6px', fontSize: '14px' }}
          >
            {currentResult.task_results.map((task, index) => (
              <option key={index} value={index}>
                {task.task_id} {task.correct ? '✓' : '✗'}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Task details */}
      <div
        style={{
          padding: '15px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          backgroundColor: '#f9f9f9',
        }}
      >
        <div style={{ marginBottom: '15px' }}>
          <strong style={{ fontSize: '14px', color: '#666' }}>Input:</strong>
          <div
            style={{
              marginTop: '5px',
              padding: '10px',
              backgroundColor: 'white',
              border: '1px solid #ddd',
              borderRadius: '3px',
            }}
          >
            {currentTask.input}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '15px' }}>
          <div>
            <strong style={{ fontSize: '14px', color: '#666' }}>Target:</strong>
            <div
              style={{
                marginTop: '5px',
                padding: '8px',
                backgroundColor: 'white',
                border: '1px solid #ddd',
                borderRadius: '3px',
                fontFamily: 'monospace',
              }}
            >
              {currentTask.target}
            </div>
          </div>

          <div>
            <strong style={{ fontSize: '14px', color: '#666' }}>Model Answer:</strong>
            <div
              style={{
                marginTop: '5px',
                padding: '8px',
                backgroundColor: currentTask.correct ? '#d4edda' : '#f8d7da',
                border: `1px solid ${currentTask.correct ? '#c3e6cb' : '#f5c6cb'}`,
                borderRadius: '3px',
                fontFamily: 'monospace',
              }}
            >
              {currentTask.model_output.answer}
            </div>
          </div>

          <div>
            <strong style={{ fontSize: '14px', color: '#666' }}>Correct:</strong>
            <div
              style={{
                marginTop: '5px',
                padding: '8px',
                backgroundColor: currentTask.correct ? '#d4edda' : '#f8d7da',
                border: `1px solid ${currentTask.correct ? '#c3e6cb' : '#f5c6cb'}`,
                borderRadius: '3px',
                textAlign: 'center',
                fontSize: '18px',
              }}
            >
              {currentTask.correct ? '✓ Yes' : '✗ No'}
            </div>
          </div>
        </div>

        <div>
          <strong style={{ fontSize: '14px', color: '#666' }}>Chain of Thought:</strong>
          <div
            style={{
              marginTop: '5px',
              padding: '10px',
              backgroundColor: 'white',
              border: '1px solid #ddd',
              borderRadius: '3px',
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace',
              fontSize: '13px',
              maxHeight: '300px',
              overflowY: 'auto',
            }}
          >
            {currentTask.model_output.cot_text}
          </div>
        </div>

        {currentTask.model_output.confidence !== null && (
          <div style={{ marginTop: '15px' }}>
            <strong style={{ fontSize: '14px', color: '#666' }}>
              Confidence: {currentTask.model_output.confidence.toFixed(4)}
            </strong>
          </div>
        )}
      </div>
    </div>
  );
};
