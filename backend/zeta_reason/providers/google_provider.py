"""
Google Gemini provider implementation.

Environment variables:
- GOOGLE_API_KEY: Your Google AI Studio API key

Setup instructions:
1. Get your API key from https://makersuite.google.com/app/apikey
2. Set GOOGLE_API_KEY environment variable or pass via api_key parameter
3. Install the Google Generative AI SDK:
   pip install google-generativeai

Implementation status:
- [STUB] This provider is not yet fully implemented
- To implement: Install google-generativeai and use the GenerativeModel API
- See: https://ai.google.dev/tutorials/python_quickstart

Example implementation:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_info.model_id)
    response = model.generate_content(prompt)
    return ProviderResponse(answer=..., cot_text=..., raw_response=...)
"""

import logging
import os
from typing import Optional

from .base import LLMProvider, ProviderResponse
from .registry import ModelInfo

logger = logging.getLogger(__name__)


class GoogleProvider(LLMProvider):
    """
    Google Gemini API provider.

    Supports Gemini models including gemini-1.5-flash, gemini-1.5-pro, etc.

    NOTE: This is currently a stub implementation. To use Google models:
    1. Install: pip install google-generativeai
    2. Set GOOGLE_API_KEY environment variable
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
        Generate a response using Google Gemini API.

        Args:
            model_info: Model metadata from registry
            prompt: The task/question to send to the model
            use_cot: Whether to use chain-of-thought prompting
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            api_key: Google API key

        Returns:
            ProviderResponse with answer and CoT text

        Raises:
            NotImplementedError: This provider is not yet implemented
        """
        # Get API key from parameter or environment
        effective_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not effective_api_key:
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY environment "
                "variable or configure it in the API Keys page."
            )

        # Stub guard: surface a clear, client-friendly error instead of a 500
        raise ValueError(
            f"Provider 'google' / model '{model_info.model_id}' is not implemented yet. "
            f"Choose a supported provider (e.g., openai, grok, deepseek) until this is added."
        )

        # Example implementation (commented out):
        """
        import google.generativeai as genai

        # Configure the API
        genai.configure(api_key=effective_api_key)

        # Build prompt with CoT instruction if needed
        full_prompt = self._build_prompt(prompt, use_cot)

        # Create model and generate
        model = genai.GenerativeModel(model_info.model_id)
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        )

        full_response = response.text
        answer = self._extract_final_answer(full_response)
        cot_text = full_response if use_cot else None

        return ProviderResponse(
            answer=answer,
            cot_text=cot_text,
            raw_response=full_response,
            confidence=None,
            prompt_tokens=None,  # Extract from response.usage_metadata if available
            completion_tokens=None,
            total_tokens=None,
        )
        """

    def _build_prompt(self, prompt: str, use_cot: bool) -> str:
        """Build the prompt with optional CoT instruction."""
        if use_cot:
            return (
                f"{prompt}\n\n"
                "Please show your reasoning step by step, then clearly mark "
                "the final answer on a separate line starting with 'FINAL_ANSWER:'."
            )
        else:
            return prompt

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
