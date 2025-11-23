# Metrics Specification

This document provides detailed specifications for all metrics computed by Zeta Reason, including mathematical formulas, interpretation guidelines, and implementation notes.

## Table of Contents

- [Overview](#overview)
- [Core Metrics](#core-metrics)
  - [Accuracy (ACC)](#accuracy-acc)
  - [Brier Score](#brier-score)
  - [Expected Calibration Error (ECE)](#expected-calibration-error-ece)
  - [Self-Consistency Entropy (SCE)](#self-consistency-entropy-sce)
  - [Unsupported Step Rate (USR)](#unsupported-step-rate-usr)
- [Auxiliary Metrics](#auxiliary-metrics)
  - [CoT Tokens](#cot-tokens)
  - [Step Count](#step-count)
  - [Latency](#latency)
- [Aggregation](#aggregation)
- [Implementation Details](#implementation-details)

## Overview

Zeta Reason computes metrics across three categories:

1. **Correctness**: How accurate are the model's answers?
2. **Calibration**: How well does the model know what it knows?
3. **Reasoning Quality**: How good is the chain-of-thought process?

All metrics are computed per-task and then aggregated across the dataset.

## Core Metrics

### Accuracy (ACC)

**Definition:** The proportion of tasks where the model's answer exactly matches the target.

**Formula:**

```
ACC = (Number of correct answers) / (Total number of tasks)
```

**Range:** 0.0 to 1.0 (often displayed as 0% to 100%)

**Interpretation:**
- `ACC = 1.0` → Perfect performance
- `ACC = 0.5` → Coin-flip level performance (for binary tasks)
- `ACC = 0.0` → Complete failure

**Implementation:**

```python
def compute_accuracy(
    tasks: List[Task],
    outputs: List[ModelOutput]
) -> float:
    """Compute exact match accuracy."""
    if len(tasks) == 0:
        return 0.0

    correct = 0
    for task, output in zip(tasks, outputs):
        # Normalize both strings for comparison
        pred = normalize_answer(output.answer)
        target = normalize_answer(task.target)

        if pred == target:
            correct += 1

    return correct / len(tasks)

def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison."""
    # Convert to lowercase
    answer = answer.lower().strip()

    # Remove punctuation
    answer = re.sub(r'[^\w\s]', '', answer)

    # Remove extra whitespace
    answer = ' '.join(answer.split())

    return answer
```

**Notes:**
- Case-insensitive comparison
- Whitespace normalized
- Punctuation removed for robustness
- Future: Support fuzzy matching, numerical tolerance

---

### Brier Score

**Definition:** A measure of calibration that penalizes both over-confidence and under-confidence.

**Formula:**

```
Brier Score = (1/N) * Σ (p_i - y_i)²

where:
  N = number of tasks
  p_i = model's confidence for task i (0 to 1)
  y_i = actual correctness (1 if correct, 0 if wrong)
```

**Range:** 0.0 to 1.0 (lower is better)

**Interpretation:**
- `Brier = 0.0` → Perfect calibration
- `Brier = 0.25` → Equivalent to always predicting 50% confidence
- `Brier = 1.0` → Worst possible calibration

**Example:**

| Task | Confidence | Correct | (p - y)² |
|------|------------|---------|----------|
| 1    | 0.9        | Yes (1) | 0.01     |
| 2    | 0.3        | No (0)  | 0.09     |
| 3    | 0.7        | No (0)  | 0.49     |
| Avg  |            |         | **0.197**|

**Implementation:**

```python
def compute_brier_score(
    tasks: List[Task],
    outputs: List[ModelOutput]
) -> float:
    """Compute Brier score for calibration."""
    if len(tasks) == 0:
        return 0.0

    score = 0.0
    for task, output in zip(tasks, outputs):
        # Determine correctness
        is_correct = 1.0 if is_answer_correct(task, output) else 0.0

        # Get confidence (default to 0.5 if not provided)
        confidence = output.confidence if output.confidence else 0.5

        # Brier score contribution
        score += (confidence - is_correct) ** 2

    return score / len(tasks)
```

**Notes:**
- Lower is better (unlike accuracy)
- Requires confidence values from model
- If no confidence, defaults to 0.5
- Related to mean squared error

---

### Expected Calibration Error (ECE)

**Definition:** The average difference between confidence and accuracy across confidence bins.

**Formula:**

```
ECE = Σ (n_b / N) * |acc_b - conf_b|

where:
  B = number of bins (typically 10)
  n_b = number of samples in bin b
  N = total number of samples
  acc_b = accuracy in bin b
  conf_b = average confidence in bin b
```

**Range:** 0.0 to 1.0 (lower is better)

**Interpretation:**
- `ECE = 0.0` → Perfect calibration
- `ECE < 0.1` → Well calibrated
- `ECE > 0.2` → Poorly calibrated

**Example:**

| Confidence Bin | Count | Accuracy | Avg Conf | \|acc - conf\| | Contribution |
|----------------|-------|----------|----------|----------------|--------------|
| [0.0, 0.1)     | 5     | 0.00     | 0.05     | 0.05           | 0.0025       |
| [0.1, 0.2)     | 8     | 0.12     | 0.15     | 0.03           | 0.0024       |
| ...            | ...   | ...      | ...      | ...            | ...          |
| [0.9, 1.0]     | 20    | 0.95     | 0.93     | 0.02           | 0.0040       |
| **Total**      | 100   |          |          |                | **0.082**    |

**Implementation:**

```python
def compute_expected_calibration_error(
    tasks: List[Task],
    outputs: List[ModelOutput],
    n_bins: int = 10
) -> float:
    """Compute Expected Calibration Error."""
    if len(tasks) == 0:
        return 0.0

    # Create bins
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bins = {i: {'confidences': [], 'correctness': []}
            for i in range(n_bins)}

    # Assign samples to bins
    for task, output in zip(tasks, outputs):
        confidence = output.confidence if output.confidence else 0.5
        is_correct = is_answer_correct(task, output)

        # Find bin
        bin_idx = min(int(confidence * n_bins), n_bins - 1)
        bins[bin_idx]['confidences'].append(confidence)
        bins[bin_idx]['correctness'].append(1.0 if is_correct else 0.0)

    # Compute ECE
    ece = 0.0
    total = len(tasks)

    for bin_data in bins.values():
        if len(bin_data['correctness']) == 0:
            continue

        bin_acc = np.mean(bin_data['correctness'])
        bin_conf = np.mean(bin_data['confidences'])
        bin_size = len(bin_data['correctness'])

        ece += (bin_size / total) * abs(bin_acc - bin_conf)

    return ece
```

**Notes:**
- More interpretable than Brier score
- Visualizable as calibration plot
- Default 10 bins, adjustable
- Sensitive to bin size choice

---

### Self-Consistency Entropy (SCE)

**Definition:** A measure of reasoning diversity when sampling multiple solutions (v0 implementation).

**Formula (v0 - Single Shot):**

```
SCE = -log(1)  # Always 0 for single-shot

For multi-shot (future):
SCE = -Σ p(answer_i) * log(p(answer_i))

where:
  p(answer_i) = proportion of times answer_i appears
```

**Range:** 0.0 to ∞ (higher = more diversity)

**Interpretation:**
- `SCE = 0.0` → Always produces same answer (consistent)
- `SCE = log(k)` → Uniform distribution over k answers
- `SCE > 2.0` → High diversity (may indicate uncertainty)

**Example (Multi-Shot):**

If model produces ["4", "4", "4", "5", "4"] across 5 samples:
- p("4") = 0.8
- p("5") = 0.2
- SCE = -(0.8 * log(0.8) + 0.2 * log(0.2)) = 0.5

**Implementation (v0):**

```python
def compute_self_consistency_entropy(
    outputs: List[ModelOutput]
) -> float:
    """
    Compute self-consistency entropy.

    v0: Returns 0.0 (single-shot, no diversity).
    Future: Will support multi-shot sampling.
    """
    # v0 implementation: always 0 for single shot
    return 0.0

# Future multi-shot implementation:
def compute_sce_multishot(
    outputs_per_task: List[List[ModelOutput]]
) -> float:
    """Compute SCE with multiple samples per task."""
    entropies = []

    for task_outputs in outputs_per_task:
        # Count answer occurrences
        answers = [o.answer for o in task_outputs]
        counts = Counter(answers)
        total = len(answers)

        # Compute entropy
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log(p)

        entropies.append(entropy)

    return np.mean(entropies)
```

**Notes:**
- v0: Placeholder (returns 0)
- v1+: Will require multi-shot sampling
- Related to confidence/uncertainty
- Higher SCE → less self-consistent

---

### Unsupported Step Rate (USR)

**Definition:** The proportion of reasoning steps that are not logically supported by previous steps or the input.

**Formula:**

```
USR = (Number of unsupported steps) / (Total number of steps)
```

**Range:** 0.0 to 1.0 (lower is better)

**Interpretation:**
- `USR = 0.0` → All steps are well-supported
- `USR = 0.1` → 10% of steps are unsupported (acceptable)
- `USR > 0.3` → High rate of logical errors

**Detection Heuristics:**

1. **Contradictions**: Step contradicts earlier step
2. **Non-sequiturs**: Step doesn't follow from previous
3. **Hallucinations**: Step introduces unsupported facts
4. **Arithmetic errors**: Calculation mistakes

**Example:**

```
Input: "What is 15 + 27?"

Good CoT (USR = 0.0):
1. We need to add 15 and 27.
2. 15 + 27 = 42.
3. Therefore, the answer is 42.

Bad CoT (USR = 0.33):
1. We need to add 15 and 27.
2. 15 is prime, so we use special rules.  [UNSUPPORTED]
3. 15 + 27 = 42.
```

**Implementation (v0):**

```python
def compute_unsupported_step_rate(
    outputs: List[ModelOutput]
) -> float:
    """
    Compute unsupported step rate.

    v0: Simple heuristic based on keywords.
    Future: Use LLM-based step evaluation.
    """
    if len(outputs) == 0:
        return 0.0

    total_steps = 0
    unsupported_steps = 0

    for output in outputs:
        steps = parse_steps(output.cot)
        total_steps += len(steps)

        for i, step in enumerate(steps):
            # Check for unsupported indicators
            if is_unsupported(step, steps[:i], output.input):
                unsupported_steps += 1

    return unsupported_steps / total_steps if total_steps > 0 else 0.0

def is_unsupported(
    step: str,
    previous_steps: List[str],
    input_text: str
) -> bool:
    """Check if step is unsupported (heuristic)."""

    # Heuristic 1: Contradictions
    for prev in previous_steps:
        if contains_contradiction(step, prev):
            return True

    # Heuristic 2: Unsupported facts
    unsupported_patterns = [
        r'assume',
        r'clearly',
        r'obviously',
        r'it is known that'
    ]
    for pattern in unsupported_patterns:
        if re.search(pattern, step.lower()):
            return True

    return False
```

**Notes:**
- v0: Heuristic-based (conservative)
- v1+: LLM-based evaluation for accuracy
- Challenging to implement reliably
- Domain-dependent

---

## Auxiliary Metrics

### CoT Tokens

**Definition:** The number of tokens in the chain-of-thought reasoning.

**Computation:**

```python
def count_tokens(text: str, model: str) -> int:
    """Count tokens using model-specific tokenizer."""
    import tiktoken

    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

**Interpretation:**
- Higher token count → More verbose reasoning
- Useful for cost estimation
- Correlates with reasoning complexity

---

### Step Count

**Definition:** The number of distinct reasoning steps in the CoT.

**Computation:**

```python
def count_steps(cot: str) -> int:
    """Count reasoning steps (heuristic)."""

    # Method 1: Count numbered steps
    numbered_steps = re.findall(r'^\d+\.', cot, re.MULTILINE)
    if len(numbered_steps) > 0:
        return len(numbered_steps)

    # Method 2: Count sentences
    sentences = re.split(r'[.!?]+', cot)
    return len([s for s in sentences if s.strip()])
```

**Interpretation:**
- More steps → More detailed reasoning
- Optimal step count depends on task complexity
- Very high counts may indicate verbosity

---

### Latency

**Definition:** Time taken to generate a response (milliseconds).

**Computation:**

```python
async def run_with_timing(self, prompt: str) -> ModelOutput:
    """Run model and measure latency."""
    start_time = time.time()

    response = await self.client.chat.completions.create(...)

    latency_ms = (time.time() - start_time) * 1000

    return ModelOutput(
        answer=...,
        latency_ms=latency_ms,
        ...
    )
```

**Interpretation:**
- Lower latency → Faster responses
- Trade-off with quality (longer prompts → higher latency)
- Useful for production deployment planning

---

## Aggregation

### Per-Task Metrics

Individual metrics computed for each task:

```json
{
  "task_id": "1",
  "input": "What is 2+2?",
  "target": "4",
  "output": {
    "answer": "4",
    "cot": "2+2 equals 4.",
    "confidence": 0.95,
    "cot_tokens": 5,
    "step_count": 1,
    "latency_ms": 850
  },
  "is_correct": true
}
```

### Dataset-Level Aggregation

Most metrics are averaged across tasks:

```python
class Metrics:
    accuracy: float              # Mean of binary correctness
    brier_score: float          # Mean of (conf - correct)²
    ece: float                  # Weighted avg across bins
    sce: float                  # Mean entropy (future)
    usr: float                  # Mean unsupported rate
    avg_cot_tokens: float       # Mean token count
    avg_step_count: float       # Mean step count
    avg_latency_ms: float       # Mean latency
```

### Statistical Significance

For comparing models, compute confidence intervals:

```python
from scipy import stats

def compute_confidence_interval(
    values: List[float],
    confidence: float = 0.95
) -> Tuple[float, float]:
    """Compute confidence interval for metric."""
    mean = np.mean(values)
    sem = stats.sem(values)
    ci = sem * stats.t.ppf((1 + confidence) / 2, len(values) - 1)
    return (mean - ci, mean + ci)
```

**Usage:**
- Compare if confidence intervals overlap
- Non-overlapping → statistically significant difference
- Bootstrap for non-normal distributions

---

## Implementation Details

### Metric Computation Pipeline

```python
def compute_metrics(
    tasks: List[Task],
    outputs: List[ModelOutput],
    config: ModelConfig
) -> Metrics:
    """Main metrics computation pipeline."""

    # 1. Correctness
    accuracy = compute_accuracy(tasks, outputs)

    # 2. Calibration
    brier_score = compute_brier_score(tasks, outputs)
    ece = compute_expected_calibration_error(tasks, outputs)

    # 3. Consistency
    sce = compute_self_consistency_entropy(outputs)

    # 4. Reasoning quality
    usr = compute_unsupported_step_rate(outputs)

    # 5. Auxiliary metrics
    avg_cot_tokens = np.mean([o.cot_tokens for o in outputs])
    avg_step_count = np.mean([o.step_count for o in outputs])
    avg_latency_ms = np.mean([o.latency_ms for o in outputs])

    return Metrics(
        accuracy=accuracy,
        brier_score=brier_score,
        ece=ece,
        sce=sce,
        usr=usr,
        avg_cot_tokens=avg_cot_tokens,
        avg_step_count=avg_step_count,
        avg_latency_ms=avg_latency_ms,
    )
```

### Error Handling

```python
def safe_compute_metric(
    compute_fn: Callable,
    *args,
    default_value: float = 0.0
) -> float:
    """Safely compute metric with fallback."""
    try:
        result = compute_fn(*args)
        if np.isnan(result) or np.isinf(result):
            return default_value
        return result
    except Exception as e:
        logger.error(f"Metric computation failed: {e}")
        return default_value
```

### Future Enhancements

1. **Multi-Shot SCE**: Implement with temperature sampling
2. **LLM-Based USR**: Use GPT-4 to evaluate step quality
3. **F1 Score**: For tasks with partial credit
4. **BLEU/ROUGE**: For generative tasks
5. **Perplexity**: For language quality
6. **Cost Tracking**: API cost per evaluation

---

## References

1. Brier, G. W. (1950). "Verification of forecasts expressed in terms of probability"
2. Naeini, M. P., et al. (2015). "Obtaining Well Calibrated Probabilities Using Bayesian Binning"
3. Wang, X., et al. (2022). "Self-Consistency Improves Chain of Thought Reasoning in Language Models"
4. Madaan, A., et al. (2023). "Self-Refine: Iterative Refinement with Self-Feedback"

---

**Last Updated:** January 2025
**Version:** 1.0.0-beta
