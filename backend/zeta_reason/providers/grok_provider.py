"""
Grok (xAI) provider implementation.

Environment variables:
- XAI_API_KEY: Your xAI API key

Setup instructions:
1. Get your API key from https://x.ai/api
2. Set XAI_API_KEY environment variable or pass via api_key parameter
3. xAI's API is OpenAI-compatible, so we can use the OpenAI SDK:
   pip install openai

Implementation status:
- [STUB] This provider is not yet fully implemented
- To implement: Use OpenAI SDK with xAI base URL
- See: https://docs.x.ai/api

Example implementation:
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )
    response = client.chat.completions.create(...)
    return ProviderResponse(answer=..., cot_text=..., raw_response=...)
"""

import logging
import os
from typing import Optional

from .base import LLMProvider, ProviderResponse
from .registry import ModelInfo

logger = logging.getLogger(__name__)


class GrokProvider(LLMProvider):
    """
    Grok (xAI) API provider.

    Supports Grok models from xAI. The API is OpenAI-compatible.

    NOTE: This is currently a stub implementation. To use Grok models:
    1. Install: pip install openai
    2. Set XAI_API_KEY environment variable
    3. Implement the generate() method below using OpenAI SDK with xAI base URL
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
        Generate a response using Grok API (xAI).

        Args:
            model_info: Model metadata from registry
            prompt: The task/question to send to the model
            use_cot: Whether to use chain-of-thought prompting
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            api_key: xAI API key

        Returns:
            ProviderResponse with answer and CoT text

        Raises:
            ValueError: If API key is missing
            ProviderError: If the API call fails
        """
        # Get API key from parameter or environment
        effective_api_key = api_key or os.getenv("XAI_API_KEY")
        if not effective_api_key:
            raise ValueError(
                "xAI API key not found. Please set XAI_API_KEY environment "
                "variable or configure it in the API Keys page."
            )

        try:
            from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
            from zeta_reason.exceptions import ProviderError

            # Initialize xAI client (OpenAI-compatible)
            client = OpenAI(
                api_key=effective_api_key,
                base_url="https://api.x.ai/v1"
            )

            # Build system message
            system_message = self._build_system_message(use_cot)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]

            # Call xAI API
            logger.debug(f"Calling xAI (Grok) API with model: {model_info.model_id}")
            response = client.chat.completions.create(
                model=model_info.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract response content
            if not response.choices or len(response.choices) == 0:
                raise ProviderError(
                    message="Grok API returned no choices",
                    provider="grok",
                    details={"model": model_info.model_id},
                )

            full_response = response.choices[0].message.content or ""
            logger.debug(f"Received response length: {len(full_response)} chars")

            answer = self._extract_final_answer(full_response)
            cot_text = full_response if use_cot else None

            # Extract token usage
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else None
            completion_tokens = usage.completion_tokens if usage else None
            total_tokens = usage.total_tokens if usage else None

            return ProviderResponse(
                answer=answer,
                cot_text=cot_text,
                raw_response=full_response,
                confidence=None,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

        except AuthenticationError as e:
            logger.error(f"Grok authentication error: {str(e)}")
            raise ProviderError(
                message="Grok authentication failed. Please check your API key.",
                provider="grok",
                status_code=401,
                error_code="authentication_error",
                details={"model": model_info.model_id},
            ) from e

        except RateLimitError as e:
            logger.error(f"Grok rate limit error: {str(e)}")
            raise ProviderError(
                message="Grok rate limit exceeded. Please try again later.",
                provider="grok",
                status_code=429,
                error_code="rate_limit_error",
                details={"model": model_info.model_id},
            ) from e

        except APIConnectionError as e:
            logger.error(f"Grok connection error: {str(e)}")
            raise ProviderError(
                message="Failed to connect to Grok API. Please check your network.",
                provider="grok",
                status_code=503,
                error_code="connection_error",
                details={"model": model_info.model_id},
            ) from e

        except APIError as e:
            logger.error(f"Grok API error: {str(e)}")
            status_code = getattr(e, 'status_code', None) or 502
            raise ProviderError(
                message=f"Grok API error: {str(e)}",
                provider="grok",
                status_code=status_code,
                error_code="api_error",
                details={"model": model_info.model_id},
            ) from e

        except ProviderError:
            raise

        except Exception as e:
            logger.error(f"Unexpected error calling Grok API: {str(e)}")
            raise ProviderError(
                message=f"Unexpected error during Grok API call: {str(e)}",
                provider="grok",
                details={"model": model_info.model_id, "error_type": type(e).__name__},
            ) from e

    def _build_system_message(self, use_cot: bool) -> str:
        """Build the system message for Grok chat completion."""
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
