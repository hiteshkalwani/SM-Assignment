"""
FastAPI application entry point.

This module creates and configures the FastAPI application with all routes,
middleware, and event handlers.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.observability import setup_langsmith
from app.utils.exceptions import ErrorResponse
from app.api.v1.router import api_router

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup: Initialize resources
    logger.info("Starting up...")

    # Initialize LangSmith if configured
    if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
        setup_langsmith()

    yield

    # Shutdown: Clean up resources
    logger.info("Shutting down...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Initialize FastAPI with metadata
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A production-ready API for the City Information Assistant",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add middleware for request/response logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Middleware to log all incoming requests and responses."""
        request_id = request.headers.get("X-Request-ID", "")

        # Log the request
        logger.info(
            f"Request: {request.method} {request.url} (ID: {request_id})\n"
            f"Headers: {dict(request.headers)}"
        )

        # Process the request
        response = await call_next(request)

        # Log the response
        logger.info(
            f"Response: {request.method} {request.url} -> {response.status_code} (ID: {request_id})"
        )

        return response

    # Register exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
        logger.error(f"Request validation error: {exc.errors()}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation Error",
                code="validation_error",
                details={"errors": exc.errors()},
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all uncaught exceptions."""
        logger.exception("Unhandled exception")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                code="internal_server_error",
                details={"error": str(exc)},
            ).model_dump(),
        )

    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Health check endpoint
    @app.get("/health", include_in_schema=False)
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}

    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root() -> Dict[str, Any]:
        """Root endpoint with API information."""
        return {
            "name": settings.PROJECT_NAME,
            "version": "0.1.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
