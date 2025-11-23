# 03_METRICS_SPEC — Zeta Reason v0.2

This document defines the metrics computed by Zeta Reason v0.2.

**Design constraints:**

- No judge LLMs (no secondary models for scoring).
- No gold chain-of-thought traces in datasets.
- Metrics must be computed from:
  - `input` (prompt)
  - `target` (ground truth final answer)
  - `answer` (model final answer)
  - `cot` (model-produced chain-of-thought, optional)
  - API usage info (tokens, latency)
- Single-run per task for now (no multi-sample consistency metrics yet).

All formulas below are deterministic and reproducible.

---

## 1. Notation

Let the dataset be:

- Tasks: \( \{ t_i \}_{i=1}^N \)
- For each task \( t_i \):
  - Input: \( x_i \) (string)
  - Target answer: \( y_i \) (string)
  - Model answer: \( \hat{y}_i \) (string)
  - Chain-of-thought text: \( c_i \) (string or `null`)
  - Prompt tokens: \( p_i \) (int, from API usage)
  - Completion tokens: \( q_i \) (int, from API usage)
  - Total tokens: \( z_i = p_i + q_i \)
  - Latency: \( L_i \) (milliseconds, measured in backend)

We also define helper functions:

- `normalize(s)`: trims whitespace, lowercases, and optionally does simple numeric normalization.
- `tokens(s)`: token count of string `s`. For v0.2, this can be:
  - A simple whitespace split, or
  - Model tokenizer count, depending on implementation.

If a value is missing (e.g. `c_i` is `null`), metrics that depend on it should skip that task in their aggregation.

---

## 2. Answer-Level Metrics

### 2.1 Accuracy (ACC)

**Intuition:**  
Proportion of tasks where the model’s final answer exactly matches the target after normalization.

**Per-task correctness:**

- \( \text{correct}_i = 1 \) if `normalize(ŷ_i) == normalize(y_i)`  
- \( \text{correct}_i = 0 \) otherwise

**Metric:**

\[
\text{ACC} = \frac{1}{N} \sum_{i=1}^{N} \text{correct}_i
\]

**Range:**  
- \([0, 1]\)

**Inputs required:**

- `target`, `answer`

---

### 2.2 Unsupported Step Rate v0 (USR_v0)

**Intuition:**  
For v0.2, we use a simple proxy: if the final answer is wrong, the “reasoning path” is treated as unsupported. This is a placeholder for future, path-sensitive USR.

**Per-task:**

- \( \text{usr\_v0}_i = 1 \) if `normalize(ŷ_i) != normalize(y_i)`  
- \( \text{usr\_v0}_i = 0 \) otherwise

**Metric:**

\[
\text{USR\_v0} = \frac{1}{N} \sum_{i=1}^{N} \text{usr\_v0}_i
\]

**Range:**  
- \([0, 1]\)

**Inputs required:**

- `target`, `answer`

> **Note:** In future versions, USR will be refined to inspect internal steps (especially for math / RAG), but v0.2 remains answer-only.

---

### 2.3 Error Rate (optional, derived)

**Intuition:**  
Direct complement of ACC.

\[
\text{ERR} = 1 - \text{ACC}
\]

This can be exposed for completeness but does not need a separate storage field if ACC is present.

---

## 3. Calibration Metrics (placeholders, optional)

For v0.2 we keep the **interfaces** for Brier and ECE, but it is acceptable for their values to be `null` when `prob_correct` is not available.

Let:

- \( c_i \in \{0,1\} \) as before (correctness),
- \( \hat{p}_i \in [0,1] \) be the model’s predicted probability of being correct (if/when available).

In v0.2, we may not have \( \hat{p}_i \); in that case, the following metrics should be computed only when non-null data exists, otherwise set to `null`.

### 3.1 Brier Score

**Intuition:**  
Mean squared error between predicted probability of correctness and actual correctness.

\[
\text{Brier} = \frac{1}{M} \sum_{i=1}^{M} (\hat{p}_i - c_i)^2
\]

Where \( M \) is the number of tasks with non-null \( \hat{p}_i \).

**Range:**  
- \([0, 1]\)

**Inputs required:**

- `prob_correct` per task (future/optional)

---

### 3.2 Expected Calibration Error (ECE)

