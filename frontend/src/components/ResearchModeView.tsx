import React, { useState, useMemo } from 'react';
import type { EvaluationResult, TaskResult } from '../types/api';

// Normalized types for unified single/multi-model handling
type NormalizedModel = {
  modelName: string;
  resultsByTaskId: Record<string, TaskResult>;
};

type NormalizedData = {
  taskIds: string[];
  models: NormalizedModel[];
};

type FilterMode = 'all' | 'correct' | 'incorrect';

interface ResearchModeViewProps {
  results: EvaluationResult[];
}

const ResearchModeView: React.FC<ResearchModeViewProps> = ({ results }) => {
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [filterMode, setFilterMode] = useState<FilterMode>('all');
  const [showRawJson, setShowRawJson] = useState(false);

  // Normalize results into a unified structure
  const normalizedData: NormalizedData = useMemo(() => {
    const taskIdSet = new Set<string>();
    const models: NormalizedModel[] = [];

    results.forEach((result) => {
      const modelName = `${result.model_configuration.model_id} (${result.model_configuration.provider})`;
      const resultsByTaskId: Record<string, TaskResult> = {};

      result.task_results.forEach((taskResult) => {
        taskIdSet.add(taskResult.task_id);
        resultsByTaskId[taskResult.task_id] = taskResult;
      });

      models.push({ modelName, resultsByTaskId });
    });

    return {
      taskIds: Array.from(taskIdSet).sort(),
      models,
    };
  }, [results]);

  // Determine correctness for filtering (based on first model or majority vote)
  const getTaskCorrectness = (taskId: string): boolean => {
    if (normalizedData.models.length === 0) return false;

    // Use first model's result as reference
    const firstModelResult = normalizedData.models[0].resultsByTaskId[taskId];
    return firstModelResult?.correct ?? false;
  };

  // Filter tasks based on selected filter mode
  const filteredTaskIds = useMemo(() => {
    return normalizedData.taskIds.filter((taskId) => {
      if (filterMode === 'all') return true;
      const isCorrect = getTaskCorrectness(taskId);
      if (filterMode === 'correct') return isCorrect;
      if (filterMode === 'incorrect') return !isCorrect;
      return true;
    });
  }, [normalizedData.taskIds, filterMode]);

  // Auto-select first task if none selected
  React.useEffect(() => {
    if (!selectedTaskId && filteredTaskIds.length > 0) {
      setSelectedTaskId(filteredTaskIds[0]);
    }
  }, [filteredTaskIds, selectedTaskId]);

  // Get current task data
  const currentTaskData = useMemo(() => {
    if (!selectedTaskId || normalizedData.models.length === 0) return null;

    const firstModelResult = normalizedData.models[0].resultsByTaskId[selectedTaskId];
    if (!firstModelResult) return null;

    return {
      taskId: selectedTaskId,
      input: firstModelResult.input,
      target: firstModelResult.target,
    };
  }, [selectedTaskId, normalizedData]);

  if (normalizedData.models.length === 0) {
    return <div className="research-mode-empty">No results to display</div>;
  }

  return (
    <div className="research-mode-container">
      {/* Sidebar */}
      <div className="research-sidebar">
        <div className="sidebar-header">
          <h3>Tasks ({filteredTaskIds.length})</h3>
        </div>

        {/* Filters */}
        <div className="filter-controls">
          <button
            className={filterMode === 'all' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilterMode('all')}
          >
            All Tasks
          </button>
          <button
            className={filterMode === 'correct' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilterMode('correct')}
          >
            Correct Only
          </button>
          <button
            className={filterMode === 'incorrect' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilterMode('incorrect')}
          >
            Incorrect Only
          </button>
        </div>

        {/* Task List */}
        <div className="task-list">
          {filteredTaskIds.map((taskId) => {
            const isCorrect = getTaskCorrectness(taskId);
            return (
              <div
                key={taskId}
                className={`task-item ${selectedTaskId === taskId ? 'selected' : ''}`}
                onClick={() => setSelectedTaskId(taskId)}
              >
                <span className={`correctness-indicator ${isCorrect ? 'correct' : 'incorrect'}`}>
                  {isCorrect ? '✓' : '✗'}
                </span>
                <span className="task-id">{taskId}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Panel */}
      <div className="research-main-panel">
        {currentTaskData ? (
          <>
            {/* Task Details */}
            <div className="task-details-section">
              <h2>Task: {currentTaskData.taskId}</h2>

              <div className="task-field">
                <label>Input:</label>
                <div className="task-input">{currentTaskData.input}</div>
              </div>

              <div className="task-field">
                <label>Target Answer:</label>
                <div className="task-target">{currentTaskData.target}</div>
              </div>
            </div>

            {/* Model Cards */}
            <div className="model-cards-section">
              <h3>Model Responses ({normalizedData.models.length})</h3>

              {normalizedData.models.map((model, idx) => {
                const taskResult = model.resultsByTaskId[selectedTaskId];
                if (!taskResult) return null;

                return (
                  <div key={idx} className="model-card">
                    <div className="model-card-header">
                      <h4>{model.modelName}</h4>
                      <span className={`correctness-badge ${taskResult.correct ? 'correct' : 'incorrect'}`}>
                        {taskResult.correct ? 'Correct ✓' : 'Incorrect ✗'}
                      </span>
                    </div>

                    <div className="model-card-body">
                      {/* Final Answer */}
                      <div className="model-field">
                        <label>Final Answer:</label>
                        <div className={`model-answer ${taskResult.correct ? 'correct-answer' : 'incorrect-answer'}`}>
                          {taskResult.model_output.answer}
                        </div>
                      </div>

                      {/* Chain of Thought */}
                      <div className="model-field">
                        <label>Chain of Thought:</label>
                        <div className="cot-text-box">
                          {taskResult.model_output.cot_text || 'No CoT available'}
                        </div>
                      </div>

                      {/* Stats Grid */}
                      <div className="model-stats-grid">
                        <div className="stat-item">
                          <span className="stat-label">CoT Tokens:</span>
                          <span className="stat-value">{taskResult.cot_tokens ?? 'N/A'}</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Step Count:</span>
                          <span className="stat-value">{taskResult.step_count ?? 'N/A'}</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Self-Correcting:</span>
                          <span className="stat-value">
                            {taskResult.self_correcting === null ? 'N/A' : taskResult.self_correcting ? 'Yes' : 'No'}
                          </span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Total Tokens:</span>
                          <span className="stat-value">{taskResult.total_tokens ?? 'N/A'}</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Latency:</span>
                          <span className="stat-value">
                            {taskResult.latency_ms !== null ? `${taskResult.latency_ms}ms` : 'N/A'}
                          </span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Confidence:</span>
                          <span className="stat-value">
                            {taskResult.model_output.confidence !== null
                              ? taskResult.model_output.confidence.toFixed(3)
                              : 'N/A'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Raw JSON Toggle */}
            <div className="raw-json-section">
              <button
                className="raw-json-toggle-btn"
                onClick={() => setShowRawJson(!showRawJson)}
              >
                {showRawJson ? 'Hide Raw JSON' : 'Show Raw JSON'}
              </button>

              {showRawJson && (
                <pre className="raw-json-display">
                  {JSON.stringify(
                    normalizedData.models.map(m => ({
                      model: m.modelName,
                      result: m.resultsByTaskId[selectedTaskId]
                    })),
                    null,
                    2
                  )}
                </pre>
              )}
            </div>
          </>
        ) : (
          <div className="no-task-selected">
            <p>Select a task from the sidebar to view details</p>
          </div>
        )}
      </div>

      <style>{`
        .research-mode-container {
          display: flex;
          gap: 20px;
          height: calc(100vh - 200px);
          min-height: 600px;
        }

        /* Sidebar Styles */
        .research-sidebar {
          width: 280px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          background: #f9f9f9;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .sidebar-header {
          padding: 16px;
          border-bottom: 1px solid #e0e0e0;
          background: #fff;
        }

        .sidebar-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }

        .filter-controls {
          padding: 12px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          border-bottom: 1px solid #e0e0e0;
          background: #fff;
        }

        .filter-btn {
          padding: 8px 12px;
          border: 1px solid #d0d0d0;
          border-radius: 4px;
          background: #fff;
          cursor: pointer;
          font-size: 13px;
          transition: all 0.2s;
        }

        .filter-btn:hover {
          background: #f0f0f0;
        }

        .filter-btn.active {
          background: #4a90e2;
          color: white;
          border-color: #4a90e2;
        }

        .task-list {
          flex: 1;
          overflow-y: auto;
          padding: 8px;
        }

        .task-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 12px;
          margin-bottom: 4px;
          border-radius: 4px;
          cursor: pointer;
          background: #fff;
          border: 1px solid #e0e0e0;
          transition: all 0.2s;
        }

        .task-item:hover {
          background: #f0f8ff;
          border-color: #4a90e2;
        }

        .task-item.selected {
          background: #e3f2fd;
          border-color: #4a90e2;
          font-weight: 500;
        }

        .correctness-indicator {
          font-size: 14px;
          font-weight: bold;
        }

        .correctness-indicator.correct {
          color: #4caf50;
        }

        .correctness-indicator.incorrect {
          color: #f44336;
        }

        .task-id {
          font-size: 13px;
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        /* Main Panel Styles */
        .research-main-panel {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          background: #fff;
        }

        .task-details-section {
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 2px solid #e0e0e0;
        }

        .task-details-section h2 {
          margin: 0 0 20px 0;
          font-size: 20px;
          color: #333;
        }

        .task-field {
          margin-bottom: 16px;
        }

        .task-field label {
          display: block;
          font-weight: 600;
          margin-bottom: 6px;
          font-size: 14px;
          color: #555;
        }

        .task-input,
        .task-target {
          padding: 12px;
          background: #f5f5f5;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          font-size: 14px;
          line-height: 1.5;
        }

        .task-target {
          font-weight: 500;
          background: #fff9e6;
          border-color: #ffe082;
        }

        /* Model Cards */
        .model-cards-section {
          margin-bottom: 30px;
        }

        .model-cards-section h3 {
          margin: 0 0 16px 0;
          font-size: 18px;
          color: #333;
        }

        .model-card {
          margin-bottom: 20px;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          overflow: hidden;
        }

        .model-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          background: #f5f5f5;
          border-bottom: 1px solid #e0e0e0;
        }

        .model-card-header h4 {
          margin: 0;
          font-size: 15px;
          font-weight: 600;
        }

        .correctness-badge {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }

        .correctness-badge.correct {
          background: #e8f5e9;
          color: #2e7d32;
        }

        .correctness-badge.incorrect {
          background: #ffebee;
          color: #c62828;
        }

        .model-card-body {
          padding: 16px;
        }

        .model-field {
          margin-bottom: 16px;
        }

        .model-field label {
          display: block;
          font-weight: 600;
          margin-bottom: 6px;
          font-size: 13px;
          color: #555;
        }

        .model-answer {
          padding: 10px 12px;
          border-radius: 4px;
          font-size: 14px;
          font-weight: 500;
          border: 1px solid;
        }

        .correct-answer {
          background: #e8f5e9;
          color: #2e7d32;
          border-color: #a5d6a7;
        }

        .incorrect-answer {
          background: #ffebee;
          color: #c62828;
          border-color: #ef9a9a;
        }

        .cot-text-box {
          padding: 12px;
          background: #fafafa;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          max-height: 300px;
          overflow-y: auto;
          font-size: 13px;
          line-height: 1.6;
          white-space: pre-wrap;
          font-family: 'Courier New', monospace;
        }

        .model-stats-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-top: 16px;
          padding: 12px;
          background: #f9f9f9;
          border-radius: 4px;
        }

        .stat-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .stat-label {
          font-size: 11px;
          color: #777;
          text-transform: uppercase;
          font-weight: 600;
        }

        .stat-value {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }

        /* Raw JSON Section */
        .raw-json-section {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 2px solid #e0e0e0;
        }

        .raw-json-toggle-btn {
          padding: 10px 16px;
          background: #4a90e2;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background 0.2s;
        }

        .raw-json-toggle-btn:hover {
          background: #357abd;
        }

        .raw-json-display {
          margin-top: 12px;
          padding: 16px;
          background: #2d2d2d;
          color: #f8f8f8;
          border-radius: 4px;
          overflow-x: auto;
          font-size: 12px;
          line-height: 1.5;
          max-height: 500px;
          overflow-y: auto;
        }

        .no-task-selected {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100%;
          color: #999;
          font-size: 16px;
        }

        .research-mode-empty {
          padding: 40px;
          text-align: center;
          color: #999;
          font-size: 16px;
        }
      `}</style>
    </div>
  );
};

export default ResearchModeView;
