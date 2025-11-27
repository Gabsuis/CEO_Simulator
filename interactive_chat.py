"""
Interactive Chat with CEO Simulator Agents

Have free-form conversations with any agent in the system.
Maintains conversation history across messages.
Saves transcript to txt file on exit.

Usage:
    python interactive_chat.py
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ Error: GOOGLE_API_KEY not found")
    print("   Create a .env file with: GOOGLE_API_KEY=your_key_here")
    sys.exit(1)

from simulation_engine_adk import SimulationEngine


class InteractiveChat:
    """Interactive chat interface for CEO Simulator agents."""
    
    def __init__(self):
        # Initialize transcript log
        self.transcript = []
        self._log("=" * 80)
        self._log("CEO SIMULATOR - INTERACTIVE CHAT")
        self._log(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log("=" * 80)
        
        print("\n" + "=" * 80)
        print("CEO SIMULATOR - INTERACTIVE CHAT")
        print("=" * 80 + "\n")
        
        print("Initializing simulation engine...")
        self._log("\nInitializing simulation engine...")
        self.engine = SimulationEngine()
        
        self.user_id = "saul"
        self.session_id = "interactive"
        self.current_agent = None
        self.agents = [a['name'] for a in self.engine.list_agents()]
        
        msg = f"\nEngine ready! {len(self.agents)} agents available"
        print(f"✅{msg}")
        self._log(msg)
        
        print(f"\nAvailable agents:")
        self._log("\nAvailable agents:")
        for i, agent in enumerate(self.agents, 1):
            line = f"  {i}. {agent}"
            print(line)
            self._log(line)
    
    def _log(self, text: str):
        """Add text to transcript."""
        self.transcript.append(text)
    
    def _save_transcript(self):
        """Save transcript to file."""
        # Create transcripts folder if needed
        transcripts_dir = Path(__file__).parent / "transcripts"
        transcripts_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = transcripts_dir / f"chat_transcript_{timestamp}.txt"
        
        # Add session end marker
        self._log("\n" + "=" * 80)
        self._log(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log("=" * 80)
        
        # Write transcript
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.transcript))
        
        print(f"\n📝 Transcript saved to: {filename}")
        return filename
    
    async def select_agent(self):
        """Let user select an agent to chat with."""
        while True:
            header = "\n" + "=" * 70 + "\nSELECT AN AGENT\n" + "=" * 70
            print(header)
            self._log(header)
            
            print("\nAvailable agents:")
            for i, agent in enumerate(self.agents, 1):
                print(f"  {i}. {agent}")
            
            print("\nOptions:")
            print("  0. Exit")
            print("  Type agent number or agent name")
            
            choice = input("\n👤 Select agent (or 0 to exit): ").strip()
            self._log(f"\n[User selection]: {choice}")
            
            if choice == "0":
                print("\n👋 Goodbye!")
                self._log("\n[User exited]")
                return False
            
            # Try as number
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.agents):
                    self.current_agent = self.agents[idx]
                    msg = f"\nSelected: {self.current_agent}"
                    print(f"✅{msg}")
                    self._log(msg)
                    return True
            except ValueError:
                pass
            
            # Try as name
            if choice in self.agents:
                self.current_agent = choice
                msg = f"\nSelected: {self.current_agent}"
                print(f"✅{msg}")
                self._log(msg)
                return True
            
            print("❌ Invalid selection. Try again.")
    
    async def chat(self):
        """Chat with the selected agent."""
        header = f"\n{'=' * 70}\nCHATTING WITH: {self.current_agent.upper()}\n{'=' * 70}"
        print(header)
        self._log(header)
        
        print("\nType your message and press Enter.")
        print("Type 'switch' to switch to a different agent (no restart!).")
        print("Type 'exit' to quit.\n")
        print("Quick agent switch: Type agent number (1-9) to switch instantly!")
        print("   or agent name (e.g., 'advisor', 'tech_cofounder')\n")
        
        message_count = 0
        
        while True:
            # Get user input
            prompt = f"\nYou: "
            user_message = input(prompt).strip()
            
            # Handle commands
            if user_message.lower() == "exit":
                print("\n👋 Goodbye!")
                self._log("\n[User exited]")
                return False
            
            if user_message.lower() == "switch":
                print("\n🔄 Switching agent...")
                self._log("\n[User switching agent]")
                return True
            
            # Check if user wants to switch to a specific agent
            # Try as number
            try:
                idx = int(user_message) - 1
                if 0 <= idx < len(self.agents):
                    agent_name = self.agents[idx]
                    print(f"\n🔄 Switching to {agent_name}...")
                    self._log(f"\n[Switched to {agent_name}]")
                    self.current_agent = agent_name
                    print(f"✅ Now chatting with: {self.current_agent.upper()}\n")
                    continue
            except ValueError:
                pass
            
            # Try as agent name
            if user_message in self.agents:
                print(f"\n🔄 Switching to {user_message}...")
                self._log(f"\n[Switched to {user_message}]")
                self.current_agent = user_message
                print(f"✅ Now chatting with: {self.current_agent.upper()}\n")
                continue
            
            if not user_message:
                print("(empty message - try again)")
                continue
            
            # Log user message
            self._log(f"\n[{self.current_agent.upper()}]")
            self._log(f"You: {user_message}")
            
            # Show thinking
            print(f"\n⏳ {self.current_agent.title()} is thinking...\n")
            
            try:
                # Send message to agent
                responses = await self.engine.handle_input(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    speaker=self.current_agent,
                    message=user_message
                )
                
                # Display response
                if responses:
                    for response in responses:
                        speaker_name = response.speaker.replace('_', ' ').title()
                        print(f"🤖 {speaker_name}:")
                        print("-" * 70)
                        print(response.text)
                        print("-" * 70)
                        
                        # Log response
                        self._log(f"\n{speaker_name}:")
                        self._log(response.text)
                        
                        message_count += 1
                        print(f"\n📊 Message #{message_count} | Session: {response.session_id}")
                else:
                    print("❌ No response received")
                    self._log("[No response received]")
            
            except Exception as e:
                print(f"\n❌ Error: {e}")
                self._log(f"[Error: {e}]")
                print("Try again or type 'switch' to select a different agent.")
    
    async def run(self):
        """Main conversation loop."""
        try:
            while True:
                # Select agent
                if not await self.select_agent():
                    break
                
                # Chat with agent
                if not await self.chat():
                    break
        
        except KeyboardInterrupt:
            print("\n\n⛔ Chat interrupted")
            self._log("\n[Chat interrupted by user]")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self._log(f"\n[Error: {e}]")
            import traceback
            traceback.print_exc()
        finally:
            # Always save transcript on exit
            self._save_transcript()


async def main():
    """Main entry point."""
    chat = InteractiveChat()
    await chat.run()


if __name__ == "__main__":
    asyncio.run(main())

