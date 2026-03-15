from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from discursiva_infra.postgres.pool import get_pool, close_pool
from api.routers.submissions import router as submissions_router

_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pool
    _pool = await get_pool()
    yield
    if _pool is not None:
        await close_pool(_pool)


app = FastAPI(
    title       = "Discursiva API",
    description = "Micro-serviço de correção de respostas discursivas",
    version     = "1.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions_router)


@app.get("/health", tags=["infra"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
