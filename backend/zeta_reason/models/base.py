"""Base abstract class for model runners."""

from abc import ABC, abstractmethod
from typing import Optional

from zeta_reason.schemas import ModelOutput


class BaseModelRunner(ABC):
    """
    Abstract base class for running inference on language models.

    Each concrete implementation (e.g., OpenAIModelRunner) should:
    1. Handle API authentication and configuration
    2. Format prompts appropriately for the model
    3. Parse responses and extract answers + CoT
    4. Return a standardized ModelOutput
    """

    def __init__(
        self,
        model_id: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_cot: bool = True,
    ):
        """
        Initialize the model runner.

        Args:
            model_id: Model identifier (e.g., 'gpt-4o-mini')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_cot: Whether to use chain-of-thought prompting
        """
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_cot = use_cot

    @abstractmethod
    def generate(self, prompt: str) -> ModelOutput:
        """
        Generate a response for the given prompt.

        Args:
            prompt: Input prompt/question

        Returns:
            ModelOutput with answer, CoT text, and optional confidence
        """
        pass

    def format_prompt(self, task_input: str) -> str:
        """
        Format the input task as a prompt for the model.

        Can be overridden by subclasses for model-specific formatting.

        Args:
            task_input: Raw task input/question

        Returns:
            Formatted prompt string
        """
        if self.use_cot:
            return (
                f"{task_input}\n\n"
                "Let's approach this step-by-step:\n"
                "1) First, let me understand the problem\n"
                "2) Then, I'll work through the solution\n"
                "3) Finally, I'll provide the answer\n\n"
                "Please show your reasoning and end with 'Answer: [your answer]'"
            )
        else:
            return task_input

    def extract_answer(self, response_text: str) -> str:
        """
        Extract the final answer from the model's response.

        Default implementation looks for "Answer: " prefix.
        Can be overridden for model-specific parsing.

        Args:
            response_text: Full response from the model

        Returns:
            Extracted answer string
        """
        # Simple heuristic: look for "Answer:" prefix
        if "Answer:" in response_text:
            answer_part = response_text.split("Answer:")[-1].strip()
            # Take first line after "Answer:"
            return answer_part.split("\n")[0].strip()

        # Fallback: return last non-empty line
        lines = [line.strip() for line in response_text.strip().split("\n") if line.strip()]
        return lines[-1] if lines else response_text.strip()
