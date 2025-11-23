"""Utilities for loading and parsing datasets."""

import json
from pathlib import Path
from typing import List

from zeta_reason.schemas import Task


def load_dataset(file_path: str) -> List[Task]:
    """
    Load a dataset from a JSONL file.

    Each line should be a JSON object with fields: id, input, target

    Args:
        file_path: Path to the JSONL file

    Returns:
        List of Task objects

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            try:
                data = json.loads(line)
                task = Task(**data)
                tasks.append(task)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num}: {e}")
            except Exception as e:
                raise ValueError(f"Invalid task format on line {line_num}: {e}")

    if not tasks:
        raise ValueError(f"No valid tasks found in {file_path}")

    return tasks


def save_dataset(tasks: List[Task], file_path: str) -> None:
    """
    Save a list of tasks to a JSONL file.

    Args:
        tasks: List of Task objects to save
        file_path: Path where to save the JSONL file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for task in tasks:
            json_line = task.model_dump_json()
            f.write(json_line + "\n")
