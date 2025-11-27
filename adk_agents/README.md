# ADK Agents Package

This package contains all Google ADK agent implementations for the YAML Simulator 2.

## Structure

```
adk_agents/
├── __init__.py              # Package exports
├── role_agents.py           # Tech, Advisor, Marketing, VC, Coach, Therapists
├── sarai_agent.py           # Meta-orchestrator (routes to other agents)
├── document_tools.py        # Document access tools (role-based permissions)
├── dataroom_tools.py        # Data Room artifact tools (graphs, canvases)
└── README.md                # This file
```

## Agents

### Role Agents (`role_agents.py`)

Each role is implemented as an ADK `LlmAgent`:

| Agent | Session Tier | Document Access | Purpose |
|-------|--------------|-----------------|---------|
| **Tech Cofounder** | Radical Transparency | Engineering docs, backlogs, specs | Technical feasibility, execution |
| **Advisor** | Radical Transparency | ALL company docs + strategy refs | Strategic guidance, frameworks |
| **Marketing Cofounder** | Radical Transparency | GTM docs, positioning, personas | Marketing strategy, messaging |
| **VC** | Private | Core canon + board-level financials | Investor perspective, milestones |
| **Coach** | Private | Core canon + coaching references | Leadership development |
| **Therapists (1-3)** | Private | Core canon only | Customer perspective |

### Sarai Agent (`sarai_agent.py`)

Meta-orchestrator with:
- **All-knowing access**: Sees all sessions and documents
- **Transfer capability**: Routes to appropriate agents
- **Evaluation tools**: Runs CEO evaluations
- **Meta-observations**: Surfaces patterns in CEO behavior

## Tools

### Document Tools (`document_tools.py`)

- `lookup_document(doc_id)`: Get document content (respects role permissions)
- `list_documents()`: List all accessible documents
- `search_documents(keyword)`: Search by keyword

### Data Room Tools (`dataroom_tools.py`)

- `create_burn_vs_cash_graph()`: Financial visualization
- `create_icp_canvas()`: Customer profile canvas
- `add_risk_to_register()`: Cagan risk register
- `set_milestone()`: 30-day milestone canvas
- `log_decision()`: Decision & commitment log

*Note: Data Room tools are stubs for now - will be implemented in Phase 4*

## Usage

### Creating Agents

```python
from adk_agents import (
    create_tech_cofounder_agent,
    create_advisor_agent,
    create_sarai_agent
)

# Create individual agents
tech = create_tech_cofounder_agent()
advisor = create_advisor_agent()
sarai = create_sarai_agent()

# Sarai can transfer to other agents
# Tech and Advisor share a session (radical transparency)
```

### Testing Agents

```bash
# Test role agents
python -m adk_agents.role_agents

# Test Sarai agent
python -m adk_agents.sarai_agent

# Test document tools
python -m adk_agents.document_tools
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### YAML Specs

Agents are configured from YAML specs in `mentalyc_sim_package_v3/specs/`:
- `tech_cofounder_spec.yaml`
- `advisor_spec.yaml`
- `marketing_cofounder_spec.yaml`
- `vc_spec.yaml`
- `coach_spec.yaml`
- `therapist_customers_spec.yaml`
- `sarai_spec.yaml`

## Session Architecture

### Three-Tier Access Model

1. **All-Knowing (Sarai)**
   - Session ID: `{base_session_id}`
   - Can see ALL sessions and documents

2. **Radical Transparency (Tech, Advisor, Marketing)**
   - Session ID: `{base_session_id}_shared`
   - Share conversation history
   - Role-specific document access

3. **Private (VC, Coach, Therapists)**
   - Session IDs: `{base_session_id}_vc`, `{base_session_id}_coach`, etc.
   - Isolated conversations
   - Limited document access

## Integration with Document Service

All agents use the `DocumentService` from `Documents/services/document_service.py`:

```python
from Documents.services.document_service import get_document_service

doc_service = get_document_service()

# Check access
has_access = doc_service.has_access("tech_cofounder", "financial_report")

# Get content for LLM
content = doc_service.get_for_llm("company_profile", "advisor")

# List accessible docs
docs = doc_service.list_accessible_documents("vc")
```

## Next Steps

### Phase 1: Core Engine (Current)
- ✅ Create agent structure
- ⏳ Integrate with simulation engine
- ⏳ Test first conversation

### Phase 2: Session Management
- ⏳ Implement multi-session routing
- ⏳ Test radical transparency vs private sessions
- ⏳ Add session persistence

### Phase 3: All Roles
- ⏳ Add remaining role agents
- ⏳ Test agent transfers
- ⏳ Verify document access control

### Phase 4: Evaluation & Data Room
- ⏳ Implement CEO evaluation logic
- ⏳ Implement Data Room tools
- ⏳ Add artifact creation/manipulation

### Phase 5: UI
- ⏳ Build 3-panel Streamlit UI
- ⏳ Connect to ADK agents
- ⏳ Deploy

## Dependencies

```bash
pip install google-adk google-generativeai pyyaml python-dotenv
```

## License

Part of the YAML Simulator 2 project.

