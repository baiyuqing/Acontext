from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import uvicorn
from acontext_server.api.api_v1 import router as api_v1_router
from acontext_server.telemetry.log import LOG


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure logging on startup
    configure_logging()
    yield


def configure_logging():
    """Configure logging for FastAPI and uvicorn"""

    # Configure uvicorn's loggers to use your format
    uvicorn_access = logging.getLogger("uvicorn.access")

    # Clear existing handlers
    uvicorn_access.handlers.clear()

    uvicorn_access.name = "acontext"

    # Add your custom handler to uvicorn loggers
    custom_handler = LOG.handlers[0] if LOG.handlers else None
    if custom_handler:
        uvicorn_access.addHandler(custom_handler)

    # Set log levels
    uvicorn_access.setLevel(logging.INFO)


app = FastAPI(lifespan=lifespan)
app.include_router(api_v1_router, prefix="/api/v1")
