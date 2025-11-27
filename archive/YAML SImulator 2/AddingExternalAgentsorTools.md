Here is a  brief for:

* a **developer** building the engine/integrations, and
* an **instructional designer** configuring new external experts/tools via YAML.

They are  in separate sections but show how they fit together.

---

## 1. Mental model: what “external agents/tools” are in this sim

From the simulator’s point of view:

> The orchestrator (Sarai/SimulationEngine) calls an **external agent** or **tool** with a structured request and gets back a structured response, then turns that into in-world dialogue or Data Room artifacts.

We distinguish:

* **External agents** – things that speak *as a role* in the room:

  * e.g., “External VC expert”, “Board advisor agent”, “Business plan analyzer persona”.
  * Engine uses an `AgentClient` to talk to them (e.g., via Google A2A, HTTP, ACP…).

* **External tools** – things that *produce artifacts* for the Data Room:

  * e.g., “burn_vs_cash_graph_tool”, “financial_summary_tool”, “risk_register_builder”.
  * Engine uses a `ToolClient` to talk to them (e.g., via MCP).

Your internal contracts:

* `AgentRequestPayload` / `AgentResponsePayload` – your **domain-level A2A shape**.
* `ToolRequestPayload` / `ToolResponsePayload` – your **domain-level MCP-ish shape**.

The wire protocol (Google Agent2Agent, MCP, HTTP, ACP…) is hidden behind:

* `AgentClient` implementations (e.g., `GoogleA2AAgentClient`, `HttpJsonAgentClient`).
* `ToolClient` implementations (e.g., `MCPToolClient`).

The SimulationEngine **never** depends on the wire protocol directly.

---

## 2. For Developers: how the external agent & tool integration works

### 2.1. Internal contracts

#### Agent side

```python
# agent_client.py
from dataclasses import dataclass
from typing import Dict, Any
from abc import ABC, abstractmethod

@dataclass
class AgentRequestPayload:
    agent_id: str      # "vc_external"
    role_id: str       # "VC"
    scene_id: str      # "what_now_30_day_challenge"
    user_id: str
    session_id: str
    question: str
    context: Dict[str, Any]  # e.g. financial_summary, roadmap_summary

@dataclass
class AgentResponsePayload:
    ok: bool
    advisor_text: str
    numeric_scores: Dict[str, float]
    meta: Dict[str, Any]

class AgentClient(ABC):
    @abstractmethod
    def call(self, req: AgentRequestPayload) -> AgentResponsePayload:
        ...
```

Then you implement protocol-specific clients:

* `HttpJsonAgentClient` – simple HTTP/JSON stub.
* `GoogleA2AAgentClient` – conceptual A2A stub.

The engine doesn’t care how `call()` is implemented.

#### Tool side (Data Room / MCP)

```python
# tool_client.py
@dataclass
class ToolRequestPayload:
    tool_id: str          # "burn_vs_cash_graph_tool"
    user_id: str
    session_id: str
    scene_id: str
    context: Dict[str, Any]

@dataclass
class ToolResponsePayload:
    ok: bool
    artifact_data: Dict[str, Any]  # {type, title, data}
    meta: Dict[str, Any]

class ToolClient(ABC):
    @abstractmethod
    def call(self, req: ToolRequestPayload) -> ToolResponsePayload:
        ...
```

Then:

* `MCPToolClient` – conceptual MCP stub that returns graph/canvas configs.

---

### 2.2. Wiring the clients into the engine

In `SimulationEngine.__init__`:

```python
class SimulationEngine:
    def __init__(
        self,
        manifest_path: str,
        session_repo: SessionRepository | None = None,
        agent_clients: Dict[str, AgentClient] | None = None,
        tool_clients: Dict[str, ToolClient] | None = None,
    ):
        self.manifest_path = manifest_path
        self.session_repo = session_repo or InMemorySessionRepository()

        # Protocol adapters, keyed by `protocol` in YAML
        self.agent_clients = agent_clients or {
            "http_json": HttpJsonAgentClient(base_url="https://agent-gateway.stub"),
            "google_a2a": GoogleA2AAgentClient(service_name="vc-expert-service"),
        }
        self.tool_clients = tool_clients or {
            "mcp": MCPToolClient(mcp_server_url="https://mcp-tool-server.stub"),
        }

        self._load_manifest_and_specs()
```

