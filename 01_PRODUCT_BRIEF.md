# Zeta Reason — v0.1 Product Brief

## 1. Overview

Zeta Reason is an open-source benchmarking tool for **chain-of-thought (CoT) reasoning** in large language models.

Instead of only asking “did the model get the final answer right?”, Zeta Reason focuses on **how** the model arrived there. It provides metrics and tooling to measure:

- Answer correctness
- Probabilistic calibration
- The structure and stability of the reasoning process
- Basic path faithfulness (are the reasoning steps actually supported?)

This brief describes the scope for **v0.1**, a minimal but usable version that can be built in ~3 days and then improved.

---

## 2. Problem

Most LLM evaluation tools:

- Only report final-answer accuracy on benchmarks.
- Treat chain-of-thought traces as opaque text.
- Make it hard to compare *how* different models reason over the same tasks.

This creates a gap for:

- Researchers who care about **alignment, safety, and robustness**.
- Engineers who need **audit trails** for model decisions.
- Teams designing **reasoning-sensitive** applications (e.g., finance, science, law).

They need a simple way to **run models on a dataset and inspect both answers and reasoning quality**.

---

## 3. What Zeta Reason v0.1 Does

For v0.1, Zeta Reason will:

1. **Run one or more models** on a dataset of tasks (prompts + targets).
2. **Collect chain-of-thought outputs** from each model.
3. **Compute a small set of metrics** capturing:
   - Accuracy
   - Calibration
   - Self-consistency
   - Simple unsupported reasoning steps
4. **Expose results via:**
   - A FastAPI backend (`/evaluate`, `/compare`).
   - A simple React UI to upload a dataset, run benchmarks, and view metrics and raw CoTs.

The v0.1 is intentionally small: it’s a **foundation** for deeper metrics and better visualization later.

---

## 4. Target Users (Initial)

- **ML / NLP researchers** who want to:
  - Compare GPT vs Anthropic vs Gemini on reasoning tasks.
  - Inspect CoT quality beyond accuracy.
- **Applied AI engineers / infra teams** who need:
  - A reproducible way to benchmark models for reasoning-heavy workloads.
- **Safety / alignment researchers** who care about:
  - Unsupported reasoning
  - Overconfident errors
  - Self-consistency behaviour.

---

## 5. Non-goals for v0.1

v0.1 will **not** attempt to:

- Provide a full UI for complex visualizations (graphs, interactive trees).
- Implement every planned metric (we start with 5).
- Support dozens of models out of the box.
- Handle large-scale distributed evaluation.

Those are **post-v0.1** improvements.

---

## 6. Success Criteria for v0.1

Zeta Reason v0.1 is successful if:

1. A user can:
   - Clone the repo.
   - Set their model API key(s).
   - Run a single command to:
     - Evaluate at least one model on an example dataset.
     - See metrics computed and displayed in both CLI and UI.

2. The tool provides at least these metrics:
   - Accuracy (ACC)
   - Brier score
   - Expected Calibration Error (ECE)
   - Self-Consistency Entropy (SCE)
   - Unsupported Step Rate (USR, simple heuristic)

3. The repo includes:
   - A clear `README.md`.
   - An example dataset.
   - A short “how it works” section that matches reality.

If these conditions are met, v0.1 is shippable and we can iterate.