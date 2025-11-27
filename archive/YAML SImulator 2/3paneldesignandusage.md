Sarai: I’ll write this as if it were a design brief going to the dev team and course designers, anchored in everything we built *and* explicitly comparing it to the two earlier bundles.

---

# Mentalyc Pivot-CEO Simulator

## Design Spec, Architecture, and Usage Guide

### 0. Purpose of this document

This document explains:

1. **What this new package is** (the `mentalyc_sim_package_v3` design).
2. **Why it’s structured this way** – especially vs. the two earlier zip bundles you explored.
3. **How developers and course authors are meant to use it.**
4. **How it supports guardrails, evaluation, and multi-panel UI.**

It’s a briefing to help someone implement or extend the orchestration engine and UI without guessing at our intent.

---

## 1. Goals & Design Criteria

We optimized this design around a handful of explicit goals:

1. **Three-layer separation of concerns**

   * **Content layer**: YAML specs for roles, scenes, data room, safety.
   * **Orchestration layer**: manifest-driven engine that loads specs, routes intents, and manages state.
   * **UI layer**: three panels (Meeting, Data Room, Sarai Panel) that only talk to the orchestrator, not raw YAML.

2. **Instructor-editable simulation**

   * Course instructors can:

     * edit scenes, characters, and evaluations in YAML,
     * add new scenes or roles,
     * tweak behavior and prompts
       without changing engine code.

3. **CEO-centric evaluation model**

   * Separate **who the CEO is** (behavioral engine, 360, KPIs) from **what specific scene they’re in** (`What now / 30-day challenge`).
   * Scenes provide **contextual evaluation** on top of the generic CEO model.

4. **Guardrails and safety as first-class**

   * Global safety rules in `safety_rules.yaml`.
   * Per-role `instruction_rules` and Sarai-enforced boundaries.
   * Clear “never do” and crisis response patterns.

5. **Manifest-driven orchestration**

   * One **canonical manifest**: `simulation_manifest.yaml`.
   * Engine loads everything via the manifest; no hardcoded filenames scattered throughout the code.

6. **Multi-panel UI from the start**

   * Meeting panel: in-character dialogue with CEO + roles.
   * Data Room: smart workspace (docs, boards, canvases, graphs).
   * Sarai Panel: private meta-layer for evaluation, observations, and prompts.

---

## 2. High-Level Architecture

### 2.1. Layers

**1) Content Layer (YAML)**
Located in `mentalyc_sim_package_v3/` and `mentalyc_sim_package_v3/specs/`.

Key files:

* `simulation_manifest.yaml` (root, single source of truth)
* `specs/ceo_role.yaml`
* `specs/scene_what_now.yaml`
* `specs/sarai_spec.yaml`
* `specs/dataroom_spec.yaml`
* `specs/dataroom_tools_scene_what_now.yaml`
* `specs/safety_rules.yaml`
* Role specs:

  * `specs/advisor_spec.yaml`
  * `specs/tech_cofounder_spec.yaml`
  * `specs/marketing_cofounder_spec.yaml`
  * `specs/coach_spec.yaml`
  * `specs/vc_spec.yaml`
  * `specs/therapist_customers_spec.yaml`

**2) Orchestration Layer (Engine)**
Not defined in code here, but this package assumes an engine that:

* Loads `simulation_manifest.yaml`.
* Builds registries for:

  * CEO spec
  * Scenes
  * Roles
  * Dataroom tools
  * Safety rules
* Tracks session state:

  * Active scene
  * Meeting participants
  * Transcript, last decisions, prompt history
  * Data Room artifacts and focus
  * CEO behavior (for evaluation)

**3) UI Layer (Your app)**
Three main views:

* **Meeting Panel**

  * Text-based meeting with CEO + roles (Advisor, Tech, Marketing, VC, Coach, Therapists).
* **Data Room Panel**

  * Visual board of active docs, canvases, graphs, and lists.
* **Sarai Panel (on-demand)**

  * Meta commentary, 360 feedback summaries, and suggested prompts.

The UI speaks only in terms of **intents** and **events**, not file details.

---

