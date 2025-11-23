"""
Provider-based model runner that uses the new provider abstraction.

This adapter bridges the old BaseModelRunner interface with the new
provider system, allowing the evaluator to use multi-provider support
without changing the evaluation pipeline.
"""

import logging
from typing import Optional

from zeta_reason.models.base import BaseModelRunner
from zeta_reason.schemas import ModelOutput
from zeta_reason.providers import get_model_info, get_provider, ProviderId
from zeta_reason.exceptions import ProviderError

logger = logging.getLogger(__name__)


class ProviderModelRunner(BaseModelRunner):
    """
    Model runner that uses the provider abstraction system.

    This runner automatically selects the correct provider based on the
    provider parameter and uses the model registry for configuration.
    """

    def __init__(
        self,
        provider: str,
        model_id: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_cot: bool = True,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the provider-based model runner.

        Args:
            provider: Provider identifier (e.g., "openai", "google", "cohere", "grok")
            model_id: Model identifier (e.g., "gpt-4o-mini", "gemini-1.5-flash")
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            use_cot: Whether to use chain-of-thought prompting
            api_key: API key for the provider (if None, reads from environment)

        Raises:
            ValueError: If provider/model is not found in registry
        """
        super().__init__(model_id, temperature, max_tokens, use_cot)

        # Look up model info from registry
        try:
            self.model_info = get_model_info(provider, model_id)
        except ValueError as e:
            raise ValueError(
                f"Model not found in registry: provider={provider}, model_id={model_id}. "
                f"Add it to AVAILABLE_MODELS in backend/zeta_reason/providers/registry.py"
            ) from e

        # Get provider implementation
        try:
            self.provider = get_provider(ProviderId(provider))
        except ValueError as e:
            raise ValueError(
                f"Provider not supported: {provider}. "
                f"Check backend/zeta_reason/providers/registry.py for available providers."
            ) from e

        # Store API key
        self.api_key = api_key or ""

        logger.info(
            f"Initialized ProviderModelRunner: provider={provider}, "
            f"model={model_id}, use_cot={use_cot}"
        )

    def generate(self, prompt: str) -> ModelOutput:
        """
        Generate a response using the provider.

        Args:
            prompt: Input prompt/question

        Returns:
            ModelOutput with answer, CoT text, and confidence

        Raises:
            ProviderError: If the API call fails with structured error info
        """
        try:
            # Call provider generate (note: we need to handle async->sync here)
            import asyncio

            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're already in an async context, so we need to use a different approach
                # Create a new event loop in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.provider.generate(
                            model_info=self.model_info,
                            prompt=prompt,
                            use_cot=self.use_cot,
                            max_tokens=self.max_tokens,
                            temperature=self.temperature,
                            api_key=self.api_key,
                        )
                    )
                    provider_response = future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run directly
                provider_response = asyncio.run(
                    self.provider.generate(
                        model_info=self.model_info,
                        prompt=prompt,
                        use_cot=self.use_cot,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        api_key=self.api_key,
                    )
                )

            # Convert ProviderResponse to ModelOutput
            return ModelOutput(
                answer=provider_response.answer,
                cot_text=provider_response.cot_text,
                confidence=provider_response.confidence,
                raw_response=provider_response.raw_response,
                prompt_tokens=provider_response.prompt_tokens,
                completion_tokens=provider_response.completion_tokens,
                total_tokens=provider_response.total_tokens,
            )

        except ProviderError:
            # Re-raise ProviderError as-is
            raise

        except Exception as e:
            logger.error(f"Unexpected error in ProviderModelRunner.generate: {str(e)}")
            raise ProviderError(
                message=f"Unexpected error during model generation: {str(e)}",
                provider=self.model_info.provider.value,
                details={
                    "model": self.model_id,
                    "error_type": type(e).__name__,
                },
            ) from e

    def format_prompt(self, task_input: str) -> str:
        """
        Format the input task as a prompt for the model.

        For provider-based runners, we just pass through the task input
        as the provider handles prompt formatting internally.

        Args:
            task_input: Raw task input/question

        Returns:
            Formatted prompt string (just the task input)
        """
        # Providers handle their own prompt formatting
        return task_input
