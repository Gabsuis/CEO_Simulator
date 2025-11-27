# simulation_engine.py
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List

try:
    import yaml  # pip install pyyaml
except ImportError:
    yaml = None

from engine_schema import (
    EngineRequest,
    EngineEvent,
    SessionState,
    SessionRepository,
    InMemorySessionRepository,
    MeetingMessage,
    DataRoomArtifact,
)


# ---------------------------------------------------------------------------
# Manifest-driven Simulation Engine (Steps 1–4)
# ---------------------------------------------------------------------------

class SimulationEngine:
    """
    Manifest-driven orchestration engine.

    - Loads specs via simulation_manifest.yaml.
    - Manages per-user, per-session state via a SessionRepository.
    - Exposes handle_input(request: EngineRequest) -> List[EngineEvent].
    """

    def __init__(self, manifest_path: str, session_repo: SessionRepository | None = None):
        self.manifest_path = manifest_path
        self.manifest: Dict[str, Any] = {}
        self.specs: Dict[str, Any] = {}
        self.session_repo: SessionRepository = session_repo or InMemorySessionRepository()
        
        # Session mode mapping: role_id -> session_access config
        self.role_session_modes: Dict[str, Dict[str, Any]] = {}

        self._load_manifest_and_specs()

    # ------------------------- Loading & Specs -----------------------------

    def _load_manifest_and_specs(self) -> None:
        if not yaml:
            raise RuntimeError("PyYAML is not installed. Please `pip install pyyaml` to load specs.")

        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            root = yaml.safe_load(f) or {}
        self.manifest = root.get("simulation_manifest", {})

        specs_section = self.manifest.get("specs", {})
        base_dir = os.path.dirname(self.manifest_path)

        def load_spec(label: str, relative_path: str):
            full = os.path.join(base_dir, relative_path)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f2:
                    self.specs[label] = yaml.safe_load(f2) or {}
            else:
                self.specs[label] = {"_error": f"Missing spec file: {full}"}

        # CEO core + scene
        if "ceo_core" in specs_section:
            load_spec("ceo_core", specs_section["ceo_core"])
        if "ceo_scene_evaluation" in specs_section:
            load_spec("ceo_scene_evaluation", specs_section["ceo_scene_evaluation"])

        # Sarai (extract session_access for all-knowing mode)
        if "sarai" in specs_section:
            load_spec("sarai", specs_section["sarai"])
            if "sarai" in self.specs and "session_access" in self.specs["sarai"].get("sarai_spec", {}):
                self.role_session_modes["sarai"] = self.specs["sarai"]["sarai_spec"]["session_access"]

        # Dataroom
        if "dataroom" in specs_section:
            load_spec("dataroom", specs_section["dataroom"])

        # Dataroom tools
        for tr in specs_section.get("dataroom_tools", []):
            load_spec(tr["id"], tr["file"])

        # Roles
        self.specs["roles"] = {}
        for role in specs_section.get("roles", []):
            rid = role["id"]
            rel = role["file"]
            full = os.path.join(base_dir, rel)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f2:
                    role_spec = yaml.safe_load(f2) or {}
                    self.specs["roles"][rid] = role_spec
                    
                    # Extract session_access config for routing
                    if "session_access" in role_spec:
                        self.role_session_modes[rid] = role_spec["session_access"]
            else:
                self.specs["roles"][rid] = {"_error": f"Missing spec file: {full}"}

        # Safety
        self.specs["safety"] = {}
        for saf in specs_section.get("safety", []):
            sid = saf["id"]
            rel = saf["file"]
            full = os.path.join(base_dir, rel)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f2:
                    self.specs["safety"][sid] = yaml.safe_load(f2) or {}
            else:
                self.specs["safety"][sid] = {"_error": f"Missing safety file: {full}"}

    # --------------------------- Sessions ---------------------------------

    def _get_session_id_for_role(self, user_id: str, base_session_id: str, role_id: str) -> str:
        """
        Generate appropriate session_id based on role's session_access mode.
        
        - all_knowing (Sarai): uses base session (can see all others)
        - radical_transparency: uses {base}_shared
        - private: uses {base}_{role_suffix}
        """
        session_config = self.role_session_modes.get(role_id, {})
        mode = session_config.get("mode", "radical_transparency")
        
        if mode == "all_knowing":
            return base_session_id
        elif mode == "radical_transparency":
            return f"{base_session_id}_shared"
        elif mode == "private":
            suffix = session_config.get("session_id_suffix", f"_{role_id}")
            return f"{base_session_id}{suffix}"
        else:
            return f"{base_session_id}_shared"  # default to shared

    def _get_or_create_session(self, user_id: str, session_id: str, role_id: str = None) -> SessionState:
        """
        Get or create session, routing to appropriate session_id based on role's access mode.
        """
        # Determine actual session_id based on role
        if role_id:
            actual_session_id = self._get_session_id_for_role(user_id, session_id, role_id)
            session_mode = self.role_session_modes.get(role_id, {}).get("mode", "radical_transparency")
        else:
            actual_session_id = session_id
            session_mode = "shared"
        
        session = self.session_repo.load(user_id, actual_session_id)
        if session is None:
            session = SessionState(
                user_id=user_id,
                session_id=actual_session_id,
                session_mode=session_mode,
                parent_session_id=session_id if actual_session_id != session_id else None
            )
            self.session_repo.save(session)
        return session

    def _save_session(self, session: SessionState) -> None:
        self.session_repo.save(session)

    # ------------------------ Public Engine API ----------------------------

    def handle_input(self, request: EngineRequest) -> List[EngineEvent]:
        """
        Main entry point: handle a single UI/client message.

        Transport-agnostic: this works for REST or WebSocket.
        
        Now routes to appropriate session based on speaker's session_access mode:
        - Sarai (all_knowing): sees all sessions
        - Radical transparency team: shared session
        - Private agents: isolated sessions
        """
        # Determine role_id from speaker for session routing
        speaker_lower = request.speaker.lower().strip()
        role_id = self._map_speaker_to_role_id(speaker_lower)
        
        session = self._get_or_create_session(request.user_id, request.session_id, role_id)

        # Track CEO prompts for evaluation
        if request.speaker == "CEO":
            session.ceo.prompt_history.append(
                {"channel": request.channel, "message": request.message}
            )

        # Route by speaker and channel
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
            events = self._handle_role_message(session, request, role_id="vc")
        elif speaker_lower == "coach":
            events = self._handle_role_message(session, request, role_id="coach")
        elif speaker_lower.startswith("therapist"):
            events = self._handle_therapist_message(session, request)
        elif speaker_lower in {"data room", "dataroom"}:
            events = self._handle_dataroom_command(session, request)
        else:
            # Default: CEO speaking in the meeting
            if request.channel == "meeting":
                events = self._handle_ceo_meeting_message(session, request)
            else:
                events = [EngineEvent.error("Unknown speaker or channel", speaker="Sarai")]

        # Persist updated session
        self._save_session(session)
        return events

    # --------------------- Internal Routing Logic -------------------------

    def _map_speaker_to_role_id(self, speaker_lower: str) -> str:
        """Map speaker string to role_id for session routing."""
        if speaker_lower == "sarai":
            return "sarai"
        elif speaker_lower in {"tech", "tech cofounder", "tech_cofounder"}:
            return "tech_cofounder"
        elif speaker_lower in {"marketing", "marketing cofounder", "marketing_cofounder"}:
            return "marketing_cofounder"
        elif speaker_lower == "advisor":
            return "advisor"
        elif speaker_lower == "vc":
            return "vc"
        elif speaker_lower == "coach":
            return "coach"
        elif "therapist" in speaker_lower:
            if "1" in speaker_lower:
                return "therapist_1"
            elif "2" in speaker_lower:
                return "therapist_2"
            elif "3" in speaker_lower:
                return "therapist_3"
            return "therapist_1"  # default
        else:
            return None

    def _handle_sarai_message(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        text = request.message.strip()
        lower = text.lower()

        # NOTE: in production, use sarai_spec["sarai_spec"]["command_map"] patterns.
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

        # Fallback: echo with explanation
        return [
            EngineEvent.message(
                channel="sarai_panel",
                speaker="Sarai",
                text=(
                    "I received your message but don't have a specific handler for it yet. "
                    "In the real engine, this is where a new Sarai command would be wired "
                    "via sarai_spec.command_map."
                ),
            )
        ]

    def _handle_ceo_meeting_message(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        # Append to meeting transcript
        session.meeting.transcript.append(MeetingMessage(speaker="CEO", text=request.message))

        return [
            EngineEvent.message(
                channel="meeting",
                speaker="Sarai",
                text=(
                    "Got it. In engine terms, this is a general CEO statement in the meeting. "
                    "Who should we involve next: Tech, Marketing, VC, Coach, or Advisor?"
                ),
            )
        ]

    def _handle_role_message(self, session: SessionState, request: EngineRequest, role_id: str) -> List[EngineEvent]:
        # Log to transcript
        session.meeting.transcript.append(MeetingMessage(speaker=request.speaker, text=request.message))

        role_spec = self.specs.get("roles", {}).get(role_id, {})
        role_name = role_spec.get("identity", {}).get("name", request.speaker)

        # Stub: In production, call LLM with role_spec + context
        reply = (
            f"{role_name}: (stub) I'd analyze your question using my role "
            f"spec and the documents I'm allowed to see."
        )

        return [
            EngineEvent.message(
                channel="meeting",
                speaker=role_name,
                text=reply,
            )
        ]

    def _handle_therapist_message(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        session.meeting.transcript.append(MeetingMessage(speaker=request.speaker, text=request.message))
        return [
            EngineEvent.message(
                channel="meeting",
                speaker=request.speaker,
                text="(Therapist stub) I'd respond as a Mentalyc customer based on my segment and usage.",
            )
        ]

    def _handle_dataroom_command(self, session: SessionState, request: EngineRequest) -> List[EngineEvent]:
        lower = request.message.lower()

        if "burn vs cash" in lower and "graph" in lower:
            return self._create_burn_vs_cash_graph(session)

        # Fallback stub
        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="data_room",
                type="data_room.update",
                speaker="Sarai",
                payload={
                    "text": "(stub) Data Room received your command, but no handler is implemented yet."
                },
            )
        ]

    # --------------------- Example Handlers (Stubs) -----------------------

    def _run_generic_ceo_evaluation(self, session: SessionState) -> List[EngineEvent]:
        text = (
            "System-level CEO evaluation (stub):\n"
            "- Situational awareness: medium (you've asked some financial and product questions).\n"
            "- Strategic focus: low–medium (you’re still exploring options).\n"
            "- Decision vs analysis: analysis-heavy so far.\n\n"
            "Engine note: this is where we’d plug in the internal_behavioral_engine "
            "and axes from ceo_role.yaml."
        )
        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="sarai_panel",
                type="evaluation",
                speaker="Sarai",
                payload={"text": text, "evaluation_type": "generic_ceo"},
            )
        ]

    def _run_scene_evaluation_what_now(self, session: SessionState) -> List[EngineEvent]:
        text = (
            "Scene-specific evaluation for 'What now / first 30 days' (stub):\n"
            "- You’ve started mapping reality but haven’t clearly declared a 30-day milestone yet.\n"
            "- CEO infrastructure (KPIs, cadences) is not fully defined in this stub.\n"
            "- Commitments: still emerging.\n\n"
            "Engine note: we'd combine ceo_role axes with scene_what_now.scene_evaluation "
            "weighting here."
        )
        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="sarai_panel",
                type="evaluation",
                speaker="Sarai",
                payload={"text": text, "evaluation_type": "scene_what_now"},
            )
        ]

    def _create_burn_vs_cash_graph(self, session: SessionState) -> List[EngineEvent]:
        artifact_id = str(uuid.uuid4())
        artifact = DataRoomArtifact(
            id=artifact_id,
            type="graph",
            title="Burn vs Cash Over Time (stub)",
            data={
                "data_source": "financial_model",
                "x": "month",
                "y": ["burn", "cash_balance"],
            },
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
                text="I’ve created a stub burn vs cash graph artifact in the Data Room.",
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
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="sarai_panel",
                type="sarai_panel.observation",
                speaker="Sarai",
                payload={"text": text},
            )
        ]

    def _summarize_meeting(self, session: SessionState) -> List[EngineEvent]:
        n_turns = len(session.meeting.transcript)
        text = (
            f"(stub) Meeting summary: {n_turns} turns so far.\n"
            "This is where we’d generate a narrative summary from the transcript."
        )
        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="sarai_panel",
                type="sarai_panel.observation",
                speaker="Sarai",
                payload={"text": text},
            )
        ]

    def _sarai_observation(self, session: SessionState) -> List[EngineEvent]:
        text = (
            "(stub) Observation: you’re starting to structure the situation, "
            "but this engine does not yet implement a full behavioral analysis.\n"
            "In production, we’d inspect your prompt history and commitments here."
        )
        return [
            EngineEvent(
                id=str(uuid.uuid4()),
                channel="sarai_panel",
                type="sarai_panel.observation",
                speaker="Sarai",
                payload={"text": text},
            )
        ]


