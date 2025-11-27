"""
Scene Context Manager

Loads scene-specific context and generates narrative summaries for agent prompts.
This allows easy switching between scenes (Scene1, Scene2, etc.) without changing agent code.

NOTE: This module now uses the new engine.scene_loader for cleaner architecture.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import get_scene_loader


class SceneContext:
    """Manages scene-specific context for agent prompts."""
    
    def __init__(self, scene_id: Optional[str] = None):
        """
        Initialize scene context.
        
        Args:
            scene_id: Scene identifier (e.g., "scene1"). If None, uses active scene.
        """
        self.scene_loader = get_scene_loader()
        self.scene_id = scene_id or self.scene_loader.get_active_scene_id()
        self.scene_config = self.scene_loader.load_scene(self.scene_id)
        self.context_data = self.scene_loader.get_scene_context(self.scene_id)
    
    def get_company_snapshot(self) -> str:
        """
        Generate a concise company snapshot for agent context.
        
        Returns:
            Formatted string with key company information
        """
        company = self.context_data.get('company', {})
        
        return f"""COMPANY SNAPSHOT:
Company: {company.get('name', 'Unknown')} ({company.get('stage', 'Unknown')} stage)
Sector: {company.get('sector', 'Unknown')}
Mission: {company.get('mission', 'Unknown')}

Team: {company.get('employees', {}).get('total', 0)} people
- CEO: {company.get('employees', {}).get('departments', {}).get('CEO', 0)}
- CTO: {company.get('employees', {}).get('departments', {}).get('CTO', 0)}
- Engineering: {company.get('employees', {}).get('departments', {}).get('Engineering', 0)}
- Marketing: {company.get('employees', {}).get('departments', {}).get('Marketing', 0)}

Financial Situation:
- Total Raised: ${company.get('funding', {}).get('total_raised_usd', 0):,}
- Cash Remaining: ${company.get('funding', {}).get('cash_remaining_usd', 0):,}
- Monthly Burn: ${company.get('key_metrics', {}).get('burn_usd_month', 0):,}
- Runway: {company.get('key_metrics', {}).get('runway_months', 0)} months ⚠️
- Current MRR: ${company.get('key_metrics', {}).get('mrr_usd', 0):,}
- Growth Rate: {company.get('key_metrics', {}).get('growth_rate_mom', 0)*100:.0f}% MoM

Product Status: {company.get('product', {}).get('current_stage', 'Unknown')}
Current Users: {company.get('customers', {}).get('current_users', {}).get('paying_therapists', 0)} paying therapists, {company.get('customers', {}).get('current_users', {}).get('active_pilots', 0)} active pilots
"""
    
    def get_scene_narrative(self) -> str:
        """
        Generate the scene-specific narrative context.
        
        For Scene 1 ("What Now?"), this includes the CEO's first 30 days framework.
        
        Returns:
            Formatted narrative string
        """
        if self.scene_id.lower() == "scene1":
            return self._get_what_now_narrative()
        
        # Add more scene narratives as needed
        return ""
    
    def _get_what_now_narrative(self) -> str:
        """Generate the 'What Now?' scene narrative."""
        return """SCENE CONTEXT: "You Just Became CEO. What Now?"

This is the CEO's first 30 days. The founder has just transitioned to the CEO role, and this moment defines how they will lead.

THE CHALLENGE:
The CEO must shift from founder mode (doing everything) to leader mode (creating clarity and systems). They face immediate pressure:
- Short runway (2.4 months) demands urgent decisions
- Team is watching: Can I trust this leader?
- Investors are evaluating: Can they scale with the company?
- The CEO is questioning themselves: Am I cut out for this?

THE FRAMEWORK - First 30 Days:
1. ASSESS REALITY
   - What do we truly know vs. assume?
   - What's proven in our PoC, what's still hypothesis?
   - What are our blind spots?

2. MEET STAKEHOLDERS
   - Talk to every team member, early customers, advisors
   - Don't pitch yet—gather information, build trust
   - Listen more than you speak

3. CLARIFY THE NEXT MILESTONE
   - Define one clear, achievable objective for the next 30 days
   - This isn't about scaling to 100 employees
   - It's about proving the product concept has real traction

