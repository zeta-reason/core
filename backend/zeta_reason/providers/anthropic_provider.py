"""
Anthropic Claude provider implementation.

Environment variables:
- ANTHROPIC_API_KEY: Your Anthropic API key

Setup instructions:
1. Get your API key from https://console.anthropic.com/
2. Set ANTHROPIC_API_KEY environment variable or pass via api_key parameter
3. Install the Anthropic SDK:
   pip install anthropic

Implementation status:
- [STUB] This provider is not yet fully implemented
- To implement: Install anthropic SDK and use the Messages API
- See: https://docs.anthropic.com/claude/reference/messages_post

Example implementation:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model_info.model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return ProviderResponse(answer=..., cot_text=..., raw_response=...)
"""

import logging
import os
from typing import Optional

from .base import LLMProvider, ProviderResponse
from .registry import ModelInfo

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude API provider.

    Supports Claude 3 and Claude 3.5 models including Opus, Sonnet, and Haiku.

    NOTE: This is currently a stub implementation. To use Claude models:
    1. Install: pip install anthropic
    2. Set ANTHROPIC_API_KEY environment variable
    3. Implement the generate() method below
    """

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
        Generate a response using Anthropic Claude API.

        Args:
            model_info: Model metadata from registry
            prompt: The task/question to send to the model
            use_cot: Whether to use chain-of-thought prompting
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            api_key: Anthropic API key

        Returns:
            ProviderResponse with answer and CoT text

        Raises:
            NotImplementedError: This provider is not yet implemented
        """
        # Get API key from parameter or environment
        effective_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not effective_api_key:
            raise ValueError(
                "Anthropic API key not found. Please set ANTHROPIC_API_KEY environment "
                "variable or configure it in the API Keys page."
            )

        # Stub guard: surface a clear, client-friendly error instead of a 500
        raise ValueError(
            f"Provider 'anthropic' / model '{model_info.model_id}' is not implemented yet. "
            f"Choose a supported provider (e.g., openai, grok, deepseek) until this is added."
        )

        # Example implementation (commented out):
        """
        import anthropic

        # Initialize client
        client = anthropic.Anthropic(api_key=effective_api_key)

        # Build system message for CoT if needed
        system_message = self._build_system_message(use_cot) if use_cot else None

        # Create message
        message = client.messages.create(
            model=model_info.model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract response
        full_response = message.content[0].text if message.content else ""
        answer = self._extract_final_answer(full_response)
        cot_text = full_response if use_cot else None

        # Extract token usage
        usage = message.usage
        prompt_tokens = usage.input_tokens if usage else None
        completion_tokens = usage.output_tokens if usage else None
        total_tokens = (prompt_tokens + completion_tokens) if (prompt_tokens and completion_tokens) else None

        return ProviderResponse(
            answer=answer,
            cot_text=cot_text,
            raw_response=full_response,
            confidence=None,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )
        """

    def _build_system_message(self, use_cot: bool) -> str:
        """Build the system message for Claude."""
        if use_cot:
            return (
                "You are a helpful reasoning assistant. Show your reasoning "
                "step by step, then clearly mark the final answer on a "
                "separate line starting with 'FINAL_ANSWER:'."
            )
        else:
            return "You are a helpful assistant. Provide a direct answer to the question."

    def _extract_final_answer(self, response_text: str) -> str:
        """Extract the final answer from the model's response."""
        if "FINAL_ANSWER:" in response_text:
            for line in response_text.split("\n"):
                if "FINAL_ANSWER:" in line:
                    answer = line.split("FINAL_ANSWER:")[-1].strip()
                    if answer:
                        return answer

        lines = [line.strip() for line in response_text.strip().split("\n") if line.strip()]
        if lines:
            return lines[-1]

        return response_text.strip()
