# Zeta Reason Backend

Backend API for Zeta Reason v0.1 - Chain-of-thought reasoning benchmarking for LLMs.

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Run the API Server

```bash
# Start the server
uvicorn zeta_reason.main:app --reload

# Server will be available at http://localhost:8000
```

### 3. Test the Health Endpoint

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"0.1.0"}
```

### 4. Run Example Evaluation

```bash
# Run the example script with DummyModelRunner
python3 scripts/run_example.py

# Test with OpenAI (requires OPENAI_API_KEY)
export OPENAI_API_KEY=your_key_here
python3 scripts/test_openai_runner.py
```

## API Endpoints

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### POST `/evaluate`

Evaluate a single model on a dataset.

**Request:**
```json
{
  "model_configuration": {
    "model_id": "dummy-1.0",
    "provider": "dummy",
    "temperature": 0.7,
    "max_tokens": 1000,
    "use_cot": true
  },
  "tasks": [
    {
      "id": "task_1",
      "input": "What is 2 + 2?",
      "target": "4"
    }
  ]
}
```

**Response:**
```json
{
  "result": {
    "model_configuration": { ... },
    "metrics": {
      "accuracy": 0.0,
      "brier_score": 0.7,
      "expected_calibration_error": 0.8,
      "self_consistency_entropy": 0.0,
      "unsupported_step_rate": 0.0
    },
    "task_results": [ ... ],
    "total_tasks": 1
  }
}
```

### POST `/compare`

Compare multiple models on the same dataset.

**Request:**
```json
{
  "model_configurations": [
    {
      "model_id": "dummy-1.0",
      "provider": "dummy",
      "temperature": 0.7,
      "max_tokens": 1000,
      "use_cot": true
    }
  ],
  "tasks": [ ... ]
}
```

**Response:**
```json
{
  "results": [ ... ]
}
```

## Project Structure

```
backend/
├── zeta_reason/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── schemas.py           # Pydantic models
│   ├── models/
│   │   ├── base.py          # BaseModelRunner
│   │   ├── dummy_runner.py  # DummyModelRunner for testing
│   │   └── openai_runner.py # OpenAIModelRunner
│   ├── metrics/
│   │   └── core.py          # Metric functions
│   ├── evaluator/
│   │   └── pipeline.py      # Evaluation pipeline
│   └── utils/
│       └── io.py            # Dataset loading
├── data/
│   └── example_arithmetic.jsonl
├── scripts/
│   ├── run_example.py       # DummyModelRunner example
│   └── test_openai_runner.py # OpenAI runner test
├── tests/
├── pyproject.toml
└── README.md
```

## Metrics

Zeta Reason v0.1 computes the following metrics:

### 1. Accuracy (ACC)
**Range:** 0.0 to 1.0 (higher is better)

Simple exact string match after stripping whitespace and converting to lowercase.

```python
accuracy(predictions: List[str], targets: List[str]) -> float
```

### 2. Brier Score
**Range:** 0.0 to 1.0 (lower is better)

Measures mean squared error between predicted probabilities and actual correctness (binary: 0 or 1). Perfect calibration = 0.0.

```python
brier_score(probs: List[float], targets: List[int]) -> float
```

### 3. Expected Calibration Error (ECE)
**Range:** 0.0 to 1.0 (lower is better)

Measures the weighted average of absolute differences between confidence and accuracy across 10 probability bins. Perfectly calibrated models have ECE = 0.0.

```python
expected_calibration_error(probs: List[float], targets: List[int], n_bins: int = 10) -> float
```

### 4. Self-Consistency Entropy (SCE)
**Range:** 0.0 to ∞ (lower is better)

Computes Shannon entropy in nats of the answer distribution when sampling multiple times. Perfect consistency (all same answer) = 0.0.

```python
self_consistency_entropy(answer_counts: Dict[str, int]) -> float
```

**Note:** For v0.1, SCE is placeholder (returns 0.0) as it requires multiple samples per task.

### 5. Unsupported Step Rate (USR)
**Range:** 0.0 to 1.0 (lower is better)

For v0.1, simple heuristic:
- If final_answer == target: 0.0 (correct reasoning)
- If final_answer != target: 1.0 (incorrect reasoning)

**TODO for post-v0.1:** Implement sophisticated reasoning quality checks using LLM-as-judge or logical consistency verification.

```python
unsupported_step_rate(cot_text: str, final_answer: str, target: str) -> float
```

## Model Providers

Zeta Reason v0.1 supports the following model providers:

### Dummy Provider
**Provider ID:** `dummy`

A deterministic dummy model for testing without API calls. Returns scripted responses based on simple pattern matching.

```python
from zeta_reason.models import DummyModelRunner

