"""Lightweight agent orchestration for retrieval-backed responses."""
"""Multi-agent orchestration inspired by Autogen."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from ..config import settings
from ..database import get_session
from .retrieval import retriever_service
from .timeline import timeline_service

POSITIVE_WORDS = {
    "great",
    "excellent",
    "helpful",
    "success",
    "progress",
    "confident",
    "win",
}
NEGATIVE_WORDS = {
    "concern",
    "issue",
    "problem",
    "delay",
    "risk",
    "uncertain",
    "worried",
}


def _sentiment_score(text: str) -> float:
    tokens = [token.lower() for token in text.split()]
    positives = sum(token in POSITIVE_WORDS for token in tokens)
    negatives = sum(token in NEGATIVE_WORDS for token in tokens)
    total = positives + negatives
    if total == 0:
        return 0.0
    return (positives - negatives) / total


def _tone_from_score(score: float) -> str:
import yaml
from nltk.sentiment import SentimentIntensityAnalyzer

from ..config import settings
from ..database import ConversationMemory, get_session
from .retrieval import retriever_service
from .timeline import timeline_service

logger = logging.getLogger(__name__)

try:  # pragma: no cover - external data download
    SentimentIntensityAnalyzer()
except LookupError:  # pragma: no cover
    import nltk

    nltk.download("vader_lexicon")


def _emotion_tone(score: float) -> str:
    if score <= -settings.sentiment_threshold:
        return "empathetic"
    if score >= settings.sentiment_threshold:
        return "confident"
    return "neutral"


@dataclass
class AgentConfig:
    name: str
    role: str
    tools: List[str]
    escalate_to: Optional[str] = None


@dataclass
class AgentResponse:
    agent: str
    message: str
    citations: List[str]
    tone: str


class Agent:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    def handle(self, trace_id: str, prompt: str) -> AgentResponse:
        message_parts: List[str] = []
        citations: List[str] = []
    """Agent capable of using configured tools."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.sentiment = SentimentIntensityAnalyzer()

    def handle(self, trace_id: str, prompt: str) -> AgentResponse:
        citations: List[str] = []
        message_parts: List[str] = []
        if "retrieval" in self.config.tools:
            results = retriever_service.search(prompt, top_k=3)
            for result in results:
                citations.append(result.document_id)
                message_parts.append(f"Result {result.document_id}: {result.snippet}")
                message_parts.append(f"Document {result.document_id}: {result.snippet[:200]}...")
        if "timeline" in self.config.tools:
            timeline = timeline_service.summarize()
            if timeline:
                message_parts.append(f"Timeline context: {json.dumps(timeline[:3])}")
        if not message_parts:
            message_parts.append("No tools executed for this prompt.")
        tone = _tone_from_score(_sentiment_score(prompt))
        message = "\n".join(message_parts)
        self._persist_memory(trace_id, prompt, message)
        return AgentResponse(agent=self.config.name, message=message, citations=citations, tone=tone)

    def _persist_memory(self, trace_id: str, prompt: str, message: str) -> None:
        with get_session() as session:
            existing = session.list_conversation_memory(trace_id)
            turn_index = len(existing)
            session.add_conversation_memory(
                trace_id=trace_id,
                agent_role=self.config.name,
                turn_index=turn_index,
                message=message,
                summary=prompt[:200],
            message_parts.append("No direct tools executed; manual reasoning required.")
        raw_message = "\n".join(message_parts)
        tone_score = self.sentiment.polarity_scores(prompt)["compound"]
        tone = _emotion_tone(tone_score)
        self._persist_memory(trace_id, prompt, raw_message)
        return AgentResponse(agent=self.config.name, message=raw_message, citations=citations, tone=tone)

    def _persist_memory(self, trace_id: str, prompt: str, message: str) -> None:
        with get_session() as session:
            turn_index = (
                session.query(ConversationMemory)
                .filter_by(trace_id=trace_id, agent_role=self.config.name)
                .count()
            )
            session.add(
                ConversationMemory(
                    trace_id=trace_id,
                    agent_role=self.config.name,
                    turn_index=turn_index,
                    message=message,
                    summary=prompt[:200],
                )
            )


class AgentOrchestrator:
    """Load agent definitions and delegate work across them."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or settings.agent_config_path
        self.agents = self._load_agents()

    def _load_agents(self) -> Dict[str, Agent]:
        if not self.config_path.exists():
            return {}
        raw = self.config_path.read_text(encoding="utf-8").strip()
        payload: Dict[str, List[Dict[str, object]]]
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"agents": []}
        agents: Dict[str, Agent] = {}
        for entry in payload.get("agents", []):
            config = AgentConfig(
                name=str(entry.get("name", "Unnamed")),
                role=str(entry.get("role", "")),
                tools=[str(tool) for tool in entry.get("tools", [])],
        payload = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
        agents: Dict[str, Agent] = {}
        for entry in payload.get("agents", []):
            config = AgentConfig(
                name=entry["name"],
                role=entry.get("role", ""),
                tools=entry.get("tools", []),
                escalate_to=entry.get("escalate_to"),
            )
            agents[config.name] = Agent(config)
        return agents

    def delegate(self, prompt: str, *, trace_id: Optional[str] = None) -> List[AgentResponse]:
        if not self.agents:
            default = AgentConfig(name="CoCounsel", role="lead", tools=["retrieval", "timeline"])
            self.agents = {default.name: Agent(default)}
            logger.info("Agent registry empty; instantiating default CoCounsel agent")
            self.agents = {
                "CoCounsel": Agent(AgentConfig(name="CoCounsel", role="lead", tools=["retrieval", "timeline"]))
            }
        trace = trace_id or f"trace-{uuid4().hex[:12]}"
        responses: List[AgentResponse] = []
        for agent in self.agents.values():
            responses.append(agent.handle(trace, prompt))
        return responses


agent_orchestrator = AgentOrchestrator()
