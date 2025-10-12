"""Gap analysis generator highlighting unmet TRD requirements with severity scores."""


from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableSequence, Sequence

TRACEABILITY_DEFAULT = Path("reports/due_diligence/traceability_matrix.json")
GAP_JSON_DEFAULT = Path("reports/due_diligence/gap_analysis.json")
GAP_MARKDOWN_DEFAULT = Path("reports/due_diligence/gap_analysis.md")

DOMAIN_BASE_WEIGHTS: Mapping[str, int] = {
    "ARCH": 6,
    "DATA": 8,
    "AGENT": 8,
    "UX": 5,
    "OPS": 7,
    "BIZ": 4,
    "INNOV": 3,
}

DOMAIN_RATIONALE: Mapping[str, str] = {
    "ARCH": "Foundational platform scaffolding must exist before feature work.",
    "DATA": "Data ingestion and enrichment unlock every downstream intelligence feature.",
    "AGENT": "Agent orchestration is the core product experience promised to clients.",
    "UX": "User-facing workflows determine adoption and perception of value.",
    "OPS": "Operational maturity and compliance are prerequisites for enterprise sales.",
    "BIZ": "Monetization artifacts are needed to justify flagship pricing tiers.",
    "INNOV": "Innovation roadmap items sustain long-term differentiation.",
}

STATUS_WEIGHTS: Mapping[str, int] = {
    "missing": 3,
    "partial": 1,
    "candidate": 0,
    "full": -5,
    "not-applicable": -5,
}

KEYWORD_BOOSTS: Mapping[str, int] = {
    "service": 2,
    "pipeline": 2,
    "orchestrator": 2,
    "environment": 2,
    "security": 3,
    "compliance": 3,
    "governance": 2,
    "ingest": 3,
    "ocr": 2,
    "vision": 1,
    "classification": 2,
    "vector": 2,
    "graph": 2,
    "timeline": 2,
    "agent": 2,
    "voice": 1,
    "simulator": 1,
    "testing": 2,
    "coverage": 1,
    "observability": 2,
    "ci": 2,
    "pricing": 1,
    "marketplace": 1,
    "feedback": 1,
    "rlhf": 2,
}

DESCRIPTION_BOOSTS: Mapping[str, int] = {
    "queue": 1,
    "retry": 1,
    "audit": 2,
    "encryption": 2,
    "autoscaling": 1,
    "collaboration": 1,
    "wake": 1,
    "compliance": 2,
    "threat": 2,
    "go-to-market": 1,
    "pricing": 1,
}

SEVERITY_LABELS: Sequence[tuple[str, int]] = (
    ("critical", 10),
    ("high", 7),
    ("medium", 4),
    ("low", 0),
)