## 3. Content Layer Details

### 3.1. `simulation_manifest.yaml` – the root manifest

This is the **entry point** for the engine.

It tells the orchestrator where to find:

* CEO core spec
* Scene evaluation spec(s)
* Sarai orchestration spec
* Dataroom spec + scene-specific tools
* Role specs
* Safety rules

The engine startup sequence is:

1. Load `simulation_manifest.yaml`.
2. Load each referenced spec file.
3. Validate structure (optional: schema).
4. Initialize state (CEO, scene, roles, dataroom, safety).

---

### 3.2. CEO vs Scene split

**`specs/ceo_role.yaml`**

Defines:

* Who the **CEO is** in the simulation:

  * Identity, mandate, knowledge model.
* CEO’s **behavior expectations**.
* CEO’s **KPI framework** (product, PMF, financial).
* Generic **evaluation model**:

  * Axes: situational awareness, strategic focus, financial discipline, stakeholder alignment, decision vs analysis.
  * Role-based 360 feedback (Tech, Marketing, VC, Therapists, Advisor, Coach).
* **Internal behavioral engine**:

  * Tracks prompts, docs accessed, commitments, temporal context.
  * Produces narrative evaluation and scores used by scenes and Sarai.

This is **scene-agnostic** – usable across many scenes.

---

**`specs/scene_what_now.yaml`**

Defines the specific scene:

* `id: what_now_30_day_challenge`
* Context: first 30 days as CEO; Mentalyc’s company state.
* Scene goals:

  * Map reality (product, team, runway, customers).
  * Choose a next milestone.
  * Establish basic CEO infrastructure.
  * Make at least one real commitment.
* Scene-specific evaluation:

  * Reuses CEO axes, but with **weights** (e.g., situational awareness 0.3, strategic focus 0.3, etc.).
  * Adds own criteria:

    * Explicit 30-day milestone.
    * Initial CEO infrastructure.
    * First real commitment.

The scene **does not redefine the CEO**.
It says: “Given how the CEO behaved, how did they show up in *this phase*?”

---

### 3.3. Sarai – orchestrator/spec brain

**`specs/sarai_spec.yaml`** describes Sarai’s behavior and API contract:

* **Profile & voice**: how Sarai should sound and behave.
* **UI channels**:

  * `meeting`, `data_room`, `sarai_panel`.
* **Interaction patterns**:

  * Default speaker logic (`Sarai:` vs `tech:` vs `Data Room:` prefixes).
* **Instruction rules & safety**:

  * Use `safety_rules.yaml` constraints.
  * Maintain role boundaries.
* **Command map**:

  * Maps user utterances to command IDs, e.g.:

    * `sarai.feedback.generic`
    * `sarai.scene_eval.what_now`
    * `sarai.micro_360`
    * `sarai.observe`
    * `sarai.summary.meeting`
    * `sarai.summary.financials`
    * `sarai.dataroom.create_graph_burn_cash`
    * `sarai.dataroom.open_icp_canvas`
* **Intent map**:

  * For each command, defines a handler and what data it uses, e.g.:

    * `ceo_evaluation.run_generic`
    * `scene_evaluation.run_what_now`
    * `dataroom.create_graph_from_financials`
* **Evaluation hooks**:

  * References CEO spec + scene specs.
* **Data layer** definitions:

  * Objects like `meeting_state`, `ceo_state`, `data_room_state`, `financial_model`, `document_index`.
  * Permissions for Sarai and roles.

This is effectively the **manifest for the orchestrator’s internal API**.

---

### 3.4. Dataroom core & scene tools

**`specs/dataroom_spec.yaml`**:

* Defines **artifact types**:

  * `document`, `kanban_board`, `todo_list`, `spreadsheet`, `graph`, `note`, `canvas`.
* Permissions:

  * CEO and Sarai can create/edit broadly.
  * Roles can “request” specific artifacts (e.g., Tech can ask for a graph).
* Command map:

  * `dataroom.show_document`
  * `dataroom.create.kanban`
  * `dataroom.create.todo`
  * `dataroom.create.spreadsheet`
  * `dataroom.create.graph`
  * `dataroom.focus_artifact`
