"""Core metric computation functions for evaluating reasoning quality."""

import math
from typing import Dict, List, Optional


def accuracy(predictions: List[str], targets: List[str]) -> float:
    """
    Compute answer accuracy (ACC).

    Simple exact string match after stripping whitespace.

    Args:
        predictions: List of predicted answers
        targets: List of ground truth answers

    Returns:
        Accuracy score between 0 and 1
    """
    if not predictions or len(predictions) != len(targets):
        return 0.0

    correct = sum(
        1 for pred, target in zip(predictions, targets)
        if pred.strip().lower() == target.strip().lower()
    )
    return correct / len(predictions)


def brier_score(probs: List[float], targets: List[int]) -> float:
    """
    Compute Brier score for probabilistic calibration.

    Lower is better. Measures mean squared error between predicted
    probability and actual correctness (binary: 0 or 1).

    Args:
        probs: List of model-assigned probabilities of being correct (0-1)
        targets: List of binary correctness values (0 or 1)

    Returns:
        Brier score (0 = perfect, higher = worse, max = 1.0)
    """
    if not probs or len(probs) != len(targets):
        return 1.0

    # Brier score = mean squared error between probability and outcome
    score = sum((prob - target) ** 2 for prob, target in zip(probs, targets))
    return score / len(probs)


def expected_calibration_error(
    probs: List[float],
    targets: List[int],
    n_bins: int = 10
) -> float:
    """
    Compute Expected Calibration Error (ECE).

    Measures the weighted average of absolute differences between
    confidence and accuracy across probability bins.

    Args:
        probs: List of model-assigned probabilities of being correct (0-1)
        targets: List of binary correctness values (0 or 1)
        n_bins: Number of bins for calibration (default: 10)

    Returns:
        ECE score (0 = perfectly calibrated, higher = worse)
    """
    if not probs or len(probs) != len(targets):
        return 1.0

    # Create bins
    bins = [[] for _ in range(n_bins)]
    bin_targets = [[] for _ in range(n_bins)]

    # Assign samples to bins based on predicted probability
    for prob, target in zip(probs, targets):
        # Clamp probability to [0, 1] and determine bin
        prob_clamped = max(0.0, min(1.0, prob))
        bin_idx = min(int(prob_clamped * n_bins), n_bins - 1)
        bins[bin_idx].append(prob_clamped)
        bin_targets[bin_idx].append(target)

    # Compute ECE as weighted average of |confidence - accuracy| per bin
    ece = 0.0
    total_samples = len(probs)

    for bin_probs, bin_tgts in zip(bins, bin_targets):
        if len(bin_probs) > 0:
            avg_confidence = sum(bin_probs) / len(bin_probs)
            avg_accuracy = sum(bin_tgts) / len(bin_tgts)
            bin_weight = len(bin_probs) / total_samples
            ece += bin_weight * abs(avg_confidence - avg_accuracy)

    return ece


def self_consistency_entropy(answer_counts: Dict[str, int]) -> float:
    """
    Compute Self-Consistency Entropy (SCE).

    Measures diversity of answers when sampling multiple times.
    Higher entropy = less consistent (more diverse answers).

    Computes Shannon entropy in nats:
    H(X) = -∑ p(x) * ln(p(x))

    Args:
        answer_counts: Dictionary mapping answer strings to their counts

    Returns:
        Shannon entropy in nats (0 = perfectly consistent, higher = more diverse)
    """
    if not answer_counts:
        return 0.0

    total = sum(answer_counts.values())
    if total == 0:
        return 0.0

    # Compute Shannon entropy in nats
    entropy = 0.0
    for count in answer_counts.values():
        if count > 0:
            prob = count / total
            entropy -= prob * math.log(prob)

    return entropy


def unsupported_step_rate(cot_text: str, final_answer: str, target: str) -> float:
    """
    Compute Unsupported Step Rate (USR).

    For v0.1, this is a simple placeholder heuristic:
    - If final_answer != target, return 1.0 (incorrect reasoning)
    - If final_answer == target, return 0.0 (correct reasoning)

    TODO: Implement more sophisticated heuristics for post-v0.1:
    - Parse reasoning steps and check logical consistency
    - Verify intermediate claims against the input
    - Detect contradictions or unsupported leaps
    - Use an LLM-as-judge to score reasoning quality
    - Check if reasoning steps actually lead to the final answer

    Args:
        cot_text: Chain-of-thought reasoning text
        final_answer: Final answer extracted from the model
        target: Ground truth answer

    Returns:
        Rate of unsupported reasoning (0-1, lower is better)
        - 0.0 = fully supported reasoning (answer correct)
        - 1.0 = unsupported reasoning (answer incorrect)
    """
    # Simple heuristic for v0.1
    if final_answer.strip().lower() == target.strip().lower():
        return 0.0
    else:
        return 1.0


# ============================================================================
# v0.2 Metrics Implementation
# ============================================================================


def usr_v0(predictions: List[str], targets: List[str]) -> float:
    """
    Compute Unsupported Step Rate v0 (USR_v0).

    Simple answer-level proxy: returns 1.0 if answer is wrong, 0.0 if right.
    Mean over all tasks gives overall USR_v0.

    Args:
        predictions: List of predicted answers
        targets: List of ground truth answers

    Returns:
        Mean USR_v0 score (0-1, lower is better)
    """
    if not predictions or len(predictions) != len(targets):
        return 1.0

    usr_scores = [
        0.0 if pred.strip().lower() == target.strip().lower() else 1.0
        for pred, target in zip(predictions, targets)
    ]
    return sum(usr_scores) / len(usr_scores)


