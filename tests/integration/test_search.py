from __future__ import annotations

from uuid import uuid4

import pytest

from apps.backend.app.database import Document, IngestionRun, get_session
from apps.backend.app.services.retrieval import retriever_service


@pytest.mark.asyncio
async def test_search_returns_ranked_documents(client) -> None:
    external_id = f"doc-{uuid4().hex[:8]}"
    with get_session() as session:
        run = IngestionRun(
            trace_id=f"run-{uuid4().hex[:12]}",
            source="integration",
            status="completed",
        )
        session.add(run)
        session.flush()

        session.add(
            Document(
                external_id=external_id,
                source_path="/tmp/contracts/sample.pdf",
                source="integration",
                checksum=uuid4().hex,
                mime_type="application/pdf",
                text_content="This master service agreement contains confidentiality clauses and discovery obligations.",
                summary="MSA excerpt covering confidentiality clauses.",
                document_type="agreement",
                privilege_risk=0.2,
                importance_score=0.8,
                metadata_json={"parties": ["Acme", "Globex"], "topics": ["confidentiality", "discovery"]},
                ingestion_run_id=run.id,
            )
        )

    retriever_service.rebuild()

    response = await client.get("/api/retrieval/search", params={"query": "confidentiality clause", "top_k": 3})
    payload = response.json()

    assert response.status_code == 200
    assert any(item["document_id"] == external_id for item in payload)
    assert payload[0]["snippet"].lower().startswith("this master service agreement")
