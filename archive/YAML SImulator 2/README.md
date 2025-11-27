Mentalyc YAML Simulator Package

Architecture + Authoring bundle for developers and instructional designers

This folder contains everything you need to understand and extend the Mentalyc Pivot-CEO Simulator:

The YAML world (roles, scenes, Sarai, Data Room, etc.).

The simulation engine skeleton (Python).

The 3-panel UI design + usage.

A concrete day-one scenario (“Saul runs his first sim”) with backlog items.

A design for external agents and tools (VC expert, MCP Data Room tools, etc.).

You can think of it as:

A self-contained starter kit for building and teaching with the Mentalyc CEO simulation.

1. What’s in this folder?

Inside YAML SImulator 2/ you’ll find:

Core design / docs

3paneldesignandusage.md
High-level design spec and usage guide:

Explains the 3-panel UI (Meeting, Data Room, Sarai panel).

Describes the 3-layer architecture:

Content (YAML specs),

Orchestration engine (Python, manifest-driven),

UI.

Compares this package to earlier bundles.
➜ Start here to understand the overall architecture.

ActionPlanForFirstPrototype.md
A concrete, end-to-end scenario and plan:

“CEO Saul starts a session → talks to Sarai, Tech, Data Room → gets evaluated → session is saved and resumed.”

Breaks down:

Minimal architecture to support that flow,

Developer tasks,

Instructional designer tasks,

A Python test harness outline.
➜ Start here if you want a day-one development plan.

AddingExternalAgentsorTools.md
Design brief for:

Developers: how to plug in external agents (VC experts, board advisors) and tools (MCP) via protocol-agnostic adapters.

Instructional designers: how to configure those agents/tools via YAML.
➜ Read this when you’re ready to add real external experts/tools.

Resulting directory.md
Short note describing what the resulting directory structure should look like after splitting the YAML bundle into the runtime mentalyc_sim_package_v3/ structure.

YAML specs & helpers

mentalyc_all_specs.yaml
A single file that contains all YAML specs, each separated by --- and annotated with a # file: comment:

simulation_manifest.yaml

specs/ceo_role.yaml

specs/scene_what_now.yaml

specs/sarai_spec.yaml

specs/dataroom_spec.yaml

specs/dataroom_tools_scene_what_now.yaml

specs/safety_rules.yaml

specs/advisor_spec.yaml

specs/tech_cofounder_spec.yaml

specs/marketing_cofounder_spec.yaml

specs/coach_spec.yaml

specs/vc_spec.yaml

specs/therapist_customers_spec.yaml
➜ This is the authoring bundle for content and roles.

yaml_splitter.py
A small Python utility that:

Reads mentalyc_all_specs.yaml,

Uses the # file: ... comments as targets,

Writes each piece out into a structured folder:

mentalyc_sim_package_v3/

simulation_manifest.yaml

specs/... (all the individual YAML files)
➜ Run this once to generate the runtime-ready mentalyc_sim_package_v3 directory.

dataroom_tools_scene_what_now.yaml
Scene-specific Data Room tools (consulting toolkit for Scene 1):

Therapist ICP & Value Canvas,

Cagan Risk Register,

30-Day Learning & Milestone Canvas,

Decision & Commitment Log,

Optional Eisenhower matrix.

vc_external_spec.yaml
Example of an external VC agent spec, including:

Identity and mandate,

external_agent block (enabled, protocol, endpoint),

Capabilities and context contract.

Engine & API code

engine_schema.py
Core data models and interfaces for the engine:

EngineRequest, EngineEvent (API contract between UI and engine),

MeetingState, DataRoomState, CEOState, SessionState,

DataRoomArtifact, MeetingMessage,

SessionRepository interface,

InMemorySessionRepository implementation.
➜ Read this to understand the engine’s event schema and state model.

simulation_engine.py
Main manifest-driven SimulationEngine:

Loads simulation_manifest.yaml and all specs.

Manages sessions via SessionRepository.

Implements handle_input(request: EngineRequest) -> List[EngineEvent].

Routes:

Sarai commands (evaluations, summaries, etc.),

Role messages (Tech, Marketing, Advisor, VC, Coach, Therapists),

Data Room commands (show document, create graph, etc.).

Contains stubbed handlers for:

Generic CEO evaluation,

Scene-specific evaluation (What Now / 30 days),

Burn vs cash graph creation,

Financial and meeting summaries.

condensed simulation_engine.py
A shorter, more didactic version of the engine:

Useful as a reference/teaching implementation.

Same core ideas, less code.

Mentalyc_API _draft_and payload.py
Draft of:

The engine API shape,

Example payloads between UI and engine,

How the 3 panels (Meeting, Data Room, Sarai) map to channel and payload fields.

