"""Agent orchestration endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ...schemas import AgentMessage
from ...services.agents import agent_orchestrator

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/delegate", response_model=List[AgentMessage])
async def delegate_agent(message: AgentMessage) -> List[AgentMessage]:
    if not message.message.strip():
        raise HTTPException(status_code=400, detail="Message must not be empty")
    responses = agent_orchestrator.delegate(message.message, trace_id=message.trace_id)
    return [
        AgentMessage(trace_id=message.trace_id, role=response.agent, message=response.message, summary=response.tone)
        for response in responses
    ]
