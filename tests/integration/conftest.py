import asyncio
from collections.abc import AsyncIterator

import pytest
from httpx import AsyncClient

from apps.backend.app.main import create_app


@pytest.fixture(scope="session")
def event_loop() -> AsyncIterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    async with AsyncClient(app=app, base_url="http://testserver") as async_client:
        yield async_client
