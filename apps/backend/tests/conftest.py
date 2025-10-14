"""Pytest helpers providing asyncio support without external plugins."""

from __future__ import annotations

import asyncio
import inspect
import os
import sys
from importlib import reload
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


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


@pytest.fixture(scope="module", autouse=True)
def configure_environment(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Provision isolated filesystem and database state for backend tests."""

    base = tmp_path_factory.mktemp("phase2")
    os.environ["DISCOVERY_DATABASE_URL"] = f"sqlite+aiosqlite:///{(base / 'state.db').as_posix()}"
    os.environ["DISCOVERY_STORAGE_DIRECTORY"] = str(base / "uploads")
    os.environ["DISCOVERY_GRAPH_PATH"] = str(base / "graph.gpickle")
    os.environ["DISCOVERY_RETRIEVER_INDEX_PATH"] = str(base / "index")
    os.environ["DISCOVERY_TIMELINE_EXPORT_PATH"] = str(base / "timeline.csv")
    os.environ["DISCOVERY_AGENT_CONFIG_PATH"] = str(base / "agents.yaml")

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

    import app.config as config

    reload(config)
    config.settings.ensure_directories()

    import app.database as database

    reload(database)
    database.init_db()

    import app.services.storage as storage

    reload(storage)

    import app.services.parser as parser

    reload(parser)

    import app.services.classifier as classifier

    reload(classifier)

    import app.services.retrieval as retrieval

    reload(retrieval)
    retrieval.retriever_service.rebuild()

    import app.services.timeline as timeline

    reload(timeline)

    import app.services.agents as agents

    reload(agents)

    import app.services.ingestion as ingestion

    reload(ingestion)

    return base
