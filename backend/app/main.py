"""FastAPI ASGI entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback

from .api.routes import router
from .api.context_routes import router as context_router
from .api.thread_routes import router as thread_router
from .api.analytics_routes import router as analytics_router
from .api.recipient_routes import router as recipient_router
from .storage import storage

app = FastAPI(
    title="SHIFT HAPPENS — AI-ассистент для корпоративной переписки",
    version="0.1.0",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(router)
app.include_router(context_router)
app.include_router(thread_router)
app.include_router(analytics_router)
app.include_router(recipient_router)


@app.on_event("startup")
async def startup_event():
    """Initialize in-memory storage on startup."""
    print(f"Storage initialized with {len(storage.contexts)} contexts, {len(storage.threads)} threads, {len(storage.messages)} messages")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions and add CORS headers."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": "SHIFT HAPPENS — AI-ассистент для корпоративной переписки", "status": "ok", "docs": "/api/docs"}


@app.get("/favicon.ico", tags=["meta"])
async def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

