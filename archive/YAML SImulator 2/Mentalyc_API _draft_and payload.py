"""
mental yc_engine.py

Concrete engine API + simple test harness for the Mentalyc Pivot-CEO Simulator.

This file is designed to work with the manifest-driven content package we defined:
- simulation_manifest.yaml
- specs/*.yaml (ceo_role.yaml, scene_what_now.yaml, sarai_spec.yaml, etc.)

High-level API
--------------

The UI (or any client) should interact with the engine via a single method:

    SimulationEngine.handle_input(request: EngineRequest) -> List[EngineEvent]

Where EngineRequest is:

    {
        "session_id": str,
        "channel": "meeting" | "data_room" | "sarai_panel",
        "speaker": str,    # "CEO", "Sarai", "tech", "advisor", "VC", "coach", etc.
        "message": str
    }

The engine responds with a list of EngineEvent objects, each of which has:

    {
        "id": str,         # event UUID
        "channel": str,    # "meeting" | "data_room" | "sarai_panel"
        "type": str,       # "message" | "data_room.update" | "sarai_panel.observation" | ...
        "speaker": str,    # who is "saying" this (CEO, Sarai, role)
        "payload": dict    # structured data, minimally {"text": "..."} for messages
    }
dDROP rop this next to the mentalyc_sim_package_v3/ folder, update the manifest_path if needed, and run it with python mentalyc_engine.py, you’ll have:

A concrete API surface (handle_input),

Events that are shaped exactly how your UI can consume them,

And clear TODOs where the real YAML-driven logic and LLM calls will plug in.

This file includes:

- Data models (dataclasses).
- A SimulationEngine skeleton with:
    - Manifest loading hooks.
    - Session management.
    - Simple command / intent routing based on the Sarai spec idea.
- A test harness that simulates a short interaction.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

try:
    import yaml  # pyyaml; make sure to install in your environment
except ImportError:
    yaml = None


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class EngineRequest:
    """Single input from the UI / client."""
    session_id: str
    channel: str  # "meeting" | "data_room" | "sarai_panel"
    speaker: str  # "CEO", "Sarai", "tech", "advisor", "VC", "coach", etc.
    message: str


@dataclass
class EngineEvent:
    """Single event produced by the engine."""
    id: str
    channel: str  # "meeting" | "data_room" | "sarai_panel"
    type: str     # "message" | "data_room.update" | "sarai_panel.observation" | "error"
    speaker: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeetingState:
    participants: List[str] = field(default_factory=lambda: ["CEO"])
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    last_decision: Optional[str] = None
    prompt_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DataRoomState:
    artifacts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    focus_artifact_id: Optional[str] = None


@dataclass
class CEOState:
    prompt_history: List[Dict[str, Any]] = field(default_factory=list)
    unlocked_documents: List[str] = field(default_factory=list)
    commitments: List[str] = field(default_factory=list)


@dataclass
class SessionState:
    session_id: str
    active_scene_id: str = "what_now_30_day_challenge"
    meeting: MeetingState = field(default_factory=MeetingState)
    dataroom: DataRoomState = field(default_factory=DataRoomState)
    ceo: CEOState = field(default_factory=CEOState)


# ---------------------------------------------------------------------------
# Simulation Engine
# ---------------------------------------------------------------------------

class SimulationEngine:
    """
    Manifest-driven orchestration engine skeleton.

    Responsibilities:
    - Load specs via simulation_manifest.yaml.
    - Maintain per-session state (meeting, dataroom, ceo).
    - Interpret user input -> detect Sarai command / role question / Data Room command.
    - Produce EngineEvents for Meeting, Data Room, Sarai panel.
    """

    def __init__(self, manifest_path: str):
        self.manifest_path = manifest_path
        self.manifest: Dict[str, Any] = {}
        self.specs: Dict[str, Any] = {}
        self.sessions: Dict[str, SessionState] = {}

        self._load_manifest_and_specs()

    # ------------------------- Loading & Specs -----------------------------

    def _load_manifest_and_specs(self) -> None:
        if not yaml:
            raise RuntimeError(
                "PyYAML is not installed. Please `pip install pyyaml` to load specs."
            )

        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self.manifest = yaml.safe_load(f) or {}

        specs_section = self.manifest.get("simulation_manifest", {}).get("specs", {})
        base_dir = os.path.dirname(self.manifest_path)

        def load_spec_label(label: str, path: str):
            full = os.path.join(base_dir, path)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    self.specs[label] = yaml.safe_load(f) or {}
            else:
                self.specs[label] = {"_error": f"Missing spec file: {full}"}

        # CEO core + scene
        if "ceo_core" in specs_section:
            load_spec_label("ceo_core", specs_section["ceo_core"])
        if "ceo_scene_evaluation" in specs_section:
            load_spec_label("ceo_scene_evaluation", specs_section["ceo_scene_evaluation"])

        # Sarai
        if "sarai" in specs_section:
            load_spec_label("sarai", specs_section["sarai"])

        # Dataroom
        if "dataroom" in specs_section:
            load_spec_label("dataroom", specs_section["dataroom"])

        # Dataroom tools
        for tr in specs_section.get("dataroom_tools", []):
            load_spec_label(tr["id"], tr["file"])

        # Roles
        self.specs["roles"] = {}
        for role in specs_section.get("roles", []):
            rid = role["id"]
            file = role["file"]
            full = os.path.join(base_dir, file)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    self.specs["roles"][rid] = yaml.safe_load(f) or {}
            else:
                self.specs["roles"][rid] = {"_error": f"Missing spec file: {full}"}

        # Safety
        self.specs["safety"] = {}
        for saf in specs_section.get("safety", []):
            sid = saf["id"]
            file = saf["file"]
            full = os.path.join(base_dir, file)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    self.specs["safety"][sid] = yaml.safe_load(f) or {}
            else:
                self.specs["safety"][sid] = {"_error": f"Missing safety file: {full}"}

    # --------------------------- Sessions ---------------------------------

    def _get_or_create_session(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
        return self.sessions[session_id]

    # ------------------------ Public Engine API ----------------------------

    def handle_input(self, request: EngineRequest) -> List[EngineEvent]:
        """
        Main entry point: handle a single UI/client message.
        """

        session = self._get_or_create_session(request.session_id)

        # Log CEO prompts for evaluation, regardless of channel
        if request.speaker == "CEO":
            session.ceo.prompt_history.append(
                {
                    "channel": request.channel,
                    "message": request.message,
                }
            )

        # Route by speaker and channel
        if request.speaker == "Sarai":
            return self._handle_sarai_message(session, request)
        elif request.speaker.lower() in {"tech", "tech cofounder", "tech_cofounder"}:
            return self._handle_role_message(session, request, role_id="tech_cofounder")
        elif request.speaker.lower() in {"marketing", "marketing cofounder", "marketing_cofounder"}:
            return self._handle_role_message(session, request, role_id="marketing_cofounder")
        elif request.speaker.lower() == "advisor":
            return self._handle_role_message(session, request, role_id="advisor")
        elif request.speaker.lower() == "vc":
            return self._handle_role_message(session, request, role_id="vc")
        elif request.speaker.lower() == "coach":
            return self._handle_role_message(session, request, role_id="coach")
        elif request.speaker.lower().startswith("therapist"):
            return self._handle_therapist_message(session, request)
        elif request.speaker.lower() in {"data room", "dataroom"}:
            return self._handle_dataroom_command(session, request)
        else:
            # Default: CEO speaking to Sarai / room from meeting channel
            if request.channel == "meeting":
                return self._handle_ceo_meeting_message(session, request)
            else:
                return [self._error_event("Unknown speaker or channel", speaker="Sarai")]

    # --------------------- Internal Routing Logic -------------------------

    def _handle_sarai_message(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        text = request.message.strip()

        # Very simple pattern matching; in a real implementation,
        # you would consult sarai_spec["sarai_spec"]["command_map"] patterns.
        lower = text.lower()

        if "generic ceo evaluation" in lower or "system-level performance" in lower:
            return self._run_generic_ceo_evaluation(session)
        if "what now" in lower and "30-day" in lower:
            return self._run_scene_evaluation_what_now(session)
        if "burn vs cash" in lower and "graph" in lower:
            return self._create_burn_vs_cash_graph(session)
        if "summarize our financial situation" in lower or "summarize burn, cash, and runway" in lower:
            return self._summarize_financials(session)
        if "summarize what happened in this meeting" in lower:
            return self._summarize_meeting(session)
        if "patterns do you see" in lower or "tell me if i’m avoiding" in lower:
            return self._sarai_observation(session)

        # Fallback: acknowledge and echo
        return [
            self._message_event(
                channel="sarai_panel",
                speaker="Sarai",
                text=(
                    "I received your message but don't have a specific handler for it yet. "
                    "Engine-wise, this is where a new command would be added."
                ),
            )
        ]

    def _handle_ceo_meeting_message(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        """
        CEO speaks in the meeting without addressing a specific role.
        For now we simply echo and store in transcript.
        """
        self._append_transcript(session, speaker="CEO", text=request.message)

        return [
            self._message_event(
                channel="meeting",
                speaker="Sarai",
                text="Got it. Who would you like to bring into this question: Tech, Marketing, VC, Coach, or Advisor?",
            )
        ]

    def _handle_role_message(self, session: SessionState, request: EngineRequest, role_id: str) -> List[EngineEvent]:
        """
        Very simple role routing: imagine underlying LLM prompted with the role spec.
        For this skeleton, we just respond with a templated message.
        """
        self._append_transcript(session, speaker=request.speaker, text=request.message)

        role_spec = self.specs.get("roles", {}).get(role_id, {})
        role_name = role_spec.get("identity", {}).get("name", request.speaker)

        # Simple stub; real implementation would call LLM with role_spec + context.
        reply = f"{role_name}: (stub) I'd analyze your question using my role spec and available documents."

        return [
            self._message_event(
                channel="meeting",
                speaker=role_name,
                text=reply,
            )
        ]

    def _handle_therapist_message(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        self._append_transcript(session, speaker=request.speaker, text=request.message)
        return [
            self._message_event(
                channel="meeting",
                speaker=request.speaker,
                text="(Therapist stub) I'd respond as a Mentalyc customer based on my segment and usage.",
            )
        ]

    def _handle_dataroom_command(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        lower = request.message.lower()

        if "burn vs cash" in lower and "graph" in lower:
            return self._create_burn_vs_cash_graph(session)

        return [
            self._message_event(
                channel="data_room",
                speaker="Sarai",
                text="(stub) Data Room received your command, but no handler is implemented yet.",
                event_type="data_room.update",
            )
        ]

    # --------------------- Example Handlers (Stubs) -----------------------

    def _run_generic_ceo_evaluation(self, session: SessionState) -> List[EngineEvent]:
        """
        Stub of: ceo_evaluation.run_generic using ceo_role.internal_behavioral_engine.
        """
        # In a real engine, you would analyze:
        # - session.ceo.prompt_history
        # - session.meeting.transcript
        # - ceo_core spec axes and weights
        text = (
            "System-level CEO evaluation (stub):\n"
            "- Situational awareness: medium (you've asked some financial and product questions).\n"
            "- Strategic focus: low–medium (you’re still exploring options).\n"
            "- Decision vs analysis: analysis-heavy so far.\n\n"
            "Engine note: this is where we’d plug in the internal_behavioral_engine "
            "and axes from ceo_role.yaml."
        )
        return [
            self._message_event(
                channel="sarai_panel",
                speaker="Sarai",
                text=text,
                event_type="sarai_panel.observation",
            )
        ]

    def _run_scene_evaluation_what_now(self, session: SessionState) -> List[EngineEvent]:
        """
        Stub of: scene_evaluation.run_what_now using scene_what_now.yaml + ceo_role engine.
        """
        text = (
            "Scene-specific evaluation for 'What now / first 30 days' (stub):\n"
            "- You’ve started mapping reality but haven’t clearly declared a 30-day milestone yet.\n"
            "- CEO infrastructure (KPIs, cadences) is not fully defined in this stub.\n"
            "- Commitments: still emerging.\n\n"
            "Engine note: we'd combine ceo_role axes with scene_what_now.scene_evaluation "
            "weighting here."
        )
        return [
            self._message_event(
                channel="sarai_panel",
                speaker="Sarai",
                text=text,
                event_type="sarai_panel.observation",
            )
        ]

    def _create_burn_vs_cash_graph(self, session: SessionState) -> List[EngineEvent]:
        """
        Stub for dataroom.create_graph_from_financials.
        Creates an artifact in DataRoomState and focuses it.
        """
        artifact_id = str(uuid.uuid4())
        session.dataroom.artifacts[artifact_id] = {
            "type": "graph",
            "title": "Burn vs Cash Over Time (stub)",
            "data_source": "financial_model",
            "config": {
                "x": "month",
                "y": ["burn", "cash_balance"],
            },
        }
        session.dataroom.focus_artifact_id = artifact_id

        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="data_room",
                type="data_room.update",
                speaker="Sarai",
                payload={
                    "action": "create_or_update_artifact",
                    "artifact_id": artifact_id,
                    "artifact": session.dataroom.artifacts[artifact_id],
                    "focus_artifact_id": artifact_id,
                },
            ),
            self._message_event(
                channel="sarai_panel",
                speaker="Sarai",
                text="I’ve created a stub burn vs cash graph artifact in the Data Room.",
                event_type="sarai_panel.observation",
            ),
        ]

    def _summarize_financials(self, session: SessionState) -> List[EngineEvent]:
        text = (
            "(stub) Financial summary:\n"
            "- We do not yet have a real financial model wired in this engine skeleton.\n"
            "- Once integrated, this handler would summarize burn, cash, and runway "
            "using the financial_model object."
        )
        return [
            self._message_event(
                channel="sarai_panel",
                speaker="Sarai",
                text=text,
                event_type="sarai_panel.observation",
            )
        ]

    def _summarize_meeting(self, session: SessionState) -> List[EngineEvent]:
        n_turns = len(session.meeting.transcript)
        text = (
            f"(stub) Meeting summary: {n_turns} turns so far.\n"
            "This is where we’d generate a narrative summary from the transcript."
        )
        return [
            self._message_event(
                channel="sarai_panel",
                speaker="Sarai",
                text=text,
                event_type="sarai_panel.observation",
            )
        ]

    def _sarai_observation(self, session: SessionState) -> List[EngineEvent]:
        text = (
            "(stub) Observation: you’re starting to structure the situation, "
            "but this engine does not yet implement a full behavioral analysis.\n"
            "In production, we’d inspect your prompt history and commitments here."
        )
        return [
            self._message_event(
                channel="sarai_panel",
                speaker="Sarai",
                text=text,
                event_type="sarai_panel.observation",
            )
        ]

    # ---------------------- Utility methods -------------------------------

    def _append_transcript(self, session: SessionState, speaker: str, text: str) -> None:
        session.meeting.transcript.append({"speaker": speaker, "text": text})

    def _message_event(
        self,
        channel: str,
        speaker: str,
        text: str,
        event_type: str = "message",
    ) -> EngineEvent:
        return EngineEvent(
            id=str(uuid.uuid4()),
            channel=channel,
            type=event_type,
            speaker=speaker,
            payload={"text": text},
        )

    def _error_event(self, msg: str, speaker: str = "Sarai") -> EngineEvent:
        return EngineEvent(
            id=str(uuid.uuid4()),
            channel="sarai_panel",
            type="error",
            speaker=speaker,
            payload={"text": msg},
        )


# ---------------------------------------------------------------------------
# Test Harness
# ---------------------------------------------------------------------------

def print_events(label: str, events: List[EngineEvent]) -> None:
    print(f"\n=== {label} ===")
    for ev in events:
        print(f"[{ev.channel}] {ev.speaker} ({ev.type}): {ev.payload}")


def main():
    """
    Simple demonstration of the engine API and example payloads.

    Assumes:
    - You have the manifest + specs in a folder:
        mental yc_sim_package_v3/simulation_manifest.yaml
    - You run this script from the parent directory of that folder.
    """
    manifest_path = os.path.join("mentalyc_sim_package_v3", "simulation_manifest.yaml")
    engine = SimulationEngine(manifest_path=manifest_path)

    session_id = "demo-session-1"

    # 1) CEO asks Sarai for generic CEO evaluation
    req1 = EngineRequest(
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",
        message="Sarai: Give me my generic CEO evaluation."
    )
    events1 = engine.handle_input(req1)
    print_events("Generic CEO evaluation", events1)

    # 2) CEO asks Sarai for scene-specific evaluation (What now 30-day challenge)
    req2 = EngineRequest(
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",
        message="Sarai: Evaluate me specifically for the 'What now' 30-day CEO challenge."
    )
    events2 = engine.handle_input(req2)
    print_events("Scene-specific evaluation (What now)", events2)

    # 3) CEO asks Sarai/Data Room to create a burn vs cash graph
    req3 = EngineRequest(
        session_id=session_id,
        channel="data_room",
        speaker="Sarai",
        message="Sarai: Create a burn vs cash graph in the Data Room."
    )
    events3 = engine.handle_input(req3)
    print_events("Burn vs cash graph creation", events3)

    # 4) CEO speaks directly to Tech Cofounder in the meeting
    req4 = EngineRequest(
        session_id=session_id,
        channel="meeting",
        speaker="tech",
        message="Given our current team, what can we realistically ship in 6 sprints?"
    )
    events4 = engine.handle_input(req4)
    print_events("Tech Cofounder response", events4)


if __name__ == "__main__":
    main()
