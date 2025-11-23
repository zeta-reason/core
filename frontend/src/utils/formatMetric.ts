/**
 * Format a metric value for display.
 * Null/undefined/NaN values are shown as "—" (em dash).
 * Real zeros are shown as "0.000" (or with specified precision).
 */
export function formatMetric(
  value: number | null | undefined,
  digits: number = 3
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';
  }
  return value.toFixed(digits);
}

/**
 * Format an integer metric value (no decimal places).
 * Null/undefined/NaN values are shown as "—".
 */
export function formatMetricInt(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';
  }
  return Math.round(value).toLocaleString();
}