# ---------------------------------------------------------------------------
# Test Harness (Example payloads)
# ---------------------------------------------------------------------------

def _print_events(label: str, events: List[EngineEvent]) -> None:
    print(f"\n=== {label} ===")
    for ev in events:
        print(f"[{ev.channel}] {ev.speaker} ({ev.type}): {ev.payload}")


def main():
    """
    Simple demonstration of the engine API and example payloads.

    Assumes:
    - Folder structure:
        mentalyc_sim_package_v3/
          simulation_manifest.yaml
          specs/...
    - You run this script from the parent directory of that folder.
    """
    manifest_path = os.path.join("mentalyc_sim_package_v3", "simulation_manifest.yaml")
    engine = SimulationEngine(manifest_path=manifest_path)

    user_id = "user-123"
    session_id = "session-demo-1"

    # 1) CEO -> Sarai: generic evaluation
    req1 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",
        message="Sarai: Give me my generic CEO evaluation."
    )
    events1 = engine.handle_input(req1)
    _print_events("Generic CEO evaluation", events1)

    # 2) CEO -> Sarai: scene-specific evaluation
    req2 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",
        message="Sarai: Evaluate me specifically for the 'What now' 30-day CEO challenge."
    )
    events2 = engine.handle_input(req2)
    _print_events("Scene-specific evaluation (What now)", events2)

    # 3) CEO -> Sarai/Data Room: create burn vs cash graph
    req3 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="data_room",
        speaker="Sarai",
        message="Sarai: Create a burn vs cash graph in the Data Room."
    )
    events3 = engine.handle_input(req3)
    _print_events("Burn vs cash graph creation", events3)

    # 4) CEO -> Tech Cofounder in the meeting
    req4 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="meeting",
        speaker="tech",
        message="Given our current team, what can we realistically ship in 6 sprints?"
    )
    events4 = engine.handle_input(req4)
    _print_events("Tech Cofounder response", events4)


if __name__ == "__main__":
    main()
