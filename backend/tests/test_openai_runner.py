"""Tests for OpenAI model runner."""

import pytest
from unittest.mock import Mock, patch

from zeta_reason.models.openai_runner import OpenAIModelRunner
from zeta_reason.schemas import ModelOutput


class TestOpenAIModelRunner:
    """Tests for OpenAIModelRunner."""

    def test_initialization_with_api_key(self):
        """Test initialization with explicit API key."""
        runner = OpenAIModelRunner(
            model_id="gpt-4o-mini",
            api_key="test-key-123"
        )
        assert runner.model_id == "gpt-4o-mini"
        assert runner.api_key == "test-key-123"

    def test_initialization_without_api_key_raises_error(self):
        """Test initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not found"):
                OpenAIModelRunner(model_id="gpt-4o-mini")

    def test_initialization_with_env_api_key(self):
        """Test initialization reads API key from environment."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key-456'}):
            runner = OpenAIModelRunner(model_id="gpt-4o-mini")
            assert runner.api_key == "env-key-456"

    @patch('zeta_reason.models.openai_runner.OpenAI')
    def test_generate_with_final_answer_marker(self, mock_openai_class):
        """Test generate extracts answer with FINAL_ANSWER marker."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock the API response
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = (
            "Let me solve this step by step:\n"
            "1) First, I understand the problem\n"
            "2) Then I calculate: 2 + 2 = 4\n"
            "3) Therefore, the answer is 4\n\n"
            "FINAL_ANSWER: 4"
        )
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Create runner and generate
        runner = OpenAIModelRunner(model_id="gpt-4o-mini", api_key="test-key")
        result = runner.generate("What is 2 + 2?")

        # Verify result
        assert isinstance(result, ModelOutput)
        assert result.answer == "4"
        assert "FINAL_ANSWER:" in result.cot_text
        assert result.raw_response is not None

    @patch('zeta_reason.models.openai_runner.OpenAI')
    def test_generate_without_final_answer_marker(self, mock_openai_class):
        """Test generate falls back to last line without marker."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock the API response without FINAL_ANSWER marker
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = (
            "Let me solve this:\n"
            "2 + 2 = 4\n"
            "The answer is 4"
        )
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Create runner and generate
        runner = OpenAIModelRunner(model_id="gpt-4o-mini", api_key="test-key")
        result = runner.generate("What is 2 + 2?")

        # Verify result - should extract last line
        assert isinstance(result, ModelOutput)
        assert result.answer == "The answer is 4"

    @patch('zeta_reason.models.openai_runner.OpenAI')
    def test_generate_calls_api_with_correct_parameters(self, mock_openai_class):
        """Test generate calls OpenAI API with correct parameters."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock the API response
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "FINAL_ANSWER: 4"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Create runner with specific parameters
        runner = OpenAIModelRunner(
            model_id="gpt-4o",
            temperature=0.5,
            max_tokens=500,
            api_key="test-key"
        )
        runner.generate("What is 2 + 2?")

        # Verify API was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]

        assert call_kwargs['model'] == "gpt-4o"
        assert call_kwargs['temperature'] == 0.5
        assert call_kwargs['max_tokens'] == 500
        assert len(call_kwargs['messages']) == 2
        assert call_kwargs['messages'][0]['role'] == 'system'
        assert call_kwargs['messages'][1]['role'] == 'user'
        assert call_kwargs['messages'][1]['content'] == "What is 2 + 2?"

    @patch('zeta_reason.models.openai_runner.OpenAI')
    def test_generate_handles_api_error(self, mock_openai_class):
        """Test generate handles API errors gracefully."""
        from zeta_reason.exceptions import ProviderError

        # Mock the OpenAI client to raise an error
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Create runner and expect ProviderError
        runner = OpenAIModelRunner(model_id="gpt-4o-mini", api_key="test-key")

        with pytest.raises(ProviderError, match="Unexpected error during OpenAI API call"):
            runner.generate("What is 2 + 2?")

    def test_format_prompt_returns_task_input(self):
        """Test format_prompt returns the task input as-is."""
        runner = OpenAIModelRunner(
            model_id="gpt-4o-mini",
            api_key="test-key",
            use_cot=True
        )

        task_input = "What is 2 + 2?"
        formatted = runner.format_prompt(task_input)

        # For OpenAI, format_prompt should just return the input
        # since CoT is handled by the system message
        assert formatted == task_input

    def test_extract_final_answer_with_marker(self):
        """Test _extract_final_answer with FINAL_ANSWER marker."""
        runner = OpenAIModelRunner(model_id="gpt-4o-mini", api_key="test-key")

        text = "Some reasoning\nFINAL_ANSWER: 42\nExtra text"
        answer = runner._extract_final_answer(text)

        assert answer == "42"

    def test_extract_final_answer_without_marker(self):
        """Test _extract_final_answer without marker falls back to last line."""
        runner = OpenAIModelRunner(model_id="gpt-4o-mini", api_key="test-key")

        text = "Line 1\nLine 2\nLine 3 is the answer"
        answer = runner._extract_final_answer(text)

        assert answer == "Line 3 is the answer"

    def test_extract_final_answer_empty_response(self):
        """Test _extract_final_answer with empty response."""
        runner = OpenAIModelRunner(model_id="gpt-4o-mini", api_key="test-key")

        text = ""
        answer = runner._extract_final_answer(text)

        assert answer == ""
