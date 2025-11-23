#!/usr/bin/env python3
"""
Test script for OpenAI model runner.

This script demonstrates how to use the OpenAI runner to evaluate tasks.
Requires OPENAI_API_KEY environment variable to be set.

Usage:
    export OPENAI_API_KEY=your_key_here
    python3 scripts/test_openai_runner.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zeta_reason.models import OpenAIModelRunner
from zeta_reason.schemas import ModelConfig, Task
from zeta_reason.evaluator import evaluate_model_on_dataset_sync


def main():
    """Test OpenAI runner with a few simple tasks."""
    print("=" * 80)
    print("OpenAI Model Runner Test")
    print("=" * 80)
    print()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print()
        print("To run this test, set your OpenAI API key:")
        print("  export OPENAI_API_KEY=your_key_here")
        print("  python3 scripts/test_openai_runner.py")
        print()
        print("Skipping OpenAI API test (no API key found).")
        return

    # Create a few simple test tasks
    tasks = [
        Task(id="simple_math_1", input="What is 15 + 27?", target="42"),
        Task(id="simple_math_2", input="What is 8 * 9?", target="72"),
        Task(id="simple_logic", input="If all cats are mammals, and some mammals are pets, can we conclude that all cats are pets? Answer yes or no.", target="no"),
    ]

    print(f"Testing with {len(tasks)} tasks:")
    for task in tasks:
        print(f"  - {task.id}: {task.input[:50]}...")
    print()

    # Create model config
    model_config = ModelConfig(
        model_id="gpt-4o-mini",
        provider="openai",
        temperature=0.3,  # Lower temperature for more deterministic outputs
        max_tokens=500,
        use_cot=True,
    )

    # Create OpenAI runner
    print(f"Creating OpenAI runner with model: {model_config.model_id}")
    try:
        runner = OpenAIModelRunner(
            model_id=model_config.model_id,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            use_cot=model_config.use_cot,
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI runner: {e}")
        return

    print()
    print("Running evaluation...")
    print("-" * 80)

    # Run evaluation
    try:
        result = evaluate_model_on_dataset_sync(runner, tasks, model_config)
    except Exception as e:
        print(f"ERROR: Evaluation failed: {e}")
        return

    print()
    print("=" * 80)
    print("RESULTS")
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

    # Show detailed results for each task
    print("=" * 80)
    print("DETAILED TASK RESULTS")
    print("=" * 80)
    for i, task_result in enumerate(result.task_results, 1):
        print()
        print(f"Task {i}: {task_result.task_id}")
        print(f"  Input:   {task_result.input}")
        print(f"  Target:  {task_result.target}")
        print(f"  Answer:  {task_result.model_output.answer}")
        print(f"  Correct: {task_result.correct}")
        print()
        print("  Chain of Thought:")
        # Print CoT with indentation
        for line in task_result.model_output.cot_text.split('\n'):
            print(f"    {line}")
        print()

    print("=" * 80)
    print("Test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
