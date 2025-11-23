"""
Multi-provider LLM abstraction for Zeta Reason.

This module provides a unified interface for evaluating reasoning tasks
across multiple LLM providers (OpenAI, Google, Cohere, Grok, etc.).
"""

from .registry import (
    ProviderId,
    ModelInfo,
    AVAILABLE_MODELS,
    list_providers,
    list_models,
    get_model_info,
    get_provider,
)
from .base import LLMProvider, ProviderResponse

__all__ = [
    "ProviderId",
    "ModelInfo",
    "AVAILABLE_MODELS",
    "list_providers",
    "list_models",
    "get_model_info",
    "get_provider",
    "LLMProvider",
    "ProviderResponse",
]
