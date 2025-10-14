import asyncio
import os
import sys
from importlib import reload
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


@pytest.fixture(scope="module", autouse=True)
def configure_environment(tmp_path_factory):
    base = tmp_path_factory.mktemp("phase2")
    os.environ["DISCOVERY_DATABASE_URL"] = f"sqlite+aiosqlite:///{(base / 'state.db').as_posix()}"
    os.environ["DISCOVERY_STORAGE_DIRECTORY"] = str(base / "uploads")
    os.environ["DISCOVERY_GRAPH_PATH"] = str(base / "graph.gpickle")
    os.environ["DISCOVERY_RETRIEVER_INDEX_PATH"] = str(base / "index")
    os.environ["DISCOVERY_TIMELINE_EXPORT_PATH"] = str(base / "timeline.csv")
    os.environ["DISCOVERY_AGENT_CONFIG_PATH"] = str(base / "agents.yaml")

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

    yield base


@pytest.mark.asyncio
async def test_ingest_and_retrieve(configure_environment):
    from app.database import Document, get_session
    from app.services import ingestion
    from app.services.retrieval import retriever_service

    base_dir = Path(configure_environment)
    document_path = base_dir / "uploads" / "contract.txt"
    document_path.parent.mkdir(parents=True, exist_ok=True)
    document_path.write_text(
        "On January 5, 2023, Alice Corp entered into a Master Services Agreement with Bob Industries for $1,200,000.",
        encoding="utf-8",
    )

    external_ids = await ingestion.ingest_paths([document_path])
    assert len(external_ids) == 1
    external_id = external_ids[0]

    with get_session() as session:
        document = session.query(Document).filter_by(external_id=external_id).one()
        assert document.document_type == "contract"
        assert "2023-01-05" in document.metadata_json.get("dates", [])

    retriever_service.rebuild()
    results = retriever_service.search("January 5 contract", top_k=1)
    assert results
    assert results[0].document_id == external_id


def test_agent_delegation(configure_environment):
    from app.services.agents import agent_orchestrator

    responses = agent_orchestrator.delegate("Summarize contract obligations", trace_id="test-trace")
    assert responses
    assert responses[0].message
