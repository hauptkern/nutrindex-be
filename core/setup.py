from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import Any
import anyio
import fastapi
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from middleware.exceptions_middleware import ExceptionsMiddleware
from middleware.rate_limit_middleware import RateLimitMiddleware
from .exceptions.handler import validation_exception_handler
from .config import (
    AppSettings,
    RateLimitSettings,
    EnvironmentOption,
    EnvironmentSettings,
    settings,
)


async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = number_of_tokens


def lifespan_factory(
        settings: (
                AppSettings
                | RateLimitSettings
                | EnvironmentSettings
        ),
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        await set_threadpool_tokens()
        yield
    return lifespan


# -------------- application --------------
def create_application(
        router: APIRouter,
        settings: (
                AppSettings
                | RateLimitSettings
                | EnvironmentSettings
        ),
        **kwargs: Any,
) -> FastAPI:
    if isinstance(settings, AppSettings):
        to_update = {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
            "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
            "license_info": {"name": settings.LICENSE_NAME},
        }
        kwargs.update(to_update)

    if isinstance(settings, EnvironmentSettings):
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    lifespan = lifespan_factory(settings)

    application = FastAPI(lifespan=lifespan, **kwargs)

    application.include_router(router)

    application.add_middleware(ExceptionsMiddleware)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    if isinstance(settings, RateLimitSettings):
        application.add_middleware(RateLimitMiddleware, rpm=settings.DEFAULT_RATE_LIMIT)

    if isinstance(settings, EnvironmentSettings):
        if settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
            docs_router = APIRouter()

            @docs_router.get("/docs", include_in_schema=False)
            async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
                return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/redoc", include_in_schema=False)
            async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
                return get_redoc_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/openapi.json", include_in_schema=False)
            async def openapi() -> dict[str, Any]:
                out: dict = get_openapi(title=application.title, version=application.version, routes=application.routes)
                return out

            application.include_router(docs_router)

        return application
