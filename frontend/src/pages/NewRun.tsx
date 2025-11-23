/**
 * New Run Page
 * Interface for creating and running new evaluations
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DatasetUpload, type SamplingConfig } from '../components/DatasetUpload';
import { ModelSelector } from '../components/ModelSelector';
import { ProgressBar } from '../components/ProgressBar';
import { evaluate, compare } from '../api/client';
import { saveExperiment, generateExperimentName } from '../api/experiments';
import { getAPIKeyForProvider } from '../utils/apiKeys';
import type { Task, ModelConfig, EvaluationResult } from '../types/api';
import styles from './NewRun.module.css';

/**
 * Randomly sample N tasks from the full dataset
 */
function randomSample<T>(array: T[], sampleSize: number): T[] {
  if (sampleSize >= array.length) {
    return [...array];
  }

  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  return shuffled.slice(0, sampleSize);
}

export const NewRun: React.FC = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [datasetFileName, setDatasetFileName] = useState<string>('');
  const [originalDatasetSize, setOriginalDatasetSize] = useState<number>(0);
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);
  const [samplingConfig, setSamplingConfig] = useState<SamplingConfig>({
    mode: 'all',
    sampleSize: 50,
  });

  const handleDatasetLoad = (loadedTasks: Task[], fileName: string) => {
    setTasks(loadedTasks);
    setDatasetFileName(fileName);
    setOriginalDatasetSize(loadedTasks.length);
    setError(null);
  };

  const handleProgressComplete = async () => {
    console.log('Evaluation completed, navigating to dashboard');
    // Navigate back to dashboard to see the new run
    navigate('/');
  };

  const handleProgressError = (errorMessage: string) => {
    console.error('Evaluation error:', errorMessage);
    setError(errorMessage);
    setIsRunning(false);
    setCurrentRunId(null);
  };

  const handleRunBenchmark = async () => {
    setError(null);

    if (tasks.length === 0) {
      setError('Please upload a dataset first');
      return;
    }

    if (models.length === 0) {
      setError('Please configure at least one model');
      return;
    }

    setIsRunning(true);
    // Generate a run ID up front so the progress bar can connect immediately
    const runId = crypto.randomUUID();
    setCurrentRunId(runId);

    try {
      // Sample tasks if needed
      const tasksToEvaluate =
        samplingConfig.mode === 'random'
          ? randomSample(tasks, samplingConfig.sampleSize)
          : tasks;

      console.log(`Running evaluation on ${tasksToEvaluate.length} tasks with ${models.length} model(s)`);

      // Inject API keys from localStorage into model configurations
      const modelsWithAPIKeys = models.map(model => ({
        ...model,
        api_key: getAPIKeyForProvider(model.provider) || model.api_key,
      }));

      let results: EvaluationResult[];

      if (models.length === 1) {
        // Single model evaluation
        const response = await evaluate({
          model_configuration: modelsWithAPIKeys[0],
          tasks: tasksToEvaluate,
          run_id: runId,
        });
        results = [response.result];
      } else {
        // Compare multiple models
        const response = await compare({
          model_configurations: modelsWithAPIKeys,
          tasks: tasksToEvaluate,
          run_id: runId,
        });
        results = response.results;
      }

      // Save experiment to history
      const experimentName = generateExperimentName({
        models: models,
        dataset_name: datasetFileName,
      });
      await saveExperiment({
        name: experimentName,
        dataset_name: datasetFileName,
        dataset_size: originalDatasetSize,
        results,
        sampling_config: {
          mode: samplingConfig.mode,
          sample_size: samplingConfig.sampleSize,
        },
        tags: [],
      });

      console.log('Experiment saved successfully');

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Evaluation failed';
      setError(message);
      setIsRunning(false);
      setCurrentRunId(null);
    }
  };

  return (
    <div className={styles.newRun}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>New Run</h1>
          <p className={styles.subtitle}>Configure and start a new evaluation run.</p>
        </div>
        <button className={styles.cancelButton} onClick={() => navigate('/')}>
          Cancel
        </button>
      </div>

      <div className={styles.content}>
        {error && (
          <div className={styles.error}>
            <span className={styles.errorIcon}>⚠️</span>
            {error}
          </div>
        )}

        {/* Dataset Upload Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>📁</span>
            Dataset
          </h2>
          <DatasetUpload
            onDatasetLoad={handleDatasetLoad}
            samplingConfig={samplingConfig}
            onSamplingConfigChange={setSamplingConfig}
          />
          {tasks.length > 0 && (
            <div className={styles.datasetInfo}>
              <span className={styles.infoLabel}>Loaded:</span>
              <span className={styles.infoValue}>
                {tasks.length} tasks from {datasetFileName}
              </span>
            </div>
          )}
        </div>

        {/* Model Configuration Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>🤖</span>
            Models
          </h2>
          <ModelSelector selectedModels={models} onModelsChange={setModels} />
        </div>

        {/* Progress Bar */}
        {isRunning && currentRunId && (
          <ProgressBar
            runId={currentRunId}
            onComplete={handleProgressComplete}
            onError={handleProgressError}
          />
        )}

        {/* Run Button */}
        <div className={styles.actions}>
          <button
            className={styles.runButton}
            onClick={handleRunBenchmark}
            disabled={isRunning || tasks.length === 0 || models.length === 0}
          >
            {isRunning ? (
              <>
                <span className={styles.spinner} />
                Running Evaluation...
              </>
            ) : (
              <>
                <span className={styles.runIcon}>▶</span>
                Run Evaluation
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
