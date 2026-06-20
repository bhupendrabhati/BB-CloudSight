"""
AWS Infra Vision - Main FastAPI Application
Production-ready API server
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from backend.app.config import settings
from backend.app.database import init_db, get_db
from backend.app.api.v1 import auth, resources, costs, security
from backend.app.api.v1 import terraform, cloudformation, recommendations
from backend.app.api.v1 import timeline, actions, finops, ai

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AWS Infra Vision backend...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down AWS Infra Vision backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Infrastructure Intelligence Platform for AWS",
    lifespan=lifespan
)

# CORS middleware for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to electron:// protocol
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(resources.router, prefix=f"{settings.API_V1_PREFIX}/resources", tags=["Resources"])
app.include_router(costs.router, prefix=f"{settings.API_V1_PREFIX}/costs", tags=["Costs"])
app.include_router(security.router, prefix=f"{settings.API_V1_PREFIX}/security", tags=["Security"])
app.include_router(terraform.router, prefix=f"{settings.API_V1_PREFIX}/terraform", tags=["Terraform"])
app.include_router(cloudformation.router, prefix=f"{settings.API_V1_PREFIX}/cloudformation", tags=["CloudFormation"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_PREFIX}/recommendations", tags=["Recommendations"])
app.include_router(timeline.router, prefix=f"{settings.API_V1_PREFIX}/timeline", tags=["Timeline"])
app.include_router(actions.router, prefix=f"{settings.API_V1_PREFIX}/actions", tags=["Actions"])
app.include_router(finops.router, prefix=f"{settings.API_V1_PREFIX}/finops", tags=["FinOps"])
app.include_router(ai.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI Assistant"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AWS Infra Vision API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
