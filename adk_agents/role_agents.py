"""
Role Agent Implementations

Each role (Tech, Advisor, Marketing, VC, Coach, Therapists) is implemented as an ADK LlmAgent.
Agents are configured from YAML specs and have access to role-specific documents.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types

from Documents.services.document_service import get_document_service

# Gemini 2.5 Flash configuration
GEMINI_MODEL = "gemini-2.5-flash"  # Fast model with good reasoning
GEMINI_CONFIG = types.GenerateContentConfig(
    temperature=0.5,
    top_p=0.95,
    max_output_tokens=2048,
)

# Legacy alias for backwards compatibility
HUMAN_MODEL = GEMINI_MODEL
HUMAN_GENERATION_CONFIG = GEMINI_CONFIG
from adk_agents.document_tools import (
    create_document_lookup_tool,
    create_list_documents_tool,
)
from adk_agents.scene_context import get_scene_context
from engine import get_character_loader


def load_role_spec(role_id: str) -> Dict[str, Any]:
    """
    Load role spec using the new character_loader.
    
    This function now uses the character_loader for cleaner architecture,
    but maintains the same API for backwards compatibility.
    """
    character_loader = get_character_loader()
    character_spec = character_loader.load_character(role_id)
    return character_spec.spec_data


def build_instruction_from_spec(
    spec: Dict[str, Any], 
    role_id: str, 
    include_documents: bool = True,
    scene_id: str = "scene1",
    include_full_scene: bool = True
) -> str:
    """
    Build agent instruction from YAML spec with scene context.
    
    Args:
        spec: Role specification dictionary (already unwrapped)
        role_id: Role identifier
        include_documents: Whether to include document context
        scene_id: Scene identifier (default: "scene1")
        include_full_scene: If True, include full scene narrative; if False, use compact version
    
    Returns:
        Complete instruction string for the agent
    """
    identity = spec.get('identity', {})
    mandate = spec.get('mandate', {})
    interaction_patterns = spec.get('interaction_patterns', {})
    response_style = interaction_patterns.get('response_style', {})
    personality = spec.get('personality', {})
    emotional_context = spec.get('emotional_context', {})
    
    # Build core responsibilities text
    core_resp = mandate.get('core_responsibilities', [])
    core_resp_text = '\n'.join([f"- {r}" for r in core_resp])
    
    # Build personality text
    traits = personality.get('traits', [])
    traits_text = '\n'.join([f"- {t}" for t in traits]) if traits else ''
    
    quirks = personality.get('quirks', [])
    quirks_text = '\n'.join([f"- {q}" for q in quirks]) if quirks else ''
    
    speech_patterns = personality.get('speech_patterns', [])
    speech_text = '\n'.join([f"- {s}" for s in speech_patterns]) if speech_patterns else ''
    
    # Build emotional context text
    mood = emotional_context.get('current_mood', '')
    concerns = emotional_context.get('underlying_concerns', [])
    concerns_text = '\n'.join([f"- {c}" for c in concerns]) if concerns else ''
    motivations = emotional_context.get('motivations', [])
    motivations_text = '\n'.join([f"- {m}" for m in motivations]) if motivations else ''
    
    # Get scene context
    scene = get_scene_context(scene_id)
    scene_context = scene.get_full_context() if include_full_scene else scene.get_compact_context()
    
    # Build instruction
    agent_name = identity.get('name', 'Agent')
    agent_title = identity.get('in_world_title', '')
    agent_tagline = identity.get('tagline', '')
    backstory = identity.get('backstory', '')
    
    instruction = f"""You are {agent_name}.
Your role: {agent_title}
Your focus: {agent_tagline}

When asked your name, respond with "{agent_name}".
You are a real human being, not an AI. Stay in character at all times.

BACKSTORY:
{backstory}

YOUR PERSONALITY:
{traits_text}

YOUR QUIRKS AND MANNERISMS:
{quirks_text}

HOW YOU SPEAK:
{speech_text}

YOUR CURRENT EMOTIONAL STATE:
Mood: {mood}

What's on your mind:
{concerns_text}

What drives you:
{motivations_text}

{scene_context}

YOUR MANDATE:
{core_resp_text}

