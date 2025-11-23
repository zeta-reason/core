"""Tests for error handling in the API."""

import pytest
from fastapi.testclient import TestClient

from zeta_reason.main import app
from zeta_reason.schemas import Task, ModelConfig
from zeta_reason.exceptions import ProviderError
from zeta_reason.models.base import BaseModelRunner, ModelOutput


class FailingModelRunner(BaseModelRunner):
    """Model runner that always fails for testing error handling."""

    def __init__(self, error_type: str = "generic", **kwargs):
        super().__init__(**kwargs)
        self.error_type = error_type

    def generate(self, prompt: str) -> ModelOutput:
        """Generate a response (always fails)."""
        if self.error_type == "provider":
            raise ProviderError(
                message="Test provider error",
                provider="test",
                status_code=502,
                error_code="test_error"
            )
        elif self.error_type == "value":
            raise ValueError("Test validation error")
        else:
            raise Exception("Test generic error")

    def format_prompt(self, task_input: str) -> str:
        """Format prompt (pass through)."""
        return task_input


class TestErrorHandling:
    """Tests for API error handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks."""
        return [
            {"id": "task1", "input": "What is 2+2?", "target": "4"},
            {"id": "task2", "input": "What is 3+3?", "target": "6"},
        ]

    def test_evaluate_empty_tasks(self, client):
        """Test evaluation with empty task list returns 400."""
        response = client.post(
            "/evaluate",
            json={
                "model_configuration": {
                    "model_id": "test-model",
                    "provider": "dummy",
                    "temperature": 0.7,
                    "max_tokens": 100,
                    "use_cot": True,
                },
                "tasks": [],  # Empty tasks
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Dataset contains no tasks" in data["error"]
        assert data["details"]["field"] == "tasks"

    def test_evaluate_unsupported_provider(self, client, sample_tasks):
        """Test evaluation with unsupported provider returns 400."""
        response = client.post(
            "/evaluate",
            json={
                "model_configuration": {
                    "model_id": "test-model",
                    "provider": "unsupported_provider",
                    "temperature": 0.7,
                    "max_tokens": 100,
                    "use_cot": True,
                },
                "tasks": sample_tasks,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Unsupported provider" in data["error"]
        assert data["details"]["provider"] == "unsupported_provider"
        assert "supported_providers" in data["details"]

    def test_evaluate_missing_openai_key(self, client, sample_tasks, monkeypatch):
        """Test evaluation with OpenAI but missing API key returns 400."""
        # Remove OPENAI_API_KEY from environment
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        response = client.post(
            "/evaluate",
            json={
                "model_configuration": {
                    "model_id": "gpt-4o-mini",
                    "provider": "openai",
                    "temperature": 0.7,
                    "max_tokens": 100,
                    "use_cot": True,
                },
                "tasks": sample_tasks,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "API key" in data["error"] or "OPENAI_API_KEY" in data["error"]

    def test_compare_empty_tasks(self, client):
        """Test comparison with empty task list returns 400."""
        response = client.post(
            "/compare",
            json={
                "model_configurations": [
                    {
                        "model_id": "test-model-1",
                        "provider": "dummy",
                        "temperature": 0.7,
                        "max_tokens": 100,
                        "use_cot": True,
                    },
                ],
                "tasks": [],  # Empty tasks
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Dataset contains no tasks" in data["error"]

    def test_compare_no_models(self, client, sample_tasks):
        """Test comparison with no models returns 400."""
        response = client.post(
            "/compare",
            json={
                "model_configurations": [],  # No models
                "tasks": sample_tasks,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "No models specified" in data["error"]

    def test_compare_unsupported_provider(self, client, sample_tasks):
        """Test comparison with unsupported provider returns 400."""
        response = client.post(
            "/compare",
            json={
                "model_configurations": [
                    {
                        "model_id": "test-model",
                        "provider": "unsupported_provider",
                        "temperature": 0.7,
                        "max_tokens": 100,
                        "use_cot": True,
                    },
                ],
                "tasks": sample_tasks,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Unsupported provider" in data["error"]
        assert data["details"]["provider"] == "unsupported_provider"
        assert data["details"]["model_index"] == 0

    def test_error_response_structure(self, client):
        """Test that error responses have the correct structure."""
        response = client.post(
            "/evaluate",
            json={
                "model_configuration": {
                    "model_id": "test-model",
                    "provider": "invalid",
                    "temperature": 0.7,
                    "max_tokens": 100,
                    "use_cot": True,
                },
                "tasks": [{"id": "t1", "input": "test", "target": "test"}],
            },
        )

        assert response.status_code == 400
        data = response.json()

        # Verify ErrorResponse structure
        assert "error" in data
        assert isinstance(data["error"], str)
        assert "details" in data
        assert isinstance(data["details"], dict)

    def test_evaluate_success_with_dummy(self, client, sample_tasks):
        """Test successful evaluation with dummy provider."""
        response = client.post(
            "/evaluate",
            json={
                "model_configuration": {
                    "model_id": "test-dummy",
                    "provider": "dummy",
                    "temperature": 0.7,
                    "max_tokens": 100,
                    "use_cot": True,
                },
                "tasks": sample_tasks,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "metrics" in data["result"]
        assert "task_results" in data["result"]

    def test_compare_success_with_dummy(self, client, sample_tasks):
        """Test successful comparison with dummy provider."""
        response = client.post(
            "/compare",
            json={
                "model_configurations": [
                    {
                        "model_id": "dummy-1",
                        "provider": "dummy",
                        "temperature": 0.3,
                        "max_tokens": 100,
                        "use_cot": True,
                    },
                    {
                        "model_id": "dummy-2",
                        "provider": "dummy",
                        "temperature": 0.7,
                        "max_tokens": 100,
                        "use_cot": True,
                    },
                ],
                "tasks": sample_tasks,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
