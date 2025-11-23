/**
 * Component for displaying metrics in a table format
 */

import React from 'react';
import type { EvaluationResult } from '../types/api';
import { formatMetric } from '../utils/formatMetric';

interface MetricsTableProps {
  results: EvaluationResult[];
}

export const MetricsTable: React.FC<MetricsTableProps> = ({ results }) => {
  if (results.length === 0) {
    return null;
  }

  const metricLabels = [
    { key: 'accuracy', label: 'Accuracy (ACC)' },
    { key: 'brier', label: 'Brier Score' },
    { key: 'ece', label: 'ECE' },
    { key: 'sce', label: 'SCE' },
    { key: 'usr', label: 'USR' },
  ];

  return (
    <div style={{ marginBottom: '20px' }}>
      <h3>Metrics Summary</h3>
      <div style={{ overflowX: 'auto' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '14px',
          }}
        >
          <thead>
            <tr style={{ backgroundColor: '#f0f0f0' }}>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                Metric
              </th>
              {results.map((result, index) => (
                <th
                  key={index}
                  style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}
                >
                  {result.model_configuration.model_id}
                  <br />
                  <span style={{ fontSize: '12px', color: '#666', fontWeight: 'normal' }}>
                    ({result.model_configuration.provider})
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metricLabels.map((metric) => (
              <tr key={metric.key}>
                <td
                  style={{
                    padding: '10px',
                    borderBottom: '1px solid #ddd',
                    fontWeight: '500',
                  }}
                >
                  {metric.label}
                </td>
                {results.map((result, index) => {
                  const value = result.metrics[metric.key as keyof typeof result.metrics];
                  return (
                    <td
                      key={index}
                      style={{
                        padding: '10px',
                        textAlign: 'right',
                        borderBottom: '1px solid #ddd',
                        fontFamily: 'monospace',
                      }}
                    >
                      {formatMetric(value as number | null, 4)}
                    </td>
                  );
                })}
              </tr>
            ))}
            <tr style={{ backgroundColor: '#f9f9f9' }}>
              <td style={{ padding: '10px', fontWeight: '500' }}>Total Tasks</td>
              {results.map((result, index) => (
                <td
                  key={index}
                  style={{
                    padding: '10px',
                    textAlign: 'right',
                    fontFamily: 'monospace',
                  }}
                >
                  {result.total_tasks}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