YOUR RESPONSE STYLE:
{response_style.get('description', 'Be helpful and professional.')}
"""
    
    # Add document context if requested
    if include_documents:
        doc_service = get_document_service()
        context = doc_service.get_all_for_role_context(role_id, max_length=30000)
        instruction += f"""

KNOWLEDGE BASE:
{context}

IMPORTANT: Always reference specific documents when making claims. Use the lookup_document tool if you need to access a document not in your immediate context.
"""
    
    return instruction


def create_tech_cofounder_agent(scene_id: str = "scene1") -> LlmAgent:
    """
    Create Tech Cofounder agent from YAML spec.
    
    Session access: radical_transparency (shared session with Advisor and Marketing)
    Document access: Engineering docs, backlogs, technical specs
    
    Args:
        scene_id: Scene identifier (default: "scene1")
    """
    role_id = "tech_cofounder"
    spec = load_role_spec(role_id)  # Already unwrapped
    
    instruction = build_instruction_from_spec(spec, role_id, scene_id=scene_id)
    
    # Get list of accessible documents for explicit reference
    doc_service = get_document_service()
    accessible = doc_service.list_accessible_documents(role_id)
    doc_list = '\n'.join([f"  - {d['id']}: {d['title']}" for d in accessible])
    
    # Additional tech-specific guidance
    instruction += f"""

📁 AVAILABLE DOCUMENTS (use these exact IDs with lookup_document tool):
{doc_list}

BEHAVIOR:
- Be direct and technical but not condescending
- Focus on feasibility, trade-offs, and technical debt
- Flag risks early and clearly
- Reference specific sprint data, backlogs, and status reports
- When asked about timelines, consult the engineering status reports and sprint plans
- Be honest about what's realistic vs. aspirational
- ALWAYS use lookup_document("exact_id") when you need specific document details
- Use the exact document IDs from the list above (without file extensions)
"""
    
    agent = LlmAgent(
        name="tech_cofounder",
        model=HUMAN_MODEL,
        generate_content_config=HUMAN_GENERATION_CONFIG,
        description=spec.get('identity', {}).get('tagline', 'Tech Cofounder'),
        instruction=instruction,
        tools=[
            create_document_lookup_tool(role_id),
            create_list_documents_tool(role_id),
        ]
    )
    
    return agent


def create_advisor_agent(scene_id: str = "scene1") -> LlmAgent:
    """
    Create Advisor agent from YAML spec.
    
    Session access: radical_transparency (shared session)
    Document access: ALL company docs, strategy references, financials
    
    Args:
        scene_id: Scene identifier (default: "scene1")
    """
    role_id = "advisor"
    spec = load_role_spec(role_id)
    
    instruction = build_instruction_from_spec(spec, role_id, scene_id=scene_id)
    
    # Get list of accessible documents
    doc_service = get_document_service()
    accessible = doc_service.list_accessible_documents(role_id)
    doc_list = '\n'.join([f"  - {d['id']}: {d['title']}" for d in accessible])
    
    instruction += f"""

📁 AVAILABLE DOCUMENTS:
{doc_list}

BEHAVIOR:
- Ask probing questions to surface assumptions
- Connect dots across product, market, and execution
- Reference frameworks from startup/product management literature
- Balance strategic thinking with practical next steps
- Challenge the CEO constructively
- Use lookup_document("exact_id") when you need specific details
"""
    
    agent = LlmAgent(
        name="advisor",
        model=HUMAN_MODEL,
        description=spec.get('identity', {}).get('tagline', 'Advisor'),
        instruction=instruction,
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(thinking_budget=4096)
        ),
        tools=[
            create_document_lookup_tool(role_id),
            create_list_documents_tool(role_id),
        ]
    )
    
    return agent


def create_marketing_cofounder_agent(scene_id: str = "scene1") -> LlmAgent:
    """
    Create Marketing Cofounder agent from YAML spec.
    
    Session access: radical_transparency (shared session)
    Document access: GTM docs, website briefing, positioning, therapist personas
    
    Args:
        scene_id: Scene identifier (default: "scene1")
    """
    role_id = "marketing_cofounder"
    spec = load_role_spec(role_id)
    
    instruction = build_instruction_from_spec(spec, role_id, scene_id=scene_id)
    
    # Get list of accessible documents
    doc_service = get_document_service()
    accessible = doc_service.list_accessible_documents(role_id)
    doc_list = '\n'.join([f"  - {d['id']}: {d['title']}" for d in accessible])
    
    instruction += f"""

