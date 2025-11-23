/**
 * Utility functions for exporting experiment data
 */

import type { ExperimentData } from '../types/experiments';
import type { EvaluationResult, TaskResult } from '../types/api';

/**
 * Convert experiment data to CSV format
 */
export function exportToCSV(experiment: ExperimentData): string {
  const headers = [
    'Model',
    'Task ID',
    'Input',
    'Target',
    'Model Answer',
    'Correct',
    'Confidence',
    'CoT Tokens',
    'CoT Chars',
    'Step Count',
    'Latency (ms)',
    'Prompt Tokens',
    'Completion Tokens',
    'Total Tokens',
  ];

  const rows: string[][] = [headers];

  // Add data rows
  experiment.results.forEach((result: EvaluationResult) => {
    const modelId = result.model_configuration.model_id;

    result.task_results.forEach((task: TaskResult) => {
      rows.push([
        modelId,
        task.task_id,
        escapeCSV(task.input),
        escapeCSV(task.target),
        escapeCSV(task.model_output.answer),
        task.correct.toString(),
        task.model_output.confidence?.toString() || '',
        task.cot_tokens?.toString() || '',
        task.cot_chars?.toString() || '',
        task.step_count?.toString() || '',
        task.latency_ms?.toFixed(2) || '',
        task.prompt_tokens?.toString() || '',
        task.completion_tokens?.toString() || '',
        task.total_tokens?.toString() || '',
      ]);
    });
  });

  return rows.map(row => row.join(',')).join('\n');
}

/**
 * Escape CSV field (handle commas, quotes, newlines)
 */
function escapeCSV(field: string): string {
  if (field.includes(',') || field.includes('"') || field.includes('\n')) {
    return `"${field.replace(/"/g, '""')}"`;
  }
  return field;
}

/**
 * Download data as a file
 */
export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain') {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Export experiment to CSV file
 */
export function exportExperimentToCSV(experiment: ExperimentData) {
  const csv = exportToCSV(experiment);
  const filename = `${experiment.metadata.name.replace(/[^a-z0-9]/gi, '_')}_${Date.now()}.csv`;
  downloadFile(csv, filename, 'text/csv');
}

/**
 * Export experiment to JSON file
 */
export function exportExperimentToJSON(experiment: ExperimentData) {
  const json = JSON.stringify(experiment, null, 2);
  const filename = `${experiment.metadata.name.replace(/[^a-z0-9]/gi, '_')}_${Date.now()}.json`;
  downloadFile(json, filename, 'application/json');
}

/**
 * Create a summary metrics CSV for comparison
 */
export function exportMetricsSummaryToCSV(experiments: ExperimentData[]): string {
  const headers = [
    'Experiment',
    'Model',
    'Dataset',
    'Tasks',
    'Accuracy',
    'Brier Score',
    'ECE',
    'SCE',
    'USR',
    'Avg CoT Tokens',
    'Avg Latency (ms)',
    'Timestamp',
  ];

  const rows: string[][] = [headers];

  experiments.forEach((exp) => {
    exp.results.forEach((result) => {
      rows.push([
        escapeCSV(exp.metadata.name),
        result.model_configuration.model_id,
        exp.metadata.dataset_name,
        exp.metadata.tasks_evaluated.toString(),
        (result.metrics.accuracy * 100).toFixed(2) + '%',
        result.metrics.brier?.toFixed(4) || 'N/A',
        result.metrics.ece?.toFixed(4) || 'N/A',
        result.metrics.sce?.toFixed(4) || 'N/A',
        result.metrics.usr?.toFixed(4) || 'N/A',
        result.metrics.cot_tokens_mean?.toFixed(1) || 'N/A',
        result.metrics.latency_mean_ms?.toFixed(2) || 'N/A',
        exp.metadata.timestamp,
      ]);
    });
  });

  return rows.map(row => row.join(',')).join('\n');
}