So:

* Roles can say `protocol: "google_a2a"` or `protocol: "http_json"`.
* Dataroom tools can say `mcp: enabled: true`.

Engine looks up the right client through these mappings.

---

### 2.3. External agent dispatch path

When the CEO talks to a role, the engine passes through `_handle_role_message`.

Pseudocode:

```python
def _handle_role_message(self, session, request, role_id):
    role_spec = self.specs.get("roles", {}).get(role_id, {})
    ext_cfg = role_spec.get("external_agent", {})
    is_external = ext_cfg.get("enabled", False)

    if is_external:
        return self._handle_external_role_message(session, request, role_id, role_spec, ext_cfg)
    else:
        return self._handle_internal_role_message(session, request, role_id, role_spec)
```

The external path:

```python
def _handle_external_role_message(self, session, request, role_id, role_spec, ext_cfg):
    protocol = ext_cfg.get("protocol", "http_json")
    agent_client = self.agent_clients.get(protocol)
    if not agent_client:
        return [EngineEvent.error(f"No AgentClient for protocol '{protocol}'")]

    # Build context (real impl: pull from SessionState, financial model, etc.)
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

    agent_res = agent_client.call(agent_req)

    # Safety filter would go here
    role_name = role_spec.get("identity", {}).get("name", request.speaker)
    safe_text = agent_res.advisor_text

    return [
        EngineEvent.message(
            channel="meeting",
            speaker=role_name,
            text=safe_text,
        )
    ]
```

**Key point:** SimulationEngine only knows **“I call AgentClient with our domain payload”**.

It doesn’t know or care if that goes out via:

* Google A2A
* ACP
* HTTP/JSON
* gRPC

---

### 2.4. Data Room MCP tool path

In `_handle_dataroom_command`, the engine can call MCP tools for specific operations.

Example: “create burn vs cash graph”:

```python
def _create_burn_vs_cash_graph(self, session: SessionState) -> List[EngineEvent]:
    tool_client = self.tool_clients.get("mcp")
    if tool_client:
        tool_req = ToolRequestPayload(
            tool_id="burn_vs_cash_graph_tool",
            user_id=session.user_id,
            session_id=session.session_id,
            scene_id=session.active_scene_id,
            context={
                "financial_model": {
                    "runway_months": 6,
                    "burn_per_month": 45000,
                    "cash_balance": 270000,
                }
            },
        )
        tool_res = tool_client.call(tool_req)
        artifact_data = tool_res.artifact_data
    else:
        artifact_data = {...}  # local fallback stub

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
```

Again, the engine only knows that:

* It calls `ToolClient` with `ToolRequestPayload`.
* It gets back artifact config that becomes a `DataRoomArtifact`.

Whether the tool was served via MCP, HTTP, or smoke signals is hidden.

---

### 2.5. Developer responsibilities

As a dev, your jobs are:

1. **Maintain the internal contracts:**

   * `AgentRequestPayload` / `AgentResponsePayload`.
   * `ToolRequestPayload` / `ToolResponsePayload`.

2. **Implement/adapt protocol clients:**

   * `GoogleA2AAgentClient.call()` – integrate with Google’s A2A stack.
   * `HttpJsonAgentClient.call()` – call your internal agent gateway.
   * `MCPToolClient.call()` – talk to your MCP tool server.

3. **Use YAML as configuration, not code:**

   * The engine reads:

     * `external_agent.protocol` for roles.
     * `mcp.enabled`, `mcp.tool_id`, `mcp.server_ref` for tools.
   * Code stays generic; YAML decides which protocol to use.

4. **Keep SessionState canonical:**

   * Never let external agents own or mutate core state.
   * Only pass minimal `context` out, and always write answer back into `SessionState` via Engine.

---

## 3. For Instructional Designers: how to add external experts and tools

You never touch Python. You work in YAML.

### 3.1. Adding an external expert (e.g., VC via Google A2A)

You already know how to define roles like Advisor/VC/Tech. An **external expert** is just a role with an `external_agent` block.

Example: `specs/vc_external_spec.yaml`

