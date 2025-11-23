"""FastAPI application for Zeta Reason."""

import logging
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from zeta_reason import __version__
from zeta_reason.config import config
from zeta_reason.schemas import (
    CompareRequest,
    CompareResponse,
    EvaluateRequest,
    EvaluateResponse,
    HealthResponse,
    ErrorResponse,
)
from zeta_reason.models import DummyModelRunner, OpenAIModelRunner, ProviderModelRunner
from zeta_reason.evaluator import evaluate_model_on_dataset, compare_models
from zeta_reason.exceptions import ProviderError
from zeta_reason.storage import ExperimentStorage
from zeta_reason.storage.experiments import (
    ExperimentSaveRequest,
    ExperimentMetadata,
    ExperimentData,
)
from zeta_reason.progress import progress_tracker
from zeta_reason.providers.registry import list_providers

logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Zeta Reason API",
    description="Chain-of-thought reasoning benchmarking for LLMs",
    version=__version__,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize experiment storage
experiment_storage = ExperimentStorage()


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version=__version__)


@app.post("/evaluate", response_model=EvaluateResponse, responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def evaluate(request: EvaluateRequest) -> EvaluateResponse:
    """
    Evaluate a single model on a dataset.

    Args:
        request: Evaluation request with model config and tasks

    Returns:
        Evaluation results with metrics and per-task results

    Raises:
        HTTPException: With appropriate status code and ErrorResponse body
    """
    try:
        # Validate input
        if not request.tasks:
            error_response = ErrorResponse(
                error="Dataset contains no tasks",
                details={"field": "tasks"}
            )
            return JSONResponse(
                status_code=400,
                content=error_response.model_dump()
            )

        # Validate provider is supported before building runner
        supported_providers = [p.value for p in list_providers()] + ["dummy"]
        if request.model_configuration.provider not in supported_providers:
            error_response = ErrorResponse(
                error="Unsupported provider",
                details={
                    "provider": request.model_configuration.provider,
                    "supported_providers": supported_providers,
                }
            )
            return JSONResponse(status_code=400, content=error_response.model_dump())

        # Create model runner based on provider
        if request.model_configuration.provider == "dummy":
            # Keep dummy runner for testing
            runner = DummyModelRunner(
                model_id=request.model_configuration.model_id,
                temperature=request.model_configuration.temperature,
                max_tokens=request.model_configuration.max_tokens,
                use_cot=request.model_configuration.use_cot,
            )
        else:
            # Use the new provider system for all real providers (openai, google, cohere, grok)
            try:
                runner = ProviderModelRunner(
                    provider=request.model_configuration.provider,
                    model_id=request.model_configuration.model_id,
                    temperature=request.model_configuration.temperature,
                    max_tokens=request.model_configuration.max_tokens,
                    use_cot=request.model_configuration.use_cot,
                    api_key=request.model_configuration.api_key,
                )
            except ValueError as e:
                # Provider or model not found in registry, or missing API key
                error_response = ErrorResponse(
                    error=str(e),
                    details={"provider": request.model_configuration.provider}
                )
                return JSONResponse(
                    status_code=400,
                    content=error_response.model_dump()
                )

        # Create progress tracking run (use client-supplied run_id if provided)
        run_id = progress_tracker.create_run(total_tasks=len(request.tasks), run_id=request.run_id)
        logger.info(f"Created evaluation run: {run_id}")

        # Get progress callback
        progress_callback = progress_tracker.get_progress_callback(run_id)

        try:
            # Run evaluation (await the async function)
            result = await evaluate_model_on_dataset(
                model_runner=runner,
                tasks=request.tasks,
                model_config=request.model_configuration,
                progress_callback=progress_callback,
            )

            # Mark run as complete
            await progress_tracker.complete_run(run_id, "Evaluation completed successfully")

            # Schedule cleanup after 60 seconds
            asyncio.create_task(_cleanup_run_later(run_id, 60))

            return EvaluateResponse(result=result, run_id=run_id)

        except Exception as e:
            # Mark run as failed
            await progress_tracker.error_run(run_id, str(e))
            raise

    except ProviderError as e:
        # Provider-specific errors (OpenAI API errors, etc.)
        logger.error(f"Provider error during evaluation: {e.message}")
        error_dict = e.to_dict()

        # Map provider status codes to HTTP status codes
        status_code = 502
        if e.status_code is not None:
            status_code = e.status_code
        elif e.status_code == 503:
            status_code = 503
        elif e.status_code == 429:
            status_code = 429

        return JSONResponse(
            status_code=status_code,
            content=error_dict
        )

    except ValueError as e:
        # Validation errors
        logger.error(f"Validation error during evaluation: {str(e)}")
        error_response = ErrorResponse(
            error=str(e),
            details={"type": "validation_error"}
        )
        return JSONResponse(
            status_code=400,
            content=error_response.model_dump()
        )

    except HTTPException:
        # Re-raise HTTPException as-is
        raise

    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error during evaluation: {str(e)}")
        error_response = ErrorResponse(
            error="Internal server error during evaluation",
            details={"message": str(e), "type": type(e).__name__}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@app.post("/compare", response_model=CompareResponse, responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def compare(request: CompareRequest) -> CompareResponse:
    """
    Compare multiple models on the same dataset.

    Args:
        request: Comparison request with multiple model configs and tasks

    Returns:
        Comparison results with metrics for each model

    Raises:
        HTTPException: With appropriate status code and ErrorResponse body
    """
    try:
        # Validate input
        if not request.tasks:
            error_response = ErrorResponse(
                error="Dataset contains no tasks",
                details={"field": "tasks"}
            )
            return JSONResponse(
                status_code=400,
                content=error_response.model_dump()
            )

        if not request.model_configurations:
            error_response = ErrorResponse(
                error="No models specified for comparison",
                details={"field": "model_configurations"}
            )
            return JSONResponse(
                status_code=400,
                content=error_response.model_dump()
            )

        # Create model runners for each config
        runners = []
        supported_providers = [p.value for p in list_providers()] + ["dummy"]
        for i, model_config in enumerate(request.model_configurations):
            if model_config.provider not in supported_providers:
                error_response = ErrorResponse(
                    error="Unsupported provider",
                    details={
                        "provider": model_config.provider,
                        "model_index": i,
                        "supported_providers": supported_providers,
                    }
                )
                return JSONResponse(status_code=400, content=error_response.model_dump())

            if model_config.provider == "dummy":
                # Keep dummy runner for testing
                runner = DummyModelRunner(
                    model_id=model_config.model_id,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                    use_cot=model_config.use_cot,
                )
                runners.append(runner)
            else:
                # Use the new provider system for all real providers
                try:
                    runner = ProviderModelRunner(
                        provider=model_config.provider,
                        model_id=model_config.model_id,
                        temperature=model_config.temperature,
                        max_tokens=model_config.max_tokens,
                        use_cot=model_config.use_cot,
                        api_key=model_config.api_key,
                    )
                    runners.append(runner)
                except ValueError as e:
                    # Provider or model not found in registry, or missing API key
                    error_response = ErrorResponse(
                        error=str(e),
                        details={
                            "provider": model_config.provider,
                            "model_index": i,
                            "model_id": model_config.model_id
                        }
                    )
                    return JSONResponse(
                        status_code=400,
                        content=error_response.model_dump()
                    )

        # Create progress tracking run (total tasks = models * tasks per model)
        total_tasks = len(request.model_configurations) * len(request.tasks)
        run_id = progress_tracker.create_run(total_tasks=total_tasks, run_id=request.run_id)
        logger.info(f"Created comparison run: {run_id}")

        # Get progress callback
        progress_callback = progress_tracker.get_progress_callback(run_id)

        try:
            # Run comparison (await the async function)
            results = await compare_models(
                model_runners=runners,
                tasks=request.tasks,
                model_configs=request.model_configurations,
                progress_callback=progress_callback,
            )

            # Mark run as complete
            await progress_tracker.complete_run(run_id, "Comparison completed successfully")

            # Schedule cleanup after 60 seconds
            asyncio.create_task(_cleanup_run_later(run_id, 60))

            return CompareResponse(results=results, run_id=run_id)

        except Exception as e:
            # Mark run as failed
            await progress_tracker.error_run(run_id, str(e))
            raise

    except ProviderError as e:
        # Provider-specific errors (OpenAI API errors, etc.)
        logger.error(f"Provider error during comparison: {e.message}")
        error_dict = e.to_dict()

        # Map provider status codes to HTTP status codes
        status_code = 502
        if e.status_code is not None:
            status_code = e.status_code
        elif e.status_code == 503:
            status_code = 503
        elif e.status_code == 429:
            status_code = 429

        return JSONResponse(
            status_code=status_code,
            content=error_dict
        )

    except ValueError as e:
        # Validation errors
        logger.error(f"Validation error during comparison: {str(e)}")
        error_response = ErrorResponse(
            error=str(e),
            details={"type": "validation_error"}
        )
        return JSONResponse(
            status_code=400,
            content=error_response.model_dump()
        )

    except HTTPException:
        # Re-raise HTTPException as-is
        raise

    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error during comparison: {str(e)}")
        error_response = ErrorResponse(
            error="Internal server error during comparison",
            details={"message": str(e), "type": type(e).__name__}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


# ============================================================================
# Experiment History Endpoints
# ============================================================================


@app.post("/api/experiments", response_model=dict)
async def save_experiment(request: ExperimentSaveRequest) -> dict:
    """
    Save a new experiment to storage.

    Args:
        request: Experiment save request

    Returns:
        Dictionary with experiment_id

    Raises:
        HTTPException: On save failure
    """
    try:
        experiment_id = experiment_storage.save(request)
        return {"experiment_id": experiment_id}
    except Exception as e:
        logger.exception(f"Failed to save experiment: {str(e)}")
        error_response = ErrorResponse(
            error="Failed to save experiment",
            details={"message": str(e), "type": type(e).__name__}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@app.get("/api/experiments", response_model=list[ExperimentMetadata])
async def list_experiments() -> list[ExperimentMetadata]:
    """
    List all experiment metadata.

    Returns:
        List of experiment metadata, sorted by timestamp (newest first)
    """
    try:
        return experiment_storage.list_metadata()
    except Exception as e:
        logger.exception(f"Failed to list experiments: {str(e)}")
        error_response = ErrorResponse(
            error="Failed to list experiments",
            details={"message": str(e), "type": type(e).__name__}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@app.get("/api/experiments/{experiment_id}", response_model=ExperimentData)
async def get_experiment(experiment_id: str) -> ExperimentData | JSONResponse:
    """
    Get full experiment data by ID.

    Args:
        experiment_id: Experiment UUID

    Returns:
        Full experiment data

    Raises:
        HTTPException: If experiment not found or load failure
    """
    try:
        experiment_data = experiment_storage.load(experiment_id)

        if experiment_data is None:
            error_response = ErrorResponse(
                error="Experiment not found",
                details={"experiment_id": experiment_id}
            )
            return JSONResponse(
                status_code=404,
                content=error_response.model_dump()
            )

        return experiment_data

    except Exception as e:
        logger.exception(f"Failed to load experiment {experiment_id}: {str(e)}")
        error_response = ErrorResponse(
            error="Failed to load experiment",
            details={"experiment_id": experiment_id, "message": str(e), "type": type(e).__name__}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@app.delete("/api/experiments/{experiment_id}", response_model=dict)
async def delete_experiment(experiment_id: str) -> dict | JSONResponse:
    """
    Delete an experiment by ID.

    Args:
        experiment_id: Experiment UUID

    Returns:
        Success message

    Raises:
        HTTPException: If experiment not found or delete failure
    """
    try:
        success = experiment_storage.delete(experiment_id)

        if not success:
            error_response = ErrorResponse(
                error="Experiment not found",
                details={"experiment_id": experiment_id}
            )
            return JSONResponse(
                status_code=404,
                content=error_response.model_dump()
            )

        return {"success": True, "experiment_id": experiment_id}

    except Exception as e:
        logger.exception(f"Failed to delete experiment {experiment_id}: {str(e)}")
        error_response = ErrorResponse(
            error="Failed to delete experiment",
            details={"experiment_id": experiment_id, "message": str(e), "type": type(e).__name__}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@app.get("/api/experiments/stats/storage", response_model=dict)
async def get_storage_stats() -> dict:
    """
    Get experiment storage statistics.

    Returns:
        Storage stats including total experiments and disk usage
    """
    try:
        return experiment_storage.get_storage_stats()
    except Exception as e:
        logger.exception(f"Failed to get storage stats: {str(e)}")
        error_response = ErrorResponse(
            error="Failed to get storage stats",
            details={"message": str(e), "type": type(e).__name__}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


# ============================================================================
# Progress Tracking Endpoints
# ============================================================================


@app.websocket("/ws/progress")
async def progress_websocket(websocket: WebSocket, run_id: str = Query(...)):
    """
    WebSocket endpoint for real-time progress updates.

    Args:
        websocket: WebSocket connection
        run_id: Evaluation run ID to track

    Usage:
        Connect to ws://localhost:8000/ws/progress?run_id=<run_id>
        to receive progress updates for a running evaluation.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for run_id: {run_id}")

    try:
        # Register this WebSocket for progress updates
        await progress_tracker.register_websocket(run_id, websocket)

        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for client messages (ping/pong to keep alive)
                data = await websocket.receive_text()
                logger.debug(f"Received message from client: {data}")
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for run_id: {run_id}")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break

    finally:
        # Unregister WebSocket on disconnect
        await progress_tracker.unregister_websocket(run_id, websocket)


@app.get("/api/progress/{run_id}", response_model=dict)
async def get_progress(run_id: str) -> dict:
    """
    Get progress status for a run (polling fallback).

    Use this endpoint for clients that don't support WebSockets.

    Args:
        run_id: Evaluation run ID

    Returns:
        Progress update dictionary or 404 if run not found
    """
    progress = progress_tracker.get_progress(run_id)

    if progress is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Run not found", "run_id": run_id}
        )

    return progress.to_dict()


# ============================================================================
# Helper Functions
# ============================================================================


async def _cleanup_run_later(run_id: str, delay_seconds: int):
    """
    Clean up progress tracking resources after a delay.

    Args:
        run_id: Run ID to clean up
        delay_seconds: Delay in seconds before cleanup
    """
    await asyncio.sleep(delay_seconds)
    progress_tracker.cleanup_run(run_id)
    logger.info(f"Cleaned up progress tracking for run_id: {run_id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "zeta_reason.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
    )
