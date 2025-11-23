/**
 * MetricsChart component
 * Visualizes metrics comparison across models using bar charts
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { EvaluationResult } from '../types/api';

interface MetricsChartProps {
  results: EvaluationResult[];
}

export function MetricsChart({ results }: MetricsChartProps) {
  if (results.length === 0) {
    return null;
  }

  // Transform data for recharts
  // Each metric becomes a data point with values from all models
  const metricsData = [
    {
      metric: 'Accuracy',
      ...Object.fromEntries(
        results.map((r) => [r.model_configuration.model_id, r.metrics.accuracy])
      ),
    },
    {
      metric: 'Brier Score',
      ...Object.fromEntries(
        results.map((r) => [r.model_configuration.model_id, r.metrics.brier_score])
      ),
    },
    {
      metric: 'ECE',
      ...Object.fromEntries(
        results.map((r) => [r.model_configuration.model_id, r.metrics.expected_calibration_error])
      ),
    },
    {
      metric: 'SCE',
      ...Object.fromEntries(
        results.map((r) => [r.model_configuration.model_id, r.metrics.self_consistency_entropy])
      ),
    },
    {
      metric: 'USR',
      ...Object.fromEntries(
        results.map((r) => [r.model_configuration.model_id, r.metrics.unsupported_step_rate])
      ),
    },
  ];

  // Generate colors for each model
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#a28bd4', '#f4a460'];

  return (
    <div style={{ marginTop: '30px' }}>
      <h3>Metrics Comparison</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={metricsData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="metric" />
          <YAxis />
          <Tooltip />
          <Legend />
          {results.map((result, index) => (
            <Bar
              key={result.model_configuration.model_id}
              dataKey={result.model_configuration.model_id}
              fill={colors[index % colors.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
