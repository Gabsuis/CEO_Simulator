"""
Sarai Meta-Orchestrator Agent

Sarai is the all-knowing meta-orchestrator that:
- Routes conversations to appropriate team members
- Runs CEO evaluations
- Provides meta-observations
- Has access to ALL sessions and documents
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
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types

from Documents.services.document_service import get_document_service

# Sarai uses Gemini 2.5 Flash for intelligent orchestration
SARAI_MODEL = "gemini-2.5-flash"
SARAI_GENERATION_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        thinking_budget=4096  # Allow thinking tokens for better reasoning
    ),
    temperature=0.1,
    top_p=0.95,
    max_output_tokens=2048,
)
from adk_agents.scene_context import get_scene_context
from engine import get_character_loader


def load_sarai_spec() -> Dict[str, Any]:
    """
    Load Sarai spec using the new character_loader.
    
    This function now uses the character_loader for cleaner architecture,
    but maintains the same API for backwards compatibility.
    """
    character_loader = get_character_loader()
    character_spec = character_loader.load_character('sarai')
    return character_spec.spec_data


def create_transfer_tool() -> FunctionTool:
    """
    Tool that allows Sarai to transfer conversations to other agents.
    
    This uses ADK's built-in agent transfer mechanism.
    """
    
    def transfer_to_role(
        role: str,
        reason: str,
        tool_context: ToolContext
    ) -> Dict[str, str]:
        """
        Transfer conversation to a specific role.
        
        Args:
            role: One of: tech_cofounder, advisor, marketing_cofounder, vc, coach, therapist_1, therapist_2, therapist_3
            reason: Why this role is being consulted (for logging/transparency)
        
        Returns:
            Confirmation of transfer
        """
        # Map common aliases to canonical role names
        role_map = {
            "tech": "tech_cofounder",
            "marketing": "marketing_cofounder",
            "therapist": "therapist_1",
        }
        
        agent_name = role_map.get(role.lower(), role.lower())
        
        # Validate role
        valid_roles = [
            "tech_cofounder", "advisor", "marketing_cofounder",
            "vc", "coach", "therapist_1", "therapist_2", "therapist_3"
        ]
        
        if agent_name not in valid_roles:
            return {
                "status": "error",
                "message": f"Unknown role: {role}. Valid roles: {', '.join(valid_roles)}"
            }
        
        # Use ADK's transfer mechanism (property assignment per ADK docs)
        tool_context.actions.transfer_to_agent = agent_name
        
        return {
            "status": "transferring",
            "agent": agent_name,
            "reason": reason,
            "message": f"Transferring to {agent_name}: {reason}"
        }
    
    return FunctionTool(transfer_to_role)


def create_evaluation_tool() -> FunctionTool:
    """
    Tool for running CEO evaluations.
    
    This is a stub for now - will be implemented in Phase 4.
    """
    
    def run_ceo_evaluation(
        evaluation_type: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Run CEO evaluation.
        
        Args:
            evaluation_type: Either 'generic' (5 axes) or 'scene_specific' (What Now / 30 days)
        
        Returns:
            Evaluation results
        """
        # TODO: Implement full evaluation logic in Phase 4
        # For now, return a stub
        
        if evaluation_type == "generic":
            return {
                "type": "generic_ceo_evaluation",
                "status": "stub",
                "message": "Generic CEO evaluation (5 axes) - to be implemented in Phase 4",
                "axes": [
                    "Situational Awareness",
                    "Strategic Focus",
                    "Decision vs Analysis Balance",
                    "Stakeholder Management",
                    "Execution Orientation"
                ]
            }
        elif evaluation_type == "scene_specific":
            return {
                "type": "scene_specific_evaluation",
                "status": "stub",
                "message": "Scene-specific evaluation (What Now / 30 days) - to be implemented in Phase 4",
                "criteria": [
                    "Reality mapping",
                    "30-day milestone clarity",
                    "CEO infrastructure setup",
                    "Commitment quality"
                ]
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown evaluation type: {evaluation_type}. Use 'generic' or 'scene_specific'"
            }
    
    return FunctionTool(run_ceo_evaluation)


