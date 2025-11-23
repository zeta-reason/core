/**
 * Central model registry for Zeta Reason frontend.
 *
 * This is the SINGLE SOURCE OF TRUTH for supported models and providers in the UI.
 * To add a new model, simply add a ModelInfo entry to AVAILABLE_MODELS below.
 *
 * Keep this synchronized with backend/zeta_reason/providers/registry.py
 */

export type ProviderId =
  | "openai"
  | "anthropic"
  | "google"
  | "cohere"
  | "grok"
  | "deepseek"
  | "qwen"
  | "glm"
  | "dummy"
  | "custom";

export interface ModelInfo {
  provider: ProviderId;
  modelId: string;
  displayName: string;
  family?: string;
  supportsCot: boolean;
  defaultMaxTokens?: number;
  defaultTemperature?: number;
  notes?: string;
}

/**
 * Provider metadata for UI display
 */
export interface ProviderInfo {
  id: ProviderId;
  displayName: string;
  description: string;
  implemented: boolean;
}

// ============================================================================
// CENTRAL MODEL REGISTRY
// ============================================================================
// To add a new model, simply append a ModelInfo entry below.
// Keep this list synchronized with backend/zeta_reason/providers/registry.py

export const AVAILABLE_MODELS: ModelInfo[] = [
  // ------------------------------------------------------------------------
  // OpenAI Models
  // ------------------------------------------------------------------------
  {
    provider: "openai",
    modelId: "gpt-4o-mini",
    displayName: "GPT-4o Mini",
    family: "gpt-4o",
    supportsCot: true,
    defaultMaxTokens: 1000,
    defaultTemperature: 0.7,
    notes: "Fast and cost-effective for reasoning tasks.",
  },
  {
    provider: "openai",
    modelId: "gpt-4.1-mini",
    displayName: "GPT-4.1 Mini",
    family: "gpt-4.1",
    supportsCot: true,
    defaultMaxTokens: 1000,
    defaultTemperature: 0.7,
  },
  {
    provider: "openai",
    modelId: "gpt-4.1",
    displayName: "GPT-4.1",
    family: "gpt-4.1",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
  },

  // ------------------------------------------------------------------------
  // Google Gemini Models
  // ------------------------------------------------------------------------
  {
    provider: "google",
    modelId: "gemini-1.5-flash",
    displayName: "Gemini 1.5 Flash",
    family: "gemini-1.5",
    supportsCot: true,
    defaultMaxTokens: 1000,
    defaultTemperature: 0.7,
    notes: "Good for fast CoT experiments with low latency.",
  },
  {
    provider: "google",
    modelId: "gemini-1.5-pro",
    displayName: "Gemini 1.5 Pro",
    family: "gemini-1.5",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Advanced reasoning capabilities.",
  },

  // ------------------------------------------------------------------------
  // Cohere Models
  // ------------------------------------------------------------------------
  {
    provider: "cohere",
    modelId: "command-r",
    displayName: "Command R",
    family: "command",
    supportsCot: true,
    defaultMaxTokens: 1000,
    defaultTemperature: 0.7,
  },
  {
    provider: "cohere",
    modelId: "command-r-plus",
    displayName: "Command R+",
    family: "command",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Enhanced reasoning and instruction-following.",
  },

  // ------------------------------------------------------------------------
  // Grok (xAI) Models
  // ------------------------------------------------------------------------
  {
    provider: "grok",
    modelId: "grok-2-latest",
    displayName: "Grok 2 (latest)",
    family: "grok-2",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
  },

  // ------------------------------------------------------------------------
  // Anthropic Claude Models
  // ------------------------------------------------------------------------
  {
    provider: "anthropic",
    modelId: "claude-3-5-sonnet-latest",
    displayName: "Claude 3.5 Sonnet (latest)",
    family: "claude-3.5",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Anthropic's mid-tier reasoning model with excellent CoT capabilities.",
  },
  {
    provider: "anthropic",
    modelId: "claude-3-5-haiku-latest",
    displayName: "Claude 3.5 Haiku (latest)",
    family: "claude-3.5",
    supportsCot: true,
    defaultMaxTokens: 1000,
    defaultTemperature: 0.7,
    notes: "Fast and cost-effective Claude model.",
  },
  {
    provider: "anthropic",
    modelId: "claude-3-opus-latest",
    displayName: "Claude 3 Opus (latest)",
    family: "claude-3",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Anthropic's most capable reasoning model.",
  },

  // ------------------------------------------------------------------------
  // DeepSeek Models (OpenAI-compatible API)
  // ------------------------------------------------------------------------
  {
    provider: "deepseek",
    modelId: "deepseek-chat",
    displayName: "DeepSeek Chat",
    family: "deepseek",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Uses OpenAI-compatible API at https://api.deepseek.com",
  },
  {
    provider: "deepseek",
    modelId: "deepseek-reasoner",
    displayName: "DeepSeek Reasoner",
    family: "deepseek",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "DeepSeek's reasoning-optimized model.",
  },

  // ------------------------------------------------------------------------
  // Qwen (Alibaba) Models
  // ------------------------------------------------------------------------
  {
    provider: "qwen",
    modelId: "qwen-plus",
    displayName: "Qwen Plus",
    family: "qwen",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "OpenAI-compatible API via Qwen platform.",
  },
  {
    provider: "qwen",
    modelId: "qwen-max",
    displayName: "Qwen Max",
    family: "qwen",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Qwen's most capable model.",
  },
  {
    provider: "qwen",
    modelId: "qwen-turbo",
    displayName: "Qwen Turbo",
    family: "qwen",
    supportsCot: true,
    defaultMaxTokens: 1000,
    defaultTemperature: 0.7,
    notes: "Fast and efficient Qwen model.",
  },

  // ------------------------------------------------------------------------
  // GLM (ZhipuAI) Models
  // ------------------------------------------------------------------------
  {
    provider: "glm",
    modelId: "glm-4",
    displayName: "GLM-4",
    family: "glm-4",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Reasoning-focused model from ZhipuAI.",
  },
  {
    provider: "glm",
    modelId: "glm-4-plus",
    displayName: "GLM-4 Plus",
    family: "glm-4",
    supportsCot: true,
    defaultMaxTokens: 2000,
    defaultTemperature: 0.7,
    notes: "Enhanced version of GLM-4.",
  },
];

