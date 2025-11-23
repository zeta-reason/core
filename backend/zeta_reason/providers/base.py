"""
Abstract base class for LLM providers.

All provider implementations must inherit from LLMProvider and implement
the generate() method to return a ProviderResponse.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, Field

from .registry import ModelInfo


class ProviderResponse(BaseModel):
    """
    Standardized response from any LLM provider.

    This is the common interface that all providers must return,
    allowing the evaluator to work with any provider uniformly.
    """
    answer: str = Field(
        description="The model's final answer (e.g., 'A', 'B', 'C', 'D')"
    )
    cot_text: Optional[str] = Field(
        default=None,
        description="Chain-of-thought reasoning text, if use_cot=True"
    )
    raw_response: str = Field(
        description="Raw response from the provider API for debugging"
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score if available (0.0 to 1.0)"
    )
    prompt_tokens: Optional[int] = Field(
        default=None,
        description="Number of tokens in the prompt"
    )
    completion_tokens: Optional[int] = Field(
        default=None,
        description="Number of tokens in the completion"
    )
    total_tokens: Optional[int] = Field(
        default=None,
        description="Total tokens used (prompt + completion)"
    )


class LLMProvider(ABC):
    """
    Abstract base class for LLM provider implementations.

    Each provider (OpenAI, Google, Cohere, etc.) must implement this interface
    to be compatible with the Zeta Reason evaluation pipeline.
    """

    @abstractmethod
    async def generate(
        self,
        model_info: ModelInfo,
        prompt: str,
        *,
        use_cot: bool,
        max_tokens: int,
        temperature: float,
        api_key: str,
    ) -> ProviderResponse:
        """
        Generate a response from the LLM.

        Args:
            model_info: Metadata about the model being called
            prompt: The prompt to send to the model
            use_cot: Whether to use chain-of-thought prompting
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0+)
            api_key: API key for authentication

        Returns:
            ProviderResponse with answer, CoT text (if requested), and metadata

        Raises:
            Exception: If the API call fails or returns invalid data
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