2. What to read first (for each audience)
For developers

If you’re implementing the engine and integrations:

High-level architecture

3paneldesignandusage.md
→ Understand the 3-panel UI and 3-layer architecture.

Day-one scenario & plan

ActionPlanForFirstPrototype.md
→ See the “Saul” scenario and the minimal slice to ship:

New session,

Sarai summary,

Tech Q&A,

Data Room document,

Evaluation,

Save & reload session.

Engine data model & API

engine_schema.py
→ Learn how requests, events, and session state are structured.

Engine implementation

simulation_engine.py
→ See how the manifest is loaded, how routing works, and where stubbed logic lives.

External agents & tools (later)

AddingExternalAgentsorTools.md

vc_external_spec.yaml
→ When you’re ready to wire real VC experts or MCP tools.

For instructional designers / course authors

If you’re designing scenes, roles, and exercises:

Big picture of the simulation

3paneldesignandusage.md
→ Understand:

What the CEO is doing,

Who the roles are,

How scenes and evaluations work,

What the Data Room and Sarai panel are for.

Day-one learning experience

ActionPlanForFirstPrototype.md
→ Follow the “Saul” scenario:

What the learner sees,

What Sarai and Tech say,

How the session should feel.

YAML content bundle

mentalyc_all_specs.yaml
→ This contains:

CEO role and evaluation model,

Scene “What Now / 30 days”,

Sarai behavior,

Advisor/Tech/Marketing/Coach/VC/Therapists roles,

Data Room spec and tools,

Safety rules.
→ You can read and edit this as your primary authoring surface.

Scene-specific tools

dataroom_tools_scene_what_now.yaml
→ See and adjust:

ICP canvas,

Risk register,

30-day milestone canvas, etc.

Optional external experts

vc_external_spec.yaml
→ When you want to add a “super VC” expert as an external agent.

You don’t need to touch the Python code; you just edit YAML and specs.

3. How to spin up the runtime package (developer)

These steps assume you have Python 3 and pip:

Install dependencies

pip install pyyaml


Generate the structured spec folder

From inside YAML SImulator 2/:

python yaml_splitter.py


This will create a folder like:

mentalyc_sim_package_v3/
  simulation_manifest.yaml
  specs/
    ceo_role.yaml
    scene_what_now.yaml
    sarai_spec.yaml
    dataroom_spec.yaml
    dataroom_tools_scene_what_now.yaml
    safety_rules.yaml
    advisor_spec.yaml
    tech_cofounder_spec.yaml
    marketing_cofounder_spec.yaml
    coach_spec.yaml
    vc_spec.yaml
    therapist_customers_spec.yaml


Run the engine test harness

The main function in simulation_engine.py shows a simple demo.
For the full “Saul” scenario, use the harness described in ActionPlanForFirstPrototype.md (or adapt the provided scenario_test.py snippet into an actual file).

Example call style:

engine = SimulationEngine(manifest_path="mentalyc_sim_package_v3/simulation_manifest.yaml")
events = engine.handle_input(EngineRequest(
    user_id="saul",
    session_id="session-001",
    channel="sarai_panel",
    speaker="Sarai",
    message="Sarai: Summarize our financial situation."
))


Then inspect/print the EngineEvents.

Add persistence (optional but recommended)

Implement a simple FileSessionRepository as outlined in ActionPlanForFirstPrototype.md.

Pass it into SimulationEngine so that sessions can be resumed across runs.

4. Where to start your development plan (day-one)

If you want a one-day, end-to-end spike that touches everything:

Follow ActionPlanForFirstPrototype.md:

Implement the Saul scenario:

New session,

Sarai financial summary,

Tech “How late is the project?”,

Data Room project status document,

Generic CEO evaluation,

Explicit “Save this session”,

Resume session and get meeting summary.

Use engine_schema.py + simulation_engine.py as your base.

Use mentalyc_all_specs.yaml + yaml_splitter.py to generate mentalyc_sim_package_v3/.

Keep everything else (external agents, MCP tools) for a second iteration, guided by AddingExternalAgentsorTools.md and vc_external_spec.yaml.

5. Summary

Developers:

Read 3paneldesignandusage.md → ActionPlanForFirstPrototype.md → engine_schema.py → simulation_engine.py.

Run yaml_splitter.py to generate specs.

Implement the “Saul” scenario and persistence.

Instructional designers:

Read 3paneldesignandusage.md → ActionPlanForFirstPrototype.md.

Explore and edit mentalyc_all_specs.yaml + dataroom_tools_scene_what_now.yaml.

Use vc_external_spec.yaml and AddingExternalAgentsorTools.md when you’re ready to add advanced experts/tools.