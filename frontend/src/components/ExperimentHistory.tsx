/**
 * Experiment History Sidebar Component
 * Displays a collapsible sidebar with saved experiments
 */

import { useState, useEffect } from 'react';
import type { ExperimentMetadata } from '../types/experiments';
import { listExperiments, deleteExperiment, getExperiment } from '../api/experiments';
import type { EvaluationResult } from '../types/api';
import styles from './ExperimentHistory.module.css';

interface ExperimentHistoryProps {
  onLoadExperiment: (results: EvaluationResult[]) => void;
}

export const ExperimentHistory: React.FC<ExperimentHistoryProps> = ({ onLoadExperiment }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [experiments, setExperiments] = useState<ExperimentMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Load experiments when sidebar opens
  useEffect(() => {
    if (isOpen) {
      loadExperiments();
    }
  }, [isOpen]);

  const loadExperiments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listExperiments();
      setExperiments(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load experiments';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadExperiment = async (experimentId: string) => {
    try {
      setError(null);
      const experimentData = await getExperiment(experimentId);
      onLoadExperiment(experimentData.results);
      setSelectedId(experimentId);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load experiment';
      setError(message);
    }
  };

  const handleDeleteExperiment = async (experimentId: string, experimentName: string) => {
    if (!confirm(`Delete experiment "${experimentName}"?`)) {
      return;
    }

    try {
      setError(null);
      await deleteExperiment(experimentId);
      // Reload experiments list
      await loadExperiments();
      // Clear selection if deleted experiment was selected
      if (selectedId === experimentId) {
        setSelectedId(null);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete experiment';
      setError(message);
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatAccuracyRange = (range: [number, number]) => {
    if (range[0] === range[1]) {
      return `${(range[0] * 100).toFixed(1)}%`;
    }
    return `${(range[0] * 100).toFixed(1)}% - ${(range[1] * 100).toFixed(1)}%`;
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        className={`${styles.toggleButton} ${isOpen ? styles.open : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title={isOpen ? 'Close History' : 'Open History'}
      >
        {isOpen ? '◄ History' : 'History ►'}
      </button>

      {/* Sidebar */}
      <div className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
        <div className={styles.header}>
          <h2>Experiment History</h2>
          <p>
            {experiments.length} saved experiment{experiments.length !== 1 ? 's' : ''}
          </p>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        {loading && <div className={styles.loading}>Loading experiments...</div>}

        {!loading && experiments.length === 0 && (
          <div className={styles.empty}>
            No experiments yet.
            <br />
            Run an evaluation to save your first experiment!
          </div>
        )}

        {!loading && experiments.length > 0 && (
          <div className={styles.experimentList}>
            {experiments.map((exp) => (
              <div
                key={exp.id}
                className={`${styles.experimentCard} ${selectedId === exp.id ? styles.selected : ''}`}
                onClick={() => handleLoadExperiment(exp.id)}
              >
                <div className={styles.experimentName}>{exp.name}</div>

                <div className={styles.experimentDate}>{formatDate(exp.timestamp)}</div>

                <div className={styles.experimentMeta}>
                  <strong>Dataset:</strong> {exp.dataset_name}
                </div>

                <div className={styles.experimentMeta}>
                  <strong>Tasks:</strong> {exp.tasks_evaluated} / {exp.dataset_size}
                </div>

                <div className={styles.experimentMeta}>
                  <strong>Models:</strong> {exp.model_count}
                </div>

                <div className={styles.experimentMeta}>
                  <strong>Accuracy:</strong> {formatAccuracyRange(exp.accuracy_range)}
                </div>

                {exp.tags.length > 0 && (
                  <div className={styles.tags}>
                    {exp.tags.map((tag, idx) => (
                      <span key={idx} className={styles.tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                <div className={styles.actions}>
                  <button
                    className={styles.loadButton}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLoadExperiment(exp.id);
                    }}
                  >
                    Load
                  </button>
                  <button
                    className={styles.deleteButton}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteExperiment(exp.id, exp.name);
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && experiments.length > 0 && (
          <button className={styles.refreshButton} onClick={loadExperiments}>
            Refresh
          </button>
        )}
      </div>
    </>
  );
};
