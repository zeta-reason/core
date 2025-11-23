"""Tests for progress tracking functionality."""

import pytest
import asyncio
from zeta_reason.progress import ProgressTracker, ProgressUpdate


@pytest.mark.asyncio
async def test_create_run():
    """Test creating a new progress tracking run."""
    tracker = ProgressTracker()

    run_id = tracker.create_run(total_tasks=10)

    assert run_id is not None
    assert len(run_id) > 0

    # Check initial state
    progress = tracker.get_progress(run_id)
    assert progress is not None
    assert progress.run_id == run_id
    assert progress.completed_tasks == 0
    assert progress.total_tasks == 10
    assert progress.percentage == 0.0
    assert progress.status == "running"


@pytest.mark.asyncio
async def test_update_progress():
    """Test updating progress during evaluation."""
    tracker = ProgressTracker()

    run_id = tracker.create_run(total_tasks=5)

    # Update progress to 2 out of 5 tasks
    await tracker.update_progress(run_id, completed_tasks=2)

    progress = tracker.get_progress(run_id)
    assert progress.completed_tasks == 2
    assert progress.total_tasks == 5
    assert progress.percentage == 40.0
    assert progress.status == "running"

    # Update to completion
    await tracker.update_progress(run_id, completed_tasks=5)

    progress = tracker.get_progress(run_id)
    assert progress.completed_tasks == 5
    assert progress.percentage == 100.0


@pytest.mark.asyncio
async def test_complete_run():
    """Test marking a run as completed."""
    tracker = ProgressTracker()

    run_id = tracker.create_run(total_tasks=3)

    # Complete the run
    await tracker.complete_run(run_id, "All tasks completed")

    progress = tracker.get_progress(run_id)
    assert progress.status == "done"
    assert progress.percentage == 100.0
    assert progress.completed_tasks == 3
    assert progress.message == "All tasks completed"


@pytest.mark.asyncio
async def test_error_run():
    """Test marking a run as failed."""
    tracker = ProgressTracker()

    run_id = tracker.create_run(total_tasks=10)

    # Update to 3 tasks, then error
    await tracker.update_progress(run_id, completed_tasks=3)
    await tracker.error_run(run_id, "Model API error")

    progress = tracker.get_progress(run_id)
    assert progress.status == "error"
    assert progress.message == "Model API error"
    assert progress.completed_tasks == 3  # Should preserve progress before error


@pytest.mark.asyncio
async def test_cleanup_run():
    """Test cleaning up completed runs."""
    tracker = ProgressTracker()

    run_id = tracker.create_run(total_tasks=5)

    # Verify run exists
    assert tracker.get_progress(run_id) is not None

    # Cleanup
    tracker.cleanup_run(run_id)

    # Verify run no longer exists
    assert tracker.get_progress(run_id) is None


@pytest.mark.asyncio
async def test_progress_callback():
    """Test progress callback for pipeline integration."""
    tracker = ProgressTracker()

    run_id = tracker.create_run(total_tasks=10)
    callback = tracker.get_progress_callback(run_id)

    # Simulate progress updates from evaluation pipeline
    for i in range(1, 11):
        callback(i, 10)
        await asyncio.sleep(0.01)  # Allow async updates to process

    # Check final state
    progress = tracker.get_progress(run_id)
    assert progress.completed_tasks == 10
    assert progress.percentage == 100.0


@pytest.mark.asyncio
async def test_multiple_runs():
    """Test tracking multiple concurrent runs."""
    tracker = ProgressTracker()

    run_id_1 = tracker.create_run(total_tasks=5)
    run_id_2 = tracker.create_run(total_tasks=10)

    # Update both runs
    await tracker.update_progress(run_id_1, completed_tasks=2)
    await tracker.update_progress(run_id_2, completed_tasks=7)

    # Check both runs have independent state
    progress_1 = tracker.get_progress(run_id_1)
    progress_2 = tracker.get_progress(run_id_2)

    assert progress_1.completed_tasks == 2
    assert progress_1.percentage == 40.0

    assert progress_2.completed_tasks == 7
    assert progress_2.percentage == 70.0


@pytest.mark.asyncio
async def test_progress_update_to_dict():
    """Test ProgressUpdate serialization to dict."""
    update = ProgressUpdate(
        run_id="test-123",
        completed_tasks=5,
        total_tasks=10,
        percentage=50.0,
        status="running",
        message="Half done"
    )

    data = update.to_dict()

    assert data["run_id"] == "test-123"
    assert data["completed_tasks"] == 5
    assert data["total_tasks"] == 10
    assert data["percentage"] == 50.0
    assert data["status"] == "running"
    assert data["message"] == "Half done"
    assert "timestamp" in data
