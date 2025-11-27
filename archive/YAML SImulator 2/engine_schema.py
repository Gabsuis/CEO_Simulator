# engine_schema.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import uuid


# ---------------------------------------------------------------------------
# Core Request / Event Types (API contract)
# ---------------------------------------------------------------------------

@dataclass
class EngineRequest:
    """
    Single input from the UI / client.

    This is the logical payload both REST and WebSocket transports will send.
    """
    user_id: str            # unique user identity (course participant)
    session_id: str         # unique simulation run for this user
    channel: str            # "meeting" | "data_room" | "sarai_panel"
    speaker: str            # "CEO", "Sarai", "tech", "advisor", "VC", "coach", "therapist 1", ...
    message: str            # raw text content from the user or Sarai


@dataclass
class EngineEvent:
    """
    Single event produced by the engine.

    The UI listens for these events and routes them to the correct panel/view.
    """
    id: str
    channel: str            # "meeting" | "data_room" | "sarai_panel"
    type: str               # "message" | "data_room.update" | "evaluation" | "error"
    speaker: str            # who is "saying" this (CEO, Sarai, Tech Cofounder, etc.)
    payload: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def message(channel: str, speaker: str, text: str) -> "EngineEvent":
        return EngineEvent(
            id=str(uuid.uuid4()),
            channel=channel,
            type="message",
            speaker=speaker,
            payload={"text": text},
        )

    @staticmethod
    def error(text: str, speaker: str = "Sarai") -> "EngineEvent":
        return EngineEvent(
            id=str(uuid.uuid4()),
            channel="sarai_panel",
            type="error",
            speaker=speaker,
            payload={"text": text},
        )


# ---------------------------------------------------------------------------
# Domain Models: Meeting, Data Room, CEO, Session
# ---------------------------------------------------------------------------

@dataclass
class MeetingMessage:
    speaker: str
    text: str


@dataclass
class DataRoomArtifact:
    """
    Generic artifact in the Data Room. Type-specific UIs can branch on `type`.

    Examples:
      - type="graph", data={"x": "month", "y": ["burn", "cash_balance"], ...}
      - type="canvas", data={"sections": [...], ...}
    """
    id: str
    type: str                # "graph" | "canvas" | "note" | "kanban_board" | "todo_list" | ...
    title: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeetingState:
    participants: List[str] = field(default_factory=lambda: ["CEO"])
    transcript: List[MeetingMessage] = field(default_factory=list)
    last_decision: Optional[str] = None
    prompt_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DataRoomState:
    artifacts: Dict[str, DataRoomArtifact] = field(default_factory=dict)
    focus_artifact_id: Optional[str] = None


@dataclass
class CEOState:
    prompt_history: List[Dict[str, Any]] = field(default_factory=list)
    unlocked_documents: List[str] = field(default_factory=list)
    commitments: List[str] = field(default_factory=list)


@dataclass
class SessionState:
    """
    In-memory representation of one simulation run for one user.
    
    Now supports multi-session architecture with three tiers:
    - all_knowing (Sarai): sees everything
    - radical_transparency (Advisor, Tech, Marketing): shared session
    - private (VC, Coach, Therapists): isolated sessions
    """
    user_id: str
    session_id: str
    active_scene_id: str = "what_now_30_day_challenge"
    meeting: MeetingState = field(default_factory=MeetingState)
    dataroom: DataRoomState = field(default_factory=DataRoomState)
    ceo: CEOState = field(default_factory=CEOState)
    
    # Multi-session tracking
    session_mode: str = "shared"  # "all_knowing" | "radical_transparency" | "private"
    parent_session_id: Optional[str] = None  # for private sessions, points to main session


# ---------------------------------------------------------------------------
# Persistence Interfaces
# ---------------------------------------------------------------------------

class SessionRepository(ABC):
    """
    Abstract persistence interface for sessions.

    Backends:
      - In-memory (dev/test)
      - SQL/NoSQL (production)
    
    Now supports multi-session architecture where one user can have multiple
    related sessions (shared + private sessions for different roles).
    """

    @abstractmethod
    def load(self, user_id: str, session_id: str) -> Optional[SessionState]:
        ...

    @abstractmethod
    def save(self, session: SessionState) -> None:
        ...
    
    @abstractmethod
    def load_all_for_user(self, user_id: str, parent_session_id: str) -> Dict[str, SessionState]:
        """Load all sessions related to a parent session (for Sarai's all-knowing view)"""
        ...


class InMemorySessionRepository(SessionRepository):
    """
    Simple in-memory repository keyed by (user_id, session_id).

    This is perfect for:
      - Local development
      - Unit tests
      - Demo runs
    
    Now supports multi-session architecture with parent/child session tracking.
    """

    def __init__(self):
        self._store: Dict[Tuple[str, str], SessionState] = {}

    def load(self, user_id: str, session_id: str) -> Optional[SessionState]:
        return self._store.get((user_id, session_id))

    def save(self, session: SessionState) -> None:
        key = (session.user_id, session.session_id)
        self._store[key] = session
    
    def load_all_for_user(self, user_id: str, parent_session_id: str) -> Dict[str, SessionState]:
        """Load all sessions for a user that share the same parent_session_id"""
        result = {}
        for (uid, sid), session in self._store.items():
            if uid == user_id and (session.parent_session_id == parent_session_id or sid == parent_session_id):
                result[sid] = session
        return result