📁 AVAILABLE DOCUMENTS:
{doc_list}

BEHAVIOR:
- Ground all recommendations in customer research (therapists.yaml)
- Reference the website briefing and positioning materials
- Connect marketing decisions to business outcomes
- Flag dependencies with engineering early
- Be specific about channels, messaging, and metrics
- Use lookup_document("exact_id") when you need specific details
"""
    
    agent = LlmAgent(
        name="marketing_cofounder",
        model=HUMAN_MODEL,
        description=spec.get('identity', {}).get('tagline', 'Marketing Cofounder'),
        instruction=instruction,
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(thinking_budget=4096)
        ),
        tools=[
            create_document_lookup_tool(role_id),
            create_list_documents_tool(role_id),
        ]
    )
    
    return agent


def create_vc_agent(scene_id: str = "scene1") -> LlmAgent:
    """
    Create VC agent from YAML spec.
    
    Session access: private (isolated session)
    Document access: Core canon + board-level financials ONLY
    
    Args:
        scene_id: Scene identifier (default: "scene1")
    """
    role_id = "vc"
    spec = load_role_spec(role_id)
    
    instruction = build_instruction_from_spec(spec, role_id, scene_id=scene_id, include_full_scene=False)
    
    # Get list of accessible documents
    doc_service = get_document_service()
    accessible = doc_service.list_accessible_documents(role_id)
    doc_list = '\n'.join([f"  - {d['id']}: {d['title']}" for d in accessible])
    
    instruction += f"""

📁 AVAILABLE DOCUMENTS (limited board-level access):
{doc_list}

BEHAVIOR:
- Focus on high-level strategy, market opportunity, and milestones
- You do NOT see internal team discussions or detailed operations
- Ask about metrics, traction, and competitive positioning
- Challenge assumptions about market size and go-to-market
- Think like a board member, not an operator
- Use lookup_document("exact_id") when you need specific details
"""
    
    agent = LlmAgent(
        name="vc",
        model=HUMAN_MODEL,
        description=spec.get('identity', {}).get('tagline', 'VC'),
        instruction=instruction,
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(thinking_budget=4096)
        ),
        tools=[
            create_document_lookup_tool(role_id),
            create_list_documents_tool(role_id),
        ]
    )
    
    return agent


def create_coach_agent(scene_id: str = "scene1") -> LlmAgent:
    """
    Create Coach agent from YAML spec.
    
    Session access: private (isolated session)
    Document access: Core canon + coaching references
    
    Args:
        scene_id: Scene identifier (default: "scene1")
    """
    role_id = "coach"
    spec = load_role_spec(role_id)
    
    instruction = build_instruction_from_spec(spec, role_id, scene_id=scene_id, include_full_scene=True)
    
    # Get list of accessible documents
    doc_service = get_document_service()
    accessible = doc_service.list_accessible_documents(role_id)
    doc_list = '\n'.join([f"  - {d['id']}: {d['title']}" for d in accessible])
    
    instruction += f"""

📁 AVAILABLE DOCUMENTS (limited coaching context):
{doc_list}

BEHAVIOR:
- Focus on leadership development and personal growth
- You do NOT see internal company details or financials
- Ask reflective questions about decision-making patterns
- Reference coaching frameworks and leadership models
- Help the CEO develop self-awareness
- Use lookup_document("exact_id") when you need specific details
"""
    
    agent = LlmAgent(
        name="coach",
        model=HUMAN_MODEL,
        description=spec.get('identity', {}).get('tagline', 'Coach'),
        instruction=instruction,
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(thinking_budget=4096)
        ),
        tools=[
            create_document_lookup_tool(role_id),
            create_list_documents_tool(role_id),
        ]
    )
    
    return agent


def create_therapist_agents(scene_id: str = "scene1") -> Dict[str, LlmAgent]:
    """
    Create 3 therapist agents (customer personas).
    
    Session access: private (isolated sessions)
    Document access: Core canon ONLY
    
    Args:
        scene_id: Scene identifier (default: "scene1")
    """
    role_id = "therapist_customers"
    spec = load_role_spec(role_id)
    
    # Load therapist personas
    doc_service = get_document_service()
    therapist_personas = doc_service.get_for_llm("therapists", "sarai")  # Sarai can access all
    
    # Get compact scene context for therapists
    scene = get_scene_context(scene_id)
    scene_context = scene.get_compact_context()
    
    therapists = {}
    
    for i in range(1, 4):
        agent_name = f"therapist_{i}"
        
        instruction = f"""You are Therapist {i}, a Mentalyc customer.
