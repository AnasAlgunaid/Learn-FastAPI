from fastapi import Request
from logging_config import logger


async def log_requests(request: Request, call_next):
    logger.info(f"New request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request completed with status code: {response.status_code}")
    return response
