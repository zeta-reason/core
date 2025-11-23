/**
 * Utility functions for managing API keys stored in localStorage
 */

interface APIKeyConfig {
  provider: string;
  displayName: string;
  key: string;
  masked: boolean;
}

/**
 * Get all stored API keys from localStorage
 */
export function getStoredAPIKeys(): Record<string, APIKeyConfig> {
  const stored = localStorage.getItem('zeta_api_keys');
  if (!stored) return {};

  try {
    return JSON.parse(stored);
  } catch (e) {
    console.error('Failed to parse stored API keys:', e);
    return {};
  }
}

/**
 * Get API key for a specific provider
 */
export function getAPIKeyForProvider(provider: string): string | undefined {
  const keys = getStoredAPIKeys();
  return keys[provider]?.key;
}

/**
 * Check if an API key is configured for a provider
 */
export function hasAPIKey(provider: string): boolean {
  const key = getAPIKeyForProvider(provider);
  return !!key && key.trim().length > 0;
}