**Intuition:**  
How well predicted probabilities align with observed accuracy across probability bins.

**Procedure:**

1. Choose \( K \) bins (e.g., \(K = 10\)) partitioning \([0,1]\).
2. For each bin \( B_k \):
   - Let \( S_k = \{ i : \hat{p}_i \in B_k \} \)
   - If \( |S_k| = 0 \), skip.
   - Compute:
     - \( \text{conf}_k = \frac{1}{|S_k|} \sum_{i \in S_k} \hat{p}_i \)
     - \( \text{acc}_k = \frac{1}{|S_k|} \sum_{i \in S_k} c_i \)
3. ECE:

\[
\text{ECE} = \sum_{k=1}^{K} \frac{|S_k|}{M} \cdot |\text{acc}_k - \text{conf}_k|
\]

Where \( M \) is the number of tasks with non-null \( \hat{p}_i \).

**Range:**  
- \([0, 1]\)

**Inputs required:**

- `prob_correct` per task (future/optional)

**v0.2 rule:**  
If no tasks have non-null `prob_correct`, Brier and ECE must be returned as `null`.

---

## 4. Diversity / Self-Consistency Metric

### 4.1 Self-Consistency Entropy v0 (SCE_v0)

**Intuition:**  
Measures the diversity of model answers across the dataset in a single pass. High entropy means a wide variety of answers; low entropy means the model tends to repeat the same answers.

> This is **not** multi-sample self-consistency; it is a dataset-level diversity measure.

**Procedure:**

