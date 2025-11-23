/**
 * Main application component for Zeta Reason frontend
 */

import { useState } from 'react';
import { DatasetUpload, type SamplingConfig } from './components/DatasetUpload';
import { ModelSelector } from './components/ModelSelector';
import { MetricsTable } from './components/MetricsTable';
import { MetricsChart } from './components/MetricsChart';
import { CotViewer } from './components/CotViewer';
import ResearchModeView from './components/ResearchModeView';
import MetricCards from './components/MetricCards';
import MetricsLegend from './components/MetricsLegend';
import ErrorBanner from './components/ErrorBanner';
import { ExperimentHistory } from './components/ExperimentHistory';
import { evaluate, compare } from './api/client';
import { saveExperiment, generateExperimentName } from './api/experiments';
import type { Task, ModelConfig, EvaluationState, EvaluationResult } from './types/api';
import { useTheme } from './contexts/ThemeContext';

import './App.css';

type UIMode = 'summary' | 'research';

/**
 * Randomly sample N tasks from the full dataset
 * Uses Fisher-Yates shuffle algorithm for unbiased sampling
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

function App() {
  const { theme, toggleTheme } = useTheme();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [datasetFileName, setDatasetFileName] = useState<string>('');
  const [originalDatasetSize, setOriginalDatasetSize] = useState<number>(0);
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [evaluationState, setEvaluationState] = useState<EvaluationState>({ type: 'idle' });
  const [uiMode, setUiMode] = useState<UIMode>('summary');
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [samplingConfig, setSamplingConfig] = useState<SamplingConfig>({
    mode: 'all',
    sampleSize: 50,
  });

  const handleDatasetLoad = (loadedTasks: Task[], fileName: string) => {
    setTasks(loadedTasks);
    setDatasetFileName(fileName);
    setOriginalDatasetSize(loadedTasks.length);
  };

  const handleLoadExperiment = (results: EvaluationResult[]) => {
    // Load experiment results into the evaluation state
    if (results.length === 1) {
      setEvaluationState({ type: 'single', result: results[0] });
    } else if (results.length > 1) {
      setEvaluationState({ type: 'compare', results });
    }
    setGlobalError(null);
  };

  const handleRunBenchmark = async () => {
    // Clear any previous global errors
    setGlobalError(null);

    if (tasks.length === 0) {
      setGlobalError('Please upload a dataset first');
      return;
    }

    if (models.length === 0) {
      setGlobalError('Please configure at least one model');
      return;
    }

    // Apply sampling based on configuration
    let tasksToEvaluate: Task[] = tasks;
    if (samplingConfig.mode === 'random') {
      const effectiveSampleSize = Math.min(samplingConfig.sampleSize, tasks.length);
      tasksToEvaluate = randomSample(tasks, effectiveSampleSize);
      console.log(`Sampling ${effectiveSampleSize} tasks from ${tasks.length} total tasks`);
    }

    setEvaluationState({ type: 'loading' });

    try {
      if (models.length === 1) {
        // Single model evaluation
        console.log('Starting single model evaluation...');
        const response = await evaluate({
          model_configuration: models[0],
          tasks: tasksToEvaluate,
        });
        console.log('Evaluation response:', response);
        setEvaluationState({ type: 'single', result: response.result });
        setGlobalError(null); // Clear any errors on success

        // Auto-save experiment
        try {
          const experimentName = generateExperimentName({
            models: [{ model_id: models[0].model_id }],
            dataset_name: datasetFileName,
          });
          const experimentId = await saveExperiment({
            name: experimentName,
            dataset_name: datasetFileName,
            dataset_size: originalDatasetSize,
            results: [response.result],
            sampling_config: samplingConfig,
          });
          console.log('Experiment saved with ID:', experimentId);
        } catch (saveError) {
          console.error('Failed to save experiment:', saveError);
          // Don't fail the evaluation if save fails
        }
      } else {
        // Multi-model comparison
        console.log('Starting comparison of', models.length, 'models...');
        const response = await compare({
          model_configurations: models,
          tasks: tasksToEvaluate,
        });
        console.log('Comparison response:', response);
        setEvaluationState({ type: 'compare', results: response.results });
        setGlobalError(null); // Clear any errors on success

        // Auto-save experiment
        try {
          const experimentName = generateExperimentName({
            models: models.map((m) => ({ model_id: m.model_id })),
            dataset_name: datasetFileName,
          });
          const experimentId = await saveExperiment({
            name: experimentName,
            dataset_name: datasetFileName,
            dataset_size: originalDatasetSize,
            results: response.results,
            sampling_config: samplingConfig,
          });
          console.log('Experiment saved with ID:', experimentId);
        } catch (saveError) {
          console.error('Failed to save experiment:', saveError);
          // Don't fail the evaluation if save fails
        }
      }
    } catch (error) {
      console.error('Evaluation error:', error);
      const message = error instanceof Error ? error.message : 'Unknown error occurred';

      // Set global error for display in ErrorBanner
      setGlobalError(message);

      // Also set evaluation state to error for backward compatibility
      setEvaluationState({ type: 'error', error: message });
    }
  };

  const getResults = () => {
    if (evaluationState.type === 'single') {
      return [evaluationState.result];
    } else if (evaluationState.type === 'compare') {
      return evaluationState.results;
    }
    return [];
  };

  const results = getResults();

  const handleDownloadResults = () => {
    let dataToDownload;
    let filename: string;

    if (evaluationState.type === 'single') {
      // Single model result
      dataToDownload = evaluationState.result;
      filename = `zeta_reason_result_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    } else if (evaluationState.type === 'compare') {
      // Multi-model comparison results
      dataToDownload = evaluationState.results;
      filename = `zeta_reason_comparison_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    } else {
      return; // No data to download
    }

    // Serialize to JSON with pretty formatting
    const jsonString = JSON.stringify(dataToDownload, null, 2);

    // Create a Blob with the JSON data
    const blob = new Blob([jsonString], { type: 'application/json' });

    // Create a temporary URL for the blob
    const url = URL.createObjectURL(blob);

    // Create a temporary anchor element and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app">
      <header className="header">
        <button className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
          {theme === 'light' ? '🌙' : '☀️'}
          <span>{theme === 'light' ? 'Dark' : 'Light'}</span>
        </button>
        <h1>Zeta Reason</h1>
        <p className="subtitle">Chain-of-Thought Reasoning Benchmarking for LLMs</p>
      </header>

      <main className="main">
        {/* Global Error Banner */}
        {globalError && (
          <ErrorBanner message={globalError} onDismiss={() => setGlobalError(null)} />
        )}

        {/* Step 1: Upload Dataset */}
        <DatasetUpload onDatasetLoad={handleDatasetLoad} onSamplingConfigChange={setSamplingConfig} />

        {/* Step 2: Configure Models */}
        <ModelSelector onModelsChange={setModels} />

        {/* Step 3: Run Benchmark */}
        <div style={{ marginBottom: '20px', textAlign: 'center' }}>
          <button
            onClick={handleRunBenchmark}
            disabled={evaluationState.type === 'loading' || tasks.length === 0}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: evaluationState.type === 'loading' || tasks.length === 0 ? 'not-allowed' : 'pointer',
              backgroundColor: evaluationState.type === 'loading' || tasks.length === 0 ? '#ccc' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
            }}
          >
            {evaluationState.type === 'loading'
              ? 'Running...'
              : models.length === 1
              ? 'Run Evaluation'
              : `Compare ${models.length} Models`}
          </button>

          {tasks.length > 0 && (
            <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
              Ready to evaluate{' '}
              {samplingConfig.mode === 'random'
                ? `${Math.min(samplingConfig.sampleSize, tasks.length)} randomly sampled task${
                    Math.min(samplingConfig.sampleSize, tasks.length) !== 1 ? 's' : ''
                  } (from ${tasks.length} total)`
                : `${tasks.length} task${tasks.length !== 1 ? 's' : ''}`}{' '}
              with {models.length} model{models.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>

        {/* Loading state */}
        {evaluationState.type === 'loading' && (
          <div
            style={{
              padding: '20px',
              textAlign: 'center',
              fontSize: '16px',
              color: '#666',
            }}
          >
            <div className="spinner"></div>
            <p>Evaluating models... This may take a while.</p>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="results">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h2 style={{ margin: 0 }}>Results</h2>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                {/* Mode Toggle */}
                <div style={{ display: 'flex', gap: '4px', border: '1px solid #ddd', borderRadius: '4px', overflow: 'hidden' }}>
                  <button
                    onClick={() => setUiMode('summary')}
                    style={{
                      padding: '8px 16px',
                      fontSize: '14px',
                      fontWeight: '500',
                      cursor: 'pointer',
                      backgroundColor: uiMode === 'summary' ? '#4a90e2' : '#fff',
                      color: uiMode === 'summary' ? 'white' : '#333',
                      border: 'none',
                      transition: 'all 0.2s',
                    }}
                  >
                    Summary
                  </button>
                  <button
                    onClick={() => setUiMode('research')}
                    style={{
                      padding: '8px 16px',
                      fontSize: '14px',
                      fontWeight: '500',
                      cursor: 'pointer',
                      backgroundColor: uiMode === 'research' ? '#4a90e2' : '#fff',
                      color: uiMode === 'research' ? 'white' : '#333',
                      border: 'none',
                      transition: 'all 0.2s',
                    }}
                  >
                    Research
                  </button>
                </div>

                <button
                  onClick={handleDownloadResults}
                  style={{
                    padding: '8px 16px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                  }}
                >
                  Download Results (JSON)
                </button>
              </div>
            </div>

            {/* Conditional rendering based on UI mode */}
            {uiMode === 'summary' ? (
              <>
                {results.length > 0 && <MetricCards metrics={results[0].metrics} />}
                <MetricsLegend compact />
                <MetricsTable results={results} />
                <MetricsChart results={results} />
                <CotViewer results={results} />
              </>
            ) : (
              <ResearchModeView results={results} />
            )}
          </div>
        )}

        {/* Footer info */}
        <footer style={{ marginTop: '40px', padding: '20px', borderTop: '1px solid #ddd', fontSize: '12px', color: '#666' }}>
          <p>
            <strong>Metrics:</strong> ACC (Accuracy), Brier Score (Calibration), ECE (Expected
            Calibration Error), SCE (Self-Consistency Entropy), USR (Unsupported Step Rate)
          </p>
          <p>
            Backend API: <code>http://localhost:8000</code>
          </p>
        </footer>
      </main>

      {/* Experiment History Sidebar */}
      <ExperimentHistory onLoadExperiment={handleLoadExperiment} />
    </div>
  );
}

export default App;
