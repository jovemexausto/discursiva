from __future__ import annotations

import asyncpg

from discursiva_infra.settings import settings


async def get_pool() -> asyncpg.Pool:
    """
    Cria um pool por invocação Lambda.

    asyncio.run() destrói o event loop ao final de cada chamada, invalidando
    qualquer pool criado em loops anteriores. A solução correta para Lambda é
    criar um pool leve (max_size=1) por invocação e fechá-lo no finally do
    handler — o overhead é desprezível com uma única conexão.

    Em produção com RDS Proxy o padrão é o mesmo: uma conexão por Lambda
    container, o Proxy gerencia o multiplexing upstream.
    """
    return await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=1,
        max_size=1,
    )


async def close_pool(pool: asyncpg.Pool) -> None:
    await pool.close()
