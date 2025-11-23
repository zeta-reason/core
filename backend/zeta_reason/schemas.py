"""Pydantic schemas for API requests/responses and internal data structures."""

from typing import Any, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Dataset & Task Schemas
# ============================================================================


class Task(BaseModel):
    """A single evaluation task with input prompt and expected target."""

    id: str = Field(..., description="Unique task identifier")
    input: str = Field(..., description="Input prompt/question for the model")
    target: str = Field(..., description="Expected correct answer")


# ============================================================================
# Model Configuration
# ============================================================================


class ModelConfig(BaseModel):
    """Configuration for a model to evaluate."""

    model_id: str = Field(..., description="Model identifier (e.g., 'gpt-4o-mini')")
    provider: str = Field(default="openai", description="Model provider (e.g., 'openai', 'dummy')")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    max_tokens: int = Field(default=1000, description="Maximum tokens to generate")
    use_cot: bool = Field(
        default=True, description="Whether to use chain-of-thought prompting"
    )
    shots: int = Field(
        default=1,
        description="Number of samples per task (for self-consistency). Currently fixed at 1 for v1.0.",
    )
    api_key: Optional[str] = Field(
        default=None, description="API key for the provider (optional, falls back to environment variable)"
    )


# ============================================================================
# Model Output
# ============================================================================


class ModelOutput(BaseModel):
    """Output from a single model inference."""

    answer: str = Field(..., description="Final extracted answer")
    cot_text: Optional[str] = Field(
        default=None,
        description="Full chain-of-thought reasoning text (may be absent if CoT disabled)",
    )
    confidence: Optional[float] = Field(
        default=None, description="Model's confidence score (0-1) if available"
    )
    raw_response: Optional[str] = Field(
        default=None, description="Raw response from the model API"
    )
    prompt_tokens: Optional[int] = Field(
        default=None, description="Prompt token count from provider usage if available"
    )
    completion_tokens: Optional[int] = Field(
        default=None, description="Completion token count from provider usage if available"
    )
    total_tokens: Optional[int] = Field(
        default=None, description="Total token count from provider usage if available"
    )


# ============================================================================
# Evaluation Results
# ============================================================================


class TaskResult(BaseModel):
    """Result for a single task evaluation."""

    task_id: str = Field(..., description="Task identifier")
    input: str = Field(..., description="Input prompt")
    target: str = Field(..., description="Expected answer")
    model_output: ModelOutput = Field(..., description="Model's output")
    correct: bool = Field(..., description="Whether the answer was correct")

    # Calibration fields
    prob_correct: Optional[float] = Field(default=None, description="Model's probability of being correct (if available); used for Brier/ECE")

    # CoT shape/process fields
    cot_tokens: Optional[int] = Field(default=None, description="Token count of the CoT text")
    cot_chars: Optional[int] = Field(default=None, description="Character count of the CoT text")
    step_count: Optional[int] = Field(default=None, description="Number of step-like lines in the CoT")
    ra_ratio: Optional[float] = Field(default=None, description="Reasoning-to-answer token ratio")
    self_correcting: Optional[bool] = Field(default=None, description="Whether CoT appears to contain a self-correction")

    # Efficiency fields
    prompt_tokens: Optional[int] = Field(default=None, description="Prompt tokens from API usage, if available")
    completion_tokens: Optional[int] = Field(default=None, description="Completion tokens from API usage, if available")
    total_tokens: Optional[int] = Field(default=None, description="Total tokens (prompt + completion), if available")
    latency_ms: Optional[float] = Field(default=None, description="Latency in milliseconds for this request")


class MetricsSummary(BaseModel):
    """Summary of all computed metrics."""

    # Answer-level metrics
    accuracy: float = Field(..., description="Proportion of correct answers (0-1)")
    brier: Optional[float] = Field(default=None, description="Brier score; may be None if prob_correct unavailable")
    ece: Optional[float] = Field(default=None, description="Expected Calibration Error; may be None if prob_correct unavailable")
    sce: Optional[float] = Field(default=None, description="Self-consistency entropy v0 over answer distribution")
    usr: Optional[float] = Field(default=None, description="Unsupported Step Rate v0 (1 if wrong, 0 if right)")

    # CoT shape metrics
    cot_tokens_mean: Optional[float] = Field(default=None, description="Mean number of tokens in the chain-of-thought")
    cot_chars_mean: Optional[float] = Field(default=None, description="Mean number of characters in the chain-of-thought")
    step_count_mean: Optional[float] = Field(default=None, description="Mean number of step-like lines in the chain-of-thought")
    ra_ratio_mean: Optional[float] = Field(default=None, description="Mean reasoning-to-answer token ratio")
    self_correction_rate: Optional[float] = Field(default=None, description="Fraction of CoTs containing self-correction markers")

    # Efficiency metrics
    prompt_tokens_mean: Optional[float] = Field(default=None, description="Mean prompt tokens per task from API usage")
    completion_tokens_mean: Optional[float] = Field(default=None, description="Mean completion tokens per task from API usage")
    total_tokens_mean: Optional[float] = Field(default=None, description="Mean total tokens per task from API usage")
    latency_mean_ms: Optional[float] = Field(default=None, description="Mean latency (ms) per task")
    latency_p95_ms: Optional[float] = Field(default=None, description="95th percentile latency (ms) per task")

    @property
    def brier_score(self) -> Optional[float]:
        """Alias for backward compatibility."""
        return self.brier

    @property
    def self_consistency_entropy(self) -> Optional[float]:
        """Alias for backward compatibility."""
        return self.sce

    @property
    def expected_calibration_error(self) -> Optional[float]:
        """Alias for backward compatibility."""
        return self.ece

    @property
    def unsupported_step_rate(self) -> Optional[float]:
        """Alias for backward compatibility."""
        return self.usr


class EvaluationResult(BaseModel):
    """Complete evaluation result for a single model."""

    model_configuration: ModelConfig = Field(..., description="Configuration of evaluated model")
    metrics: MetricsSummary = Field(..., description="Computed metrics summary")
    task_results: list[TaskResult] = Field(
        ..., description="Per-task detailed results"
    )
    total_tasks: int = Field(..., description="Total number of tasks evaluated")


# ============================================================================
# API Request/Response Schemas
# ============================================================================


class EvaluateRequest(BaseModel):
    """Request to evaluate a single model on a dataset."""

    model_configuration: ModelConfig = Field(..., description="Model configuration")
    tasks: list[Task] = Field(..., description="List of tasks to evaluate")
    run_id: Optional[str] = Field(default=None, description="Optional client-supplied run ID for progress tracking")


class EvaluateResponse(BaseModel):
    """Response from single model evaluation."""

    result: EvaluationResult = Field(..., description="Evaluation result")
    run_id: Optional[str] = Field(default=None, description="Progress tracking run ID (if progress tracking enabled)")


class CompareRequest(BaseModel):
    """Request to compare multiple models on the same dataset."""

    model_configurations: list[ModelConfig] = Field(
        ..., description="List of model configurations to compare"
    )
    tasks: list[Task] = Field(..., description="List of tasks to evaluate")
    run_id: Optional[str] = Field(default=None, description="Optional client-supplied run ID for progress tracking")


class CompareResponse(BaseModel):
    """Response from multi-model comparison."""

    results: list[EvaluationResult] = Field(
        ..., description="Evaluation results for each model"
    )
    run_id: Optional[str] = Field(default=None, description="Progress tracking run ID (if progress tracking enabled)")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="Service health status")
    version: str = Field(default="0.1.0", description="API version")


class ErrorResponse(BaseModel):
    """Error response for API failures."""

    error: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Additional error context and details"
    )
