# simulation_engine.py (key parts only)
# Below is a condensed version of simulation_engine.py showing the key changes:
# Accept agent_clients and tool_clients in __init__.
# Detect external agent roles via external_agent.enabled and protocol.
# Use MCP for the Data Room burn vs cash graph.

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List

import yaml  # assume installed

from engine_schema import (
    EngineRequest,
    EngineEvent,
    SessionState,
    SessionRepository,
    InMemorySessionRepository,
    MeetingMessage,
    DataRoomArtifact,
)
from agent_client import (
    AgentClient,
    AgentRequestPayload,
    AgentResponsePayload,
    HttpJsonAgentClient,
    GoogleA2AAgentClient,
)
from tool_client import (
    ToolClient,
    ToolRequestPayload,
    ToolResponsePayload,
    MCPToolClient,
)


class SimulationEngine:
    """
    Manifest-driven orchestration engine, now with protocol-agnostic agent & tool adapters:

    - AgentClient: for external roles (VC external, board advisor, etc.)
    - ToolClient: for Data Room tools (MCP or others)
    """

    def __init__(
        self,
        manifest_path: str,
        session_repo: SessionRepository | None = None,
        agent_clients: Dict[str, AgentClient] | None = None,
        tool_clients: Dict[str, ToolClient] | None = None,
    ):
        self.manifest_path = manifest_path
        self.manifest: Dict[str, Any] = {}
        self.specs: Dict[str, Any] = {}
        self.session_repo: SessionRepository = session_repo or InMemorySessionRepository()

        # Protocol adapters
        # Keys correspond to `protocol` fields in specs (e.g., "google_a2a", "http_json", "mcp").
        self.agent_clients: Dict[str, AgentClient] = agent_clients or {
            "http_json": HttpJsonAgentClient(base_url="https://agent-gateway.stub"),
            "google_a2a": GoogleA2AAgentClient(service_name="vc-expert-service"),
        }
        self.tool_clients: Dict[str, ToolClient] = tool_clients or {
            "mcp": MCPToolClient(mcp_server_url="https://mcp-tool-server.stub"),
        }

        self._load_manifest_and_specs()

    # (manifest loading unchanged, but you also load vc_external_spec as a role)

    # ------------------------ Public Engine API ----------------------------

    def handle_input(self, request: EngineRequest) -> List[EngineEvent]:
        session = self._get_or_create_session(request.user_id, request.session_id)

        if request.speaker == "CEO":
            session.ceo.prompt_history.append(
                {"channel": request.channel, "message": request.message}
            )

        speaker_lower = request.speaker.lower().strip()

        if speaker_lower == "sarai":
            events = self._handle_sarai_message(session, request)
        elif speaker_lower in {"tech", "tech cofounder", "tech_cofounder"}:
            events = self._handle_role_message(session, request, role_id="tech_cofounder")
        elif speaker_lower in {"marketing", "marketing cofounder", "marketing_cofounder"}:
            events = self._handle_role_message(session, request, role_id="marketing_cofounder")
        elif speaker_lower == "advisor":
            events = self._handle_role_message(session, request, role_id="advisor")
        elif speaker_lower == "vc":
            # This could now be internal or external VC depending on spec
            events = self._handle_role_message(session, request, role_id="vc")
        elif speaker_lower == "vc_external":
            events = self._handle_role_message(session, request, role_id="vc_external")
        elif speaker_lower == "coach":
            events = self._handle_role_message(session, request, role_id="coach")
        elif speaker_lower.startswith("therapist"):
            events = self._handle_therapist_message(session, request)
        elif speaker_lower in {"data room", "dataroom"}:
            events = self._handle_dataroom_command(session, request)
        else:
            if request.channel == "meeting":
                events = self._handle_ceo_meeting_message(session, request)
            else:
                events = [EngineEvent.error("Unknown speaker or channel", speaker="Sarai")]

        self._save_session(session)
        return events

    # --------------------- Role dispatch: internal vs external -------------

    def _handle_role_message(
        self,
        session: SessionState,
        request: EngineRequest,
        role_id: str,
    ) -> List[EngineEvent]:
        role_spec = self.specs.get("roles", {}).get(role_id, {})

        ext_cfg = role_spec.get("external_agent", {})
        is_external = ext_cfg.get("enabled", False)

        if is_external:
            return self._handle_external_role_message(session, request, role_id, role_spec, ext_cfg)
        else:
            return self._handle_internal_role_message(session, request, role_id, role_spec)

    def _handle_internal_role_message(
        self,
        session: SessionState,
        request: EngineRequest,
        role_id: str,
        role_spec: Dict[str, Any],
    ) -> List[EngineEvent]:
        session.meeting.transcript.append(MeetingMessage(speaker=request.speaker, text=request.message))

        role_name = role_spec.get("identity", {}).get("name", request.speaker)
        reply = (
            f"{role_name}: (internal stub) I'd analyze your question using my role spec "
            f"and the documents I'm allowed to see."
        )
        return [
            EngineEvent.message(
                channel="meeting",
                speaker=role_name,
                text=reply,
            )
        ]

    def _handle_external_role_message(
        self,
        session: SessionState,
        request: EngineRequest,
        role_id: str,
        role_spec: Dict[str, Any],
        ext_cfg: Dict[str, Any],
    ) -> List[EngineEvent]:
        session.meeting.transcript.append(MeetingMessage(speaker=request.speaker, text=request.message))

        protocol = ext_cfg.get("protocol", "http_json")
        agent_client = self.agent_clients.get(protocol)
        if not agent_client:
            return [
                EngineEvent.error(
                    f"No AgentClient configured for protocol '{protocol}'",
                    speaker="Sarai",
                )
            ]

        # Build context (you'd implement rich context; here it's stubbed)
        context = {
            "financial_summary": {"runway_months": 6},  # stub
            "scene_id": session.active_scene_id,
        }

        agent_req = AgentRequestPayload(
            agent_id=role_spec.get("identity", {}).get("id", role_id),
            role_id=role_id,
            scene_id=session.active_scene_id,
            user_id=session.user_id,
            session_id=session.session_id,
            question=request.message,
            context=context,
        )

        agent_res: AgentResponsePayload = agent_client.call(agent_req)

        # Safety filtering would go here (omitted for brevity)
        role_name = role_spec.get("identity", {}).get("name", request.speaker)
        safe_text = agent_res.advisor_text

        return [
            EngineEvent.message(
                channel="meeting",
                speaker=role_name,
                text=safe_text,
            )
        ]

    # --------------------- Data Room MCP example ---------------------------

    def _handle_dataroom_command(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        lower = request.message.lower()

        if "burn vs cash" in lower and "graph" in lower:
            return self._create_burn_vs_cash_graph(session)
        # More commands here...
        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="data_room",
                type="data_room.update",
                speaker="Sarai",
                payload={"text": "(stub) Data Room command not recognized."},
            )
        ]

    def _create_burn_vs_cash_graph(self, session: SessionState) -> List[EngineEvent]:
        """
        Example: use MCPToolClient to generate artifact data for the graph.
        """
        tool_client = self.tool_clients.get("mcp")
        if tool_client:
            tool_req = ToolRequestPayload(
                tool_id="burn_vs_cash_graph_tool",
                user_id=session.user_id,
                session_id=session.session_id,
                scene_id=session.active_scene_id,
                context={
                    "financial_model": {
                        "runway_months": 6,  # stub
                        "burn_per_month": 45000,
                        "cash_balance": 270000,
                    }
                },
            )
            tool_res: ToolResponsePayload = tool_client.call(tool_req)
            artifact_data = tool_res.artifact_data
        else:
            # fallback: static stub
            artifact_data = {
                "type": "graph",
                "title": "Burn vs Cash Over Time (local stub)",
                "data": {
                    "x": "month",
                    "y": ["burn", "cash_balance"],
                },
            }

        artifact_id = str(uuid.uuid4())
        artifact = DataRoomArtifact(
            id=artifact_id,
            type=artifact_data["type"],
            title=artifact_data["title"],
            data=artifact_data.get("data", {}),
        )
        session.dataroom.artifacts[artifact_id] = artifact
        session.dataroom.focus_artifact_id = artifact_id

        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="data_room",
                type="data_room.update",
                speaker="Sarai",
                payload={
                    "action": "create_or_update_artifact",
                    "artifact": {
                        "id": artifact.id,
                        "type": artifact.type,
                        "title": artifact.title,
                        "data": artifact.data,
                    },
                    "focus_artifact_id": artifact_id,
                },
            ),
            EngineEvent.message(
                channel="sarai_panel",
                speaker="Sarai",
                text="I’ve created a burn vs cash graph artifact in the Data Room (via MCP stub).",
            ),
        ]
