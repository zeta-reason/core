"""Evaluation pipeline logic."""

from .pipeline import (
    compare_models,
    compare_models_sync,
    evaluate_model_on_dataset,
    evaluate_model_on_dataset_sync,
)

__all__ = [
    "evaluate_model_on_dataset",
    "evaluate_model_on_dataset_sync",
    "compare_models",
    "compare_models_sync",
]
