"""
CEO Simulator - Streamlit Web Interface

Deploy to Streamlit Cloud: https://share.streamlit.io/
Local: streamlit run streamlit_app.py
"""

import streamlit as st
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# CHARACTER INTRODUCTION HELPERS
# ============================================================================

def get_character_image_path(character_name):
    """Get the path to character image"""
    image_map = {
        "sarai": "sarai.png",
        "tech_cofounder": "tech_cofounder.png",
        "advisor": "advisor.png",
        "marketing_cofounder": "marketing_cofounder.png",
        "vc": "vc.png",
        "coach": "coach.png",
        "therapist_1": "therapist_analytical.png",
        "therapist_2": "therapist_empathic.png",
        "therapist_3": "therapist_skeptical.png"
    }
    return f"Documents/assets/characters/{image_map.get(character_name, 'sarai.png')}"

def normalize_character_key(character_name):
    """Normalize character names for tracking"""
    if character_name.startswith('therapist_'):
        return 'therapist_customers'  # All therapists share the same base spec
    return character_name.lower().replace(' ', '_')

def show_character_introduction(character_name, character_spec):
    """Display character introduction with image and key info"""

    # Load character image
    image_path = get_character_image_path(character_name)
    try:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(image_path, width=150, use_column_width=False)
        with col2:
            st.markdown("---")
    except:
        # Fallback emoji if image fails
        emoji_map = {
            "sarai": "🧠", "tech_cofounder": "👨‍💻", "advisor": "🎯",
            "marketing_cofounder": "📈", "vc": "💰", "coach": "🏆"
        }
        st.markdown(f"<div style='font-size: 80px; text-align: center; margin: 20px 0;'>{emoji_map.get(character_name, '🤖')}</div>", unsafe_allow_html=True)

    # Character info card
    identity = character_spec.get('identity', {})
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
        <h2 style="margin-top: 0;">{identity.get('name', character_name.title())}</h2>
        <h3 style="opacity: 0.9; margin-bottom: 15px;">{identity.get('in_world_title', 'AI Agent')}</h3>
        <p style="font-style: italic; margin-bottom: 15px;">"{identity.get('tagline', 'AI assistant')}"</p>
    </div>
    """, unsafe_allow_html=True)

    # Personality traits
    personality = character_spec.get('personality', {})
    if 'traits' in personality and personality['traits']:
        with st.expander("🔍 Key Personality Traits", expanded=True):
            for trait in personality['traits'][:3]:  # Show top 3
                st.markdown(f"• {trait}")

    # Quick backstory
    if 'backstory' in identity:
        with st.expander("📖 Quick Background", expanded=False):
            st.markdown(identity['backstory'])

    st.markdown("---")
    st.info("💡 **Pro tip:** This character only appears once per session. Get to know them!")

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="CEO Simulator",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .header { 
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .agent-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        background: #667eea;
        color: white;
        font-weight: bold;
        margin: 5px 5px 5px 0;
    }
    .chat-message {
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .message-user {
        background: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .message-assistant {
        background: #f5f5f5;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CHECK API KEY
# ============================================================================

if not os.getenv("GOOGLE_API_KEY"):
    st.error("❌ API Key not found!")
    st.info("""
    ### Setup Instructions:
    
    **Local Development:**
    1. Create `.streamlit/secrets.toml`
    2. Add: `GOOGLE_API_KEY = "your-key-here"`
    3. Restart the app
    
    **Streamlit Cloud:**
    1. Deploy your repo to GitHub
    2. Go to app settings → Secrets
    3. Add your `GOOGLE_API_KEY`
    """)
    st.stop()

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

# Engine version - increment this to force cache refresh when engine code changes
ENGINE_VERSION = "2.0"

@st.cache_resource
def get_simulation_engine(_version: str):
    """Initialize simulation engine (cached across reruns).
    
    The _version parameter forces cache invalidation when we update the engine.
    """
    from simulation_engine_adk import SimulationEngine
    return SimulationEngine()

# Initialize session state
if "engine" not in st.session_state:
    st.session_state.engine = get_simulation_engine(ENGINE_VERSION)

# Check if engine needs refresh (version mismatch or missing new methods)
if not hasattr(st.session_state.engine, 'get_debug_logs'):
    # Clear the cache and reinitialize
    get_simulation_engine.clear()
    st.session_state.engine = get_simulation_engine(ENGINE_VERSION)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_agent" not in st.session_state:
    agents = [a['name'] for a in st.session_state.engine.list_agents()]
    st.session_state.current_agent = "sarai"

if "user_id" not in st.session_state:
    st.session_state.user_id = f"streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "message_count" not in st.session_state:
    st.session_state.message_count = 0

if "introduced_characters" not in st.session_state:
    st.session_state.introduced_characters = set()  # Track which characters have been introduced

# ============================================================================
# SIDEBAR - AGENT SELECTION & INFO
# ============================================================================

with st.sidebar:
    st.markdown("### 🎮 CEO Simulator")
    st.divider()
    
    # Agent selection
    agents = [a['name'] for a in st.session_state.engine.list_agents()]
    agent_display = [a.replace('_', ' ').title() for a in agents]
    
    selected_idx = agent_display.index(
        st.session_state.current_agent.replace('_', ' ').title()
    )
    
    selected_display = st.selectbox(
        "Select Character",
        agent_display,
        index=selected_idx,
        key="agent_selector"
    )
    
    st.session_state.current_agent = agents[agent_display.index(selected_display)]
    
    st.divider()
    
    # Current session info
    st.markdown("**📊 Session Info**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", st.session_state.message_count)
    with col2:
        st.metric("Current Agent", selected_display)
    
    # Character description (if available)
    st.markdown("---")
    st.markdown("**ℹ️ About This Character**")
    
    agent_info = {
        "sarai": "Meta-orchestrator with access to all sessions. Routes conversations and provides evaluations.",
        "tech_cofounder": "Pragmatic engineer. Focuses on feasibility, trade-offs, and technical reality.",
        "advisor": "Strategic thinker. Asks probing questions and connects dots across domains.",
        "marketing_cofounder": "Customer-obsessed marketer. Focuses on GTM and customer research.",
        "vc": "Board-level investor. High-level strategy and market opportunity focus.",
        "coach": "Executive coach. Leadership development and personal growth focus.",
        "therapist_1": "Customer persona 1. Real-world user feedback and pain points.",
        "therapist_2": "Customer persona 2. Real-world user feedback and pain points.",
        "therapist_3": "Customer persona 3. Real-world user feedback and pain points.",
    }
    
    description = agent_info.get(st.session_state.current_agent, "AI agent")
    st.markdown(f"> {description}")
    
    # Controls
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Clear Chat", use_container_width=True):
            # Reset the ADK session state in the engine
            st.session_state.engine.reset_session(
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id
            )
            # Generate new session ID to ensure fresh start
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # Clear UI state
            st.session_state.messages = []
            st.session_state.message_count = 0
            st.session_state.introduced_characters = set()  # Reset introductions
            st.rerun()
    with col2:
        # Generate transcript for download
        if st.session_state.messages:
            transcript_lines = [
                "=" * 60,
                "CEO SIMULATOR - CHAT TRANSCRIPT",
                f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 60,
                ""
            ]
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    transcript_lines.append(f"You: {msg['content']}")
                else:
                    transcript_lines.append(f"{msg['agent']}: {msg['content']}")
                transcript_lines.append("")
            transcript_lines.append("=" * 60)
            transcript_text = "\n".join(transcript_lines)
            
            st.download_button(
                label="📥 Export",
                data=transcript_text,
                file_name=f"ceo_sim_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.button("📥 Export", use_container_width=True, disabled=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 12px;">
    Made with 🎨 Streamlit<br>
    Powered by 🧠 Google Gemini
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN CHAT AREA
# ============================================================================

# Header
st.markdown(f"""
<div class="header">
    <h1>🎮 Chatting with {st.session_state.current_agent.replace('_', ' ').title()}</h1>
    <p>Free-form conversation. Switch agents anytime!</p>
