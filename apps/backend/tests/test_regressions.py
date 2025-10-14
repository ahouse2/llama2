"""Regression guardrails for core backend services."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path


def test_schema_models_roundtrip() -> None:
    schemas = import_module("app.schemas")

    config = schemas.AgentConfig(name="Investigator", role="analysis", tools=["retrieval"])
    response = schemas.AgentResponse(agent="Investigator", message="Ready", citations=["doc-1"], tone="neutral")
    result = schemas.SearchResult(
        document_id="doc-1",
        score=0.87,
        snippet="Important clause excerpt.",
        highlights={"clauses": ["Section 4.2"]},
        trace_id="trace-abc",
    )

    assert config.tools == ["retrieval"]
    assert response.citations == ["doc-1"]
    assert result.highlights["clauses"] == ["Section 4.2"]


def test_agent_orchestrator_delegate_with_custom_manifest(configure_environment: Path) -> None:
    agents_module = import_module("app.services.agents")

    manifest = Path(configure_environment) / "regression_agents.yaml"
    manifest.write_text(
        """
        agents:
          - name: Analyst
            role: review
            tools: [retrieval]
        """.strip(),
        encoding="utf-8",
    )

    orchestrator = agents_module.AgentOrchestrator(config_path=manifest)
    responses = orchestrator.delegate("Summarize precedent", trace_id="regression-trace")

    assert responses
    assert all(isinstance(response, agents_module.AgentResponse) for response in responses)

    flow_responses = agents_module.agent_delegation_flow(prompt="Summarize precedent", trace_id="flow-regression")
    assert flow_responses


def test_hybrid_retriever_search_returns_models(configure_environment: Path) -> None:
    database = import_module("app.database")
    retrieval = import_module("app.services.retrieval")
    schemas = import_module("app.schemas")

    with database.get_session() as session:
        run = session.query(database.IngestionRun).filter_by(trace_id="regression-trace").one_or_none()
        if run is None:
            run = database.IngestionRun(trace_id="regression-trace", source="tests", status="completed")
            session.add(run)
            session.flush()
        if (
            session.query(database.Document)
            .filter_by(external_id="doc-regression")
            .one_or_none()
            is None
        ):
            session.add(
                database.Document(
                    external_id="doc-regression",
                    source_path="/tmp/doc-regression.txt",
                    source="tests",
                    checksum="checksum",
                    mime_type="text/plain",
                    text_content="This regression document discusses hybrid retrieval validation.",
                    summary="Hybrid retrieval regression document",
                    document_type="memo",
                    privilege_risk=0.2,
                    importance_score=0.6,
                    metadata_json={"entities": ["Hybrid Retrieval"], "dates": ["2024-01-01"]},
                    ingestion_run=run,
                )
            )

    retrieval.retriever_service.rebuild()
    results = retrieval.retriever_service.search("hybrid retrieval validation", top_k=3)

    assert isinstance(retrieval.retriever_service, retrieval.HybridRetriever)
    assert all(isinstance(result, schemas.SearchResult) for result in results)
