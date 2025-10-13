"""Pytest helpers providing asyncio support without external plugins."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers documented for async execution."""

    config.addinivalue_line(
        "markers",
        "asyncio: execute the test within an asyncio event loop using an in-repo runner.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> Any:
    """Execute coroutine tests marked with @pytest.mark.asyncio via a local event loop."""

    if inspect.iscoroutinefunction(pyfuncitem.obj) and pyfuncitem.get_closest_marker("asyncio"):
        argnames = getattr(pyfuncitem._fixtureinfo, "argnames", ())
        call_kwargs = {name: pyfuncitem.funcargs[name] for name in argnames}
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(pyfuncitem.obj(**call_kwargs))
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            asyncio.set_event_loop(None)
        return True
    return None