RECOMMENDATION_OVERRIDES: Mapping[str, Sequence[str]] = {
    "ARCH-READ": [
        "Author a living architecture document grounded in actual repository components and deployment targets.",
        "Backfill system diagrams capturing data flow, trust boundaries, and hosting assumptions for audit readiness.",
    ],
    "ARCH-REPO": [
        "Restructure the monorepo into `/apps/backend`, `/apps/frontend`, `/infra`, `/docs`, and `/tests` with runnable code in each segment.",
        "Introduce automated checks ensuring directory conventions stay enforced going forward.",
    ],
    "ARCH-DEVENV": [
        "Create reproducible devcontainers plus Poetry and PNPM lockfiles covering backend and frontend toolchains.",
        "Document onboarding steps so new engineers can bootstrap environments in under 30 minutes.",
    ],
    "ARCH-SECOPS": [
        "Draft an initial threat model outlining data flows, trust zones, and mitigations.",
        "Codify access control and audit logging baselines that future services must satisfy.",
    ],
    "DATA-INGEST": [
        "Implement an asynchronous ingestion orchestrator (e.g., Prefect or Celery) handling uploads, folder sync, and API triggers.",
        "Provision persistence for ingestion state plus dashboards for monitoring throughput and failures.",
    ],
    "DATA-OCR": [
        "Stand up an OCR/multimodal transcription microservice capable of processing scanned legal documents at scale.",
        "Integrate QA heuristics so low-confidence pages get flagged for manual review.",
    ],
    "DATA-PARSE": [
        "Develop LLM-assisted parsing pipelines to extract metadata, entities, and privilege risk indicators.",
        "Persist structured outputs atomically so downstream search and analytics remain consistent.",
    ],
    "DATA-EMBED": [
        "Deploy a vector store (Qdrant/Chroma) and populate it with embedded document nodes using consistent chunking.",
        "Configure hybrid retrieval combining semantic and lexical signals with persistence across restarts.",
    ],
    "DATA-GRAPH": [
        "Build graph extraction routines that produce high-confidence triples into Neo4j or an equivalent graph database.",
        "Expose APIs (Cypher/GraphQL) enabling timeline and relationship queries backed by provenance metadata.",
    ],
    "DATA-TIMELINE": [
        "Create a timeline synthesis service aligning events, citations, and contradiction detection logic.",
        "Offer exportable timeline views consumable by the frontend and reporting channels.",
    ],
    "AGENT-NET": [
        "Implement the multi-agent coordination layer with explicit role prompts and routing policies.",
        "Instrument memory and escalation pathways to guarantee accountable delegation across agents.",
    ],
    "AGENT-COCOUNSEL": [
        "Ship a voice-enabled co-counsel persona orchestrating retrieval, reasoning, and empathetic responses.",
        "Integrate microphone capture, TTS playback, and citation discipline per TRD guardrails.",
    ],
    "AGENT-DEV": [
        "Deliver a self-improving developer agent capable of drafting patches and staging diffs for approval.",
        "Automate evaluation hooks so only validated changes propagate to production branches.",
    ],
    "AGENT-EVAL": [
        "Construct an agentic evaluation harness measuring grounding, delegation accuracy, and regressions.",
        "Automate recurring evaluation runs with baselines for pass/fail gating.",
    ],
    "UX-CHAT": [
        "Build the neon-themed chat console with streaming responses and inline citation previews.",
        "Ensure accessibility (WCAG 2.2 AA) across light/dark modes and responsive breakpoints.",
    ],
    "UX-DOCS": [
        "Integrate a document viewer supporting highlights, annotation, and citation-linked navigation.",
        "Support large PDF rendering with efficient lazy loading for 100+ page filings.",
    ],
    "UX-TIMELINE": [
        "Deliver an interactive timeline UI with zoom, category filters, and evidence pop-outs.",
        "Wire the timeline to backend APIs so citations remain synchronized with underlying data.",
    ],
    "UX-VOICE": [
        "Implement microphone capture, wake-word detection, and playback controls in the client.",
        "Provide persona-selectable TTS voices aligning with trial roles (judge, opposing counsel, witness).",
    ],
    "UX-SIM": [
        "Prototype the mock courtroom simulator with animated judge/opposing/witness characters.",
        "Script procedural states (motions, objections, witness flow) and integrate AI-driven dialogues.",
    ],
    "UX-KNOWLEDGE": [
        "Curate the Trial University knowledge hub with searchable legal education content.",
        "Add adaptive learning paths and exportable references to support attorney upskilling.",
    ],
    "OPS-CI": [
        "Author CI pipelines covering lint, test, build, and artifact publication.",
        "Track provenance metadata so deployments meet enterprise traceability standards.",
    ],
    "OPS-OBS": [
        "Deploy observability stack (OpenTelemetry, Prometheus, Grafana, Loki) tracking ingestion latency and agent responsiveness.",
        "Establish alerting tied to SLOs with on-call runbooks.",
    ],
    "OPS-SEC": [
        "Implement zero-trust access controls, tenant isolation, and encryption-in-depth.",
        "Prepare SOC2/HIPAA readiness artifacts and evidence collection workflows.",
    ],
    "OPS-TEST": [
        "Stand up automated testing tiers (unit, integration, load, chaos) with defined coverage targets.",
        "Integrate test gates into CI/CD to prevent regressions from shipping.",
    ],
    "BIZ-PRICING": [
        "Model ROI demonstrating how the platform justifies $1k/mo flagship pricing.",
        "Bundle differentiators (court simulator, analytics, compliance) into coherent packaging collateral.",
    ],
    "BIZ-GTM": [
        "Produce sales demos, playbooks, and sandbox environments for anchor law firms.",
        "Capture testimonials and case studies to accelerate go-to-market execution.",
    ],
    "INNOV-RL": [
        "Design a reinforcement learning feedback loop capturing attorney feedback at citation-level granularity.",
        "Stand up guardrailed RLHF training and offline evaluation suites before deploying updates.",
    ],
    "INNOV-MARKETPLACE": [
        "Define SDK contracts and certification for third-party workflow plugins.",
        "Seed the marketplace with pilot partners and revenue-sharing agreements.",
    ],
}


