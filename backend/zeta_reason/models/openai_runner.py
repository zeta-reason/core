"""OpenAI model runner implementation."""

import logging
import os
from typing import Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from openai.types.chat import ChatCompletion

from zeta_reason.models.base import BaseModelRunner
from zeta_reason.schemas import ModelOutput
from zeta_reason.exceptions import ProviderError

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIModelRunner(BaseModelRunner):
    """
    Model runner for OpenAI chat completion models.

    Uses the OpenAI chat completions API to generate chain-of-thought
    reasoning and final answers.
    """

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_cot: bool = True,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the OpenAI model runner.

        Args:
            model_id: OpenAI model identifier (e.g., 'gpt-4o-mini', 'gpt-4o')
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            use_cot: Whether to use chain-of-thought prompting
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)

        Raises:
            ValueError: If API key is not provided and not found in environment
        """
        super().__init__(model_id, temperature, max_tokens, use_cot)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment "
                "variable or pass api_key parameter."
            )

        # Initialize OpenAI client with a sane timeout to avoid hanging requests
        self.client = OpenAI(api_key=self.api_key, timeout=30.0)

        logger.info(f"Initialized OpenAIModelRunner with model: {model_id}")

    def generate(self, prompt: str) -> ModelOutput:
        """
        Generate a response using OpenAI chat completions API.

        Args:
            prompt: Input prompt/question

        Returns:
            ModelOutput with answer, CoT text, and confidence

        Raises:
            ProviderError: If the API call fails with structured error info
        """
        try:
            # Prepare messages for chat completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful reasoning assistant. Show your reasoning "
                        "step by step, then clearly mark the final answer on a "
                        "separate line starting with 'FINAL_ANSWER:'."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]

            # Call OpenAI API
            logger.debug(f"Calling OpenAI API with model: {self.model_id}")
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Extract response content
            if not response.choices or len(response.choices) == 0:
                raise ProviderError(
                    message="OpenAI API returned no choices",
                    provider="openai",
                    details={"model": self.model_id},
                )

            full_response = response.choices[0].message.content or ""
            logger.debug(f"Received response length: {len(full_response)} chars")

            # Extract answer and CoT
            answer = self._extract_final_answer(full_response)
            cot_text = full_response

            # TODO: Extract confidence/probability when available
            # For now, we don't have access to token probabilities in standard API
            confidence = None

            return ModelOutput(
                answer=answer,
                cot_text=cot_text,
                confidence=confidence,
                raw_response=full_response,
            )

        except AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {str(e)}")
            raise ProviderError(
                message="OpenAI authentication failed. Please check your API key.",
                provider="openai",
                status_code=401,
                error_code="authentication_error",
                details={"model": self.model_id},
            ) from e

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {str(e)}")
            raise ProviderError(
                message="OpenAI rate limit exceeded. Please try again later.",
                provider="openai",
                status_code=429,
                error_code="rate_limit_error",
                details={"model": self.model_id},
            ) from e

        except APIConnectionError as e:
            logger.error(f"OpenAI connection error: {str(e)}")
            raise ProviderError(
                message="Failed to connect to OpenAI API. Please check your network.",
                provider="openai",
                status_code=503,
                error_code="connection_error",
                details={"model": self.model_id},
            ) from e

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            # Extract status code from the error if available
            status_code = getattr(e, 'status_code', None) or 502
            raise ProviderError(
                message=f"OpenAI API error: {str(e)}",
                provider="openai",
                status_code=status_code,
                error_code="api_error",
                details={"model": self.model_id},
            ) from e

        except ProviderError:
            # Re-raise ProviderError as-is
            raise

        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI API: {str(e)}")
            raise ProviderError(
                message=f"Unexpected error during OpenAI API call: {str(e)}",
                provider="openai",
                details={"model": self.model_id, "error_type": type(e).__name__},
            ) from e

    def _extract_final_answer(self, response_text: str) -> str:
        """
        Extract the final answer from the model's response.

        Looks for "FINAL_ANSWER:" marker, falls back to last line.

        Args:
            response_text: Full response from the model

        Returns:
            Extracted answer string
        """
        # Look for FINAL_ANSWER: marker
        if "FINAL_ANSWER:" in response_text:
            # Find the line with FINAL_ANSWER: and extract everything after it
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

    def format_prompt(self, task_input: str) -> str:
        """
        Format the input task as a prompt for OpenAI.

        For OpenAI, we rely on the system message to guide CoT,
        so we just pass the task input directly.

        Args:
            task_input: Raw task input/question

        Returns:
            Formatted prompt string (just the task input)
        """
        # For OpenAI, the system message handles CoT instruction,
        # so we just return the task input as-is
        return task_input
