"""
Central model registry for Zeta Reason.

This is the SINGLE SOURCE OF TRUTH for supported models and providers.
To add a new model, simply add a ModelInfo entry to AVAILABLE_MODELS below.

Environment variables expected:
- OPENAI_API_KEY: For OpenAI models (optional if passed via x-api-key header)
- ANTHROPIC_API_KEY: For Anthropic Claude models
- GOOGLE_API_KEY: For Google Gemini models
- COHERE_API_KEY: For Cohere models
- XAI_API_KEY: For Grok (xAI) models
- DEEPSEEK_API_KEY: For DeepSeek models
- QWEN_API_KEY: For Qwen (Alibaba) models
- GLM_API_KEY: For GLM (ZhipuAI) models
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class ProviderId(str, Enum):
    """Supported LLM provider identifiers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    GROK = "grok"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    GLM = "glm"
    CUSTOM = "custom"


@dataclass
class ModelInfo:
    """
    Metadata for a supported model.

    Attributes:
        provider: Which LLM provider hosts this model
        model_id: Provider-specific model identifier (e.g., "gpt-4o-mini")
        display_name: Human-readable name for UI display
        family: Optional model family grouping (e.g., "gpt-4o")
        supports_cot: Whether this model supports chain-of-thought prompting
        default_max_tokens: Default max tokens for completion
        default_temperature: Default temperature for sampling
        notes: Optional notes about model capabilities or use cases
    """
    provider: ProviderId
    model_id: str
    display_name: str
    family: Optional[str] = None
    supports_cot: bool = True
    default_max_tokens: Optional[int] = None
    default_temperature: Optional[float] = 0.7
    notes: Optional[str] = None


# ============================================================================
# CENTRAL MODEL REGISTRY
# ============================================================================
# To add a new model, simply append a ModelInfo entry below.
# Keep this list synchronized with frontend/src/config/modelRegistry.ts

AVAILABLE_MODELS: List[ModelInfo] = [
    # ------------------------------------------------------------------------
    # OpenAI Models
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.OPENAI,
        model_id="gpt-4o-mini",
        display_name="GPT-4o Mini",
        family="gpt-4o",
        supports_cot=True,
        default_max_tokens=1000,
        notes="Fast and cost-effective for reasoning tasks.",
    ),
    ModelInfo(
        provider=ProviderId.OPENAI,
        model_id="gpt-4.1-mini",
        display_name="GPT-4.1 Mini",
        family="gpt-4.1",
        supports_cot=True,
        default_max_tokens=1000,
    ),
    ModelInfo(
        provider=ProviderId.OPENAI,
        model_id="gpt-4.1",
        display_name="GPT-4.1",
        family="gpt-4.1",
        supports_cot=True,
        default_max_tokens=2000,
    ),

    # ------------------------------------------------------------------------
    # Google Gemini Models
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.GOOGLE,
        model_id="gemini-1.5-flash",
        display_name="Gemini 1.5 Flash",
        family="gemini-1.5",
        supports_cot=True,
        default_max_tokens=1000,
        notes="Good for fast CoT experiments with low latency.",
    ),
    ModelInfo(
        provider=ProviderId.GOOGLE,
        model_id="gemini-1.5-pro",
        display_name="Gemini 1.5 Pro",
        family="gemini-1.5",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Advanced reasoning capabilities.",
    ),

    # ------------------------------------------------------------------------
    # Cohere Models
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.COHERE,
        model_id="command-r",
        display_name="Command R",
        family="command",
        supports_cot=True,
        default_max_tokens=1000,
    ),
    ModelInfo(
        provider=ProviderId.COHERE,
        model_id="command-r-plus",
        display_name="Command R+",
        family="command",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Enhanced reasoning and instruction-following.",
    ),

    # ------------------------------------------------------------------------
    # Grok (xAI) Models
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.GROK,
        model_id="grok-2-latest",
        display_name="Grok 2 (latest)",
        family="grok-2",
        supports_cot=True,
        default_max_tokens=2000,
    ),

    # ------------------------------------------------------------------------
    # Anthropic Claude Models
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.ANTHROPIC,
        model_id="claude-3-5-sonnet-latest",
        display_name="Claude 3.5 Sonnet (latest)",
        family="claude-3.5",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Anthropic's mid-tier reasoning model with excellent CoT capabilities.",
    ),
    ModelInfo(
        provider=ProviderId.ANTHROPIC,
        model_id="claude-3-5-haiku-latest",
        display_name="Claude 3.5 Haiku (latest)",
        family="claude-3.5",
        supports_cot=True,
        default_max_tokens=1000,
        notes="Fast and cost-effective Claude model.",
    ),
    ModelInfo(
        provider=ProviderId.ANTHROPIC,
        model_id="claude-3-opus-latest",
        display_name="Claude 3 Opus (latest)",
        family="claude-3",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Anthropic's most capable reasoning model.",
    ),

    # ------------------------------------------------------------------------
    # DeepSeek Models (OpenAI-compatible API)
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.DEEPSEEK,
        model_id="deepseek-chat",
        display_name="DeepSeek Chat",
        family="deepseek",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Uses OpenAI-compatible API at https://api.deepseek.com",
    ),
    ModelInfo(
        provider=ProviderId.DEEPSEEK,
        model_id="deepseek-reasoner",
        display_name="DeepSeek Reasoner",
        family="deepseek",
        supports_cot=True,
        default_max_tokens=2000,
        notes="DeepSeek's reasoning-optimized model.",
    ),

    # ------------------------------------------------------------------------
    # Qwen (Alibaba) Models
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.QWEN,
        model_id="qwen-plus",
        display_name="Qwen Plus",
        family="qwen",
        supports_cot=True,
        default_max_tokens=2000,
        notes="OpenAI-compatible API via Qwen platform.",
    ),
    ModelInfo(
        provider=ProviderId.QWEN,
        model_id="qwen-max",
        display_name="Qwen Max",
        family="qwen",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Qwen's most capable model.",
    ),
    ModelInfo(
        provider=ProviderId.QWEN,
        model_id="qwen-turbo",
        display_name="Qwen Turbo",
        family="qwen",
        supports_cot=True,
        default_max_tokens=1000,
        notes="Fast and efficient Qwen model.",
    ),

    # ------------------------------------------------------------------------
    # GLM (ZhipuAI) Models
    # ------------------------------------------------------------------------
    ModelInfo(
        provider=ProviderId.GLM,
        model_id="glm-4",
        display_name="GLM-4",
        family="glm-4",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Reasoning-focused model from ZhipuAI.",
    ),
    ModelInfo(
        provider=ProviderId.GLM,
        model_id="glm-4-plus",
        display_name="GLM-4 Plus",
        family="glm-4",
        supports_cot=True,
        default_max_tokens=2000,
        notes="Enhanced version of GLM-4.",
    ),
]


