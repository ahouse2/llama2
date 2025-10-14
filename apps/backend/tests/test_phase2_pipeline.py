import asyncio
from pathlib import Path

import pytest


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
