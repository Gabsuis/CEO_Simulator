"""
Interactive Conversation Script

Chat with any agent in the simulation interactively.

Usage:
    python interactive_conversation.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ Error: GOOGLE_API_KEY not found")
    print("   Create a .env file with: GOOGLE_API_KEY=your_key_here")
    print("   Get your key at: https://aistudio.google.com/apikey")
    sys.exit(1)

from simulation_engine_adk import SimulationEngine


def print_header():
    """Print welcome header."""
    print("\n" + "🎭" * 30)
    print("MENTALYC CEO SIMULATOR - INTERACTIVE MODE")
    print("🎭" * 30 + "\n")


def print_agents(engine):
    """Print available agents."""
    print("📋 Available Agents:\n")
    
    tiers = engine.get_session_tiers()
    
    print("🌟 ALL-KNOWING:")
    print("   • sarai - Meta-orchestrator (can transfer to others)\n")
    
    print("🤝 RADICAL TRANSPARENCY (shared session):")
    print("   • tech - Tech Cofounder (engineering, backlogs)")
    print("   • advisor - Strategic Advisor (all company docs)")
    print("   • marketing - Marketing Cofounder (GTM, positioning)\n")
    
    print("🔒 PRIVATE (isolated sessions):")
    print("   • vc - Venture Capitalist (board-level only)")
    print("   • coach - Leadership Coach (personal development)")
    print("   • therapist - Customer (therapist persona)\n")


def print_help():
    """Print help commands."""
    print("💡 Commands:")
    print("   /agents  - List available agents")
    print("   /switch  - Switch to a different agent")
    print("   /history - Show conversation history")
    print("   /help    - Show this help")
    print("   /quit    - Exit the conversation")
    print()


async def interactive_loop(engine, user_id="saul", session_id="interactive-001"):
    """Run interactive conversation loop."""
    
    current_agent = None
    conversation_count = 0
    
    print_help()
    
    while True:
        # Agent selection
        if current_agent is None:
            print_agents(engine)
            agent_input = input("👤 Select an agent to talk to: ").strip().lower()
            
            # Validate agent
            valid_agents = ['sarai', 'tech', 'advisor', 'marketing', 'vc', 'coach', 'therapist']
            if agent_input not in valid_agents:
                print(f"❌ Unknown agent: {agent_input}")
                print(f"   Valid options: {', '.join(valid_agents)}\n")
                continue
            
            current_agent = agent_input
            print(f"\n✅ Now talking to: {current_agent.upper()}")
            print(f"💬 Type your message (or /help for commands)\n")
        
        # Get user input
        user_input = input("💼 CEO: ").strip()
        
        # Handle empty input
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith('/'):
            command = user_input.lower()
            
            if command == '/quit':
                print("\n👋 Goodbye! Thanks for using the simulator.")
                break
            
            elif command == '/help':
                print()
                print_help()
                continue
            
            elif command == '/agents':
                print()
                print_agents(engine)
                continue
            
            elif command == '/switch':
                current_agent = None
                print("\n🔄 Switching agents...\n")
                continue
            
            elif command == '/history':
                print("\n📜 Conversation history:")
                print(f"   Total messages: {conversation_count}")
                print(f"   Current agent: {current_agent}")
                print(f"   Session ID: {session_id}\n")
                continue
            
            else:
                print(f"❌ Unknown command: {command}")
                print("   Type /help for available commands\n")
                continue
        
        # Send message to agent
        print(f"\n⏳ {current_agent.title()} is thinking...\n")
        
        try:
            responses = await engine.handle_input(
                user_id=user_id,
                session_id=session_id,
                speaker=current_agent,
                message=user_input
            )
            
            # Display responses
            for response in responses:
                agent_name = response.speaker.replace('_', ' ').title()
                print(f"🤖 {agent_name}:")
                print("-" * 60)
                print(response.text)
                print("-" * 60)
                print()
            
            conversation_count += 1
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("   Please try again or switch agents.\n")
        
        # Prompt for next message
        print()


async def main():
    """Main function."""
    print_header()
    
    print("🔧 Initializing simulation engine...")
    engine = SimulationEngine()
    
    print("\n✅ Engine ready! Starting interactive conversation...\n")
    
    try:
        await interactive_loop(engine)
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

