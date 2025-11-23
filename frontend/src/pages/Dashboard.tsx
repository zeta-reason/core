/**
 * Dashboard - Past Runs View
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listExperiments } from '../api/experiments';
import type { ExperimentMetadata } from '../types/experiments';
import styles from './Dashboard.module.css';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [experiments, setExperiments] = useState<ExperimentMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadExperiments();
  }, []);

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

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    // Less than 1 hour
    if (diff < 3600000) {
      const minutes = Math.floor(diff / 60000);
      return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    }

    // Less than 24 hours
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    }

    // More than 24 hours
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatModels = (modelIds: string[]) => {
    if (modelIds.length === 0) return 'N/A';
    if (modelIds.length === 1) return modelIds[0];
    return `${modelIds[0]}, ${modelIds[1]}${modelIds.length > 2 ? `, +${modelIds.length - 2}` : ''}`;
  };

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Dashboard</h1>
          <p className={styles.subtitle}>View past runs or start a new comparison.</p>
        </div>
        <div className={styles.headerButtons}>
          <button className={styles.compareButton} onClick={() => navigate('/compare')}>
            📊 Compare Runs
          </button>
          <button className={styles.newRunButton} onClick={() => navigate('/new')}>
            <span className={styles.buttonIcon}>⊕</span>
            New Run
          </button>
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>📋</span>
            Past Runs
          </h2>
        </div>

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        {loading ? (
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>Loading experiments...</p>
          </div>
        ) : experiments.length === 0 ? (
          <div className={styles.empty}>
            <div className={styles.emptyIcon}>🤖</div>
            <h3 className={styles.emptyTitle}>No runs found</h3>
            <p className={styles.emptyText}>Get started by creating a new run.</p>
            <button className={styles.emptyButton} onClick={() => navigate('/new')}>
              Create New Run
            </button>
          </div>
        ) : (
          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Dataset</th>
                  <th>Models</th>
                  <th>Status</th>
                  <th>Started</th>
                  <th>Prompts</th>
                </tr>
              </thead>
              <tbody>
                {experiments.map((exp) => (
                  <tr
                    key={exp.id}
                    className={styles.tableRow}
                    onClick={() => navigate(`/run/${exp.id}`)}
                  >
                    <td className={styles.runId}>
                      <span className={styles.runIdText}>{exp.id.substring(0, 12)}...</span>
                    </td>
                    <td>
                      <div className={styles.datasetInfo}>
                        <span className={styles.datasetName}>{exp.dataset_name}</span>
                        <span className={styles.datasetVersion}>@1.0</span>
                      </div>
                    </td>
                    <td className={styles.models}>{formatModels(exp.model_ids)}</td>
                    <td>
                      <span className={styles.statusBadge}>completed</span>
                    </td>
                    <td className={styles.started}>{formatDate(exp.timestamp)}</td>
                    <td className={styles.prompts}>{exp.tasks_evaluated}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
