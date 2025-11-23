/**
 * Run Details Page
 * Shows detailed results for a specific run with prompt list sidebar
 */

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getExperiment } from '../api/experiments';
import { exportExperimentToCSV, exportExperimentToJSON } from '../utils/export';
import type { ExperimentData } from '../types/experiments';
import type { EvaluationResult, TaskResult } from '../types/api';
import styles from './RunDetails.module.css';

export const RunDetails: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const [experiment, setExperiment] = useState<ExperimentData | null>(null);
  const [selectedPromptIndex, setSelectedPromptIndex] = useState<number>(0);
  const [selectedModelIndex, setSelectedModelIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (runId) {
      loadExperiment();
    }
  }, [runId]);

  const loadExperiment = async () => {
    if (!runId) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getExperiment(runId);
      setExperiment(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load experiment';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <p>Loading run details...</p>
      </div>
    );
  }

  if (error || !experiment) {
    return (
      <div className={styles.error}>
        {error || 'Experiment not found'}
      </div>
    );
  }

  const results = experiment.results as EvaluationResult[];
  const safeModelIndex = Math.min(selectedModelIndex, Math.max(results.length - 1, 0));
  const activeResult = results[safeModelIndex];
  const taskResults = activeResult?.task_results || [];
  const selectedTask = taskResults[selectedPromptIndex];

  return (
    <div className={styles.runDetails}>
      {/* Prompt List Sidebar */}
      <div className={styles.promptSidebar}>
        <div className={styles.sidebarHeader}>
          <h3 className={styles.sidebarTitle}>Prompts</h3>
          <span className={styles.promptCount}>{taskResults.length}</span>
        </div>

        <div className={styles.promptList}>
          {taskResults.map((task: TaskResult, index: number) => (
            <div
              key={task.task_id}
              className={`${styles.promptItem} ${
                index === selectedPromptIndex ? styles.promptItemActive : ''
              } ${task.correct ? styles.promptItemCorrect : styles.promptItemIncorrect}`}
              onClick={() => setSelectedPromptIndex(index)}
            >
              <div className={styles.promptHeader}>
                <span className={styles.promptNumber}>#{index + 1}</span>
                <span className={styles.promptStatus}>
                  {task.correct ? '✓' : '✗'}
                </span>
              </div>
              <div className={styles.promptPreview}>
                {task.input.substring(0, 60)}
                {task.input.length > 60 ? '...' : ''}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className={styles.mainContent}>
        {/* Header */}
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>
              Run Details
            </h1>
            <p className={styles.subtitle}>
              {experiment.metadata.dataset_name} • {experiment.metadata.model_ids.join(', ')}
            </p>
            {results.length > 1 && (
              <div className={styles.modelSwitcher}>
                {results.map((result, idx) => (
                  <button
                    key={result.model_configuration.model_id + idx}
                    className={`${styles.modelPill} ${idx === safeModelIndex ? styles.modelPillActive : ''}`}
                    onClick={() => {
                      setSelectedModelIndex(idx);
                      setSelectedPromptIndex(0);
                    }}
                  >
                    {result.model_configuration.model_id}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className={styles.headerActions}>
            <div className={styles.headerStats}>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Accuracy</span>
                <span className={styles.statValue}>
                  {(activeResult.metrics.accuracy * 100).toFixed(1)}%
                </span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Tasks</span>
                <span className={styles.statValue}>{experiment.metadata.tasks_evaluated}</span>
              </div>
            </div>
            <div className={styles.exportButtons}>
              <button
                className={styles.exportButton}
                onClick={() => exportExperimentToCSV(experiment)}
                title="Export to CSV"
              >
                📊 Export CSV
              </button>
              <button
                className={styles.exportButton}
                onClick={() => exportExperimentToJSON(experiment)}
                title="Export to JSON"
              >
                📄 Export JSON
              </button>
            </div>
          </div>
        </div>

        {/* Selected Task Details */}
        {selectedTask && (
          <div className={styles.taskDetails}>
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}>Input</h3>
              <div className={styles.taskInput}>{selectedTask.input}</div>
            </div>

            <div className={styles.resultRow}>
              <div className={styles.section}>
                <h3 className={styles.sectionTitle}>Expected Answer</h3>
                <div className={styles.expectedAnswer}>{selectedTask.target}</div>
              </div>

              <div className={styles.section}>
                <h3 className={styles.sectionTitle}>Model Answer</h3>
                <div
                  className={`${styles.modelAnswer} ${
                    selectedTask.correct ? styles.correct : styles.incorrect
                  }`}
                >
                  {selectedTask.model_output.answer}
                  {selectedTask.correct && (
                    <span className={styles.correctBadge}>✓ Correct</span>
                  )}
                  {!selectedTask.correct && (
                    <span className={styles.incorrectBadge}>✗ Incorrect</span>
                  )}
                </div>
              </div>
            </div>

            {selectedTask.model_output.confidence !== null && (
              <div className={styles.section}>
                <h3 className={styles.sectionTitle}>Confidence</h3>
                <div className={styles.confidence}>
                  <div className={styles.confidenceBar}>
                    <div
                      className={styles.confidenceFill}
                      style={{ width: `${selectedTask.model_output.confidence * 100}%` }}
                    />
                  </div>
                  <span className={styles.confidenceValue}>
                    {(selectedTask.model_output.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}

            {selectedTask.model_output.cot_text && (
              <div className={styles.section}>
                <h3 className={styles.sectionTitle}>Chain of Thought</h3>
                <div className={styles.cotText}>
                  <pre className={styles.cotPre}>{selectedTask.model_output.cot_text}</pre>
                </div>
              </div>
            )}

            {/* Task Metrics */}
            <div className={styles.taskMetrics}>
              {selectedTask.latency_ms !== null && (
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Latency</span>
                  <span className={styles.metricValue}>
                    {selectedTask.latency_ms.toFixed(0)}ms
                  </span>
                </div>
              )}
              {selectedTask.cot_tokens !== null && (
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>CoT Tokens</span>
                  <span className={styles.metricValue}>{selectedTask.cot_tokens}</span>
                </div>
              )}
              {selectedTask.step_count !== null && (
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Steps</span>
                  <span className={styles.metricValue}>{selectedTask.step_count}</span>
                </div>
              )}
              {selectedTask.prompt_tokens !== null && (
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Prompt Tokens</span>
                  <span className={styles.metricValue}>{selectedTask.prompt_tokens}</span>
                </div>
              )}
              {selectedTask.completion_tokens !== null && (
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Completion Tokens</span>
                  <span className={styles.metricValue}>{selectedTask.completion_tokens}</span>
                </div>
              )}
              {selectedTask.total_tokens !== null && (
                <div className={styles.metric}>
                  <span className={styles.metricLabel}>Total Tokens</span>
                  <span className={styles.metricValue}>{selectedTask.total_tokens}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