1. Compute normalized answers \( \tilde{y}_i = \text{normalize}(\hat{y}_i) \).
2. Let \( \mathcal{A} \) be the set of distinct normalized answers.
3. For each answer \( a \in \mathcal{A} \):
   - \( n_a = \#\{ i : \tilde{y}_i = a \} \)
   - \( p_a = n_a / N \)
4. Define entropy (natural log or base-2; must document choice):

\[
\text{SCE\_v0} = - \sum_{a \in \mathcal{A}} p_a \log p_a
\]

**Range:**  
- \([0, \log |\mathcal{A}|]\)

**Inputs required:**

- `answer` (final answers only)

**Implementation note:**  
- Choose a consistent log base (e.g., natural log).
- Optionally expose a normalized SCE by dividing by \(\log |\mathcal{A}|\).

---

## 5. CoT Shape / Process Metrics

These metrics use only the model-produced CoT text, **not** gold traces.

For tasks where `cot` is non-null:

### 5.1 CoT Token Length (COT_TOKENS_MEAN)

**Per-task:**

\[
\text{cot\_tokens}_i = \text{tokens}(c_i)
\]

**Model-level:**

\[
\text{COT\_TOKENS\_MEAN} = \frac{1}{M} \sum_{i=1}^{M} \text{cot\_tokens}_i
\]

Where \( M \) is number of tasks with non-null `cot`.

**Range:**  
- \([0, +\infty)\)

---

### 5.2 CoT Character Length (COT_CHARS_MEAN)

**Per-task:**

\[
\text{cot\_chars}_i = \text{len}(c_i)
\]

**Model-level:**

\[
\text{COT\_CHARS\_MEAN} = \frac{1}{M} \sum_{i=1}^{M} \text{cot\_chars}_i
\]

---

### 5.3 Step Count (STEP_COUNT_MEAN)

We approximate steps via simple pattern matching (e.g., lines starting with `1.`, `2.`, `-`, `*`).

**Per-task:**

- Split `c_i` into lines.
- Count lines that match a step pattern (regex can be e.g. `^\s*(\d+\.|-|\*)\s+`).

\[
\text{step\_count}_i = \text{number of step-like lines in } c_i
\]

**Model-level:**

\[
\text{STEP\_COUNT\_MEAN} = \frac{1}{M} \sum_{i=1}^{M} \text{step\_count}_i
\]

---

### 5.4 Reasoning-to-Answer Ratio (RA_RATIO_MEAN)

**Per-task:**

Let:

- \( r_i = \text{tokens}(c_i) \) (CoT tokens)
- \( a_i = \text{tokens}(\hat{y}_i) \) (answer tokens)

\[
\text{ra\_ratio}_i = \frac{r_i}{\max(1, a_i)}
\]

**Model-level:**

\[
\text{RA\_RATIO\_MEAN} = \frac{1}{M} \sum_{i=1}^{M} \text{ra\_ratio}_i
\]

---

### 5.5 Self-Correction Rate (SELF_CORRECTION_RATE)

We use simple keyword heuristics to flag “self-corrections” in CoT.

**Per-task:**

- `self_correcting_i = 1` if `c_i` contains any of the substrings:
  - “actually”, “sorry”, “correction”, “let me fix”, “I made a mistake” (case-insensitive)
- Else, `self_correcting_i = 0`.

**Model-level:**

\[
\text{SELF\_CORRECTION\_RATE} = \frac{1}{M} \sum_{i=1}^{M} \text{self\_correcting}_i
\]

**Range:**  
- \([0, 1]\)

**Inputs required:**

- `cot` (model-produced)

---

## 6. Efficiency Metrics

These use API usage and timing info, not semantics.

### 6.1 Mean Tokens per Task (TOKENS_MEAN)

Using API usage stats:

**Per-task:**

- `prompt_tokens_i = p_i`
- `completion_tokens_i = q_i`
- `total_tokens_i = z_i = p_i + q_i`

**Model-level:**

- Prompt tokens mean:

\[
\text{PROMPT\_TOKENS\_MEAN} = \frac{1}{N} \sum_{i=1}^{N} p_i
\]

- Completion tokens mean:

\[
\text{COMPLETION\_TOKENS\_MEAN} = \frac{1}{N} \sum_{i=1}^{N} q_i
\]

- Total tokens mean:

\[
\text{TOTAL\_TOKENS\_MEAN} = \frac{1}{N} \sum_{i=1}^{N} z_i
\]

---

### 6.2 Latency Metrics (LATENCY_MEAN, LATENCY_P95)

**Per-task:**

- \( L_i \) = latency in milliseconds for the model call (measured in backend).

**Model-level:**

- Mean latency:

\[
\text{LATENCY\_MEAN\_MS} = \frac{1}{N} \sum_{i=1}^{N} L_i
\]

- 95th percentile latency (P95):

Let \( \{L_i\} \) sorted ascending be \( L_{(1)}, \dots, L_{(N)} \).  

\[
\text{LATENCY\_P95\_MS} = L_{(\lceil 0.95N \rceil)}
\]

**Range:**  
- \([0, +\infty)\) ms

**Inputs required:**

- Latency measurement per request

---

## 7. Schema & Implementation Notes

### 7.1 MetricsSummary Extensions

The existing `MetricsSummary` can be extended to include:

- `accuracy: float`
- `brier: float | None`
- `ece: float | None`
- `sce: float | None`   // SCE_v0 as defined above
- `usr: float | None`   // USR_v0
- `cot_tokens_mean: float | None`
- `cot_chars_mean: float | None`
- `step_count_mean: float | None`
- `ra_ratio_mean: float | None`
- `self_correction_rate: float | None`
- `prompt_tokens_mean: float | None`
- `completion_tokens_mean: float | None`
- `total_tokens_mean: float | None`
- `latency_mean_ms: float | None`
- `latency_p95_ms: float | None`

Fields that cannot be computed due to missing data (e.g., missing CoT or usage info) should be set to `null`.

### 7.2 Per-Task Logging

For future analyses and exports, it is recommended (but not strictly required) to store per-task fields in `PerTaskResult`, such as:

- `correct: bool`
- `cot: string | null`
- `cot_tokens: int | null`
- `step_count: int | null`
- `self_correcting: bool | null`
- `prompt_tokens: int | null`
- `completion_tokens: int | null`
- `total_tokens: int | null`
- `latency_ms: float | null`

The evaluator should compute these once, then aggregate for `MetricsSummary`.

---

## 8. Future Extensions (Not in v0.2)

These are **not** required for v0.2 but should be considered when designing APIs:

- Multi-sample self-consistency metrics:
  - Per-task SCE over repeated runs
  - Determinism Index at temp 0 (DI@0)
  - Mode accuracy and stability
- Domain-specific USR (e.g., math-aware USR using equation checking)
- RAG-aware USR for retrieval-based tasks
- More advanced calibration metrics using logprobs or self-reported confidence.

For v0.2, the focus is on **judge-free, single-pass metrics** defined above.