from __future__ import annotations

import asyncpg

from discursiva_infra.settings import get_settings


async def get_pool() -> asyncpg.Pool:
    """Cria e retorna um pool de conexões com o Postgres, configurado conforme as variáveis de ambiente."""
    settings = get_settings()
    return await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=settings.database_pool_min_size,
        max_size=settings.database_pool_max_size,
    )


async def close_pool(pool: asyncpg.Pool) -> None:
    """Fecha um pool de conexões com o Postgres."""
    await pool.close()
