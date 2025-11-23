"""Evaluation pipeline for running models on datasets and computing metrics."""

import asyncio
import logging
import re
import time
from collections import Counter
from typing import List, Optional, Callable

from zeta_reason.models.base import BaseModelRunner
from zeta_reason.schemas import (
    EvaluationResult,
    MetricsSummary,
    ModelConfig,
    Task,
    TaskResult,
)
from zeta_reason.metrics import (
    accuracy,
    brier_score_v2,
    expected_calibration_error_v2,
    sce_v0,
    usr_v0,
    mean_or_none,
    self_correction_rate,
    latency_mean,
    latency_p95,
)

logger = logging.getLogger(__name__)


async def evaluate_model_on_dataset(
    model_runner: BaseModelRunner,
    tasks: List[Task],
    model_config: ModelConfig | None = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> EvaluationResult:
    """
    Evaluate a single model on a dataset of tasks.

    This is an async function to support potential future async model runners,
    though current implementations are synchronous.

    Args:
        model_runner: The model runner instance to use
        tasks: List of tasks to evaluate
        model_config: Optional model configuration (if None, creates from runner params)
        progress_callback: Optional callback(completed_tasks, total_tasks) for progress updates

    Returns:
        EvaluationResult containing metrics and per-task results

    Raises:
        ValueError: If tasks list is empty
    """
    if not tasks:
        raise ValueError("Dataset contains no tasks")

    # Create model config if not provided
    if model_config is None:
        model_config = ModelConfig(
            model_id=model_runner.model_id,
            provider="unknown",
            temperature=model_runner.temperature,
            max_tokens=model_runner.max_tokens,
            use_cot=model_runner.use_cot,
        )

    logger.info(
        f"Starting evaluation: model={model_config.model_id}, "
        f"provider={model_config.provider}, tasks={len(tasks)}"
    )

    task_results = []
    total_tasks = len(tasks)

    # Run model on each task
    for i, task in enumerate(tasks, 1):
        logger.debug(f"Evaluating task {i}/{total_tasks}: {task.id}")

        # Format prompt and generate response
        # Measure latency
        start_time = time.perf_counter()
        prompt = model_runner.format_prompt(task.input)
        model_output = await asyncio.to_thread(model_runner.generate, prompt)
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000.0

        # Check correctness (case-insensitive exact match)
        is_correct = model_output.answer.strip().lower() == task.target.strip().lower()

        # Extract CoT text
        cot_text = model_output.cot_text

        # Compute per-task CoT metrics
        cot_tokens = None
        cot_chars = None
        step_count = None
        ra_ratio = None
        self_correcting = None

        if cot_text is not None and cot_text.strip():
            # Token count (simple whitespace split)
            cot_tokens = len(cot_text.split())

            # Character count
            cot_chars = len(cot_text)

            # Step count (count lines matching step patterns)
            lines = cot_text.split('\n')
            step_pattern = re.compile(r'^\s*(\d+\.|-|\*)\s+')
            step_count = sum(1 for line in lines if step_pattern.match(line))

            # Reasoning-to-answer ratio
            answer_tokens = len(model_output.answer.split())
            ra_ratio = cot_tokens / max(1, answer_tokens)

            # Self-correction detection (keyword matching)
            cot_lower = cot_text.lower()
            correction_keywords = ['actually', 'sorry', 'correction', 'let me fix', 'i made a mistake']
            self_correcting = any(keyword in cot_lower for keyword in correction_keywords)

        # Extract token usage from model_output if available
        prompt_tokens = model_output.prompt_tokens
        completion_tokens = model_output.completion_tokens
        total_tokens = model_output.total_tokens

        # Store task result with all new fields
        task_results.append(
            TaskResult(
                task_id=task.id,
                input=task.input,
                target=task.target,
                model_output=model_output,
                correct=is_correct,
                prob_correct=model_output.confidence,  # Use confidence as prob_correct
                cot_tokens=cot_tokens,
                cot_chars=cot_chars,
                step_count=step_count,
                ra_ratio=ra_ratio,
                self_correcting=self_correcting,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
            )
        )

        # Report progress after each task
        if progress_callback is not None:
            try:
                progress_callback(i, total_tasks)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    logger.info(f"Completed {len(tasks)} task evaluations, computing metrics...")

    # Collect lists for aggregation
    preds = [r.model_output.answer for r in task_results]
    targets_list = [r.target for r in task_results]
    correct_flags = [r.correct for r in task_results]
    prob_correct_list = [r.prob_correct for r in task_results]

    cot_tokens_list = [r.cot_tokens for r in task_results]
    cot_chars_list = [r.cot_chars for r in task_results]
    step_counts = [r.step_count for r in task_results]
    ra_ratios = [r.ra_ratio for r in task_results]
    self_corrections = [r.self_correcting for r in task_results]

    prompt_tokens_list = [r.prompt_tokens for r in task_results]
    completion_tokens_list = [r.completion_tokens for r in task_results]
    total_tokens_list = [r.total_tokens for r in task_results]
    latencies = [r.latency_ms for r in task_results]

    # Compute answer-level metrics
    acc = accuracy(preds, targets_list)
    usr = usr_v0(preds, targets_list)
    sce = sce_v0(preds)

    # Compute calibration metrics (will be None if prob_correct unavailable)
    brier = brier_score_v2(prob_correct_list, correct_flags)
    ece = expected_calibration_error_v2(prob_correct_list, correct_flags)

    # Compute CoT shape metrics
    cot_tokens_mean = mean_or_none(cot_tokens_list)
    cot_chars_mean = mean_or_none(cot_chars_list)
    step_count_mean = mean_or_none(step_counts)
    ra_ratio_mean = mean_or_none(ra_ratios)
    self_correction_rate_val = self_correction_rate(self_corrections)

    # Compute efficiency metrics
    prompt_tokens_mean = mean_or_none(prompt_tokens_list)
    completion_tokens_mean = mean_or_none(completion_tokens_list)
    total_tokens_mean = mean_or_none(total_tokens_list)
    latency_mean_val = latency_mean(latencies)
    latency_p95_val = latency_p95(latencies)

    # Build MetricsSummary
    metrics = MetricsSummary(
        accuracy=acc,
        brier=brier,
        ece=ece,
        sce=sce,
        usr=usr,
        cot_tokens_mean=cot_tokens_mean,
        cot_chars_mean=cot_chars_mean,
        step_count_mean=step_count_mean,
        ra_ratio_mean=ra_ratio_mean,
        self_correction_rate=self_correction_rate_val,
        prompt_tokens_mean=prompt_tokens_mean,
        completion_tokens_mean=completion_tokens_mean,
        total_tokens_mean=total_tokens_mean,
        latency_mean_ms=latency_mean_val,
        latency_p95_ms=latency_p95_val,
    )

    logger.info(
        f"Evaluation complete: ACC={acc:.4f}, USR={usr or 0:.4f}, "
        f"SCE={sce or 0:.4f}, latency_mean={latency_mean_val or 0:.2f}ms"
    )

    return EvaluationResult(
        model_configuration=model_config,
        metrics=metrics,
        task_results=task_results,
        total_tasks=len(tasks),
    )


async def compare_models(
    model_runners: List[BaseModelRunner],
    tasks: List[Task],
    model_configs: List[ModelConfig],
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[EvaluationResult]:
    """
    Compare multiple models on the same dataset.

    Evaluates each model sequentially on the same set of tasks.

    Args:
        model_runners: List of model runner instances
        tasks: List of tasks to evaluate
        model_configs: List of model configurations (matching model_runners)
        progress_callback: Optional callback(completed_tasks, total_tasks) for overall progress

    Returns:
        List of EvaluationResult, one per model

    Raises:
        ValueError: If model_runners and model_configs lengths don't match, or tasks is empty
    """
    if len(model_runners) != len(model_configs):
        raise ValueError(
            f"Number of model runners ({len(model_runners)}) must match "
            f"number of model configs ({len(model_configs)})"
        )

    if not tasks:
        raise ValueError("Dataset contains no tasks")

    logger.info(f"Starting comparison of {len(model_runners)} models on {len(tasks)} tasks")

    # Calculate total tasks across all models for progress tracking
    total_tasks = len(model_runners) * len(tasks)
    completed_tasks = 0

    # Wrapper to track progress across all models
    def model_progress_callback(completed_in_model: int, total_in_model: int):
        nonlocal completed_tasks
        # Update global progress based on current model progress
        global_completed = (completed_tasks // len(tasks)) * len(tasks) + completed_in_model
        if progress_callback is not None:
            try:
                progress_callback(global_completed, total_tasks)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    results = []
    for i, (runner, config) in enumerate(zip(model_runners, model_configs), 1):
        logger.info(f"Evaluating model {i}/{len(model_runners)}: {config.model_id}")
        result = await evaluate_model_on_dataset(runner, tasks, config, model_progress_callback)
        results.append(result)
        completed_tasks = i * len(tasks)

    logger.info(f"Comparison complete for {len(model_runners)} models")
    return results


# Synchronous wrappers for backward compatibility
def evaluate_model_on_dataset_sync(
    model_runner: BaseModelRunner,
    tasks: List[Task],
    model_config: ModelConfig | None = None,
) -> EvaluationResult:
    """
    Synchronous wrapper for evaluate_model_on_dataset.

    Use this if you're calling from non-async code.
    """
    return asyncio.run(evaluate_model_on_dataset(model_runner, tasks, model_config))


def compare_models_sync(
    model_runners: List[BaseModelRunner],
    tasks: List[Task],
    model_configs: List[ModelConfig],
) -> List[EvaluationResult]:
    """
    Synchronous wrapper for compare_models.

    Use this if you're calling from non-async code.
    """
    return asyncio.run(compare_models(model_runners, tasks, model_configs))
