from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import datetime

class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Write to logs.txt
        with open("logs.txt", mode="a") as log_file:
            log_file.write(f"{request.method} {request.url} at {datetime.datetime.now()}\n")
        response = await call_next(request)
        return response