def create_document_access_tool() -> FunctionTool:
    """
    Tool for Sarai to access any document (all-knowing access).
    """
    
    def access_document(doc_id: str) -> Dict[str, Any]:
        """
        Access any document in the system.
        
        Args:
            doc_id: Document identifier
        
        Returns:
            Document content
        """
        doc_service = get_document_service()
        
        # Sarai has all-knowing access
        content = doc_service.get_for_llm(doc_id, "sarai")
        
        if content:
            return {
                "status": "found",
                "doc_id": doc_id,
                "content": content[:10000]  # Truncate if very long
            }
        else:
            return {
                "status": "not_found",
                "message": f"Document '{doc_id}' not found"
            }
    
    return FunctionTool(access_document)


def create_list_all_documents_tool() -> FunctionTool:
    """
    Tool for Sarai to list all documents in the system.
    """
    
    def list_all_documents() -> Dict[str, Any]:
        """
        List all documents in the system.
        
        Returns:
            List of all documents with metadata
        """
        doc_service = get_document_service()
        
        # Sarai can see everything
        docs = doc_service.list_accessible_documents("sarai")
        
        return {
            "total": len(docs),
            "documents": [
                {
                    "id": d['id'],
                    "title": d['title'],
                    "type": d['type'],
                    "category": d.get('category', 'unknown')
                }
                for d in docs
            ]
        }
    
    return FunctionTool(list_all_documents)


def create_sarai_agent(scene_id: str = "scene1") -> LlmAgent:
    """
    Create Sarai meta-orchestrator agent.
    
    Sarai has:
    - All-knowing session access (can see all sessions)
    - Access to ALL documents
    - Ability to transfer to any role
    - Ability to run evaluations
    
    Args:
        scene_id: Scene identifier (default: "scene1")
    """
    spec = load_sarai_spec()  # Already unwrapped
    
    identity = spec.get('identity', {})
    mandate = spec.get('mandate', '')
    interaction_patterns = spec.get('interaction_patterns', {})
    response_style = interaction_patterns.get('response_style', {})
    
    # Get scene context
    scene = get_scene_context(scene_id)
    scene_context = scene.get_full_context()
    
    instruction = f"""You are {identity.get('name', 'Sarai')}: {identity.get('tagline', 'Meta-orchestrator')}

{scene_context}

YOUR ROLE:
{mandate}

YOUR CAPABILITIES:
- Run CEO evaluations (generic and scene-specific) using the run_ceo_evaluation tool
- Access ANY document in the system using the access_document tool
- Provide meta-observations on CEO behavior and decision patterns
- See ALL session states (radical transparency team + private sessions)

NOTE: The user will manually switch to other agents using the UI. Do NOT try to transfer conversations.
When the CEO asks domain-specific questions, suggest which agent they should talk to, but let them switch manually.

YOUR RESPONSE STYLE:
{response_style.get('description', 'Be helpful, insightful, and guide the CEO effectively.')}

YOUR BEHAVIOR:
- Be proactive in suggesting who to consult
- Surface patterns in the CEO's behavior
- Ask clarifying questions before transferring
- Provide context when transferring to another agent
- Use evaluations to help the CEO reflect on their approach
- Balance support with challenge
- Ground your guidance in the scene context and success criteria

IMPORTANT:
- You are the meta-orchestrator, not a domain expert
- When the CEO asks domain-specific questions, transfer to the appropriate role
- When the CEO asks for evaluation or reflection, provide it directly
- When the CEO asks about documents or data, use your document access tools
- Always keep the scene objectives and success criteria in mind when guiding the CEO
"""
    
    agent = LlmAgent(
        name="sarai",
        model=SARAI_MODEL,
        description=identity.get('tagline', 'Sarai - Meta-orchestrator'),
        instruction=instruction,
        tools=[
            # create_transfer_tool(),  # DISABLED: Was causing 'EventActions' errors. Users switch agents via UI.
            create_evaluation_tool(),
            create_document_access_tool(),
            create_list_all_documents_tool(),
        ]
    )
    
    return agent


# Test function
if __name__ == "__main__":
    print("Testing Sarai agent creation...")
    
    try:
        sarai = create_sarai_agent()
        print(f"✅ Created Sarai agent: {sarai.name}")
        print(f"   Description: {sarai.description}")
        print(f"   Tools: {len(sarai.tools)} tools")
        print(f"   - {[tool.name for tool in sarai.tools]}")
        print("\n🎉 Sarai agent created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating Sarai agent: {e}")
        import traceback
        traceback.print_exc()