@dataclass
class SeverityComponent:
    name: str
    value: int
    reason: str


@dataclass
class GapRecord:
    requirement_id: str
    title: str
    status: str
    path_titles: List[str]
    severity_label: str
    severity_score: int
    components: List[SeverityComponent] = field(default_factory=list)
    rationale: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "status": self.status,
            "path_titles": self.path_titles,
            "severity": {
                "label": self.severity_label,
                "score": self.severity_score,
                "components": [component.__dict__ for component in self.components],
            },
            "rationale": self.rationale,
            "recommended_actions": self.recommended_actions,
        }


def classify_severity(score: int) -> str:
    for label, threshold in SEVERITY_LABELS:
        if score >= threshold:
            return label
    return "low"


def tokenize(values: Iterable[str]) -> List[str]:
    tokens: List[str] = []
    for value in values:
        lower = value.lower()
        tokens.append(lower)
        tokens.extend(lower.replace("/", " ").split())
    return tokens


def compute_gap(record: Dict[str, object]) -> GapRecord:
    requirement_id = str(record["id"])
    status = str(record.get("status", "missing"))
    path_titles = list(record.get("path_titles", []))
    title = str(record.get("title", requirement_id))

    domain = requirement_id.split("-")[0]
    base_weight = DOMAIN_BASE_WEIGHTS.get(domain, 3)
    components: MutableSequence[SeverityComponent] = []
    components.append(
        SeverityComponent(
            name="domain_base",
            value=base_weight,
            reason=DOMAIN_RATIONALE.get(domain, "Domain baseline importance."),
        )
    )

    status_weight = STATUS_WEIGHTS.get(status, 0)
    components.append(
        SeverityComponent(
            name=f"status_{status}",
            value=status_weight,
            reason=f"Requirement currently marked as {status} in the traceability matrix.",
        )
    )

    keyword_tokens = tokenize(record.get("keywords", [])) + tokenize([title])
    description_tokens = tokenize([record.get("description", "")])

    matched_keywords: List[str] = []
    total_keyword_boost = 0
    for keyword, boost in KEYWORD_BOOSTS.items():
        if any(keyword in token for token in keyword_tokens):
            total_keyword_boost += boost
            matched_keywords.append(f"keyword '{keyword}' (+{boost})")

    if total_keyword_boost:
        components.append(
            SeverityComponent(
                name="keyword_signal",
                value=total_keyword_boost,
                reason="; ".join(matched_keywords),
            )
        )

    matched_description: List[str] = []
    total_description_boost = 0
    for phrase, boost in DESCRIPTION_BOOSTS.items():
        if any(phrase in token for token in description_tokens):
            total_description_boost += boost
            matched_description.append(f"descriptor '{phrase}' (+{boost})")

    if total_description_boost:
        components.append(
            SeverityComponent(
                name="description_signal",
                value=total_description_boost,
                reason="; ".join(matched_description),
            )
        )

    severity_score = sum(component.value for component in components)
    severity_label = classify_severity(severity_score)

    rationale: List[str] = [
        f"Domain baseline contributes {base_weight} points ({DOMAIN_RATIONALE.get(domain, 'Domain baseline importance.')}).",
        f"Status '{status}' contributes {status_weight} points because implementation is not complete.",
    ]
    if matched_keywords:
        rationale.append(
            "Keyword signals: " + ", ".join(matched_keywords) + f" for +{total_keyword_boost} points."
        )
    if matched_description:
        rationale.append(
            "Description signals: "
            + ", ".join(matched_description)
            + f" for +{total_description_boost} points."
        )

    recommended_actions = list(RECOMMENDATION_OVERRIDES.get(requirement_id, []))
    if not recommended_actions:
        recommended_actions = [
            "Translate requirement narrative into a concrete implementation plan with owners and milestones.",
            "Document acceptance criteria and integrate progress tracking into the roadmap.",
        ]

    return GapRecord(
        requirement_id=requirement_id,
        title=title,
        status=status,
        path_titles=path_titles,
        severity_label=severity_label,
        severity_score=severity_score,
        components=list(components),
        rationale=rationale,
        recommended_actions=recommended_actions,
    )


