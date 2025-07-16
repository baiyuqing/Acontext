from contextlib import asynccontextmanager
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from ..schema.pydantic.response import BasicResponse
from ..telemetry.log import LOG

router = APIRouter()


@router.get("/ping", tags=["chore"])
async def ping() -> BasicResponse:
    LOG.info("ping")
    return BasicResponse(data={"message": "pong"})