</div>
""", unsafe_allow_html=True)

# Message display area
message_container = st.container()

with message_container:
    # Display all messages
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message message-user">
                <strong>👤 You:</strong><br>{msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message message-assistant">
                <strong>🤖 {msg["agent"]}:</strong><br>{msg["content"]}
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# CHAT INPUT
# ============================================================================

st.divider()

col1, col2 = st.columns([0.85, 0.15])

with col1:
    user_input = st.chat_input(
        f"Type your message to {st.session_state.current_agent.replace('_', ' ').title()}...",
        key="chat_input"
    )

with col2:
    # Quick commands
    st.markdown("**Quick:**")
    if st.button("Switch", use_container_width=True, key="switch_btn"):
        st.session_state.show_agent_selector = True

# ============================================================================
# PROCESS INPUT
# ============================================================================

if user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message immediately
    st.markdown(f"""
    <div class="chat-message message-user">
        <strong>👤 You:</strong><br>{user_input}
    </div>
    """, unsafe_allow_html=True)
    
    # Get response from agent
    with st.spinner(f"✨ {st.session_state.current_agent.replace('_', ' ').title()} is thinking..."):
        try:
            # Run async function in sync context
            async def get_response():
                return await st.session_state.engine.handle_input(
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.session_id,
                    speaker=st.session_state.current_agent,
                    message=user_input
                )
            
            # Create event loop and run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            responses = loop.run_until_complete(get_response())
            loop.close()
            
            if responses:
                for response in responses:
                    agent_name = response.speaker.replace('_', ' ').title()
                    character_key = normalize_character_key(response.speaker)

                    # Check if this is the first time meeting this character
                    if character_key not in st.session_state.introduced_characters:
                        # Load character spec and show introduction
                        try:
                            from engine.character_loader import CharacterLoader
                            loader = CharacterLoader()
                            char_spec = loader.load_character(character_key)

                            st.markdown("---")
                            show_character_introduction(response.speaker, char_spec)
                            st.markdown("---")

                            # Mark as introduced
                            st.session_state.introduced_characters.add(character_key)

                            # Add a small delay for dramatic effect
                            time.sleep(1)

                        except Exception as e:
                            st.warning(f"Could not load character introduction: {e}")

                    # Add to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "agent": agent_name,
                        "content": response.text
                    })

                    # Display response
                    st.markdown(f"""
                    <div class="chat-message message-assistant">
                        <strong>🤖 {agent_name}:</strong><br>{response.text}
                    </div>
                    """, unsafe_allow_html=True)

                    st.session_state.message_count += 1
            else:
                st.error("❌ No response received from the agent. Try again.")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Check that your GOOGLE_API_KEY is set correctly.")
    
    st.rerun()

# ============================================================================
# EMPTY STATE
# ============================================================================

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 40px; color: #999;">
        <h3>👋 Welcome to CEO Simulator</h3>
        <p>Select a character and start a conversation!</p>
        <p style="font-size: 12px;">
            💡 Tip: You can switch characters at any time without losing your chat history.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# DEBUG PANEL
# ============================================================================

with st.expander("🔧 Debug Panel", expanded=False):
    # Basic info row
    st.markdown("### 📊 Session Info")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("User ID", st.session_state.user_id[-8:])
    with col2:
        st.metric("Session ID", st.session_state.session_id[-15:])
    with col3:
        st.metric("Messages", st.session_state.message_count)
    with col4:
        st.metric("API Key", "✅" if os.getenv("GOOGLE_API_KEY") else "❌")

    # Engine status
    st.markdown("### 🔧 Engine Status")
    has_debug = hasattr(st.session_state.engine, 'get_debug_logs')
    has_reset = hasattr(st.session_state.engine, 'reset_session')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Debug Available", "✅" if has_debug else "❌")
    with col2:
        st.metric("Reset Available", "✅" if has_reset else "❌")
    with col3:
        if st.button("🔄 Force Refresh", use_container_width=True, help="Force reload the engine if it's outdated"):
            # Clear the engine cache and reinitialize
            get_simulation_engine.clear()
            st.session_state.engine = get_simulation_engine(ENGINE_VERSION)
            st.success("Engine refreshed! Refreshing page...")
            st.rerun()

    if not has_debug or not has_reset:
        st.warning("⚠️ Engine may be outdated. Use the 'Force Refresh' button or clear cache.")
        st.info("**Alternative:** Click hamburger menu (☰) → 'Clear cache' → 'Rerun'")
    
    st.divider()
    
    # Debug logs section
    st.markdown("### 📋 Engine Debug Logs")
    
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        log_limit = st.slider("Show last N logs", min_value=5, max_value=50, value=15)
    with col2:
        if st.button("🗑️ Clear Logs"):
            st.session_state.engine.clear_debug_logs()
            st.success("Logs cleared!")
    
    # Get and display logs
    try:
        if not hasattr(st.session_state.engine, 'get_debug_logs'):
            st.error("⚠️ Debug panel not available. Please refresh the page to update the engine.")
            st.info("**To fix:** Click the hamburger menu (☰) → 'Clear cache' → 'Rerun'")
            logs = []
        else:
            logs = st.session_state.engine.get_debug_logs(limit=log_limit)
        
        if logs:
            for log in reversed(logs):  # Most recent first
                # Color code by level
                level_colors = {
                    'info': '🔵',
                    'warning': '🟡', 
                    'error': '🔴'
                }
                level_icon = level_colors.get(log['level'], '⚪')
                
                # Format timestamp
                timestamp = log['timestamp'].split('T')[1].split('.')[0] if 'T' in log['timestamp'] else log['timestamp']
                
                # Create expandable log entry
                with st.container():
                    st.markdown(f"**{level_icon} [{timestamp}] {log['message']}**")
                    
                    if log['details']:
                        with st.expander("Details", expanded=log['level'] == 'error'):
                            for key, value in log['details'].items():
                                if key == 'traceback':
                                    st.code(value, language='python')
                                elif isinstance(value, list):
                                    st.write(f"**{key}:** {', '.join(str(v) for v in value)}")
                                else:
                                    st.write(f"**{key}:** {value}")
                    
                    st.markdown("---")
        else:
            st.info("No debug logs yet. Send a message to generate logs.")
    except Exception as e:
        st.error(f"Error loading logs: {e}")
    
    st.divider()
    
    # Last response metadata
    st.markdown("### 📨 Last Response Details")
    if st.session_state.messages:
        last_msg = st.session_state.messages[-1]
        if last_msg.get('role') == 'assistant':
            st.json({
                "agent": last_msg.get('agent', 'unknown'),
                "content_length": len(last_msg.get('content', '')),
                "content_preview": last_msg.get('content', '')[:200] + '...' if len(last_msg.get('content', '')) > 200 else last_msg.get('content', '')
            })
        else:
            st.info("Last message was from user, not an agent.")
    else:
        st.info("No messages yet.")
    
    st.divider()
    
    # Conversation history (for Sarai's all-knowing view)
    st.markdown("### 🗂️ Conversation History (All Sessions)")
    try:
        history = st.session_state.engine.conversation_history
        if history:
            for session_key, messages in history.items():
                with st.expander(f"Session: {session_key} ({len(messages)} messages)"):
                    for msg in messages[-5:]:  # Show last 5 per session
                        role_icon = "👤" if msg['role'] == 'user' else "🤖"
                        st.markdown(f"{role_icon} **{msg['speaker']}**: {msg['message'][:100]}...")
        else:
            st.info("No conversation history recorded yet.")
    except Exception as e:
        st.error(f"Error loading history: {e}")

