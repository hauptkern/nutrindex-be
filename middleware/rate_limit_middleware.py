from collections import defaultdict
from typing import Dict, List
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, rpm: int = 10) -> None:
        super().__init__(app)
        self.rpm = rpm
        self.rate_limit_records: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host
        current_time = time.time()

        self.rate_limit_records[client_ip] = [
            timestamp for timestamp in self.rate_limit_records[client_ip]
            if current_time - timestamp < 60
        ]

        if len(self.rate_limit_records[client_ip]) >= self.rpm:
            return Response(content="Rate limit exceeded", status_code=429)

        self.rate_limit_records[client_ip].append(current_time)
        return await call_next(request)
