Here is one very specific “thread the needle” scenario all the way through the architecture and turn it into actionable dev + instructor backlog items, plus a concrete Python test harness.
aA developer and an instructional designer, they can  build a thin but complete “Saul runs his first sim” path that exercises:

* Identity & sessions
* Sarai panel
* Meeting panel (Tech role)
* Data Room panel
* Evaluations
* Persistence & resume

---

## 1️⃣ Scenario walkthrough (what should happen end-to-end)

**User:** CEO Saul

Day 1 flow we want working:

1. **CEO Saul starts a new session**

   * Saul logs in / is identified as `user_id="saul"`.
   * A new `session_id` is created (e.g., `session-001`).
   * `SimulationEngine` initializes a fresh `SessionState` for Saul.

2. **CEO asks Sarai to summarize company financials**

   * UI sends an engine request like:

     * `channel="sarai_panel"`, `speaker="Sarai"`, `message="Sarai: Summarize our financial situation."`
   * Engine:

     * Recognizes a Sarai command (`summarize financials`).
     * Generates a stub financial summary (based on YAML financial model later).
     * Returns a `sarai_panel` message event.

3. **CEO speaks to Tech and asks “How late is the project?”**

   * UI sends:

     * `channel="meeting"`, `speaker="tech"`, `message="How late is the project?"`
   * Engine:

     * Routes to Tech role.
     * Uses internal Tech role spec (no external agent needed here).
     * Returns a stub tech response in the meeting channel.

4. **CEO asks to see the data Tech based it on in the Data Room**

   * UI sends:

     * `channel="data_room"`, `speaker="Data Room"`, `message="Data Room: show the project status document."`
   * Engine:

     * Looks up a known document id (e.g., `tech_project_status_doc`) from spec.
     * Creates a `DataRoomArtifact` of type `"document"` with a title like `"Tech Project Status (stub)"`.
     * Emits a `data_room.update` event with that artifact and sets it as `focus_artifact_id`.

5. **CEO sees the document**

   * UI:

     * Renders the artifact in the Data Room panel.
     * (From the engine perspective, this is just the `data_room.update` event already done in step 4.)

6. **CEO asks Sarai for an evaluation**

   * UI sends:

     * `channel="sarai_panel"`, `speaker="Sarai"`, `message="Sarai: Give me my generic CEO evaluation."`
   * Engine:

     * Calls `_run_generic_ceo_evaluation` (stub).
     * Uses `SessionState.ceo.prompt_history` and `meeting.transcript` as inputs.
     * Returns an `evaluation` event in `sarai_panel`.

7. **CEO says to save the session**

   * UI sends:

     * `channel="sarai_panel"`, `speaker="Sarai"`, `message="Sarai: Save this session."`
   * Engine:

     * Responds with an acknowledgment message.
     * (The session is already being saved on every `handle_input` via the repository, but this call can force a flush or mark a “checkpoint”.)

8. **CEO logs in again later**

   * Saul logs in (`user_id="saul"`).
   * UI reconnects to the same `session_id="session-001"` (or selects it from a session list).
   * Engine:

     * Loads existing `SessionState` from persistent storage (not memory).
   * CEO can now ask:

     * “Sarai: Summarize what happened in this meeting so far.”
   * Engine:

     * Uses the loaded transcript to generate a stub meeting summary.
     * Returns a `sarai_panel` message, proving state persisted.

That’s the “one-day” slice we want working.

---

## 2️⃣ Minimal architecture for this scenario

We can do this in one day by aiming for:

### Core components

1. **Engine schema & state**

   * `engine_schema.py`

     * `EngineRequest`, `EngineEvent`
     * `SessionState`, `MeetingState`, `DataRoomState`, `CEOState`
     * `DataRoomArtifact`, `MeetingMessage`
     * `SessionRepository` interface
     * `InMemorySessionRepository` + a minimal `FileSessionRepository` (JSON on disk)

2. **Orchestrator**

   * `simulation_engine.py`

     * Loads `simulation_manifest.yaml` + specs.
     * Implements `handle_input(request: EngineRequest) -> List[EngineEvent>`.
     * Implements handlers:

       * `_handle_sarai_message`
       * `_handle_role_message` (Tech internal only)
       * `_handle_dataroom_command`
       * `_run_generic_ceo_evaluation`
       * `_summarize_financials`
       * `_summarize_meeting`

