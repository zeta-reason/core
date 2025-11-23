# Zeta Reason — 3-Day Implementation Plan (v0.1)

This plan assumes **3 focused days** using AI coding assistants (e.g., Claude Code) plus manual review.

---

## Day 1 — Backend + Metrics

### Goals

- Scaffold the backend project.
- Implement core metrics and evaluation pipeline.
- Expose `/evaluate` and `/compare` endpoints.

### Tasks

1. **Project scaffold**

   - Create Python backend project:
     - `zeta_reason/`
       - `__init__.py`
       - `main.py` (FastAPI app)
       - `models/` (LLM wrappers)
       - `metrics/` (metric functions)
       - `evaluator/` (pipeline logic)
       - `schemas/` (Pydantic models)
     - `scripts/run_example.py`
     - `requirements.txt` or `pyproject.toml`

2. **Dataset & schema definitions**

   - Define a minimal task schema (Pydantic):

     ```python
     class Task(BaseModel):
         id: str
         input: str
         target: str
     ```

   - Define evaluation request/response schemas for:
     - `/evaluate`
     - `/compare`

3. **Model interface**

   - Create an abstract `BaseModelRunner` with:
     - `generate(self, prompt: str) -> ModelOutput`
   - Implement `OpenAIModelRunner` as the first concrete class.
   - Include optional CoT prompting pattern.

4. **Metrics implementation**

   Implement in `metrics/core.py`:

   - `accuracy(preds, targets) -> float`
   - `brier_score(probs, targets) -> float`
   - `expected_calibration_error(buckets) -> float`
   - `self_consistency_entropy(answer_counts) -> float`
   - `unsupported_step_rate(cot_text, final_answer, target) -> float`
     - v0.1: simple heuristics / rule-based checks.

5. **Evaluator pipeline**

   - Implement a function:

     ```python
     def evaluate_model_on_dataset(model_runner, tasks: List[Task]) -> EvaluationResult:
         # run model, collect CoTs, compute metrics
     ```

6. **API endpoints**

   - `POST /evaluate`
     - Input: model config + dataset (inline JSON or uploaded path)
     - Output: metrics + sample CoTs
   - `POST /compare`
     - Input: list of models + dataset
     - Output: per-model metrics table

7. **Smoke tests**

   - Add a tiny synthetic dataset (e.g., 5 arithmetic tasks).
   - Hard-code a “dummy model” for local testing that returns scripted answers.

---

## Day 2 — Frontend (React)

### Goals

- Minimal UI to upload dataset, choose models, run eval, and view metrics + CoTs.

### Tasks

1. **Frontend scaffold**

   - Create `frontend/` React app (Vite + TypeScript).
   - Basic structure:
     - `src/App.tsx`
     - `src/components/MetricsTable.tsx`
     - `src/components/CotViewer.tsx`
     - `src/api/client.ts`

2. **Pages & flows**

   - Single page with:
     - File upload (JSONL dataset).
     - Model selection:
       - Text field for `model_id` (e.g., `gpt-4o-mini`).
       - Later we can add dropdowns.
     - “Run Benchmark” button.

3. **API integration**

   - Implement API client to call:
     - `POST /evaluate`
     - `POST /compare`
   - Handle loading + error states.

4. **Metrics display**

   - `MetricsTable`:
     - Rows: metrics
     - Columns: models
     - v0.1: simple HTML table.

5. **CoT viewer**

   - `CotViewer`:
     - Dropdown/select to choose a sample by `task.id`.
     - Show:
       - input
       - target
       - model answer
       - raw CoT text

6. **Local integration test**

   - Run backend (`uvicorn`) and frontend (`npm run dev`) together.
   - Confirm:
     - Uploading example dataset works.
     - Metrics are displayed.
     - CoT viewer shows a sample.

---

## Day 3 — Glue, Docs, Release

### Goals

- End-to-end test.
- Add example dataset & script.
- Write docs and tag release.

### Tasks

1. **Example dataset**

   - Add `data/example_arithmetic.jsonl` with 10–20 tasks.

2. **Example script**

   - `scripts/run_example.py`:
     - Loads example dataset.
     - Runs one configured model.
     - Prints metrics to console.

3. **README and docs**

   - Write `README.md` with:
     - One-paragraph description.
     - Features list.
     - Quickstart (backend + frontend).
     - Example usage (CLI + UI).
   - Link to:
     - `01_PRODUCT_BRIEF.md`
     - `03_METRICS_SPEC.md` (when ready).

4. **Basic testing**

   - Run:
     - `pytest` (if tests exist).
     - Manual checks on:
       - Success and failure cases.
       - Invalid requests (missing fields, bad file).

5. **Cleanup**

   - Remove dead code / unused files.
   - Check in `.gitignore`.
   - Ensure config (e.g., API keys) uses env vars.

6. **Release**

   - Commit and push to GitHub.
   - Tag `v0.1.0`.
   - Optional: write a short “Introducing Zeta Reason v0.1” note in `docs/` or as a GitHub release description.

---

## Notes

- v0.1 intentionally uses **one main model backend** first (OpenAI).
- Additional models, more metrics, and richer visualization are planned for **post-v0.1**.