def sce_v0(predictions: List[str]) -> Optional[float]:
    """
    Compute Self-Consistency Entropy v0 (SCE_v0).

    Measures diversity of answers across the dataset (single pass).
    Uses natural log (ln).

    Args:
        predictions: List of predicted answers

    Returns:
        Shannon entropy in nats, or None if no predictions
    """
    if not predictions:
        return None

    # Normalize and count answers
    normalized = [pred.strip().lower() for pred in predictions]
    answer_counts: Dict[str, int] = {}
    for answer in normalized:
        answer_counts[answer] = answer_counts.get(answer, 0) + 1

    total = len(normalized)
    if total == 0:
        return None

    # Compute Shannon entropy using natural log
    entropy = 0.0
    for count in answer_counts.values():
        if count > 0:
            prob = count / total
            entropy -= prob * math.log(prob)

    return entropy


def mean_or_none(values: List[Optional[float]]) -> Optional[float]:
    """
    Compute mean of numeric values, filtering out None.

    Args:
        values: List of numeric values or None

    Returns:
        Arithmetic mean, or None if no valid values
    """
    valid_values = [v for v in values if v is not None]
    if not valid_values:
        return None
    return sum(valid_values) / len(valid_values)



# Alias for consistency with naming conventions
safe_mean = mean_or_none
def self_correction_rate(flags: List[Optional[bool]]) -> Optional[float]:
    """
    Compute self-correction rate from boolean flags.

    Args:
        flags: List of True/False/None indicating self-correction

    Returns:
        Fraction of True values among non-None, or None if all None
    """
    valid_flags = [f for f in flags if f is not None]
    if not valid_flags:
        return None

    num_corrections = sum(1 for f in valid_flags if f)
    return num_corrections / len(valid_flags)


def latency_mean(latencies: List[Optional[float]]) -> Optional[float]:
    """
    Compute mean latency.

    Args:
        latencies: List of latency values in milliseconds

    Returns:
        Mean latency, or None if no valid values
    """
    return mean_or_none(latencies)


def latency_p95(latencies: List[Optional[float]]) -> Optional[float]:
    """
    Compute 95th percentile latency.

    Args:
        latencies: List of latency values in milliseconds

    Returns:
        95th percentile latency, or None if no valid values
    """
    valid_latencies = [lat for lat in latencies if lat is not None]
    if not valid_latencies:
        return None

    sorted_latencies = sorted(valid_latencies)
    n = len(sorted_latencies)
    idx = math.ceil(0.95 * n) - 1
    idx = max(0, min(idx, n - 1))  # Clamp to valid range

    return sorted_latencies[idx]


def brier_score_v2(probs: List[Optional[float]], correct: List[bool]) -> Optional[float]:
    """
    Compute Brier score with None-handling for v0.2.

    Filters for indices where prob is not None.

    Args:
        probs: List of predicted probabilities (or None)
        correct: List of correctness flags (True/False)

    Returns:
        Brier score, or None if no usable entries
    """
    if len(probs) != len(correct):
        return None

    # Filter for valid probabilities
    valid_pairs = [(p, c) for p, c in zip(probs, correct) if p is not None]
    if not valid_pairs:
        return None

    # Convert correctness to 1.0/0.0
    scores = [(prob - (1.0 if is_correct else 0.0)) ** 2
              for prob, is_correct in valid_pairs]

    return sum(scores) / len(scores)


def expected_calibration_error_v2(
    probs: List[Optional[float]],
    correct: List[bool],
    num_bins: int = 10
) -> Optional[float]:
    """
    Compute Expected Calibration Error (ECE) with None-handling for v0.2.

    Filters for indices where prob is not None.

    Args:
        probs: List of predicted probabilities (or None)
        correct: List of correctness flags (True/False)
        num_bins: Number of bins (default 10)

    Returns:
        ECE score, or None if no usable entries
    """
    if len(probs) != len(correct):
        return None

    # Filter for valid probabilities
    valid_pairs = [(p, c) for p, c in zip(probs, correct) if p is not None]
    if not valid_pairs:
        return None

    # Create bins
    bins: List[List[float]] = [[] for _ in range(num_bins)]
    bin_correctness: List[List[float]] = [[] for _ in range(num_bins)]

    # Assign to bins
    for prob, is_correct in valid_pairs:
        # Clamp to [0, 1]
        prob_clamped = max(0.0, min(1.0, prob))
        bin_idx = min(int(prob_clamped * num_bins), num_bins - 1)
        bins[bin_idx].append(prob_clamped)
        bin_correctness[bin_idx].append(1.0 if is_correct else 0.0)

    # Compute ECE
    ece = 0.0
    total_samples = len(valid_pairs)

    for bin_probs, bin_correct in zip(bins, bin_correctness):
        if len(bin_probs) > 0:
            avg_conf = sum(bin_probs) / len(bin_probs)
            avg_acc = sum(bin_correct) / len(bin_correct)
            bin_weight = len(bin_probs) / total_samples
            ece += bin_weight * abs(avg_conf - avg_acc)

    return ece