3. **Persistence**

   * Use `FileSessionRepository` so that:

     * Every call to `handle_input` saves the session to disk.
     * New engine process can re-load it by `user_id` + `session_id`.

4. **Specs (YAML)**

   * Minimal versions of:

     * `simulation_manifest.yaml`
     * `specs/sarai_spec.yaml` (just enough to document commands)
     * `specs/tech_cofounder_spec.yaml`
     * `specs/dataroom_spec.yaml`
     * `specs/ceo_role.yaml` (evaluation axes)
     * `specs/safety_rules.yaml` (basic guardrails)
   * A simple docs index entry for `tech_project_status_doc` and `financial_model_summary`.

5. **No external agents or MCP needed for this one-day slice**

   * All responses can be internal stubs.
   * The agent/tool abstraction is future-proofed, but we don’t need to wire A2A/MCP for this scenario.

---

## 3️⃣ Code changes / implementation notes

### 3.1. FileSessionRepository (persistence)

A minimal JSON-on-disk implementation:

```python
# persistence_file.py
import json
import os
from typing import Optional, Tuple
from engine_schema import SessionState, SessionRepository

class FileSessionRepository(SessionRepository):
    """
    Very simple JSON-based session persistence for dev.

    Stores each session as:
      sessions/{user_id}__{session_id}.json
    """

    def __init__(self, base_dir: str = "sessions"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _path(self, user_id: str, session_id: str) -> str:
        fname = f"{user_id}__{session_id}.json"
        return os.path.join(self.base_dir, fname)

    def load(self, user_id: str, session_id: str) -> Optional[SessionState]:
        path = self._path(user_id, session_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # For a real version, you’d reconstruct dataclasses properly.
        # For this one-day spike, you can just store a dict or implement a simple from_dict.
        return SessionState(
            user_id=data["user_id"],
            session_id=data["session_id"],
            active_scene_id=data.get("active_scene_id", "what_now_30_day_challenge"),
            # For MVP: you can keep meeting/dataroom/ceo as simple dicts,
            # or write small helper functions to reconstruct them.
        )

    def save(self, session: SessionState) -> None:
        path = self._path(session.user_id, session.session_id)
        # For MVP: convert dataclasses via .__dict__ or asdict()
        import dataclasses
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(session), f, indent=2)
```

For one day, you can be a little sloppy with exact reconstruction (or only partially reconstruct state), as long as the test harness demonstrates:

* Transcript exists.
* Data Room artifact exists.
* CEO prompt history exists.

### 3.2. Sarai command handlers

Add to `_handle_sarai_message`:

* `"summarize our financial situation"` → `_summarize_financials`
* `"generic ceo evaluation"` → `_run_generic_ceo_evaluation`
* `"summarize what happened in this meeting"` → `_summarize_meeting`
* `"save this session"` → `_ack_save` (and maybe force `self._save_session`)

Example patterns:

```python
def _handle_sarai_message(self, session, request):
    text = request.message.strip().lower()

    if "summarize our financial situation" in text or "summarize burn, cash, and runway" in text:
        return self._summarize_financials(session)

    if "generic ceo evaluation" in text or "system-level performance" in text:
        return self._run_generic_ceo_evaluation(session)

    if "summarize what happened in this meeting" in text:
        return self._summarize_meeting(session)

    if "save this session" in text:
        # session is already being saved, but we can acknowledge
        self._save_session(session)
        return [
            EngineEvent.message(
                channel="sarai_panel",
                speaker="Sarai",
                text="I’ve saved your session state. You can safely come back later.",
            )
        ]

    # fallback...
```

### 3.3. Tech role handler

This is already in place as `_handle_role_message` → `_handle_internal_role_message` for `role_id="tech_cofounder"`.

For the one-day demo, you can special-case the “How late is the project?” question:

```python
def _handle_internal_role_message(...):
    # simple rule-based stub
    question = request.message.lower()
    role_name = role_spec.get("identity", {}).get("name", request.speaker)

    if "how late is the project" in question:
        reply = (
            f"{role_name}: We're about 2 sprints behind the original plan, mostly due to "
            "compliance work and some underestimated integration complexity."
        )
    else:
        reply = (
            f"{role_name}: (internal stub) I'd analyze your question using my role spec "
            f"and the documents I'm allowed to see."
        )

    ...
```

