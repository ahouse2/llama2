# Pipeline Deep-Dive

## Ingestion Flow
1. Ingest documents through Prefect deployment hooks.
2. Persist structured entities into the knowledge graph service.
3. Index semantic embeddings via the hybrid TF-IDF + vector pipeline.

## Retrieval Flow
1. Accept natural language queries from the frontend console.
2. Evaluate retrieval strategies: lexical search, graph traversal, or hybrid scoring.
3. Aggregate results with provenance metadata and deliver to the conversation agent.

## Governance
- Scheduled benchmarks validate recall/precision thresholds.
- Artifact lifecycle automation rotates embedding checkpoints and graph snapshots.
