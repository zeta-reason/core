import React from 'react';
import type { MetricsSummary } from '../types/api';
import { formatMetric, formatMetricInt } from '../utils/formatMetric';

interface MetricCardsProps {
  metrics: MetricsSummary;
}

interface MetricCardData {
  label: string;
  value: number | null;
  unit?: string;
  useInteger?: boolean;
  highlight?: 'accuracy';
}

const MetricCards: React.FC<MetricCardsProps> = ({ metrics }) => {

  const cardData: MetricCardData[] = [
    {
      label: 'Accuracy',
      value: metrics.accuracy,
      highlight: 'accuracy',
    },
    {
      label: 'Unsupported Step Rate',
      value: metrics.usr,
    },
    {
      label: 'Self-Consistency Entropy',
      value: metrics.sce,
    },
    {
      label: 'Avg CoT Tokens',
      value: metrics.cot_tokens_mean,
      useInteger: true,
    },
    {
      label: 'Avg Latency',
      value: metrics.latency_mean_ms,
      unit: 'ms',
      useInteger: true,
    },
    {
      label: 'Avg Total Tokens',
      value: metrics.total_tokens_mean,
      useInteger: true,
    },
  ];

  const getAccuracyColor = (accuracy: number): string => {
    if (accuracy > 0.8) return '#4caf50'; // Green
    if (accuracy < 0.5) return '#f44336'; // Red
    return '#2196f3'; // Blue (default)
  };

  return (
    <div className="metric-cards-container">
      <div className="metric-cards-grid">
        {cardData.map((card, index) => {
          const displayValue = card.useInteger
            ? formatMetricInt(card.value)
            : formatMetric(card.value, 3);

          const isAccuracy = card.highlight === 'accuracy';
          const accentColor =
            isAccuracy && card.value !== null && card.value !== undefined
              ? getAccuracyColor(card.value)
              : '#4a90e2';

          return (
            <div
              key={index}
              className="metric-card"
              style={{
                borderTop: `3px solid ${accentColor}`,
              }}
            >
              <div className="metric-label">{card.label}</div>
              <div
                className="metric-value"
                style={{
                  color: isAccuracy && card.value !== null && card.value !== undefined ? accentColor : '#333',
                }}
              >
                {displayValue}
                {card.unit && card.value !== null && card.value !== undefined && (
                  <span className="metric-unit"> {card.unit}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <style>{`
        .metric-cards-container {
          margin-bottom: 24px;
        }

        .metric-cards-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }

        @media (max-width: 900px) {
          .metric-cards-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (max-width: 600px) {
          .metric-cards-grid {
            grid-template-columns: 1fr;
          }
        }

        .metric-card {
          background: #fff;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 20px;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .metric-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .metric-label {
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          color: #666;
          letter-spacing: 0.5px;
          margin-bottom: 8px;
        }

        .metric-value {
          font-size: 32px;
          font-weight: 700;
          line-height: 1.2;
        }

        .metric-unit {
          font-size: 18px;
          font-weight: 500;
          color: #999;
          margin-left: 4px;
        }
      `}</style>
    </div>
  );
};

export default MetricCards;