* Integration with scenes:

  * Points to `dataroom_tools_scene_what_now.yaml` for scene-specific tools.

**`specs/dataroom_tools_scene_what_now.yaml`**:

Defines the **consulting toolkit** for Scene 1:

* Therapist ICP & Value Canvas.
* Cagan Risk Register (value/usability/feasibility/business viability).
* 30-Day Learning & Milestone Canvas.
* Decision & Commitment Log.
* Optional Eisenhower Matrix (CEO tasks).

Defines:

* What tools to auto-create at scene start.
* Command shortcuts to access/focus each tool.

---

### 3.5. Safety rules

**`specs/safety_rules.yaml`**:

* Global “never do”:

  * No clinical diagnosis/treatment for the player.
  * No self-harm encouragement or instructions.
  * No professional legal/tax/medical advice.
* Crisis handling protocols.
* Role-specific constraints:

  * Coach = non-clinical.
  * Therapists = customers, not the player’s clinicians.
  * VC = no funding guarantees.
  * Advisor = no legal/tax advice.
* How to handle attempts to break simulation/safety boundaries.

The engine and Sarai combine this with role `instruction_rules`.

---

### 3.6. Role specs

Each role has its own YAML:

* Identity, mandate, non-responsibilities.
* Knowledge core: what they can see.
* Interaction patterns: how the CEO calls them.
* Core functions: types of analysis/feedback they provide.
* Instruction rules & document access.

This allows instructors to tweak each role independently.

---

## 4. Orchestration Engine Responsibilities

This package assumes an engine with the following behavior:

### 4.1. Boot

1. Read `simulation_manifest.yaml`.
2. Load and parse each referenced spec file.
3. Build internal representations:

   * `ceo_model`, `scene_models`, `role_models`, `sarai_model`, `dataroom_model`, `safety_model`.
4. Initialize session state:

   * Active scene set to `what_now_30_day_challenge`.
   * Meeting participants (start with CEO; others joined as requested).
   * Data Room initial tools for this scene.
   * Sarai Panel off by default.

### 4.2. Handle user input

For each user message:

1. Parse speaker and content: e.g. `"Sarai: ..."`, `"tech: ..."`, `"Data Room: ..."`
2. If addressed to Sarai:

   * Use `sarai_spec.command_map` to map patterns → `command_id`.
   * Use `sarai_spec.intent_map` to route to the appropriate handler.
   * Apply safety rules (global + per-role as needed).
3. If addressed to a role (Advisor, Tech, etc.):

   * Use role spec + global safety to constrain answer.
4. If addressed to the Data Room:

   * Use `dataroom_spec.command_map` and/or `dataroom_tools_scene_what_now` shortcuts.

Engine output:

* Messages for **Meeting Panel** (role or CEO responses).
* State changes and artifacts for **Data Room Panel**.
* Sarai’s meta responses + evaluations for **Sarai Panel**.

---

## 5. UI Integration & “How to Use”

### 5.1. Meeting Panel

* Shows a chronological transcript: CEO + roles + Sarai-as-meta-if-addressed.
* When user types:

  * If no prefix: treat as CEO speaking to Sarai or the room, per your UI design.
  * If with prefix: `tech: ...`, `VC: ...`, etc → route accordingly.

Engine returns:

* One or more messages:

  * Each tagged with `speaker` and `channel="meeting"`.

---

### 5.2. Data Room Panel

* Renders lists/boards/canvases/graphs based on `dataroom_state`.
* When a doc/tool is referenced in the meeting:

  * Engine sets/updates the Data Room’s `artifacts` and `focus_artifact_id`.
* When CEO or Sarai issues a Data Room command:

  * Engine creates or updates artifacts per `dataroom_spec` and `dataroom_tools_scene_what_now`.

UI responsibilities:

* Present artifact types visually (e.g., Kanban columns, todo lists, etc.).
* Allow interactions that map back to intent (e.g., “move card”, “edit field”), which the orchestrator can model as structured events.

---

### 5.3. Sarai Panel (on-demand)

