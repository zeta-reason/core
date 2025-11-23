#!/usr/bin/env python3
"""Example script to run evaluation using the DummyModelRunner."""

import sys
from pathlib import Path

# Add parent directory to path so we can import zeta_reason
sys.path.insert(0, str(Path(__file__).parent.parent))

from zeta_reason.models import DummyModelRunner
from zeta_reason.schemas import ModelConfig
from zeta_reason.utils import load_dataset
from zeta_reason.evaluator import evaluate_model_on_dataset_sync


def main():
    """Run example evaluation on arithmetic dataset."""
    print("=" * 80)
    print("Zeta Reason v0.1 - Example Evaluation")
    print("=" * 80)
    print()

    # Load dataset
    dataset_path = Path(__file__).parent.parent / "data" / "example_arithmetic.jsonl"
    print(f"Loading dataset from: {dataset_path}")
    tasks = load_dataset(str(dataset_path))
    print(f"Loaded {len(tasks)} tasks")
    print()

    # Create model config
    model_config = ModelConfig(
        model_id="dummy-1.0",
        provider="dummy",
        temperature=0.7,
        max_tokens=1000,
        use_cot=True,
    )

    # Create model runner
    print(f"Creating DummyModelRunner: {model_config.model_id}")
    runner = DummyModelRunner(
        model_id=model_config.model_id,
        temperature=model_config.temperature,
        max_tokens=model_config.max_tokens,
        use_cot=model_config.use_cot,
    )
    print()

    # Run evaluation
    print("Running evaluation...")
    print("-" * 80)
    result = evaluate_model_on_dataset_sync(runner, tasks, model_config)
    print()

    # Print results
    print("=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    print()
    print(f"Model: {result.model_configuration.model_id}")
    print(f"Total tasks: {result.total_tasks}")
    print()
    print("Metrics:")
    print(f"  Accuracy (ACC):              {result.metrics.accuracy:.4f}")
    print(f"  Brier Score:                 {result.metrics.brier_score:.4f}")
    print(f"  Expected Calibration Error:  {result.metrics.expected_calibration_error:.4f}")
    print(f"  Self-Consistency Entropy:    {result.metrics.self_consistency_entropy:.4f}")
    print(f"  Unsupported Step Rate:       {result.metrics.unsupported_step_rate:.4f}")
    print()

    # Show a few sample results
    print("=" * 80)
    print("SAMPLE TASK RESULTS (first 3)")
    print("=" * 80)
    for i, task_result in enumerate(result.task_results[:3], 1):
        print()
        print(f"Task {i}: {task_result.task_id}")
        print(f"  Input:   {task_result.input}")
        print(f"  Target:  {task_result.target}")
        print(f"  Answer:  {task_result.model_output.answer}")
        print(f"  Correct: {task_result.correct}")
        print(f"  CoT (first 100 chars): {task_result.model_output.cot_text[:100]}...")
        print()

    print("=" * 80)
    print("Evaluation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