4. BUILD CEO INFRASTRUCTURE
   - Calendar discipline: Allocate time deliberately (recruiting, fundraising, product)
   - Leadership cadence: Weekly team check-ins, even with 3 people
   - Tracking systems: Simple CRM for investors/candidates, burn model for cash

THE CEO'S JOB (from Year One Action Plan):
"Set direction, build team, and ensure resources."

KEY MINDSET SHIFTS:
- Vision → Execution: Translate ideas into strategy, systems, results
- Speed → Scale: Build discipline to scale sustainably
- Doing → Leading: Create leverage by empowering the team
- Ownership → Stewardship: Responsible to investors, employees, customers

SUCCESS CRITERIA FOR THIS SCENE:
✓ Map reality honestly (product, team, runway)
✓ Choose one concrete 30-day milestone
✓ Establish basic infrastructure (KPIs, cadences)
✓ Declare focus and commitment

THE EVALUATION:
The CEO will be evaluated on:
- Situational Awareness: Do they see reality clearly?
- Strategic Focus: Can they pick a direction and stick to it?
- Financial Discipline: Do they manage burn and runway responsibly?
- Stakeholder Alignment: Can they coordinate the team?
- Decision vs Analysis: Do they balance understanding with action?

YOUR ROLE:
Guide the CEO through this transition. Challenge assumptions. Surface risks. Help them build the clarity and infrastructure they need to lead effectively.

Remember: "Your job isn't to have the best idea. It's to create the conditions for the best ideas to win."
"""
    
    def get_scene_objectives(self) -> str:
        """
        Get the specific objectives for this scene.
        
        Returns:
            Formatted objectives string
        """
        objectives = self.context_data.get('scene_objectives', [])
        success_criteria = self.context_data.get('success_criteria', [])
        
        if not objectives and not success_criteria:
            return ""
        
        objectives_text = '\n'.join([f"  • {obj}" for obj in objectives]) if objectives else ""
        criteria_text = '\n'.join([f"  ✓ {c}" for c in success_criteria]) if success_criteria else ""
        
        result = "SCENE OBJECTIVES:\n"
        if objectives_text:
            result += objectives_text + "\n"
        if criteria_text:
            result += "\nSUCCESS CRITERIA:\n" + criteria_text + "\n"
        
        return result
    
    def get_full_context(self) -> str:
        """
        Get the complete scene context for agent prompts.
        
        Returns:
            Full formatted context string
        """
        return f"""
{'='*80}
SCENE CONTEXT
{'='*80}

{self.get_company_snapshot()}

{self.get_scene_narrative()}

{self.get_scene_objectives()}

{'='*80}
"""
    
    def get_compact_context(self) -> str:
        """
        Get a compact version of scene context (for roles with limited context needs).
        
        Returns:
            Compact formatted context string
        """
        company = self.context_data.get('company', {})
        
        return f"""SCENE: {self.scene_config.title}
Company: {company.get('name')} - {company.get('stage')} stage {company.get('sector', 'Startup')}
Runway: {company.get('key_metrics', {}).get('runway_months', 0)} months | MRR: ${company.get('key_metrics', {}).get('mrr_usd', 0):,} | Burn: ${company.get('key_metrics', {}).get('burn_usd_month', 0):,}/mo

Challenge: {self.scene_config.description}
"""


# Singleton instance
_scene_context = None

def get_scene_context(scene_id: Optional[str] = None) -> SceneContext:
    """
    Get or create the scene context singleton.
    
    Args:
        scene_id: Scene identifier (default: active scene)
    
    Returns:
        SceneContext instance
    """
    global _scene_context
    if _scene_context is None or (scene_id and _scene_context.scene_id != scene_id):
        _scene_context = SceneContext(scene_id)
    return _scene_context


# Test function
if __name__ == "__main__":
    print("Testing Scene Context Manager...")
    print()
    
    try:
        scene = get_scene_context()
        print(f"✅ Loaded scene: {scene.scene_config.title}")
        print()
        
        print("=" * 80)
        print("FULL CONTEXT:")
        print("=" * 80)
        print(scene.get_full_context())
        
        print()
        print("=" * 80)
        print("COMPACT CONTEXT:")
        print("=" * 80)
        print(scene.get_compact_context())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