### 3.4. Data Room “show project status document”

Extend `_handle_dataroom_command`:

```python
def _handle_dataroom_command(self, session, request):
    lower = request.message.lower()

    if "show the project status document" in lower or "show project status" in lower:
        return self._show_project_status_document(session)

    # other handlers...
```

Implement `_show_project_status_document`:

```python
def _show_project_status_document(self, session: SessionState) -> List[EngineEvent]:
    artifact_id = str(uuid.uuid4())
    artifact = DataRoomArtifact(
        id=artifact_id,
        type="document",
        title="Tech Project Status (stub)",
        data={
            "doc_id": "tech_project_status_doc",
            "summary": "Stub doc: project is ~2 sprints behind due to compliance and integration work.",
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
        )
    ]
```

---

## 4️⃣ Backlog stories (developer vs instructor)

### 4.1. Developer stories

**D1: Implement file-based session persistence**

* **As** a developer
* **I want** a `FileSessionRepository` that saves/loads `SessionState` via JSON
* **So that** a session can be resumed across process restarts.
* **Acceptance:**

  * Given `user_id="saul"` and `session_id="session-001"`, when I call `handle_input` and then restart the engine and call `handle_input` again with the same IDs, I can still access prior transcript and Data Room artifacts.

---

**D2: Wire Sarai financial summary command**

* **As** a CEO user
* **I want** to ask Sarai “Summarize our financial situation”
* **So that** I get a quick, human-readable financial summary in the Sarai panel.
* **Implementation:**

  * Add pattern matching in `_handle_sarai_message`.
  * Implement `_summarize_financials(session)` stub.
* **Acceptance:**

  * In the test harness, when I send that command, I get a `sarai_panel` event with a `payload["text"]` that includes `"(stub) Financial summary"`.

---

**D3: Wire Tech “how late is the project?”**

* **As** Saul
* **I want** to ask Tech “How late is the project?”
* **So that** I get a concrete answer.
* **Implementation:**

  * In `_handle_internal_role_message` for `role_id="tech_cofounder"`, detect that phrase and return a fixed stub.
* **Acceptance:**

  * In the test harness, when I send a `speaker="tech"` message with that phrase, I get a `meeting` event whose text mentions “2 sprints behind”.

---

**D4: Data Room project status document**

* **As** Saul
* **I want** to say “Data Room: show the project status document”
* **So that** the Data Room panel displays the tech status doc.
* **Implementation:**

  * Add `_show_project_status_document(session)` as above.
  * Wire it into `_handle_dataroom_command`.
* **Acceptance:**

  * In the test harness, after that command, `SessionState.dataroom.artifacts` contains a `document` artifact with title “Tech Project Status (stub)”, and the engine emits a `data_room.update` event referencing it.

---

**D5: Generic CEO evaluation command**

* **As** Saul
* **I want** to ask Sarai “Give me my generic CEO evaluation”
* **So that** I get a narrative evaluation based on my behavior so far.
* **Implementation:**

  * Use the stub `_run_generic_ceo_evaluation` already present, ensure it’s wired to the phrase.
* **Acceptance:**

  * In the test harness, this call returns an event with `type="evaluation"` and a multi-line text.

---

**D6: Explicit “save session” command**

* **As** Saul
* **I want** to explicitly tell Sarai “Save this session”
* **So that** I feel safe leaving and coming back.
* **Implementation:**

  * Add pattern in `_handle_sarai_message`.
  * Force `self._save_session(session)` and return an acknowledgment message.
* **Acceptance:**

  * In the test harness, when that command is sent, an acknowledgment message is emitted and the JSON file for that session exists on disk.

---

**D7: Resume session test**

* **As** a developer
* **I want** a harness that simulates Saul leaving and coming back
* **So that** I can confirm persistence works.
* **Implementation:**

  * In `scenario_test.py` (below), run commands, then re-instantiate the engine with the same `FileSessionRepository`.
* **Acceptance:**

  * When asking Sarai to summarize the meeting after re-instantiating, the summary reflects earlier turns.

---

### 4.2. Instructional designer stories

**I1: Define minimal financial model summary**