* Not always visible; the CEO explicitly calls Sarai.
* Shows:

  * Sarai observations about CEO behavior.
  * Summaries of 360 feedback.
  * Scene-specific evaluation snippets.
  * Suggested prompts (“Ask for a full 360 now”, etc).

Engine triggers:

* On specific commands (e.g., `sarai.feedback.generic`, `sarai.scene_eval.what_now`).
* Possibly after key decisions (depending on how far you take it).

---

## 6. “How to Use” – For Developers vs Course Authors

### 6.1. For Developers

* **Boot**:

  * Load manifest, build engine, maintain a single session state per user.
* **Connect to UI**:

  * Provide a single API like:

    * `POST /simulate` with `{ session_id, channel, speaker, message }`.
  * Engine returns:

    * List of messages with:

      * `channel`: `meeting | data_room | sarai_panel`
      * `speaker`
      * `payload` (text, plus optional structured data for Data Room artifacts).
* **Scene management**:

  * For now: scene = `what_now_30_day_challenge` only.
  * Later: allow scene switching via manifest.

### 6.2. For Course Authors

* Edit **content layer only**:

  * Scenes (`scene_*.yaml`)
  * Role specs
  * Dataroom tools for each scene
  * Safety rules
* Don’t touch engine code.
* For new scene:

  * Create `scene_new.yaml`.
  * Create `dataroom_tools_scene_new.yaml`.
  * Add them into `simulation_manifest.yaml`.
  * Optionally define new evaluation hooks in `sarai_spec.yaml`.

---

## 7. Why This Approach vs the Two Earlier Zip Bundles

You saw two earlier bundles:

* **Bundle A (lighter)**: fewer specs, more implicit behavior in code.
* **Bundle B (full)**: rich `sarai_spec`, more complex manifest, but CEO/scene were more entangled.

### 7.1. Problems with earlier bundles

**Bundle A (lightweight)**

* Pros:

  * Simple, quick to understand.
* Cons:

  * Harder to extend to multiple scenes and roles.
  * Less explicit about safety, evaluation, and UI channels.
  * More logic likely to drift into hardcoded engine behavior.

**Bundle B (full)**

* Pros:

  * Strong `sarai_spec` with detailed command/intent maps.
  * Better separation of orchestrator concerns.
  * More explicit safety logic.
* Cons:

  * CEO behavior and scene logic were somewhat intertwined.
  * Less clean “CEO core vs scene evaluation” split.
  * Harder for instructors to reason about **“What good looks like in this specific scene?”**

### 7.2. What this new package does differently

This `mentalyc_sim_package_v3` is essentially:

* **Bundle B’s strengths**, plus:

  * Cleaner **CEO vs Scene** split:

    * `ceo_role.yaml` handles behavioral engine and generic evaluations.
    * `scene_what_now.yaml` defines scene-specific expectations and weighting.
  * **Explicit three-panel UI support** baked into `sarai_spec` (meeting, data_room, sarai_panel).
  * **Scene-specific Data Room toolkit**:

    * `dataroom_tools_scene_what_now.yaml` wraps up the consulting tools you want for the first 30 days.
  * **Safer and clearer guardrails**:

    * `safety_rules.yaml` + per-role `instruction_rules`.
  * **Instructor-first structure**:

    * It’s obvious where to edit scenes, roles, dataroom tools, safety, and orchestrator behavior, without touching code.

In short:

* **Compared to Bundle A**: this design is more explicit, extensible, and aligned with the UI we actually want to ship.
* **Compared to Bundle B**: this design keeps B’s orchestration richness but fixes the CEO/scene coupling and adds a structured Data Room toolkit driven by scenes.

---

## 8. Summary

Sarai: For a developer, the message is:

> “Treat `simulation_manifest.yaml` as the only entry point. Build a manifest-driven engine that knows nothing about specific scenes or roles beyond what it reads from these YAML files. Then wire that engine to a three-panel UI via a simple message API where Sarai handles commands, roles answer in-character, the Data Room manages artifacts, and CEO evaluations are derived from the behavior log plus the active scene’s evaluation spec.”


