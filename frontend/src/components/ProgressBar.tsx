/**
 * Progress Bar Component
 * Displays real-time progress for batch evaluations
 */

import { useEffect, useState } from 'react';
import styles from './ProgressBar.module.css';

export interface ProgressUpdate {
  run_id: string;
  completed_tasks: number;
  total_tasks: number;
  percentage: number;
  status: 'running' | 'done' | 'error';
  message?: string;
  timestamp?: string;
}

interface ProgressBarProps {
  runId: string | null;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || API_BASE_URL.replace(/^http/, 'ws');
const WS_URL = `${WS_BASE_URL}/ws/progress`;
const POLLING_URL = `${API_BASE_URL}/api/progress`;
const POLLING_INTERVAL = 1000; // Poll every second

export const ProgressBar: React.FC<ProgressBarProps> = ({ runId, onComplete, onError }) => {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionMethod, setConnectionMethod] = useState<'websocket' | 'polling' | null>(null);

  useEffect(() => {
    if (!runId) {
      setProgress(null);
      return;
    }

    setIsConnecting(true);

    // Try WebSocket first
    let ws: WebSocket | null = null;
    let pollingInterval: NodeJS.Timeout | null = null;
    let isWebSocketFailed = false;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(`${WS_URL}?run_id=${runId}`);

        ws.onopen = () => {
          console.log('WebSocket connected for run_id:', runId);
          setIsConnecting(false);
          setConnectionMethod('websocket');
        };

        ws.onmessage = (event) => {
          try {
            const update: ProgressUpdate = JSON.parse(event.data);
            console.log('Progress update:', update);
            setProgress(update);

            if (update.status === 'done') {
              console.log('Evaluation complete');
              onComplete?.();
            } else if (update.status === 'error') {
              console.error('Evaluation error:', update.message);
              onError?.(update.message || 'Unknown error');
            } else if (update.percentage === 100 && update.status === 'running') {
              // Edge case: 100% but status still "running"
              // Wait briefly for the "done" status update
              setTimeout(() => {
                const currentProgress = update;
                if (currentProgress.percentage === 100) {
                  console.log('Evaluation complete (100% reached)');
                  onComplete?.();
                }
              }, 500);
            }
          } catch (err) {
            console.error('Failed to parse progress update:', err);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          if (!isWebSocketFailed) {
            isWebSocketFailed = true;
            // Fall back to polling
            startPolling();
          }
        };

        ws.onclose = () => {
          console.log('WebSocket closed');
        };
      } catch (err) {
        console.error('Failed to create WebSocket:', err);
        // Fall back to polling
        startPolling();
      }
    };

    const startPolling = () => {
      console.log('Falling back to polling for run_id:', runId);
      setConnectionMethod('polling');
      setIsConnecting(false);

      const poll = async () => {
        try {
          const response = await fetch(`${POLLING_URL}/${runId}`);

          if (!response.ok) {
            if (response.status === 404) {
              // Run not found, stop polling
              console.warn('Run not found, stopping polling');
              if (pollingInterval) clearInterval(pollingInterval);
              return;
            }
            throw new Error(`Polling failed: ${response.statusText}`);
          }

          const update: ProgressUpdate = await response.json();
          setProgress(update);

          if (update.status === 'done') {
            console.log('Evaluation complete (polling)');
            if (pollingInterval) clearInterval(pollingInterval);
            onComplete?.();
          } else if (update.status === 'error') {
            console.error('Evaluation error (polling):', update.message);
            if (pollingInterval) clearInterval(pollingInterval);
            onError?.(update.message || 'Unknown error');
          } else if (update.percentage === 100 && update.status === 'running') {
            // Edge case: 100% but status still "running"
            console.log('Evaluation complete (polling - 100% reached)');
            if (pollingInterval) clearInterval(pollingInterval);
            onComplete?.();
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      };

      // Start polling immediately and then at intervals
      poll();
      pollingInterval = setInterval(poll, POLLING_INTERVAL);
    };

    // Try WebSocket connection
    connectWebSocket();

    // Cleanup
    return () => {
      if (ws) {
        ws.close();
      }
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [runId, onComplete, onError]);

  if (!runId || !progress) {
    return null;
  }

  const { completed_tasks, total_tasks, percentage, status } = progress;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.info}>
          <span className={styles.label}>
            {status === 'running'
              ? 'Evaluating...'
              : status === 'done'
              ? 'Complete'
              : 'Error'}
          </span>
          <span className={styles.stats}>
            {completed_tasks} / {total_tasks} tasks ({percentage.toFixed(1)}%)
          </span>
        </div>
        {connectionMethod === 'polling' && (
          <span className={styles.pollingIndicator} title="Using polling (WebSocket unavailable)">
            ⟳
          </span>
        )}
      </div>

      <div className={styles.barContainer}>
        <div
          className={`${styles.bar} ${status === 'error' ? styles.barError : ''} ${
            status === 'done' ? styles.barComplete : ''
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {isConnecting && <div className={styles.connecting}>Connecting...</div>}
    </div>
  );
};
