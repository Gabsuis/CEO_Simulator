"""
Data Room Tools for ADK Agents

Tools for creating and manipulating Data Room artifacts:
- Graphs (burn vs cash, runway, etc.)
- Canvases (ICP, Risk Register, 30-day milestones)
- Reports and summaries

These tools will be implemented in Phase 4-5.
For now, this file provides stubs.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.tools import FunctionTool


def create_burn_vs_cash_graph_tool() -> FunctionTool:
    """
    Tool to create a burn vs cash graph in the Data Room.
    
    Stub for now - will be implemented in Phase 4.
    """
    
    def create_burn_vs_cash_graph() -> Dict[str, Any]:
        """
        Create a burn rate vs cash balance graph.
        
        Returns:
            Graph artifact metadata
        """
        return {
            "status": "stub",
            "artifact_type": "graph",
            "title": "Burn vs Cash Over Time",
            "message": "Graph creation to be implemented in Phase 4",
            "data_source": "financial_report_12m_budget_simulation"
        }
    
    return FunctionTool(create_burn_vs_cash_graph)


def create_icp_canvas_tool() -> FunctionTool:
    """
    Tool to create/update the Ideal Customer Profile canvas.
    
    Stub for now - will be implemented in Phase 4.
    """
    
    def create_icp_canvas(
        segment: str,
        pain_points: str,
        value_proposition: str
    ) -> Dict[str, Any]:
        """
        Create or update the ICP canvas.
        
        Args:
            segment: Customer segment description
            pain_points: Key pain points
            value_proposition: Value prop for this segment
        
        Returns:
            Canvas artifact metadata
        """
        return {
            "status": "stub",
            "artifact_type": "canvas",
            "title": "Therapist ICP & Value Canvas",
            "message": "Canvas creation to be implemented in Phase 4",
            "data": {
                "segment": segment,
                "pain_points": pain_points,
                "value_proposition": value_proposition
            }
        }
    
    return FunctionTool(create_icp_canvas)


def create_risk_register_tool() -> FunctionTool:
    """
    Tool to create/update the Cagan Risk Register.
    
    Stub for now - will be implemented in Phase 4.
    """
    
    def add_risk_to_register(
        risk_type: str,
        description: str,
        mitigation: str
    ) -> Dict[str, Any]:
        """
        Add a risk to the Cagan Risk Register.
        
        Args:
            risk_type: One of: value, usability, feasibility, viability
            description: Risk description
            mitigation: How to mitigate this risk
        
        Returns:
            Updated risk register
        """
        return {
            "status": "stub",
            "artifact_type": "risk_register",
            "title": "Cagan Product Risk Register",
            "message": "Risk register to be implemented in Phase 4",
            "risk": {
                "type": risk_type,
                "description": description,
                "mitigation": mitigation
            }
        }
    
    return FunctionTool(add_risk_to_register)


def create_milestone_canvas_tool() -> FunctionTool:
    """
    Tool to create/update the 30-Day Learning & Milestone Canvas.
    
    Stub for now - will be implemented in Phase 4.
    """
    
    def set_milestone(
        milestone: str,
        learning_goal: str,
        success_criteria: str
    ) -> Dict[str, Any]:
        """
        Set a 30-day milestone.
        
        Args:
            milestone: The milestone to achieve
            learning_goal: What we'll learn
            success_criteria: How we'll know we succeeded
        
        Returns:
            Updated milestone canvas
        """
        return {
            "status": "stub",
            "artifact_type": "milestone_canvas",
            "title": "30-Day Learning & Milestone Canvas",
            "message": "Milestone canvas to be implemented in Phase 4",
            "milestone": {
                "goal": milestone,
                "learning": learning_goal,
                "success": success_criteria
            }
        }
    
    return FunctionTool(set_milestone)


def create_decision_log_tool() -> FunctionTool:
    """
    Tool to log decisions and commitments.
    
    Stub for now - will be implemented in Phase 4.
    """
    
    def log_decision(
        decision: str,
        rationale: str,
        commitment: str
    ) -> Dict[str, Any]:
        """
        Log a decision in the Decision & Commitment Log.
        
        Args:
            decision: The decision made
            rationale: Why this decision
            commitment: What action will be taken
        
        Returns:
            Updated decision log
        """
        return {
            "status": "stub",
            "artifact_type": "decision_log",
            "title": "Decision & Commitment Log",
            "message": "Decision log to be implemented in Phase 4",
            "entry": {
                "decision": decision,
                "rationale": rationale,
                "commitment": commitment
            }
        }
    
    return FunctionTool(log_decision)


# Collection of all Data Room tools
def get_all_dataroom_tools():
    """Get all Data Room tools as a list."""
    return [
        create_burn_vs_cash_graph_tool(),
        create_icp_canvas_tool(),
        create_risk_register_tool(),
        create_milestone_canvas_tool(),
        create_decision_log_tool(),
    ]


# Test function
if __name__ == "__main__":
    print("Testing Data Room tools...")
    
    try:
        tools = get_all_dataroom_tools()
        print(f"✅ Created {len(tools)} Data Room tools:")
        for tool in tools:
            print(f"   - {tool.name}")
        
        print("\n🎉 All Data Room tools created successfully!")
        print("   (These are stubs - will be implemented in Phase 4)")
        
    except Exception as e:
        print(f"❌ Error creating Data Room tools: {e}")
        import traceback
        traceback.print_exc()

