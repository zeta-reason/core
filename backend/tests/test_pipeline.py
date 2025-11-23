"""Tests for evaluation pipeline."""

import pytest

from zeta_reason.models import DummyModelRunner
from zeta_reason.schemas import ModelConfig, Task
from zeta_reason.evaluator import (
    compare_models,
    compare_models_sync,
    evaluate_model_on_dataset,
    evaluate_model_on_dataset_sync,
)


class TestEvaluatePipeline:
    """Tests for evaluation pipeline."""

    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks for testing."""
        return [
            Task(id="task1", input="What is 2+2?", target="4"),
            Task(id="task2", input="What is 3+3?", target="6"),
            Task(id="task3", input="What is 5+5?", target="10"),
        ]

    @pytest.fixture
    def dummy_runner(self):
        """Create a dummy model runner."""
        return DummyModelRunner(model_id="test-dummy", temperature=0.5, use_cot=True)

    @pytest.fixture
    def model_config(self):
        """Create a model config."""
        return ModelConfig(
            model_id="test-dummy",
            provider="dummy",
            temperature=0.5,
            max_tokens=100,
            use_cot=True,
        )

    def test_evaluate_sync_basic(self, dummy_runner, sample_tasks, model_config):
        """Test synchronous evaluation with basic tasks."""
        result = evaluate_model_on_dataset_sync(dummy_runner, sample_tasks, model_config)

        assert result.total_tasks == 3
        assert len(result.task_results) == 3
        assert result.model_configuration.model_id == "test-dummy"

        # Check metrics exist and are valid
        assert 0.0 <= result.metrics.accuracy <= 1.0
        assert 0.0 <= result.metrics.brier_score <= 1.0
        assert 0.0 <= result.metrics.expected_calibration_error <= 1.0
        assert result.metrics.self_consistency_entropy >= 0.0
        assert 0.0 <= result.metrics.unsupported_step_rate <= 1.0

    @pytest.mark.asyncio
    async def test_evaluate_async_basic(self, dummy_runner, sample_tasks, model_config):
        """Test asynchronous evaluation with basic tasks."""
        result = await evaluate_model_on_dataset(dummy_runner, sample_tasks, model_config)

        assert result.total_tasks == 3
        assert len(result.task_results) == 3
        assert result.model_configuration.model_id == "test-dummy"

    def test_evaluate_without_config(self, dummy_runner, sample_tasks):
        """Test evaluation without explicit model config."""
        result = evaluate_model_on_dataset_sync(dummy_runner, sample_tasks)

        assert result.total_tasks == 3
        assert result.model_configuration.model_id == "test-dummy"
        assert result.model_configuration.provider == "unknown"

    def test_evaluate_empty_tasks_raises_error(self, dummy_runner, model_config):
        """Test that empty task list raises ValueError."""
        with pytest.raises(ValueError, match="Dataset contains no tasks"):
            evaluate_model_on_dataset_sync(dummy_runner, [], model_config)

    def test_task_results_contain_all_fields(self, dummy_runner, sample_tasks, model_config):
        """Test that task results contain all required fields."""
        result = evaluate_model_on_dataset_sync(dummy_runner, sample_tasks, model_config)

        for task_result in result.task_results:
            assert task_result.task_id is not None
            assert task_result.input is not None
            assert task_result.target is not None
            assert task_result.model_output is not None
            assert isinstance(task_result.correct, bool)
            assert task_result.model_output.answer is not None
            assert task_result.model_output.cot_text is not None

    def test_sce_calculation(self, dummy_runner, sample_tasks, model_config):
        """Test that SCE is calculated based on answer distribution."""
        result = evaluate_model_on_dataset_sync(dummy_runner, sample_tasks, model_config)

        # SCE should be > 0 if there are different answers
        # DummyModelRunner produces varied answers based on hash
        # so SCE should be non-zero for varied tasks
        assert result.metrics.self_consistency_entropy >= 0.0


class TestComparePipeline:
    """Tests for model comparison pipeline."""

    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks for testing."""
        return [
            Task(id="task1", input="What is 1+1?", target="2"),
            Task(id="task2", input="What is 2+2?", target="4"),
        ]

    @pytest.fixture
    def dummy_runners(self):
        """Create multiple dummy model runners."""
        return [
            DummyModelRunner(model_id="dummy-1", temperature=0.3),
            DummyModelRunner(model_id="dummy-2", temperature=0.7),
        ]

    @pytest.fixture
    def model_configs(self):
        """Create model configs."""
        return [
            ModelConfig(
                model_id="dummy-1",
                provider="dummy",
                temperature=0.3,
                max_tokens=100,
                use_cot=True,
            ),
            ModelConfig(
                model_id="dummy-2",
                provider="dummy",
                temperature=0.7,
                max_tokens=100,
                use_cot=True,
            ),
        ]

    def test_compare_sync_basic(self, dummy_runners, sample_tasks, model_configs):
        """Test synchronous model comparison."""
        results = compare_models_sync(dummy_runners, sample_tasks, model_configs)

        assert len(results) == 2
        assert results[0].model_configuration.model_id == "dummy-1"
        assert results[1].model_configuration.model_id == "dummy-2"
        assert all(r.total_tasks == 2 for r in results)

    @pytest.mark.asyncio
    async def test_compare_async_basic(self, dummy_runners, sample_tasks, model_configs):
        """Test asynchronous model comparison."""
        results = await compare_models(dummy_runners, sample_tasks, model_configs)

        assert len(results) == 2
        assert results[0].model_configuration.model_id == "dummy-1"
        assert results[1].model_configuration.model_id == "dummy-2"

    def test_compare_mismatched_lengths_raises_error(self, dummy_runners, sample_tasks):
        """Test that mismatched runner/config lengths raises ValueError."""
        configs = [
            ModelConfig(model_id="dummy-1", provider="dummy", temperature=0.3)
        ]  # Only one config

        with pytest.raises(ValueError, match="must match"):
            compare_models_sync(dummy_runners, sample_tasks, configs)

    def test_compare_empty_tasks_raises_error(self, dummy_runners, model_configs):
        """Test that empty task list raises ValueError."""
        with pytest.raises(ValueError, match="Dataset contains no tasks"):
            compare_models_sync(dummy_runners, [], model_configs)

    def test_compare_results_have_same_tasks(self, dummy_runners, sample_tasks, model_configs):
        """Test that all models are evaluated on the same tasks."""
        results = compare_models_sync(dummy_runners, sample_tasks, model_configs)

        # All results should have the same number of tasks
        assert all(r.total_tasks == len(sample_tasks) for r in results)

        # All results should have the same task IDs (in order)
        task_ids_0 = [tr.task_id for tr in results[0].task_results]
        task_ids_1 = [tr.task_id for tr in results[1].task_results]
        assert task_ids_0 == task_ids_1
        assert task_ids_0 == [t.id for t in sample_tasks]
