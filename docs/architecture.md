# Zeta Reason Architecture

This document provides a comprehensive overview of Zeta Reason's system architecture, including component interactions, data flow, and design decisions.

## Table of Contents

- [High-Level Overview](#high-level-overview)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Data Flow](#data-flow)
- [Storage Layer](#storage-layer)
- [API Specification](#api-specification)
- [Design Decisions](#design-decisions)

## High-Level Overview

Zeta Reason follows a modern client-server architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + Vite)                    │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ DatasetUpload│  │ ModelSelector│  │ ExperimentHist  │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ MetricsTable │  │ MetricsChart │  │ CotViewer       │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ SummaryMode  │  │ ResearchMode │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │ HTTP/JSON
                            │ REST API
┌───────────────────────────▼───────────────────────────────────┐
│                   Backend (FastAPI)                            │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               API Endpoints (main.py)                    │ │
│  │  /evaluate  /compare  /api/experiments  /health         │ │
│  └──────────────────────┬──────────────────────────────────┘ │
│                         │                                     │
│  ┌──────────────────────▼──────────────────────────────────┐ │
│  │            Evaluation Engine (evaluator.py)             │ │
│  │  • Task orchestration                                    │ │
│  │  • Model runner coordination                             │ │
│  │  • Error handling & retries                              │ │
│  └──────────────────────┬──────────────────────────────────┘ │
│                         │                                     │
│  ┌──────────────────────▼──────────────────────────────────┐ │
│  │            Metrics Engine (metrics.py)                   │ │
│  │  • Accuracy computation                                  │ │
│  │  • Calibration metrics (Brier, ECE)                      │ │
│  │  • Consistency metrics (SCE)                             │ │
│  │  • Reasoning quality (USR, tokens, steps)                │ │
│  └──────────────────────┬──────────────────────────────────┘ │
│                         │                                     │
│  ┌──────────────────────▼──────────────────────────────────┐ │
│  │         Model Runners (models/)                          │ │
│  │  ┌──────────────┐  ┌──────────────┐                     │ │
│  │  │ OpenAIRunner │  │ DummyRunner  │  [+ more]           │ │
│  │  └──────────────┘  └──────────────┘                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         Storage Layer (storage/)                          │ │
│  │  • File-based experiment persistence                      │ │
│  │  • Metadata indexing                                      │ │
│  │  • CRUD operations                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│              External Model APIs                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  OpenAI API  │  │ Anthropic API│  │  Custom APIs │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Core Components

#### 1. FastAPI Application (`main.py`)

The main entry point that defines all API routes and middleware:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Zeta Reason API",
    description="Chain-of-thought reasoning benchmarking for LLMs",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Key Routes:**
- `POST /evaluate` - Single model evaluation
- `POST /compare` - Multi-model comparison
- `POST /api/experiments` - Save experiment
- `GET /api/experiments` - List experiments
- `GET /api/experiments/{id}` - Get experiment
- `DELETE /api/experiments/{id}` - Delete experiment
- `GET /api/experiments/stats/storage` - Storage stats
- `GET /health` - Health check

#### 2. Evaluation Engine (`evaluator.py`)

Orchestrates the evaluation process:

```python
async def evaluate_model_on_dataset(
    model_runner: ModelRunner,
    tasks: List[Task],
    model_config: ModelConfig,
) -> EvaluationResult:
    """
    Evaluate a single model on a dataset.

    Process:
    1. Iterate through tasks
    2. Call model runner for each task
    3. Collect outputs and metadata
    4. Compute metrics
    5. Return aggregated results
    """
    outputs = []
    for task in tasks:
        output = await model_runner.run(task.input)
        outputs.append(output)

    metrics = compute_metrics(tasks, outputs, model_config)
    return EvaluationResult(metrics=metrics, outputs=outputs, ...)
```

**Features:**
- Async/await for concurrent API calls
- Error handling with graceful degradation
- Progress tracking
- Retry logic for transient failures

#### 3. Metrics Engine (`metrics.py`)

Computes all evaluation metrics:

```python
def compute_metrics(
    tasks: List[Task],
    outputs: List[ModelOutput],
    config: ModelConfig
) -> Metrics:
    """Compute comprehensive metrics."""

    accuracy = compute_accuracy(tasks, outputs)
    brier_score = compute_brier_score(tasks, outputs)
    ece = compute_expected_calibration_error(tasks, outputs)
    sce = compute_self_consistency_entropy(outputs)
    usr = compute_unsupported_step_rate(outputs)

    # Token and latency stats
    avg_cot_tokens = np.mean([o.cot_tokens for o in outputs])
    avg_steps = np.mean([o.step_count for o in outputs])
    avg_latency = np.mean([o.latency_ms for o in outputs])

    return Metrics(
        accuracy=accuracy,
        brier_score=brier_score,
        ece=ece,
        sce=sce,
        usr=usr,
        avg_cot_tokens=avg_cot_tokens,
        avg_step_count=avg_steps,
        avg_latency_ms=avg_latency,
    )
```

See [Metrics Specification](metrics_spec.md) for detailed formulas.

#### 4. Model Runners (`models/`)

Abstract interface for different LLM providers:

```python
class ModelRunner(ABC):
    """Abstract base class for model runners."""

    @abstractmethod
    async def run(self, prompt: str) -> ModelOutput:
        """Run model on a single prompt."""
        pass

class OpenAIModelRunner(ModelRunner):
    """OpenAI API integration."""

    def __init__(self, model_id: str, temperature: float, ...):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_id = model_id
        # ...

    async def run(self, prompt: str) -> ModelOutput:
        response = await self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            # ...
        )
        return self._parse_response(response)
```

**Currently Supported:**
- OpenAI (GPT-4 family)
- DeepSeek (Chat, Reasoner)
- Qwen (Alibaba)
- GLM (ZhipuAI)
- Dummy (synthetic responses for testing)

**Not yet implemented (stubs; will return errors until shipped):**
- Anthropic (Claude)
- Google Gemini
- Cohere (Command R/R+)
- Grok (xAI)

**Planned:**
- HuggingFace models

#### 5. Storage Layer (`storage/`)

File-based persistence for experiments:

```python
class ExperimentStorage:
    """Manages experiment storage."""

    def __init__(self, base_dir: str = "experiments"):
        self.base_dir = Path(base_dir)
        self.metadata_file = self.base_dir / "metadata.json"

    def save(self, request: ExperimentSaveRequest) -> str:
        """Save experiment, returns UUID."""
        experiment_id = str(uuid.uuid4())
        # Save full data to {experiment_id}.json
        # Update metadata index
        return experiment_id

    def list_metadata(self) -> List[ExperimentMetadata]:
        """List all experiments (metadata only)."""
        # Read from metadata.json for fast listing

    def load(self, experiment_id: str) -> ExperimentData:
        """Load full experiment data."""
        # Read from {experiment_id}.json
```

**Storage Structure:**
```
experiments/
├── metadata.json                    # Lightweight index
├── {uuid-1}.json                   # Full experiment data
├── {uuid-2}.json
└── ...
```

#### 6. Progress Tracking (`progress.py`)

Real-time progress updates for long-running evaluations via WebSocket:

```python
class ProgressTracker:
    """Manages progress tracking for evaluation runs."""

    def create_run(self, total_tasks: int) -> str:
        """Create a new run, returns run_id."""
        run_id = str(uuid.uuid4())
        self._progress_state[run_id] = ProgressUpdate(
            run_id=run_id,
            completed_tasks=0,
            total_tasks=total_tasks,
            percentage=0.0,
            status="running"
        )
        return run_id

    async def update_progress(self, run_id: str, completed_tasks: int):
        """Update progress and broadcast to WebSocket clients."""
        # Update state
        # Broadcast to all connected WebSockets

    def get_progress_callback(self, run_id: str) -> Callable:
        """Get callback for pipeline integration."""
        # Returns callback that can be called from evaluation pipeline
```

**WebSocket Endpoint:**
```
ws://localhost:8000/ws/progress?run_id={run_id}
```

**Polling Fallback:**
```
GET /api/progress/{run_id}
```

**Features:**
- WebSocket-based real-time updates
- Automatic fallback to HTTP polling for unsupported clients
- Progress state includes: completed_tasks, total_tasks, percentage, status
- Supports multiple concurrent evaluation runs
- Automatic cleanup after 60 seconds

### Error Handling

Zeta Reason implements comprehensive error handling:

```python
class ProviderError(Exception):
    """Provider-specific errors (API failures, rate limits, etc.)."""
    def __init__(self, message: str, status_code: int, provider: str):
        self.message = message
        self.status_code = status_code
        self.provider = provider

# In API routes:
try:
    result = await evaluate_model_on_dataset(...)
except ProviderError as e:
    # Map to appropriate HTTP status
    return JSONResponse(
        status_code=502,  # Bad Gateway
        content={"error": e.message, "provider": e.provider}
    )
except ValueError as e:
    # Validation errors
    return JSONResponse(status_code=400, content={"error": str(e)})
```

## Frontend Architecture

### Technology Stack

- **React 18** - UI framework
- **TypeScript 5** - Type safety
- **Vite** - Build tool and dev server
- **CSS Modules** - Scoped styling

### Component Hierarchy

```
App
├── ThemeProvider (Context)
│   └── App Component
│       ├── Header
│       │   └── ThemeToggle
│       ├── ErrorBanner
│       ├── DatasetUpload
│       ├── ModelSelector
│       │   ├── ModelCard (× N)
│       │   └── PresetSelector
│       ├── RunButton
│       ├── Results (conditional)
│       │   ├── ModeToggle (Summary/Research)
│       │   ├── Summary Mode
│       │   │   ├── MetricCards
│       │   │   ├── MetricsLegend
│       │   │   ├── MetricsTable
│       │   │   ├── MetricsChart
│       │   │   └── CotViewer
│       │   └── Research Mode
│       │       └── ResearchModeView
│       │           ├── FilterBar
│       │           ├── TaskList
│       │           └── TaskDetail
│       └── ExperimentHistory (Sidebar)
│           ├── ToggleButton
│           └── ExperimentList
│               └── ExperimentCard (× N)
```

### State Management

Zeta Reason uses React's built-in state management:

```typescript
function App() {
  // Core data
  const [tasks, setTasks] = useState<Task[]>([]);
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [evaluationState, setEvaluationState] =
    useState<EvaluationState>({ type: 'idle' });

  // UI state
  const [uiMode, setUiMode] = useState<'summary' | 'research'>('summary');
  const [globalError, setGlobalError] = useState<string | null>(null);

  // Config state
  const [samplingConfig, setSamplingConfig] = useState<SamplingConfig>({
    mode: 'all',
    sampleSize: 50,
  });

  // Dataset metadata
  const [datasetFileName, setDatasetFileName] = useState<string>('');
  const [originalDatasetSize, setOriginalDatasetSize] = useState<number>(0);
}
```

**State Flow:**
1. User uploads dataset → `setTasks()`
2. User configures models → `setModels()`
3. User clicks run → `setEvaluationState({ type: 'loading' })`
4. Backend returns results → `setEvaluationState({ type: 'single', result })`
5. Results render conditionally based on state

### Theme System

CSS variables for light/dark themes:

```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #333;
  --accent-primary: #4a90e2;
  /* ... */
}

[data-theme='dark'] {
  --bg-primary: #1a1a1a;
  --text-primary: #e0e0e0;
  --accent-primary: #5fa3e8;
  /* ... */
}
```

Theme context provides toggle functionality:

```typescript
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    return localStorage.getItem('zeta-reason-theme') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('zeta-reason-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev =>
    prev === 'light' ? 'dark' : 'light'
  );

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

## Data Flow

### Evaluation Flow

```
User Action: Click "Run Evaluation"
    ↓
Frontend: handleRunBenchmark()
    ↓
Apply sampling (if random mode)
    ↓
POST /evaluate or /compare
    ↓
Backend: evaluate() or compare()
    ↓
Create ModelRunner instances
    ↓
For each task:
    ↓
    Call ModelRunner.run(task.input)
        ↓
        External API call (OpenAI, etc.)
        ↓
        Parse response
        ↓
    Return ModelOutput
    ↓
Collect all outputs
    ↓
Compute metrics
    ↓
Return EvaluationResult
    ↓
Frontend: setEvaluationState({ type: 'single', result })
    ↓
Auto-save experiment
    ↓
POST /api/experiments
    ↓
Backend: save to file system
    ↓
Return experiment_id
    ↓
Frontend: Display results
```

### Experiment History Flow

```
After evaluation completes:
    ↓
Auto-save trigger
    ↓
Generate experiment name
    ↓
POST /api/experiments
    {
        name: "gpt-4 vs gpt-3.5 on GSM8K - Jan 20, 2025",
        dataset_name: "gsm8k.jsonl",
        dataset_size: 100,
        results: [...],
        sampling_config: {...}
    }
    ↓
Backend: ExperimentStorage.save()
    ↓
Generate UUID
    ↓
Create metadata
    ↓
Save {uuid}.json with full data
    ↓
Update metadata.json index
    ↓
Return experiment_id
    ↓
Frontend: Log to console

User clicks "History ►":
    ↓
GET /api/experiments
    ↓
Backend: read metadata.json
    ↓
Return list of ExperimentMetadata
    ↓
Frontend: Display in sidebar

User clicks "Load" on experiment:
    ↓
GET /api/experiments/{id}
    ↓
Backend: read {id}.json
    ↓
Return full ExperimentData
    ↓
Frontend: setEvaluationState({ type: 'compare', results })
    ↓
Display loaded results
```

## Storage Layer

### File Structure

```
experiments/
├── metadata.json                    # Index file
└── {uuid}.json                     # Individual experiments
```

### Metadata Schema

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "gpt-4 vs gpt-3.5-turbo on GSM8K - Jan 20, 2025",
  "timestamp": "2025-01-20T14:30:00.000Z",
  "dataset_name": "gsm8k.jsonl",
  "dataset_size": 100,
  "tasks_evaluated": 50,
  "model_count": 2,
  "model_ids": ["gpt-4", "gpt-3.5-turbo"],
  "accuracy_range": [0.65, 0.82],
  "tags": []
}
```

### Full Experiment Data

```json
{
  "metadata": { /* as above */ },
  "results": [
    {
      "model_configuration": {
        "model_id": "gpt-4",
        "provider": "openai",
        "temperature": 0.7,
        "max_tokens": 1000,
        "use_cot": true,
        "shots": 1
      },
      "metrics": {
        "accuracy": 0.82,
        "brier_score": 0.15,
        "ece": 0.08,
        "sce": 1.2,
        "usr": 0.05,
        "avg_cot_tokens": 350,
        "avg_step_count": 4.5,
        "avg_latency_ms": 1200
      },
      "task_results": [ /* individual task outputs */ ],
      "total_tasks": 50,
      "correct_count": 41
    }
  ],
  "sampling_config": {
    "mode": "random",
    "sample_size": 50
  }
}
```

### Design Rationale

**Why file-based storage?**
1. **Simplicity** - No database setup required
2. **Portability** - Easy to backup/share
3. **Inspection** - Human-readable JSON
4. **Performance** - Fast for <1000 experiments
5. **Migration** - Easy to move to DB later

**Trade-offs:**
- Not suitable for 10,000+ experiments
- No ACID guarantees
- Manual concurrency handling

## API Specification

### Core Endpoints

#### POST /evaluate

Evaluate a single model on a dataset.

**Request:**
```json
{
  "model_configuration": {
    "model_id": "gpt-4",
    "provider": "openai",
    "temperature": 0.7,
    "max_tokens": 1000,
    "use_cot": true,
    "shots": 1
  },
  "tasks": [
    {
      "id": "1",
      "input": "What is 2+2?",
      "target": "4"
    }
  ]
}
```

**Response:**
```json
{
  "result": {
    "model_configuration": { /* same as request */ },
    "metrics": { /* computed metrics */ },
    "task_results": [ /* outputs per task */ ],
    "total_tasks": 1,
    "correct_count": 1
  }
}
```

#### POST /compare

Compare multiple models on the same dataset.

**Request:**
```json
{
  "model_configurations": [
    { /* model 1 config */ },
    { /* model 2 config */ }
  ],
  "tasks": [ /* same as /evaluate */ ]
}
```

**Response:**
```json
{
  "results": [
    { /* result for model 1 */ },
    { /* result for model 2 */ }
  ]
}
```

### Experiment Endpoints

See [Storage Layer](#storage-layer) for schemas.

## Design Decisions

### 1. Why FastAPI?

**Pros:**
- Automatic OpenAPI documentation
- Async/await support for concurrent API calls
- Type hints with Pydantic
- High performance
- Easy testing

**Alternatives considered:**
- Flask (synchronous, less modern)
- Django (too heavyweight)

### 2. Why React + Vite?

**Pros:**
- Fast development with HMR
- Modern build tooling
- Component-based architecture
- Rich ecosystem

**Alternatives considered:**
- Next.js (overkill for SPA)
- Vue (smaller community for this use case)

### 3. Why File-Based Storage?

See [Storage Layer](#storage-layer) rationale.

### 4. Why Async Evaluation?

**Reasoning:**
- Model API calls are I/O-bound
- Async allows concurrent requests
- Significant speedup for multi-model comparison

**Example:**
- Synchronous: 10 tasks × 2 models × 1s = 20s
- Async: 10 tasks × max(2 models) × 1s = 10s

### 5. Why Auto-Save Experiments?

**Reasoning:**
- Prevents data loss
- Encourages iteration
- Builds research history automatically

**Trade-off:**
- Disk usage (mitigated by JSON compression potential)

## Performance Considerations

### Backend

- **Async I/O**: Concurrent API calls
- **Caching**: Potential for result caching (future)
- **Batch Processing**: Group tasks for API efficiency

### Frontend

- **Code Splitting**: Load Research Mode lazily
- **Virtualization**: For large task lists (future)
- **Memoization**: React.memo for expensive components

### Storage

- **Metadata Index**: Fast listing without loading full data
- **Lazy Loading**: Only load experiment data when needed
- **Compression**: Potential future optimization

## Security Considerations

1. **API Keys**: Environment variables, never committed
2. **CORS**: Restricted to localhost in development
3. **Input Validation**: Pydantic schemas
4. **Error Handling**: No sensitive info in error messages
5. **Rate Limiting**: (Future) Prevent API abuse

## Extensibility

### Adding New Model Providers

1. Implement `ModelRunner` interface
2. Add configuration in `ModelConfig`
3. Update frontend model selector
4. Add tests

Example:
```python
class AnthropicModelRunner(ModelRunner):
    async def run(self, prompt: str) -> ModelOutput:
        # Implement Claude API integration
        pass
```

### Adding New Metrics

1. Implement computation function in `metrics.py`
2. Add to `Metrics` schema
3. Update frontend display components
4. Add tests

Example:
```python
def compute_perplexity(outputs: List[ModelOutput]) -> float:
    # Implement metric
    pass
```

### Adding Export Formats

1. Add export function in `frontend/src/utils/export.ts`
2. Add button in UI
3. Handle format-specific logic

## Future Enhancements

See [Roadmap](roadmap.md) for planned features:

- Database migration (PostgreSQL)
- WebSocket for real-time progress
- Docker containerization
- Kubernetes deployment
- Multi-user authentication
- Public leaderboards

---

**Last Updated:** January 2025
**Version:** 1.0.0
