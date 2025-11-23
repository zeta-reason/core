"""File-based storage for experiment results."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from zeta_reason.schemas import EvaluationResult, ModelConfig


# ============================================================================
# Storage Schemas
# ============================================================================


class SamplingConfig(BaseModel):
    """Sampling configuration for an experiment."""

    mode: str = Field(..., description="Sampling mode: 'all' or 'random'")
    sample_size: int = Field(..., description="Number of tasks to sample")


class ExperimentMetadata(BaseModel):
    """Lightweight metadata for experiment listing."""

    id: str = Field(..., description="Unique experiment ID (UUID)")
    name: str = Field(..., description="User-provided or auto-generated name")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    dataset_name: str = Field(..., description="Original dataset filename")
    dataset_size: int = Field(..., description="Total tasks in original dataset")
    tasks_evaluated: int = Field(..., description="Number of tasks actually evaluated")
    model_count: int = Field(..., description="Number of models compared")
    model_ids: List[str] = Field(..., description="List of model IDs")
    accuracy_range: List[float] = Field(
        ..., description="[min, max] accuracy across models"
    )
    tags: List[str] = Field(default_factory=list, description="User-defined tags")


class ExperimentData(BaseModel):
    """Complete experiment data including results."""

    metadata: ExperimentMetadata = Field(..., description="Experiment metadata")
    results: List[EvaluationResult] = Field(
        ..., description="Full evaluation results"
    )
    sampling_config: SamplingConfig = Field(..., description="Sampling configuration")


class ExperimentSaveRequest(BaseModel):
    """Request to save a new experiment."""

    name: str = Field(..., description="Experiment name")
    dataset_name: str = Field(..., description="Dataset filename")
    dataset_size: int = Field(..., description="Total tasks in dataset")
    results: List[EvaluationResult] = Field(..., description="Evaluation results")
    sampling_config: SamplingConfig = Field(..., description="Sampling configuration")
    tags: List[str] = Field(default_factory=list, description="Optional tags")


# ============================================================================
# Storage Manager
# ============================================================================


class ExperimentStorage:
    """Manages file-based storage of experiments."""

    def __init__(self, base_dir: str = "experiments"):
        """
        Initialize experiment storage.

        Args:
            base_dir: Directory to store experiment files (relative to project root)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.metadata_file = self.base_dir / "metadata.json"

        # Initialize metadata file if it doesn't exist
        if not self.metadata_file.exists():
            self._write_metadata([])

    def _read_metadata(self) -> List[ExperimentMetadata]:
        """Read metadata index from disk."""
        try:
            with open(self.metadata_file, "r") as f:
                data = json.load(f)
                return [ExperimentMetadata(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_metadata(self, metadata_list: List[ExperimentMetadata]) -> None:
        """Write metadata index to disk."""
        tmp_path = self.metadata_file.with_suffix(self.metadata_file.suffix + ".tmp")
        with open(tmp_path, "w") as f:
            json.dump([m.model_dump() for m in metadata_list], f, indent=2)
        # Atomic replace to avoid partial writes/corruption under concurrent requests
        os.replace(tmp_path, self.metadata_file)

    def _get_experiment_path(self, experiment_id: str) -> Path:
        """Get file path for experiment data."""
        return self.base_dir / f"{experiment_id}.json"

    def save(self, request: ExperimentSaveRequest) -> str:
        """
        Save a new experiment.

        Args:
            request: Experiment save request

        Returns:
            Experiment ID (UUID)
        """
        # Generate unique ID
        experiment_id = str(uuid.uuid4())

        # Calculate metadata
        accuracies = [result.metrics.accuracy for result in request.results]
        model_ids = [result.model_configuration.model_id for result in request.results]
        tasks_evaluated = request.results[0].total_tasks if request.results else 0

        # Create metadata
        metadata = ExperimentMetadata(
            id=experiment_id,
            name=request.name,
            timestamp=datetime.utcnow().isoformat() + "Z",
            dataset_name=request.dataset_name,
            dataset_size=request.dataset_size,
            tasks_evaluated=tasks_evaluated,
            model_count=len(request.results),
            model_ids=model_ids,
            accuracy_range=[min(accuracies), max(accuracies)] if accuracies else [0.0, 0.0],
            tags=request.tags,
        )

        # Create full experiment data
        experiment_data = ExperimentData(
            metadata=metadata,
            results=request.results,
            sampling_config=request.sampling_config,
        )

        # Save experiment file
        experiment_path = self._get_experiment_path(experiment_id)
        with open(experiment_path, "w") as f:
            json.dump(experiment_data.model_dump(), f, indent=2)

        # Update metadata index
        metadata_list = self._read_metadata()
        metadata_list.append(metadata)
        self._write_metadata(metadata_list)

        return experiment_id

    def list_metadata(self) -> List[ExperimentMetadata]:
        """
        List all experiment metadata.

        Returns:
            List of experiment metadata, sorted by timestamp (newest first)
        """
        metadata_list = self._read_metadata()
        # Sort by timestamp descending
        metadata_list.sort(key=lambda x: x.timestamp, reverse=True)
        return metadata_list

    def load(self, experiment_id: str) -> Optional[ExperimentData]:
        """
        Load full experiment data.

        Args:
            experiment_id: Experiment UUID

        Returns:
            Full experiment data, or None if not found
        """
        experiment_path = self._get_experiment_path(experiment_id)

        if not experiment_path.exists():
            return None

        try:
            with open(experiment_path, "r") as f:
                data = json.load(f)
                return ExperimentData(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def delete(self, experiment_id: str) -> bool:
        """
        Delete an experiment.

        Args:
            experiment_id: Experiment UUID

        Returns:
            True if deleted, False if not found
        """
        experiment_path = self._get_experiment_path(experiment_id)

        if not experiment_path.exists():
            return False

        # Delete experiment file
        experiment_path.unlink()

        # Update metadata index
        metadata_list = self._read_metadata()
        metadata_list = [m for m in metadata_list if m.id != experiment_id]
        self._write_metadata(metadata_list)

        return True

    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        metadata_list = self._read_metadata()
        total_experiments = len(metadata_list)

        # Calculate total disk usage
        total_size = 0
        for metadata in metadata_list:
            experiment_path = self._get_experiment_path(metadata.id)
            if experiment_path.exists():
                total_size += experiment_path.stat().st_size

        # Add metadata file size
        if self.metadata_file.exists():
            total_size += self.metadata_file.stat().st_size

        return {
            "total_experiments": total_experiments,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
