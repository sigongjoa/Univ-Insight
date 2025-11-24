"""
FastAPI application entry point for Univ-Insight.

Main server configuration and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import init_db
from src.api import routes


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="Univ-Insight API",
        description="AI-powered university research curation and career design agent",
        version="1.0.0"
    )

    # Initialize database on startup
    @app.on_event("startup")
    def startup_event():
        print("[FastAPI] Initializing database...")
        init_db()
        print("[FastAPI] Database initialized")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    def health_check():
        """Health check endpoint"""
        return {"status": "ok"}

    # Include routers
    app.include_router(routes.router, prefix="/api/v1")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    from src.core.config import settings

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