def generate_gap_analysis(matrix_path: Path) -> List[GapRecord]:
    data = json.loads(matrix_path.read_text())
    gaps: List[GapRecord] = []
    for requirement in data.get("requirements", []):
        if requirement.get("children"):
            continue
        status = str(requirement.get("status", "missing"))
        if status in {"full", "candidate", "not-applicable"}:
            continue
        gaps.append(compute_gap(requirement))
    gaps.sort(key=lambda gap: (-gap.severity_score, gap.requirement_id))
    return gaps


def emit_json(gaps: Sequence[GapRecord], destination: Path, source: Path) -> None:
    summary: Dict[str, object] = {
        "total_gaps": len(gaps),
        "severity_counts": {},
    }
    for gap in gaps:
        summary["severity_counts"].setdefault(gap.severity_label, 0)
        summary["severity_counts"][gap.severity_label] += 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_traceability": str(source),
        "severity_scale": [
            {"label": label, "minimum_score": threshold}
            for label, threshold in SEVERITY_LABELS
        ],
        "gaps": [gap.to_dict() for gap in gaps],
        "summary": summary,
    }
    destination.write_text(json.dumps(payload, indent=2))


def format_gap_markdown(gap: GapRecord) -> str:
    lines: List[str] = []
    lines.append(f"### {gap.requirement_id} · {gap.title}")
    lines.append(f"- **Severity**: `{gap.severity_label}` ({gap.severity_score})")
    lines.append(f"- **Status**: `{gap.status}`")
    if gap.path_titles:
        lines.append(f"- **Requirement Path**: {' › '.join(gap.path_titles)}")
    lines.append("- **Rationale**:")
    for bullet in gap.rationale:
        lines.append(f"  - {bullet}")
    lines.append("- **Recommended Actions**:")
    for action in gap.recommended_actions:
        lines.append(f"  - {action}")
    lines.append("")
    return "\n".join(lines)


def emit_markdown(gaps: Sequence[GapRecord], destination: Path, source: Path) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: List[str] = []
    lines.append("# Gap Analysis · TRD Alignment")
    lines.append("")
    lines.append(f"- Generated: {timestamp}")
    lines.append(f"- Source Traceability Matrix: `{source}`")
    lines.append("")

    if not gaps:
        lines.append("All TRD requirements are fully satisfied. 🎉")
    else:
        severity_counts: Dict[str, int] = {}
        for gap in gaps:
            severity_counts.setdefault(gap.severity_label, 0)
            severity_counts[gap.severity_label] += 1

        lines.append("## Summary")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("| --- | ---: |")
        for label, _threshold in SEVERITY_LABELS:
            count = severity_counts.get(label, 0)
            lines.append(f"| {label.title()} | {count} |")
        lines.append("")

        lines.append("## Top Critical Findings")
        lines.append("")
        critical_gaps = [gap for gap in gaps if gap.severity_label == "critical"][:5]
        if not critical_gaps:
            lines.append("- No requirements currently exceed the critical threshold.")
        else:
            for gap in critical_gaps:
                lines.append(f"- `{gap.requirement_id}` · {gap.title} (score {gap.severity_score})")
        lines.append("")

        lines.append("## Detailed Findings")
        lines.append("")
        for gap in gaps:
            lines.append(format_gap_markdown(gap))

    destination.write_text("\n".join(lines))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TRD gap analysis reports with severity scoring.")
    parser.add_argument(
        "--traceability",
        type=Path,
        default=TRACEABILITY_DEFAULT,
        help="Path to traceability_matrix.json",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=GAP_JSON_DEFAULT,
        help="Destination path for JSON output",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=GAP_MARKDOWN_DEFAULT,
        help="Destination path for Markdown summary",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    gaps = generate_gap_analysis(args.traceability)
    emit_json(gaps, args.json_output, args.traceability)
    emit_markdown(gaps, args.markdown_output, args.traceability)


if __name__ == "__main__":
    main()