/**
 * Provider information for UI display
 */
export const PROVIDER_INFO: Record<ProviderId, ProviderInfo> = {
  openai: {
    id: "openai",
    displayName: "OpenAI",
    description: "GPT-4 and GPT-3.5 models",
    implemented: true,
  },
  anthropic: {
    id: "anthropic",
    displayName: "Anthropic (Claude)",
    description: "Claude 3 and 3.5 models",
    implemented: false, // Stub implementation
  },
  google: {
    id: "google",
    displayName: "Google (Gemini)",
    description: "Gemini 1.5 models",
    implemented: false, // Stub implementation
  },
  cohere: {
    id: "cohere",
    displayName: "Cohere",
    description: "Command R models",
    implemented: false, // Stub implementation
  },
  grok: {
    id: "grok",
    displayName: "Grok (xAI)",
    description: "Grok 2 models",
    implemented: false, // Stub implementation
  },
  deepseek: {
    id: "deepseek",
    displayName: "DeepSeek",
    description: "DeepSeek Chat and Reasoner models",
    implemented: true,
  },
  qwen: {
    id: "qwen",
    displayName: "Qwen (Alibaba)",
    description: "Qwen Plus, Max, and Turbo models",
    implemented: true,
  },
  glm: {
    id: "glm",
    displayName: "GLM (ZhipuAI)",
    description: "GLM-4 and GLM-4-Plus models",
    implemented: true,
  },
  dummy: {
    id: "dummy",
    displayName: "Dummy (Testing)",
    description: "Dummy provider for testing",
    implemented: true,
  },
  custom: {
    id: "custom",
    displayName: "Custom",
    description: "Custom provider",
    implemented: false,
  },
};

// ============================================================================
// Registry Query Functions
// ============================================================================

/**
 * Get list of all providers that have at least one model registered
 */
export function listProviders(): ProviderId[] {
  const providers = new Set(AVAILABLE_MODELS.map((m) => m.provider));
  return Array.from(providers).sort((a, b) => a.localeCompare(b));
}

/**
 * List all models, optionally filtered by provider
 */
export function listModels(provider: ProviderId | null = null): ModelInfo[] {
  if (!provider) {
    return AVAILABLE_MODELS;
  }
  return AVAILABLE_MODELS.filter((m) => m.provider === provider);
}

/**
 * Get metadata for a specific model
 */
export function getModelInfo(
  provider: ProviderId,
  modelId: string
): ModelInfo | undefined {
  return AVAILABLE_MODELS.find(
    (m) => m.provider === provider && m.modelId === modelId
  );
}

/**
 * Get provider information
 */
export function getProviderInfo(provider: ProviderId): ProviderInfo {
  return PROVIDER_INFO[provider] || PROVIDER_INFO.custom;
}

/**
 * Check if a provider is implemented
 */
export function isProviderImplemented(provider: ProviderId): boolean {
  return PROVIDER_INFO[provider]?.implemented || false;
}
