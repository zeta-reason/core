/**
 * API client for communicating with the Zeta Reason backend
 */

import type {
  CompareRequest,
  CompareResponse,
  EvaluateRequest,
  EvaluateResponse,
} from '../types/api';

// Backend API base URL (configurable via environment variable)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  method: 'GET' | 'POST',
  body?: unknown
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Backend returns ErrorResponse with 'error' and optional 'details' fields
      const errorMessage =
        errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unknown error occurred');
  }
}

/**
 * Evaluate a single model on a dataset
 */
export async function evaluate(request: EvaluateRequest): Promise<EvaluateResponse> {
  return apiRequest<EvaluateResponse>('/evaluate', 'POST', request);
}

/**
 * Compare multiple models on the same dataset
 */
export async function compare(request: CompareRequest): Promise<CompareResponse> {
  return apiRequest<CompareResponse>('/compare', 'POST', request);
}

/**
 * Health check endpoint
 */
export async function healthCheck(): Promise<{ status: string; version: string }> {
  return apiRequest<{ status: string; version: string }>('/health', 'GET');
}
