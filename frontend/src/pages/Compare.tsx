/**
 * Compare Page
 * Compare multiple experiment runs side-by-side
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getExperiment, listExperiments } from '../api/experiments';
import { exportMetricsSummaryToCSV, downloadFile } from '../utils/export';
import type { ExperimentMetadata, ExperimentData } from '../types/experiments';
import styles from './Compare.module.css';

export const Compare: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [allExperiments, setAllExperiments] = useState<ExperimentMetadata[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loadedExperiments, setLoadedExperiments] = useState<ExperimentData[]>([]);
  const [selectedModelIndex, setSelectedModelIndex] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadExperimentList();

    // Load experiments from URL params
    const ids = searchParams.get('ids');
    if (ids) {
      const idList = ids.split(',');
      setSelectedIds(idList);
      loadExperimentsForComparison(idList);
    }
  }, []);

  const loadExperimentList = async () => {
    try {
      const experiments = await listExperiments();
      setAllExperiments(experiments);
    } catch (err) {
      console.error('Failed to load experiments:', err);
    }
  };

  const loadExperimentsForComparison = async (ids: string[]) => {
    setLoading(true);
    try {
      const promises = ids.map(id => getExperiment(id));
      const results = await Promise.all(promises);
      setLoadedExperiments(results);
      // Reset model selections per experiment
      const defaults: Record<string, number> = {};
      results.forEach(exp => {
        defaults[exp.metadata.id] = 0;
      });
      setSelectedModelIndex(defaults);
    } catch (err) {
      console.error('Failed to load experiments for comparison:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleExperiment = (id: string) => {
    const newSelected = selectedIds.includes(id)
      ? selectedIds.filter(sid => sid !== id)
      : [...selectedIds, id];

    setSelectedIds(newSelected);
  };

  const handleCompare = () => {
    if (selectedIds.length > 0) {
      loadExperimentsForComparison(selectedIds);
    }
  };

  const handleExportCSV = () => {
    if (loadedExperiments.length > 0) {
      const csv = exportMetricsSummaryToCSV(loadedExperiments);
      downloadFile(csv, `comparison_${Date.now()}.csv`, 'text/csv');
    }
  };

  return (
    <div className={styles.compare}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Compare Experiments</h1>
          <p className={styles.subtitle}>Select experiments to compare their performance</p>
        </div>
        <button className={styles.backButton} onClick={() => navigate('/')}>
          ← Back to Dashboard
        </button>
      </div>

      <div className={styles.content}>
        {/* Experiment Selection */}
        <div className={styles.selectionPanel}>
          <h2 className={styles.sectionTitle}>Select Experiments ({selectedIds.length} selected)</h2>
          <div className={styles.experimentList}>
            {allExperiments.map((exp) => (
              <div
                key={exp.id}
                className={`${styles.experimentItem} ${
                  selectedIds.includes(exp.id) ? styles.selected : ''
                }`}
                onClick={() => toggleExperiment(exp.id)}
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(exp.id)}
                  onChange={() => {}}
                  className={styles.checkbox}
                />
                <div className={styles.experimentInfo}>
                  <div className={styles.experimentName}>{exp.name}</div>
                  <div className={styles.experimentMeta}>
                    {exp.dataset_name} • {exp.model_ids.join(', ')} • {exp.tasks_evaluated} tasks
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button
            className={styles.compareButton}
            onClick={handleCompare}
            disabled={selectedIds.length === 0}
          >
            Compare Selected ({selectedIds.length})
          </button>
        </div>

        {/* Comparison Results */}
        {loading && (
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>Loading experiments...</p>
          </div>
        )}

        {!loading && loadedExperiments.length > 0 && (
          <div className={styles.comparisonPanel}>
            <div className={styles.comparisonHeader}>
              <h2 className={styles.sectionTitle}>Comparison Results</h2>
              <button className={styles.exportButton} onClick={handleExportCSV}>
                📊 Export CSV
              </button>
            </div>

            <div className={styles.tableContainer}>
              <table className={styles.comparisonTable}>
                <thead>
                  <tr>
                    <th>Metric</th>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      const result = exp.results[modelIdx];
                      return (
                        <th key={exp.metadata.id}>
                          <div className={styles.columnHeader}>
                            <div className={styles.columnTitle}>{exp.metadata.name}</div>
                            <div className={styles.columnSubtitle}>
                              <select
                                className={styles.modelSelect}
                                value={modelIdx}
                                onChange={(e) =>
                                  setSelectedModelIndex((prev) => ({
                                    ...prev,
                                    [exp.metadata.id]: parseInt(e.target.value, 10),
                                  }))
                                }
                              >
                                {exp.results.map((res, idx) => (
                                  <option key={res.model_configuration.model_id + idx} value={idx}>
                                    {res.model_configuration.model_id}
                                  </option>
                                ))}
                              </select>
                            </div>
                            <div className={styles.columnSubtitle}>
                              {result?.model_configuration.model_id}
                            </div>
                          </div>
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className={styles.metricLabel}>Dataset</td>
                    {loadedExperiments.map((exp) => (
                      <td key={exp.metadata.id}>{exp.metadata.dataset_name}</td>
                    ))}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>Tasks Evaluated</td>
                    {loadedExperiments.map((exp) => (
                      <td key={exp.metadata.id}>{exp.metadata.tasks_evaluated}</td>
                    ))}
                  </tr>
                  <tr className={styles.highlightRow}>
                    <td className={styles.metricLabel}>Accuracy</td>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      const accuracy = exp.results[modelIdx]?.metrics.accuracy ?? 0;
                      return (
                        <td key={exp.metadata.id} className={styles.accuracyCell}>
                          {(accuracy * 100).toFixed(2)}%
                        </td>
                      );
                    })}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>Brier Score</td>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      return (
                        <td key={exp.metadata.id}>
                          {exp.results[modelIdx]?.metrics.brier?.toFixed(4) ?? 'N/A'}
                        </td>
                      );
                    })}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>ECE</td>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      return (
                        <td key={exp.metadata.id}>
                          {exp.results[modelIdx]?.metrics.ece?.toFixed(4) ?? 'N/A'}
                        </td>
                      );
                    })}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>SCE</td>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      return (
                        <td key={exp.metadata.id}>
                          {exp.results[modelIdx]?.metrics.sce?.toFixed(4) ?? 'N/A'}
                        </td>
                      );
                    })}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>USR</td>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      return (
                        <td key={exp.metadata.id}>
                          {exp.results[modelIdx]?.metrics.usr?.toFixed(4) ?? 'N/A'}
                        </td>
                      );
                    })}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>Avg CoT Tokens</td>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      return (
                        <td key={exp.metadata.id}>
                          {exp.results[modelIdx]?.metrics.cot_tokens_mean?.toFixed(1) ?? 'N/A'}
                        </td>
                      );
                    })}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>Avg Latency (ms)</td>
                    {loadedExperiments.map((exp) => {
                      const modelIdx = selectedModelIndex[exp.metadata.id] || 0;
                      return (
                        <td key={exp.metadata.id}>
                          {exp.results[modelIdx]?.metrics.latency_mean_ms?.toFixed(2) ?? 'N/A'}
                        </td>
                      );
                    })}
                  </tr>
                  <tr>
                    <td className={styles.metricLabel}>Timestamp</td>
                    {loadedExperiments.map((exp) => (
                      <td key={exp.metadata.id}>
                        {new Date(exp.metadata.timestamp).toLocaleString()}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
