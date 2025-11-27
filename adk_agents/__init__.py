"""
ADK Agents for YAML Simulator 2

This package contains all ADK agent implementations for the Mentalyc CEO Simulator.
Each role (Tech, Advisor, Marketing, VC, Coach, Therapists) is implemented as an LlmAgent.
Sarai acts as the meta-orchestrator that routes to other agents.
"""

from .role_agents import (
    create_tech_cofounder_agent,
    create_advisor_agent,
    create_marketing_cofounder_agent,
    create_vc_agent,
    create_coach_agent,
    create_therapist_agents,
)
from .sarai_agent import create_sarai_agent
from .document_tools import (
    create_document_lookup_tool,
    create_list_documents_tool,
)

__all__ = [
    'create_tech_cofounder_agent',
    'create_advisor_agent',
    'create_marketing_cofounder_agent',
    'create_vc_agent',
    'create_coach_agent',
    'create_therapist_agents',
    'create_sarai_agent',
    'create_document_lookup_tool',
    'create_list_documents_tool',
]

