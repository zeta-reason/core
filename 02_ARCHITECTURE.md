# Zeta Reason — Architecture (v0.1)

This document describes the system architecture for **Zeta Reason v0.1**, a minimal but usable tool for benchmarking chain-of-thought (CoT) reasoning in large language models.

The focus is on:
- A simple but clean **backend** (FastAPI)
- A minimal **frontend** (React)
- A clear **evaluation pipeline** for running models on datasets and computing metrics

---

## 1. High-Level Overview

Zeta Reason v0.1 has three main layers:

1. **Frontend (React)**  
   - Single-page app for:
     - Uploading a dataset (JSONL)
     - Specifying model(s) to evaluate
     - Triggering evaluation
     - Viewing metrics table and sample CoT traces

2. **Backend (FastAPI)**  
   - Exposes HTTP API:
     - `POST /evaluate`: evaluate a single model on a dataset
     - `POST /compare`: evaluate multiple models on the same dataset
     - `GET /health`: basic health check
   - Orchestrates:
     - Loading dataset
     - Calling model(s)
     - Collecting answers + CoTs
     - Computing metrics

3. **Core Evaluation & Metrics Logic (Python)**  
   - Pure Python modules for:
     - Model abstraction (`BaseModelRunner`)
     - Evaluation pipeline
     - Metric computation

The architecture is designed so that **metrics and evaluation logic are independent of the UI and web framework**, making it easy to reuse in scripts or future integrations.

---

## 2. Tech Stack

### Backend

- **Language:** Python 3.11+
- **Web framework:** FastAPI
- **Server:** Uvicorn (for local dev)
- **Environment/config:** `python-dotenv` or standard env vars (`os.environ`)

### Frontend

- **Framework:** React (with TypeScript)
- **Bundler:** Vite (or Create React App if preferred)
- **HTTP client:** `fetch` or `axios` (simple abstraction layer)

### Other

- **Data format:** JSONL for datasets (`.jsonl` file with one task per line)
- **Model provider (v0.1):** OpenAI API (extensible via `BaseModelRunner`)
- **Auth:** None (local dev only for v0.1)
- **Storage:** In-memory during evaluation; datasets uploaded from browser or loaded from local file via scripts

---

## 3. Directory Structure (Target)

A suggested repo layout:

```text
zeta-reason/
  backend/
    zeta_reason/
      __init__.py
      main.py               # FastAPI app
      config.py             # env/config helpers
      schemas.py            # Pydantic models for API & internal types
      models/
        __init__.py
        base.py             # BaseModelRunner, ModelOutput
        openai_runner.py    # OpenAIModelRunner implementation
        dummy_runner.py     # For local testing without API calls
      metrics/
        __init__.py
        core.py             # ACC, Brier, ECE, SCE, USR
      evaluator/
        __init__.py
        pipeline.py         # evaluate_model_on_dataset, compare_models
      utils/
        __init__.py
        io.py               # dataset loading/parsing

    tests/
      test_metrics.py
      test_pipeline.py

    data/
      example_arithmetic.jsonl

    scripts/
      run_example.py

    pyproject.toml or requirements.txt

  frontend/
    index.html
    package.json
    vite.config.ts
    tsconfig.json
    src/
      main.tsx
      App.tsx
      api/
        client.ts           # functions to call backend API
      components/
        DatasetUpload.tsx
        ModelSelector.tsx
        MetricsTable.tsx
        CotViewer.tsx
      types/
        api.ts              # TS types mirroring backend schemas

  README.md
  01_PRODUCT_BRIEF.md
  02_ARCHITECTURE.md
  07_IMPLEMENTATION_PLAN_3DAY.md
  .gitignore