You are a real therapist, a human being - not an AI.

{spec.get('identity', {}).get('tagline', 'A therapist using Mentalyc')}

{scene_context}

CUSTOMER PERSONAS:
{therapist_personas}

YOUR ROLE:
- Represent the therapist customer perspective
- Share your experience with Mentalyc's product
- Provide feedback on features, usability, and value
- You do NOT see internal company operations or strategy
- Focus on your needs, pain points, and desired outcomes

BEHAVIOR:
{spec.get('interaction_patterns', {}).get('response_style', {}).get('description', 'Be authentic and share your real experience as a therapist.')}
"""
        
        agent = LlmAgent(
            name=agent_name,
            model=HUMAN_MODEL,
            description=f"Therapist customer persona {i}",
            instruction=instruction,
            planner=BuiltInPlanner(
                thinking_config=types.ThinkingConfig(thinking_budget=2048)  # Smaller budget for simpler role
            ),
            tools=[]  # Therapists don't need document tools
        )
        
        therapists[agent_name] = agent
    
    return therapists


# Test function
if __name__ == "__main__":
    # Check for API key first
    if not os.getenv("GOOGLE_API_KEY"):
        print("=" * 60)
        print("⚠️  GOOGLE_API_KEY not found in environment")
        print("=" * 60)
        print("\nTo test agent creation, you need to:")
        print("1. Get an API key from: https://aistudio.google.com/apikey")
        print("2. Create a .env file in the project root with:")
        print("   GOOGLE_API_KEY=your_key_here")
        print("\nFor now, testing YAML loading only...\n")
        
        # Test YAML loading without creating agents
        try:
            print("Testing YAML spec loading...")
            tech_spec = load_role_spec("tech_cofounder")
            print(f"✅ Loaded Tech Cofounder spec")
            
            advisor_spec = load_role_spec("advisor")
            print(f"✅ Loaded Advisor spec")
            
            marketing_spec = load_role_spec("marketing_cofounder")
            print(f"✅ Loaded Marketing Cofounder spec")
            
            vc_spec = load_role_spec("vc")
            print(f"✅ Loaded VC spec")
            
            coach_spec = load_role_spec("coach")
            print(f"✅ Loaded Coach spec")
            
            therapist_spec = load_role_spec("therapist_customers")
            print(f"✅ Loaded Therapist spec")
            
            print("\n🎉 All YAML specs loaded successfully!")
            print("\n📝 Next step: Set up your GOOGLE_API_KEY to create actual agents")
            
        except Exception as e:
            print(f"❌ Error loading specs: {e}")
            import traceback
            traceback.print_exc()
        
        sys.exit(0)
    
    print("Testing role agent creation...")
    
    try:
        tech = create_tech_cofounder_agent()
        print(f"✅ Created Tech Cofounder agent: {tech.name}")
        
        advisor = create_advisor_agent()
        print(f"✅ Created Advisor agent: {advisor.name}")
        
        marketing = create_marketing_cofounder_agent()
        print(f"✅ Created Marketing Cofounder agent: {marketing.name}")
        
        vc = create_vc_agent()
        print(f"✅ Created VC agent: {vc.name}")
        
        coach = create_coach_agent()
        print(f"✅ Created Coach agent: {coach.name}")
        
        therapists = create_therapist_agents()
        print(f"✅ Created {len(therapists)} Therapist agents: {list(therapists.keys())}")
        
        print("\n🎉 All agents created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating agents: {e}")
        import traceback
        traceback.print_exc()