runner = DummyModelRunner(
    model_id="dummy-1.0",
    temperature=0.7,
    max_tokens=1000,
    use_cot=True
)
```

### OpenAI Provider
**Provider ID:** `openai`

Uses OpenAI's chat completions API (GPT-4, GPT-4o, GPT-4o-mini, etc.).

**Requirements:**
- Set `OPENAI_API_KEY` environment variable or pass `api_key` parameter
- Supports all OpenAI chat models

**System Prompt:**
```
You are a helpful reasoning assistant. Show your reasoning step by step,
then clearly mark the final answer on a separate line starting with 'FINAL_ANSWER:'.
```

**Answer Extraction:**
1. Looks for `FINAL_ANSWER:` marker in response
2. Falls back to last non-empty line if marker not found

```python
from zeta_reason.models import OpenAIModelRunner

runner = OpenAIModelRunner(
    model_id="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,
    use_cot=True,
    api_key="your-api-key"  # Optional, reads from env if not provided
)
```

**Example API Request:**
```json
{
  "model_configuration": {
    "model_id": "gpt-4o-mini",
    "provider": "openai",
    "temperature": 0.7,
    "max_tokens": 1000,
    "use_cot": true
  },
  "tasks": [...]
}
```

## Evaluation Pipeline

The evaluation pipeline supports both synchronous and asynchronous execution:

### Async API (Recommended for FastAPI)
```python
from zeta_reason.evaluator import evaluate_model_on_dataset, compare_models

# Single model evaluation (async)
result = await evaluate_model_on_dataset(runner, tasks, model_config)

# Multi-model comparison (async)
results = await compare_models(runners, tasks, configs)
```

### Sync API (For Scripts)
```python
from zeta_reason.evaluator import evaluate_model_on_dataset_sync, compare_models_sync

# Single model evaluation (sync)
result = evaluate_model_on_dataset_sync(runner, tasks, model_config)

# Multi-model comparison (sync)
results = compare_models_sync(runners, tasks, configs)
```

**Features:**
- Automatic answer counting for SCE calculation (measures answer diversity across dataset)
- Comprehensive logging at INFO and DEBUG levels
- Thread-safe execution using `asyncio.to_thread` for model inference
- Graceful error handling with detailed error messages

## Development

### Run Tests

```bash
pip install -e ".[dev]"
pytest

# Run with coverage
pytest --cov=zeta_reason tests/

# Run specific test file
pytest tests/test_pipeline.py -v
```

### Code Formatting

```bash
black zeta_reason/
ruff check zeta_reason/
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# OpenAI API key (required for openai provider)
OPENAI_API_KEY=your_key_here

# Server config
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

## Next Steps (Post-v0.1)

- [x] Implement OpenAIModelRunner ✅
- [ ] Add Anthropic, Gemini model runners
- [ ] Enhance metrics (particularly USR with LLM-as-judge)
- [ ] Add proper self-consistency evaluation (multiple samples)
- [ ] Add logprobs support for confidence scores
- [ ] Add more comprehensive tests
- [ ] Add API authentication