# ============================================================================
# Registry Query Functions
# ============================================================================

def list_providers() -> List[ProviderId]:
    """Get list of all providers that have at least one model registered."""
    return sorted(set(m.provider for m in AVAILABLE_MODELS), key=lambda p: p.value)


def list_models(provider: Optional[ProviderId] = None) -> List[ModelInfo]:
    """
    List all models, optionally filtered by provider.

    Args:
        provider: If specified, only return models from this provider

    Returns:
        List of ModelInfo objects
    """
    if provider is None:
        return AVAILABLE_MODELS
    return [m for m in AVAILABLE_MODELS if m.provider == provider]


def get_model_info(provider: str, model_id: str) -> ModelInfo:
    """
    Look up metadata for a specific model.

    Args:
        provider: Provider identifier (e.g., "openai")
        model_id: Model identifier (e.g., "gpt-4o-mini")

    Returns:
        ModelInfo for the requested model

    Raises:
        ValueError: If the model is not found in the registry
    """
    for m in AVAILABLE_MODELS:
        if m.provider.value == provider and m.model_id == model_id:
            return m
    raise ValueError(
        f"Unknown model: provider={provider}, model_id={model_id}. "
        f"Add it to AVAILABLE_MODELS in providers/registry.py"
    )


# ============================================================================
# Provider Factory
# ============================================================================

def get_provider(provider: ProviderId) -> "LLMProvider":
    """
    Get provider implementation for the given provider ID.

    Args:
        provider: Provider identifier

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider is not supported
    """
    # Import here to avoid circular dependencies
    from .openai_provider import OpenAIProvider
    from .anthropic_provider import AnthropicProvider
    from .google_provider import GoogleProvider
    from .cohere_provider import CohereProvider
    from .grok_provider import GrokProvider
    from .deepseek_provider import DeepSeekProvider
    from .qwen_provider import QwenProvider
    from .glm_provider import GLMProvider

    if provider == ProviderId.OPENAI:
        return OpenAIProvider()
    if provider == ProviderId.ANTHROPIC:
        return AnthropicProvider()
    if provider == ProviderId.GOOGLE:
        return GoogleProvider()
    if provider == ProviderId.COHERE:
        return CohereProvider()
    if provider == ProviderId.GROK:
        return GrokProvider()
    if provider == ProviderId.DEEPSEEK:
        return DeepSeekProvider()
    if provider == ProviderId.QWEN:
        return QwenProvider()
    if provider == ProviderId.GLM:
        return GLMProvider()

    raise ValueError(
        f"Unsupported provider: {provider}. "
        f"Implement it in providers/{provider.value}_provider.py"
    )