* **As** an instructor
* **I want** a short “company financials” summary in YAML
* **So that** the stub `_summarize_financials` has realistic content to echo.
* **Implementation:**

  * Add a small `financial_model_summary` section in a doc or in `ceo_role.yaml` or `sarai_spec.yaml`.
* **Acceptance:**

  * The copy Sarai uses matches the text defined by the instructor.

---

**I2: Define Tech project status document**

* **As** an instructor
* **I want** a short tech project status doc (even as stub copy)
* **So that** when Saul opens it in the Data Room, it feels real.
* **Implementation:**

  * Add `tech_project_status_doc` to your document index or a YAML snippet.
* **Acceptance:**

  * The title and summary text in the Data Room artifact match the defined doc.

---

**I3: Document Sarai commands for this scenario**

* **As** an instructor
* **I want** the Sarai panel commands for this scenario documented and discoverable
* **So that** students know they can:

  * Summarize financials
  * Get CEO evaluation
  * Summarize meeting
  * Save the session
* **Implementation:**

  * Update `sarai_spec.yaml` with `command_map` entries and example prompts.
* **Acceptance:**

  * The commands used in the scenario appear in the spec and match the code behavior.

---

## 5️⃣ Detailed test harness (Python, end-to-end)

Here’s a concrete harness you can run locally to exercise the whole scenario:

```python
# scenario_test.py

import os
from engine_schema import EngineRequest
from simulation_engine import SimulationEngine
from persistence_file import FileSessionRepository


def print_events(label, events):
    print(f"\n=== {label} ===")
    for ev in events:
        ch = ev.channel
        sp = ev.speaker
        t = ev.type
        text = ev.payload.get("text") or ev.payload
        print(f"[{ch}] {sp} ({t}): {text}")


def run_saul_scenario():
    # Setup: manifest + file-based persistence
    manifest_path = os.path.join("mentalyc_sim_package_v3", "simulation_manifest.yaml")
    repo = FileSessionRepository(base_dir="sessions")

    # Saul starts a new session
    user_id = "saul"
    session_id = "session-001"

    engine = SimulationEngine(
        manifest_path=manifest_path,
        session_repo=repo,
    )

    # 1) CEO asks Sarai to summarize company financials
    req1 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",  # UI chooses 'Sarai' for commands directed to Sarai
        message="Sarai: Summarize our financial situation."
    )
    ev1 = engine.handle_input(req1)
    print_events("Sarai summarizes financials", ev1)

    # 2) CEO speaks to Tech and asks how late is the project
    req2 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="meeting",
        speaker="tech",
        message="How late is the project?"
    )
    ev2 = engine.handle_input(req2)
    print_events("Tech answers project delay", ev2)

    # 3) CEO asks to see the data Tech based it on in the Data Room
    req3 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="data_room",
        speaker="Data Room",
        message="Data Room: show the project status document."
    )
    ev3 = engine.handle_input(req3)
    print_events("Data Room shows project status document", ev3)

    # 4) CEO asks Sarai for a generic evaluation
    req4 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",
        message="Sarai: Give me my generic CEO evaluation."
    )
    ev4 = engine.handle_input(req4)
    print_events("Sarai generic CEO evaluation", ev4)

    # 5) CEO says to save the session
    req5 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",
        message="Sarai: Save this session."
    )
    ev5 = engine.handle_input(req5)
    print_events("Save session", ev5)

    # Simulate Saul leaving: in real life, engine process might stop here
    del engine

    # --- Later: Saul logs in again and resumes the same session ---

    engine2 = SimulationEngine(
        manifest_path=manifest_path,
        session_repo=repo,
    )

    # 6) CEO (Saul) asks Sarai to summarize what happened in the meeting so far
    req6 = EngineRequest(
        user_id=user_id,
        session_id=session_id,
        channel="sarai_panel",
        speaker="Sarai",
        message="Sarai: Summarize what happened in this meeting so far."
    )
    ev6 = engine2.handle_input(req6)
    print_events("Sarai summarizes meeting after reload", ev6)


if __name__ == "__main__":
    run_saul_scenario()
```

**What this harness proves:**

* New `SessionState` is created for Saul on first request.
* Sarai can:

  * Summarize financials.
  * Evaluate CEO.
  * Summarize meeting after reload.
* Tech can answer a specific question in the meeting.
* Data Room can show a project status document.
* Session state is persisted to disk and reloaded across engine instances.


