"""
OpenAI provider implementation.

Environment variables:
- OPENAI_API_KEY: Your OpenAI API key (falls back to this if not passed via api_key parameter)

API Key sources (in order of precedence):
1. api_key parameter passed to generate()
2. OPENAI_API_KEY environment variable
3. Raises ValueError if neither is available
"""

import logging
import os
from typing import Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from openai.types.chat import ChatCompletion

from .base import LLMProvider, ProviderResponse
from .registry import ModelInfo
from zeta_reason.exceptions import ProviderError

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI Chat Completions API provider.

    Supports all OpenAI chat models including GPT-4o, GPT-4.1, etc.
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
        Generate a response using OpenAI Chat Completions API.

        Args:
            model_info: Model metadata from registry
            prompt: The task/question to send to the model
            use_cot: Whether to use chain-of-thought prompting
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            api_key: OpenAI API key

        Returns:
            ProviderResponse with answer and CoT text

        Raises:
            ProviderError: If the API call fails
        """
        # Get API key from parameter or environment
        effective_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not effective_api_key:
            raise ProviderError(
                message="OpenAI API key not found. Please set OPENAI_API_KEY environment variable or pass api_key parameter.",
                provider="openai",
                status_code=400,
                error_code="missing_api_key",
                details={"model": model_info.model_id},
            )

        try:
            # Initialize OpenAI client
            # Set an explicit timeout to avoid hanging requests
            client = OpenAI(api_key=effective_api_key, timeout=30.0)

            # Prepare messages for chat completion
            system_message = self._build_system_message(use_cot)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]

            # Call OpenAI API
            logger.debug(f"Calling OpenAI API with model: {model_info.model_id}")
            response: ChatCompletion = client.chat.completions.create(
                model=model_info.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract response content
            if not response.choices or len(response.choices) == 0:
                raise ProviderError(
                    message="OpenAI API returned no choices",
                    provider="openai",
                    details={"model": model_info.model_id},
                )

            full_response = response.choices[0].message.content or ""
            logger.debug(f"Received response length: {len(full_response)} chars")

            # Extract answer and CoT
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
                confidence=None,  # OpenAI doesn't provide confidence by default
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

        except AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {str(e)}")
            raise ProviderError(
                message="OpenAI authentication failed. Please check your API key.",
                provider="openai",
                status_code=401,
                error_code="authentication_error",
                details={"model": model_info.model_id},
            ) from e

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {str(e)}")
            raise ProviderError(
                message="OpenAI rate limit exceeded. Please try again later.",
                provider="openai",
                status_code=429,
                error_code="rate_limit_error",
                details={"model": model_info.model_id},
            ) from e

        except APIConnectionError as e:
            logger.error(f"OpenAI connection error: {str(e)}")
            raise ProviderError(
                message="Failed to connect to OpenAI API. Please check your network.",
                provider="openai",
                status_code=503,
                error_code="connection_error",
                details={"model": model_info.model_id},
            ) from e

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            status_code = getattr(e, 'status_code', None) or 502
            raise ProviderError(
                message=f"OpenAI API error: {str(e)}",
                provider="openai",
                status_code=status_code,
                error_code="api_error",
                details={"model": model_info.model_id},
            ) from e

        except ProviderError:
            raise

        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI API: {str(e)}")
            raise ProviderError(
                message=f"Unexpected error during OpenAI API call: {str(e)}",
                provider="openai",
                details={"model": model_info.model_id, "error_type": type(e).__name__},
            ) from e

    def _build_system_message(self, use_cot: bool) -> str:
        """Build the system message for OpenAI chat completion."""
        if use_cot:
            return (
                "You are a helpful reasoning assistant. Show your reasoning "
                "step by step, then clearly mark the final answer on a "
                "separate line starting with 'FINAL_ANSWER:'."
            )
        else:
            return (
                "You are a helpful assistant. Provide a direct answer to the question."
            )

    def _extract_final_answer(self, response_text: str) -> str:
        """
        Extract the final answer from the model's response.

        Looks for "FINAL_ANSWER:" marker, falls back to last line.
        """
        # Look for FINAL_ANSWER: marker
        if "FINAL_ANSWER:" in response_text:
            for line in response_text.split("\n"):
                if "FINAL_ANSWER:" in line:
                    answer = line.split("FINAL_ANSWER:")[-1].strip()
                    if answer:
                        return answer

        # Fallback: return last non-empty line
        lines = [line.strip() for line in response_text.strip().split("\n") if line.strip()]
        if lines:
            return lines[-1]

        # Last resort: return the whole response stripped
        return response_text.strip()
