import React from 'react';

interface MetricsLegendProps {
  compact?: boolean;
}

const MetricsLegend: React.FC<MetricsLegendProps> = ({ compact = false }) => {
  if (compact) {
    return (
      <div className="metrics-legend-compact">
        <span className="legend-item">
          <code>0.000</code> = measured zero
        </span>
        <span className="legend-separator">•</span>
        <span className="legend-item">
          <code>—</code> = no data
        </span>

        <style>{`
          .metrics-legend-compact {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #666;
            padding: 4px 0;
          }

          .legend-item {
            display: inline-flex;
            align-items: center;
            gap: 4px;
          }

          .legend-item code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #333;
            border: 1px solid #e0e0e0;
          }

          .legend-separator {
            color: #ccc;
            font-weight: bold;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="metrics-legend">
      <div className="legend-header">Metric Values:</div>
      <div className="legend-items">
        <div className="legend-row">
          <code className="legend-code">0.000</code>
          <span className="legend-description">Real measured zero (metric computed, value is 0)</span>
        </div>
        <div className="legend-row">
          <code className="legend-code">—</code>
          <span className="legend-description">No data available (metric not yet implemented or insufficient data)</span>
        </div>
      </div>

      <style>{`
        .metrics-legend {
          background: #f9f9f9;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          padding: 12px 16px;
          margin: 16px 0;
          font-size: 13px;
        }

        .legend-header {
          font-weight: 600;
          color: #555;
          margin-bottom: 8px;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .legend-items {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .legend-row {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .legend-code {
          background: #fff;
          padding: 4px 8px;
          border-radius: 4px;
          font-family: 'Courier New', monospace;
          font-size: 13px;
          color: #333;
          border: 1px solid #d0d0d0;
          min-width: 60px;
          text-align: center;
          font-weight: 600;
        }

        .legend-description {
          color: #666;
          line-height: 1.4;
        }
      `}</style>
    </div>
  );
};

export default MetricsLegend;