```yaml
vc_external_spec:
  identity:
    id: "vc_external"
    name: "VC (External)"
    in_world_title: "External VC Agent"
    tagline: "External VC using an expert model"

  mandate:
    core_responsibilities:
      - "Give funding and runway perspective based on structured company data."
      - "Evaluate fundraising readiness and runway risk."

  external_agent:
    enabled: true
    protocol: "google_a2a"          # tells the engine which AgentClient to use
    endpoint: "vc-expert-service"   # interpreted by dev’s A2A client
    capabilities:
      - "runway_and_burn_assessment"
      - "fundraising_readiness"
    context_contract:
      input_schema:
        - "financial_summary"
        - "roadmap_summary"
        - "ceo_goals"
      output_schema:
        - "advisor_text"
        - "numeric_scores"

  instruction_rules:
    allowed_topics:
      - "runway and burn"
      - "fundability"
      - "milestones vs runway"
    forbidden_topics:
      - "clinical advice"
      - "guaranteeing real-world funding"
```

You’d then:

* Add this role to `simulation_manifest.yaml` under `roles`.
* Optionally design example prompts:

  * “vc_external: Given our current burn and runway, what would you expect me to prove before a raise?”

The engine will:

* See `external_agent.enabled: true`.
* Use `protocol: "google_a2a"` to pick the right client.
* Automatically route CEO questions addressed to `vc_external` through the external expert and back into the meeting.

You don’t need to know what Google A2A is; you only pick the **label** agreed with devs.

---

### 3.2. Adding an external Data Room tool (via MCP)

You can think of a Data Room tool as:

> “A fancy calculator or workspace that can create/modify artifacts (graphs, canvases) given context.”

You configure tools in a scene-specific tools spec, e.g. `dataroom_tools_scene_what_now.yaml`.

Here’s how to define a MCP-backed burn vs cash graph:

```yaml
dataroom_tools_scene_what_now:
  scene_id: "what_now_30_day_challenge"
  description: "Tools for first 30 days as CEO."

  tools:
    - id: "burn_vs_cash_graph_tool"
      type: "graph"
      display_name: "Burn vs Cash Graph (MCP)"
      mcp:
        enabled: true
        tool_id: "burn_vs_cash_graph"      # name on the MCP server
        server_ref: "default_mcp_server"   # key for devs to pick the right MCPToolClient
```

You also define **how this tool is triggered** in natural language (optional, but nice):

```yaml
  command_shortcuts:
    - command_id: "dataroom.burn_vs_cash_graph"
      patterns:
        - "Data Room: create a burn vs cash graph."
        - "Sarai: put a burn vs cash chart in the Data Room."
      creates_or_focuses_tool: "burn_vs_cash_graph_tool"
```

What happens at runtime:

1. CEO says: “Data Room: create a burn vs cash graph.”
2. Engine matches this pattern (`dataroom.burn_vs_cash_graph`).
3. Engine calls `MCPToolClient` with `ToolRequestPayload` for `burn_vs_cash_graph_tool`.
4. MCP server returns artifact details (type, title, config/data).
5. Engine turns it into a `DataRoomArtifact` and emits a `data_room.update` event.
6. UI draws the graph.

You only describe **what the tool is and how to call it**, not how it computes the chart.

---

### 3.3. Safety & boundaries for external things

Everything still flows through the same safety rails:

* Global rules in `safety_rules.yaml`.
* Per-role `instruction_rules`.

If an external VC agent suggests something outside bounds, the **engine** (via Sarai) should:

* Filter/soften it.
* Replace with our standard “I can’t safely do that; here’s a safer alternative” messaging.

As an instructional designer, you:

* Define what the role/tool *is allowed* to talk about (`allowed_topics` / `forbidden_topics`).
* Devs enforce that through safety filters on the engine side.

---

## 4. Combined story in one sentence
The core design is:

> The simulation engine always speaks in its **own internal language** (`AgentRequestPayload`, `AgentResponsePayload`, `ToolRequestPayload`, `ToolResponsePayload`) and lets protocol adapters (A2A, MCP, HTTP, etc.) handle the messy details—while YAML specs let instructional designers declare *which* experts and tools exist, what they do, and which protocol label they use, without ever touching code.

I
