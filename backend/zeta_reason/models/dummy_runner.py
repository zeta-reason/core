"""Dummy model runner for testing without API calls."""

import hashlib
from zeta_reason.models.base import BaseModelRunner
from zeta_reason.schemas import ModelOutput


class DummyModelRunner(BaseModelRunner):
    """
    A deterministic dummy model for testing purposes.

    Returns scripted responses based on simple pattern matching,
    without making any actual API calls.
    """

    def __init__(
        self,
        model_id: str = "dummy-1.0",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_cot: bool = True,
    ):
        """Initialize the dummy model runner."""
        super().__init__(model_id, temperature, max_tokens, use_cot)

    def generate(self, prompt: str) -> ModelOutput:
        """
        Generate a deterministic response based on the prompt.

        Args:
            prompt: Input prompt

        Returns:
            ModelOutput with scripted answer and CoT
        """
        # Use hash for deterministic but varied responses
        prompt_hash = int(hashlib.md5(prompt.encode()).hexdigest(), 16)

        # Simple pattern matching for arithmetic
        if any(op in prompt.lower() for op in ["+", "plus", "add"]):
            answer = str((prompt_hash % 100) + 10)
            cot_text = (
                f"Let me solve this step by step:\n"
                f"1) I need to add the numbers\n"
                f"2) Performing the calculation\n"
                f"3) The result is {answer}\n\n"
                f"Answer: {answer}"
            )
        elif any(op in prompt.lower() for op in ["-", "minus", "subtract"]):
            answer = str((prompt_hash % 50) + 5)
            cot_text = (
                f"Let me solve this step by step:\n"
                f"1) I need to subtract the numbers\n"
                f"2) Performing the calculation\n"
                f"3) The result is {answer}\n\n"
                f"Answer: {answer}"
            )
        elif any(op in prompt.lower() for op in ["*", "times", "multiply"]):
            answer = str((prompt_hash % 200) + 20)
            cot_text = (
                f"Let me solve this step by step:\n"
                f"1) I need to multiply the numbers\n"
                f"2) Performing the calculation\n"
                f"3) The result is {answer}\n\n"
                f"Answer: {answer}"
            )
        elif any(op in prompt.lower() for op in ["/", "divide", "divided"]):
            answer = str((prompt_hash % 20) + 2)
            cot_text = (
                f"Let me solve this step by step:\n"
                f"1) I need to divide the numbers\n"
                f"2) Performing the calculation\n"
                f"3) The result is {answer}\n\n"
                f"Answer: {answer}"
            )
        else:
            # Generic response for non-arithmetic questions
            answer = "42"
            cot_text = (
                f"Let me think about this:\n"
                f"1) This is an interesting question\n"
                f"2) After careful consideration\n"
                f"3) The answer is 42\n\n"
                f"Answer: 42"
            )

        # Simulate confidence based on hash
        confidence = 0.5 + (prompt_hash % 50) / 100.0  # Range: 0.5 to 0.99

        return ModelOutput(
            answer=answer,
            cot_text=cot_text,
            confidence=confidence,
            raw_response=cot_text,
        )
