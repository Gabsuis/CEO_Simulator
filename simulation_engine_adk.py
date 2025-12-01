"""
Simulation Engine - ADK Version

Main orchestrator for the YAML Simulator 2, powered by Google ADK.
Manages multi-agent conversations with 3-tier session architecture.

Session Architecture:
- All-Knowing (Sarai): Sees ALL conversations from all sessions
- Radical Transparency (Tech, Advisor, Marketing): Shared session, see each other's messages
- Private (VC, Coach, Therapists): Isolated sessions, only Sarai can see them

Usage:
    engine = SimulationEngine()
    response = await engine.handle_input(
        user_id="saul",
        session_id="session-001",
        speaker="tech",
        message="How late is the website project?"
    )
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Google ADK imports
from google.adk import Runner
from google.adk.sessions import InMemorySessionService, BaseSessionService
from google.genai.types import Content, Part

# Import our agents
from adk_agents import (
    create_sarai_agent,
    create_tech_cofounder_agent,
    create_advisor_agent,
    create_marketing_cofounder_agent,
    create_vc_agent,
    create_coach_agent,
    create_therapist_agents,
)


@dataclass
class EngineResponse:
    """Response from the simulation engine."""
    speaker: str
    text: str
    session_id: str
    session_tier: str
    metadata: Dict[str, Any]


@dataclass
class DebugLog:
    """Debug information from engine operations."""
    timestamp: str
    level: str  # 'info', 'warning', 'error'
    message: str
    details: Dict[str, Any]


class SimulationEngine:
    """
    ADK-powered simulation engine with 3-tier session architecture.
    
    Session Tiers:
    - All-Knowing: Sarai (sees all sessions)
    - Radical Transparency: Tech, Advisor, Marketing (shared session)
    - Private: VC, Coach, Therapists (isolated sessions)
    """
    
    def __init__(self, session_service: Optional[BaseSessionService] = None, scene_id: str = "scene1"):
        """
        Initialize the simulation engine.
        
        Args:
            session_service: Optional session service (defaults to in-memory)
            scene_id: Scene identifier (default: "scene1")
        """
        print("🚀 Initializing Simulation Engine...")
        print(f"   Scene: {scene_id}")
        
        # Store scene ID
        self.scene_id = scene_id
        
        # Session management
        self.session_service = session_service or InMemorySessionService()
        
        # Create all agents
        print("   Creating agents...")
        self.agents = self._create_all_agents()
        print(f"   ✅ Created {len(self.agents)} agents")
        
        # Create runners for each agent
        print("   Setting up runners...")
        self.runners = self._create_runners()
        print(f"   ✅ Created {len(self.runners)} runners")
        
        # Define session routing
        self.session_routing = self._define_session_routing()
        
        # Track conversation history for Sarai's all-knowing view
        # Format: {session_id: [(timestamp, role, speaker, message), ...]}
        self.conversation_history: Dict[str, List[tuple]] = {}
        
        # Debug log for troubleshooting
        self.debug_logs: List[DebugLog] = []
        self.max_debug_logs = 100  # Keep last 100 entries
        
        print("✅ Simulation Engine ready!\n")
    
    def _create_all_agents(self) -> Dict[str, Any]:
        """Create all ADK agents with scene context."""
        agents = {
            'sarai': create_sarai_agent(scene_id=self.scene_id),
            'tech_cofounder': create_tech_cofounder_agent(scene_id=self.scene_id),
            'advisor': create_advisor_agent(scene_id=self.scene_id),
            'marketing_cofounder': create_marketing_cofounder_agent(scene_id=self.scene_id),
            'vc': create_vc_agent(scene_id=self.scene_id),
            'coach': create_coach_agent(scene_id=self.scene_id),
        }
        
        # Add therapist agents (they use compact scene context)
        therapists = create_therapist_agents(scene_id=self.scene_id)
        agents.update(therapists)
        
        return agents
    
    def _create_runners(self) -> Dict[str, Runner]:
        """Create ADK runners for each agent."""
        runners = {}
        
        for agent_name, agent in self.agents.items():
            runners[agent_name] = Runner(
                agent=agent,
                app_name="mentalyc_simulator",
                session_service=self.session_service
            )
        
        return runners
    
    def _define_session_routing(self) -> Dict[str, Dict[str, str]]:
        """
        Define session routing rules for 3-tier architecture.
        
        Returns:
            Dict mapping speaker aliases to session config
        """
        return {
            # Sarai - All-knowing
            'sarai': {
                'agent': 'sarai',
                'tier': 'all_knowing',
                'session_suffix': ''
            },
            
            # Radical Transparency Team (shared session)
            'tech': {
                'agent': 'tech_cofounder',
                'tier': 'radical_transparency',
                'session_suffix': '_shared'
            },
            'tech_cofounder': {
                'agent': 'tech_cofounder',
                'tier': 'radical_transparency',
                'session_suffix': '_shared'
            },
            'advisor': {
                'agent': 'advisor',
                'tier': 'radical_transparency',
                'session_suffix': '_shared'
            },
            'marketing': {
                'agent': 'marketing_cofounder',
                'tier': 'radical_transparency',
                'session_suffix': '_shared'
            },
            'marketing_cofounder': {
                'agent': 'marketing_cofounder',
                'tier': 'radical_transparency',
                'session_suffix': '_shared'
            },
            
            # Private Sessions
            'vc': {
                'agent': 'vc',
                'tier': 'private',
                'session_suffix': '_vc'
            },
            'coach': {
                'agent': 'coach',
                'tier': 'private',
                'session_suffix': '_coach'
            },
            'therapist': {
                'agent': 'therapist_1',
                'tier': 'private',
                'session_suffix': '_therapist1'
            },
            'therapist_1': {
                'agent': 'therapist_1',
                'tier': 'private',
                'session_suffix': '_therapist1'
            },
            'therapist_2': {
                'agent': 'therapist_2',
                'tier': 'private',
                'session_suffix': '_therapist2'
            },
            'therapist_3': {
                'agent': 'therapist_3',
                'tier': 'private',
                'session_suffix': '_therapist3'
            },
        }
    
    def _get_session_config(self, speaker: str) -> Dict[str, str]:
        """
        Get session configuration for a speaker.
        
        Args:
            speaker: Speaker name (e.g., 'tech', 'advisor', 'vc')
        
        Returns:
            Session config dict
        """
        speaker_lower = speaker.lower().strip()
        
        if speaker_lower in self.session_routing:
            return self.session_routing[speaker_lower]
        
        # Default to Sarai for unknown speakers
        return self.session_routing['sarai']
    
    def _build_session_id(self, base_session_id: str, session_suffix: str) -> str:
        """Build full session ID with suffix."""
        if session_suffix:
            return f"{base_session_id}{session_suffix}"
        return base_session_id
    
    def _log(self, level: str, message: str, details: Dict[str, Any] = None) -> None:
        """
        Add a debug log entry.
        
        Args:
            level: 'info', 'warning', or 'error'
            message: Log message
            details: Optional additional details
        """
        log_entry = DebugLog(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            details=details or {}
        )
        self.debug_logs.append(log_entry)
        
        # Keep only the last N entries
        if len(self.debug_logs) > self.max_debug_logs:
            self.debug_logs = self.debug_logs[-self.max_debug_logs:]
        
        # Also print for console debugging
        prefix = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(level, "📝")
        print(f"{prefix} [{level.upper()}] {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def get_debug_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent debug logs as dictionaries."""
        return [
            {
                "timestamp": log.timestamp,
                "level": log.level,
                "message": log.message,
                "details": log.details
            }
            for log in self.debug_logs[-limit:]
        ]
    
    def clear_debug_logs(self) -> None:
        """Clear all debug logs."""
        self.debug_logs = []
    
    def _record_conversation(
        self,
        session_id: str,
        tier: str,
        role: str,
        speaker: str,
        message: str
    ) -> None:
        """
        Record a conversation entry for Sarai's all-knowing view.
        
        Args:
            session_id: The full session ID
            tier: Session tier (radical_transparency, private, all_knowing)
            role: 'user' or 'assistant'
            speaker: Who is speaking (e.g., 'tech_cofounder', 'ceo')
            message: The message content
        """
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'timestamp': datetime.now().isoformat(),
            'tier': tier,
            'role': role,
            'speaker': speaker,
            'message': message
        })
    
    def _get_all_knowing_context(self, base_session_id: str) -> str:
        """
        Aggregate all conversation history for Sarai's all-knowing view.
        
        Args:
            base_session_id: The base session ID (without tier suffixes)
        
        Returns:
            Formatted string of all conversations across all tiers
        """
        # Define the session suffixes we want to aggregate
        session_tiers = {
            '_shared': 'RADICAL TRANSPARENCY TEAM (Tech, Advisor, Marketing)',
            '_vc': 'PRIVATE: VC',
            '_coach': 'PRIVATE: Coach',
            '_therapist1': 'PRIVATE: Therapist 1',
            '_therapist2': 'PRIVATE: Therapist 2',
            '_therapist3': 'PRIVATE: Therapist 3',
        }
        
        context_parts = []
        total_messages = 0
        
        for suffix, tier_name in session_tiers.items():
            full_session_id = f"{base_session_id}{suffix}"
            
            if full_session_id in self.conversation_history:
                messages = self.conversation_history[full_session_id]
                if messages:
                    tier_context = f"\n📍 {tier_name}:\n"
                    for entry in messages:
                        role_label = "CEO" if entry['role'] == 'user' else entry['speaker'].replace('_', ' ').title()
                        tier_context += f"[{role_label}]: {entry['message'][:500]}{'...' if len(entry['message']) > 500 else ''}\n"
                    context_parts.append(tier_context)
                    total_messages += len(messages)
        
        if not context_parts:
            return ""
        
        header = f"""
================================================================================
ALL-KNOWING SESSION HISTORY ({total_messages} messages across all sessions)
================================================================================
"""
        return header + "\n".join(context_parts) + "\n================================================================================\n"
    
    async def handle_input(
        self,
        user_id: str,
        session_id: str,
        speaker: str,
        message: str
    ) -> List[EngineResponse]:
        """
        Handle user input and route to appropriate agent.
        
        Args:
            user_id: User identifier (e.g., 'saul')
            session_id: Base session ID (e.g., 'session-001')
            speaker: Who is speaking (e.g., 'tech', 'advisor', 'sarai')
            message: The message text
        
        Returns:
            List of engine responses
        """
        # Get session configuration
        config = self._get_session_config(speaker)
        agent_name = config['agent']
        tier = config['tier']
        session_suffix = config['session_suffix']
        
        # Build full session ID
        full_session_id = self._build_session_id(session_id, session_suffix)
        
        self._log('info', f"Processing message for {agent_name}", {
            'user_id': user_id,
            'session_id': full_session_id,
            'tier': tier,
            'message_preview': message[:100] + '...' if len(message) > 100 else message
        })
        
        # Get runner for this agent
        runner = self.runners[agent_name]
        
        # Ensure session exists (create if needed)
        try:
            await self.session_service.create_session(
                app_name="mentalyc_simulator",
                user_id=user_id,
                session_id=full_session_id
            )
            self._log('info', f"Session created/verified: {full_session_id}")
        except Exception as e:
            # Session might already exist, that's okay
            self._log('info', f"Session already exists or creation skipped: {str(e)}")
        
        # Prepare the message
        final_message = message
        
        # Special handling for Sarai: Prepend all-knowing context
        if agent_name == 'sarai':
            all_knowing_context = self._get_all_knowing_context(session_id)
            if all_knowing_context:
                final_message = f"{all_knowing_context}\nCURRENT MESSAGE FROM CEO:\n{message}"
                self._log('info', 'Added all-knowing context to Sarai message', {
                    'context_length': len(all_knowing_context)
                })
        
        # Record the user's message (for all-knowing aggregation)
        # Don't record Sarai's own session to avoid duplication
        if tier != 'all_knowing':
            self._record_conversation(
                session_id=full_session_id,
                tier=tier,
                role='user',
                speaker='ceo',
                message=message
            )
        
        # Create ADK content
        content = Content(
            role='user',
            parts=[Part(text=final_message)]
        )
        
        # Run through agent
        responses = []
        collected_text = []
        event_count = 0
        event_types = []
        function_calls = []
        
        try:
            self._log('info', f"Calling ADK runner for {agent_name}...")
            
            events = runner.run_async(
                user_id=user_id,
                session_id=full_session_id,
                new_message=content
            )
            
            async for event in events:
                event_count += 1
                event_type = type(event).__name__
                event_types.append(event_type)
                
                # Log event details
                self._log('info', f"Received event #{event_count}: {event_type}", {
                    'has_content': hasattr(event, 'content') and event.content is not None,
                    'has_actions': hasattr(event, 'actions'),
                })
                
                # Check for function calls
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            func_name = getattr(part.function_call, 'name', 'unknown')
                            function_calls.append(func_name)
                            self._log('info', f"Function call detected: {func_name}")
                        
                        # Collect text parts
                        if hasattr(part, 'text') and part.text:
                            collected_text.append(part.text)
                            self._log('info', f"Collected text part ({len(part.text)} chars)")
            
            self._log('info', f"ADK runner completed", {
                'total_events': event_count,
                'event_types': list(set(event_types)),
                'function_calls': function_calls,
                'text_parts_collected': len(collected_text),
                'total_text_length': sum(len(t) for t in collected_text)
            })
            
            # Combine all collected text into a single response
            if collected_text:
                full_response = "\n".join(collected_text)
                responses.append(EngineResponse(
                    speaker=agent_name,
                    text=full_response,
                    session_id=full_session_id,
                    session_tier=tier,
                    metadata={
                        'base_session_id': session_id,
                        'session_suffix': session_suffix,
                        'original_speaker': speaker,
                        'event_count': event_count,
                        'function_calls': function_calls
                    }
                ))
                self._log('info', f"Response created for {agent_name}", {
                    'response_length': len(full_response)
                })
            else:
                # No text collected - this is the silent failure case
                self._log('warning', f"No text response from {agent_name}", {
                    'total_events': event_count,
                    'event_types': list(set(event_types)),
                    'function_calls': function_calls,
                    'possible_causes': [
                        'Model returned only function calls',
                        'Model returned empty response',
                        'All events had no text content'
                    ]
                })
                # Return an informative message instead of empty
                responses.append(EngineResponse(
                    speaker='system',
                    text=f"⚠️ {agent_name.replace('_', ' ').title()} did not provide a text response. Events received: {event_count}, Function calls: {function_calls or 'none'}. Check debug panel for details.",
                    session_id=full_session_id,
                    session_tier='system',
                    metadata={
                        'warning': 'no_text_response',
                        'event_count': event_count,
                        'event_types': list(set(event_types)),
                        'function_calls': function_calls
                    }
                ))
                
                # Record agent's response (for all-knowing aggregation)
                # Don't record Sarai's own responses
                if tier != 'all_knowing':
                    self._record_conversation(
                        session_id=full_session_id,
                        tier=tier,
                        role='assistant',
                        speaker=agent_name,
                        message=full_response
                    )
        
        except Exception as e:
            # Error handling with detailed logging
            import traceback
            error_traceback = traceback.format_exc()
            
            self._log('error', f"Exception in handle_input for {agent_name}", {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': error_traceback
            })
            
            responses.append(EngineResponse(
                speaker='system',
                text=f"❌ Error from {agent_name.replace('_', ' ').title()}: {type(e).__name__}: {str(e)}",
                session_id=full_session_id,
                session_tier='system',
                metadata={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': error_traceback
                }
            ))
        
        return responses
    
    async def get_session_history(
        self,
        user_id: str,
        session_id: str,
        speaker: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            user_id: User identifier
            session_id: Base session ID
            speaker: Optional speaker to get specific session tier
        
        Returns:
            List of message dicts
        """
        # Determine which session to load
        if speaker:
            config = self._get_session_config(speaker)
            full_session_id = self._build_session_id(session_id, config['session_suffix'])
        else:
            full_session_id = session_id
        
        # Load session from service
        session = await self.session_service.get_session(
            app_name="mentalyc_simulator",
            user_id=user_id,
            session_id=full_session_id
        )
        
        if not session:
            return []
        
        # Extract messages
        messages = []
        if hasattr(session, 'messages'):
            for msg in session.messages:
                messages.append({
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': getattr(msg, 'timestamp', None)
                })
        
        return messages
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all available agents."""
        return [
            {
                'name': name,
                'description': agent.description if hasattr(agent, 'description') else ''
            }
            for name, agent in self.agents.items()
        ]
    
    def get_session_tiers(self) -> Dict[str, List[str]]:
        """Get agents organized by session tier."""
        tiers = {
            'all_knowing': [],
            'radical_transparency': [],
            'private': []
        }
        
        for speaker, config in self.session_routing.items():
            agent = config['agent']
            tier = config['tier']
            if agent not in tiers[tier]:
                tiers[tier].append(agent)
        
        return tiers
    
    def reset_session(self, user_id: str, session_id: str) -> None:
        """
        Reset all session data for a user/session combination.
        
        This clears:
        - All conversation history for Sarai's all-knowing view
        - Recreates the session service to clear ADK session state
        
        Args:
            user_id: User identifier
            session_id: Base session ID
        """
        print(f"🔄 Resetting session for user={user_id}, session={session_id}")
        
        # Clear conversation history for all session tiers
        session_suffixes = ['', '_shared', '_vc', '_coach', '_therapist1', '_therapist2', '_therapist3']
        for suffix in session_suffixes:
            full_session_id = f"{session_id}{suffix}"
            if full_session_id in self.conversation_history:
                del self.conversation_history[full_session_id]
                print(f"   Cleared history for: {full_session_id}")
        
        # Reset the session service (creates fresh in-memory storage)
        self.session_service = InMemorySessionService()
        
        # Recreate runners with the new session service
        self.runners = self._create_runners()
        
        print("✅ Session reset complete")


# ============================================================================
# Test Functions
# ============================================================================

async def test_first_conversation():
    """Test first conversation with Tech Cofounder."""
    print("=" * 60)
    print("TEST: First Conversation with Tech Cofounder")
    print("=" * 60)
    
    # Create engine
    engine = SimulationEngine()
    
    # Test parameters
    user_id = "saul"
    session_id = "test-001"
    
    # Ask Tech Cofounder a question
    print("\n💬 CEO: How late is the website project? Look at the engineering status report.\n")
    
    responses = await engine.handle_input(
        user_id=user_id,
        session_id=session_id,
        speaker="tech",
        message="How late is the website project? Look at the engineering status report and give me specifics."
    )
    
    # Display responses
    for response in responses:
        print(f"🤖 {response.speaker.upper()}:")
        print(f"{response.text}\n")
        print(f"   Session: {response.session_id}")
        print(f"   Tier: {response.session_tier}\n")
    
    print("=" * 60)
    print("✅ Test complete!")
    print("=" * 60)


async def test_session_routing():
    """Test session routing across different tiers."""
    print("\n" + "=" * 60)
    print("TEST: Session Routing (3-Tier Architecture)")
    print("=" * 60)
    
    engine = SimulationEngine()
    user_id = "saul"
    session_id = "test-002"
    
    # Test radical transparency (shared session)
    print("\n1️⃣ Testing Radical Transparency (Tech, Advisor, Marketing share session)")
    
    print("\n   CEO → Tech: What's our technical status?")
    await engine.handle_input(user_id, session_id, "tech", "What's our technical status?")
    
    print("   CEO → Advisor: What should we prioritize?")
    await engine.handle_input(user_id, session_id, "advisor", "What should we prioritize?")
    
    print("   ✅ Both use session: test-002_shared\n")
    
    # Test private sessions
    print("2️⃣ Testing Private Sessions (VC, Coach isolated)")
    
    print("\n   CEO → VC: How are we doing on fundraising?")
    await engine.handle_input(user_id, session_id, "vc", "How are we doing on fundraising?")
    
    print("   CEO → Coach: I'm feeling overwhelmed.")
    await engine.handle_input(user_id, session_id, "coach", "I'm feeling overwhelmed.")
    
    print("   ✅ VC uses: test-002_vc")
    print("   ✅ Coach uses: test-002_coach\n")
    
    # Show session tiers
    print("3️⃣ Session Tier Organization:")
    tiers = engine.get_session_tiers()
    for tier_name, agents in tiers.items():
        print(f"\n   {tier_name.upper()}:")
        for agent in agents:
            print(f"      - {agent}")
    
    print("\n" + "=" * 60)
    print("✅ Session routing test complete!")
    print("=" * 60)


async def test_agent_list():
    """Test listing all agents."""
    print("\n" + "=" * 60)
    print("TEST: Agent Inventory")
    print("=" * 60)
    
    engine = SimulationEngine()
    agents = engine.list_agents()
    
    print(f"\n📋 Total Agents: {len(agents)}\n")
    
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent['name']}")
        if agent['description']:
            print(f"   {agent['description'][:80]}...")
        print()
    
    print("=" * 60)
    print("✅ Agent list test complete!")
    print("=" * 60)


async def main():
    """Run all tests."""
    print("\n" + "🎯" * 30)
    print("SIMULATION ENGINE - ADK VERSION")
    print("🎯" * 30 + "\n")
    
    # Test 1: First conversation
    await test_first_conversation()
    
    # Test 2: Session routing
    await test_session_routing()
    
    # Test 3: Agent list
    await test_agent_list()
    
    print("\n" + "🎉" * 30)
    print("ALL TESTS COMPLETE!")
    print("🎉" * 30 + "\n")
    
    print("Next steps:")
    print("1. Review the responses above")
    print("2. Check that documents were referenced")
    print("3. Verify session routing worked correctly")
    print("4. Try your own conversations!")
    print()


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment")
        print("   Please create a .env file with your API key")
        print("   Get one at: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main())

