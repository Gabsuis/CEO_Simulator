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

def get_character_avatar(character_name):
    """Get avatar URL or emoji for character"""
    avatars = {
        "sarai": "🧠",
        "tech_cofounder": "👨‍💻",
        "advisor": "🎯",
        "marketing_cofounder": "📈",
        "vc": "💰",
        "coach": "🏆",
        "therapist_1": "👥",
        "therapist_2": "👥",
        "therapist_3": "👥"
    }
    return avatars.get(character_name.lower(), "🤖")

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
    identity = character_spec.get_identity()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
        <h2 style="margin-top: 0;">{identity.get('name', character_name.title())}</h2>
        <h3 style="opacity: 0.9; margin-bottom: 15px;">{identity.get('in_world_title', 'AI Agent')}</h3>
        <p style="font-style: italic; margin-bottom: 15px;">"{identity.get('tagline', 'AI assistant')}"</p>
    </div>
    """, unsafe_allow_html=True)

    # Personality traits
    personality = character_spec.spec_data.get('personality', {})
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

# Custom CSS - Enhanced for Dream UI
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
    .agent-badge-new {
        background: linear-gradient(45deg, #ff6b6b, #ffa500) !important;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.3);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 10px rgba(255, 107, 107, 0.3); }
        50% { box-shadow: 0 0 20px rgba(255, 107, 107, 0.6); }
    }

    /* Enhanced Message Styling */
    .chat-message {
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .chat-message:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    .message-user {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196F3;
        margin-left: 20px;
        margin-right: 60px;
    }
    .message-assistant {
        background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
        border-left: 4px solid #667eea;
        margin-right: 20px;
        margin-left: 60px;
    }

    /* Avatar Styling */
    .agent-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        margin-right: 16px;
        border: 3px solid #667eea;
        object-fit: cover;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .agent-avatar:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }

    /* Typing Indicator */
    .message-typing {
        animation: typing 1.5s infinite;
        display: inline-block;
    }
    @keyframes typing {
        0%, 60%, 100% { opacity: 1; }
        30% { opacity: 0.3; }
    }

    /* Dream UI Elements */
    .dream-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    .dream-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        text-align: center;
    }
    .character-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }
    .character-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .character-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    .character-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
    }

    /* Scene Elements */
    .scene-banner {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        text-align: center;
    }

    /* Meeting Panel Styling */
    .meeting-panel {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
    }

    /* Top Bar Styling */
    .topbar-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .topbar-collapsed {
        height: 70px;
    }
    .topbar-expanded {
        height: auto;
        max-height: 60vh;
        overflow-y: auto;
    }
    .topbar-content {
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .topbar-main {
        display: flex;
        align-items: center;
        gap: 20px;
        flex: 1;
    }
    .topbar-controls {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .character-selector-compact {
        min-width: 250px;
    }
    .topbar-toggle {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    .topbar-toggle:hover {
        background: rgba(255,255,255,0.3);
    }
    .topbar-expanded-content {
        padding: 0 16px 16px 16px;
        border-top: 1px solid rgba(255,255,255,0.2);
    }

    /* Push main content down when topbar is present */
    .main-content-spacer {
        margin-top: 90px;
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

if "selected_characters" not in st.session_state:
    st.session_state.selected_characters = set()  # Track which characters have been selected

if "topbar_expanded" not in st.session_state:
    st.session_state.topbar_expanded = True  # Track if top bar is expanded

# ============================================================================
# TOP BAR - AGENT SELECTION & INFO
# ============================================================================

# Top Bar Container
topbar_class = "topbar-expanded" if st.session_state.topbar_expanded else "topbar-collapsed"

st.markdown(f"""
<div class="topbar-container {topbar_class}">
    <div class="topbar-content">
        <div class="topbar-main">
            <h3 style="margin: 0; color: white;">🎮 CEO Simulator</h3>
""", unsafe_allow_html=True)

# Agent selection (always visible)
agents = [a['name'] for a in st.session_state.engine.list_agents()]

# Create display names with new character indicators
agent_display = []
agent_map = {}  # Map display name back to agent ID

for agent in agents:
    agent_title = agent.replace('_', ' ').title()
    is_new = agent not in st.session_state.selected_characters
    display_name = f"🆕 {agent_title}" if is_new else f"👤 {agent_title}"
    agent_display.append(display_name)
    agent_map[display_name] = agent

# Find current agent's display name in the list
current_agent_title = st.session_state.current_agent.replace('_', ' ').title()
current_is_new = st.session_state.current_agent not in st.session_state.selected_characters
current_display = f"🆕 {current_agent_title}" if current_is_new else f"👤 {current_agent_title}"

# Find the index, default to 0 if not found (shouldn't happen but safety check)
try:
    selected_idx = agent_display.index(current_display)
except ValueError:
    selected_idx = 0  # Default to first agent if current not found

# Character selector (always visible)
selected_display = st.selectbox(
    "Character",
    agent_display,
    index=selected_idx,
    key="character_selector",
    label_visibility="collapsed"
)

# Get the actual agent name from the map
selected_agent_name = agent_map.get(selected_display, agents[0])

# Check if this is a new character selection
previous_agent = st.session_state.get('current_agent', None)
st.session_state.current_agent = selected_agent_name

st.markdown("""
        </div>
        <div class="topbar-controls">
""", unsafe_allow_html=True)

# Toggle button
toggle_label = "🔽 Collapse" if st.session_state.topbar_expanded else "🔼 Expand"
if st.button(toggle_label, key="topbar_toggle"):
    st.session_state.topbar_expanded = not st.session_state.topbar_expanded
    st.rerun()

st.markdown("""
        </div>
    </div>
""", unsafe_allow_html=True)

# Expanded content (only show when expanded)
if st.session_state.topbar_expanded:
    st.markdown('<div class="topbar-expanded-content">', unsafe_allow_html=True)

    # Show introduction for newly selected characters
    if st.session_state.current_agent != previous_agent and st.session_state.current_agent not in st.session_state.selected_characters:
        try:
            from engine.character_loader import CharacterLoader
            loader = CharacterLoader()
            char_spec = loader.load_character(normalize_character_key(st.session_state.current_agent))

            show_character_introduction(st.session_state.current_agent, char_spec)

            # Mark as selected
            st.session_state.selected_characters.add(st.session_state.current_agent)

        except Exception as e:
            st.warning(f"Could not load character introduction: {e}")

    # Enhanced Dream UI Session Info
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); padding: 16px; border-radius: 12px; margin: 16px 0;">
        <h4 style="margin-top: 0; color: #667eea;">📊 Session Dashboard</h4>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 Messages", st.session_state.message_count)
        st.metric("🎭 Characters Met", len(st.session_state.selected_characters))
    with col2:
        st.metric("👤 Current Agent", selected_display)
        st.metric("🏢 Scene", "What Now? (30 days)")

    # Scene Status - Dream UI Element
    st.markdown("---")
    st.markdown("**🏢 Scene Status**")
    scene_progress = min(len(st.session_state.selected_characters) * 20, 100)  # Simple progress based on characters met
    st.progress(scene_progress / 100)
    st.caption(f"Scene Progress: {scene_progress}% (based on team engagement)")

    # Quick Character Actions
    st.markdown("---")
    st.markdown("**⚡ Quick Switches**")
    quick_chars = ["sarai", "tech_cofounder", "advisor", "vc"]
    for char in quick_chars:
        if char != st.session_state.current_agent:
            char_title = char.replace('_', ' ').title()
            if st.button(f"→ {char_title}", key=f"quick_{char}", use_container_width=True, help=f"Quick switch to {char_title}"):
                st.session_state.current_agent = char
                st.rerun()
    
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
            st.session_state.selected_characters = set()  # Reset selections
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
    </div>
</div>
""", unsafe_allow_html=True)

# Add spacer for main content to account for fixed top bar
st.markdown('<div class="main-content-spacer"></div>', unsafe_allow_html=True)

# ============================================================================
# MAIN CHAT AREA
# ============================================================================

# Enhanced Dream UI Header
current_char_name = st.session_state.current_agent.replace('_', ' ').title()
st.markdown(f"""
<div class="dream-header">
    <h1>🎮 CEO Simulator - Meeting Room</h1>
    <h2>Currently speaking with {current_char_name}</h2>
    <p style="opacity: 0.9; margin-bottom: 0;">Navigate complex business challenges with your expert team</p>
</div>

<div class="scene-banner">
    <h3 style="margin: 0;">🏢 Scene: "What Now?" - First 30 Days as CEO</h3>
    <p style="margin: 8px 0 0 0; opacity: 0.9;">Mentalyc is 2.4 months from runway depletion. Time to make critical decisions.</p>
</div>
""", unsafe_allow_html=True)

# Message display area
message_container = st.container()

with message_container:
    # Enhanced Dream UI Meeting Panel
    st.markdown("""
    <div class="meeting-panel">
        <h3 style="margin-top: 0; color: #667eea;">💬 Meeting Room</h3>
        <p style="color: #666; margin-bottom: 16px;">Real-time conversation with your team</p>
    </div>
    """, unsafe_allow_html=True)

    # Display all messages with enhanced styling and avatars
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            avatar = "👤"
            st.markdown(f"""
            <div class="chat-message message-user">
                <div style="display: flex; align-items: flex-start; margin-bottom: 8px;">
                    <div class="agent-avatar" style="background: #2196F3; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white;">{avatar}</div>
                    <div style="flex: 1;">
                        <strong style="color: #1976D2;">You</strong>
                        <div style="color: #424242; margin-top: 4px;">{msg["content"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            character_key = msg["agent"].lower().replace(' ', '_')
            avatar = get_character_avatar(character_key)

            # Try to show character image if available
            image_path = get_character_image_path(character_key)
            avatar_html = ""
            try:
                # For now, use emoji avatars - could enhance to show mini character images
                avatar_html = f'<div class="agent-avatar" style="background: #667eea; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white;">{avatar}</div>'
            except:
                avatar_html = f'<div class="agent-avatar" style="background: #667eea; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white;">{avatar}</div>'

            st.markdown(f"""
            <div class="chat-message message-assistant">
                <div style="display: flex; align-items: flex-start; margin-bottom: 8px;">
                    {avatar_html}
                    <div style="flex: 1;">
                        <strong style="color: #667eea;">{msg["agent"]}</strong>
                        <div style="color: #424242; margin-top: 4px;">{msg["content"]}</div>
                    </div>
                </div>
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
    # Dream UI Welcome Experience
    st.markdown("""
    <div class="dream-card">
        <h2 style="text-align: center; color: #667eea; margin-bottom: 8px;">🎮 Welcome to CEO Simulator</h2>
        <p style="text-align: center; color: #666; margin-bottom: 24px; font-size: 18px;">
            Step into the shoes of a CEO and navigate complex business challenges with your expert team
        </p>

        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); padding: 16px; border-radius: 12px; margin-bottom: 24px; border-left: 4px solid #f39c12;">
            <h4 style="color: #d68910; margin-top: 0;">📊 Current Scenario</h4>
            <p style="margin-bottom: 0; color: #8b4513;"><strong>Mentalyc</strong> - AI therapy platform | <strong>Runway:</strong> 2.4 months | <strong>Challenge:</strong> First 30 days as CEO</p>
        </div>

        <h3 style="color: #667eea; margin-bottom: 16px;">👥 Meet Your Team</h3>
        <p style="color: #666; margin-bottom: 20px;">Click on any character to get introduced and start a conversation. Each brings unique expertise to help you succeed.</p>
    </div>
    """, unsafe_allow_html=True)

    # Character Grid - Dream UI Style
    st.markdown('<div class="character-grid">', unsafe_allow_html=True)

    characters_info = [
        {"id": "sarai", "name": "Sarai", "emoji": "🧠", "title": "Meta-Orchestrator", "desc": "All-knowing guide & conversation router"},
        {"id": "tech_cofounder", "name": "Omer", "emoji": "👨‍💻", "title": "CTO/Co-founder", "desc": "Technical reality & engineering constraints"},
        {"id": "advisor", "name": "Strategy Advisor", "emoji": "🎯", "title": "Strategic Advisor", "desc": "Business strategy & market focus"},
        {"id": "marketing_cofounder", "name": "Marketing Co-founder", "emoji": "📈", "title": "Head of Marketing", "desc": "GTM strategy & customer acquisition"},
        {"id": "vc", "name": "VC Investor", "emoji": "💰", "title": "Lead Investor", "desc": "Fundraising & market opportunity"},
        {"id": "coach", "name": "Leadership Coach", "emoji": "🏆", "title": "Executive Coach", "desc": "Leadership & personal growth"},
    ]

    cols = st.columns(3)
    for i, char in enumerate(characters_info):
        col_idx = i % 3
        with cols[col_idx]:
            is_selected = char["id"] == st.session_state.current_agent
            selected_class = "selected" if is_selected else ""

            st.markdown(f"""
            <div class="character-card {selected_class}">
                <div style="font-size: 48px; margin-bottom: 12px;">{char["emoji"]}</div>
                <h4 style="margin: 8px 0; color: #333;">{char["name"]}</h4>
                <p style="font-size: 14px; color: #667eea; margin: 4px 0; font-weight: bold;">{char["title"]}</p>
                <p style="font-size: 13px; color: #666; margin: 8px 0 0 0;">{char["desc"]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Actions - Moving towards Dream UI
    st.markdown("""
    <div class="dream-card">
        <h4 style="color: #667eea; margin-bottom: 16px;">🚀 Quick Start Actions</h4>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎯 Get Situation Overview", use_container_width=True, help="Ask Sarai for a comprehensive overview of your current situation"):
            st.session_state.current_agent = "sarai"
            st.session_state.messages.append({
                "role": "user",
                "content": "Give me a comprehensive overview of my current situation as CEO of Mentalyc. What's our runway, key challenges, and immediate priorities?"
            })
            st.rerun()

    with col2:
        if st.button("💰 Check Financial Health", use_container_width=True, help="Get VC's perspective on your financial situation"):
            st.session_state.current_agent = "vc"
            st.session_state.messages.append({
                "role": "user",
                "content": "What's your assessment of our financial situation? How much runway do we have and what are the key fundraising considerations?"
            })
            st.rerun()

    with col3:
        if st.button("👥 Team Dynamics Check", use_container_width=True, help="Ask Coach about team morale and leadership"):
            st.session_state.current_agent = "coach"
            st.session_state.messages.append({
                "role": "user",
                "content": "How am I doing as a leader so far? Any observations about team dynamics or my leadership approach?"
            })
            st.rerun()

    st.markdown("""
    <div class="dream-card">
        <h4 style="color: #667eea; margin-bottom: 12px;">💡 Pro Tips</h4>
        <ul style="color: #666; margin: 0; padding-left: 20px;">
            <li><strong>🆕 New characters</strong> appear with glowing indicators in the sidebar</li>
            <li><strong>Switch anytime</strong> - your conversation history is preserved</li>
            <li><strong>Start with Sarai</strong> to get oriented, then dive deep with specialists</li>
            <li><strong>Characters remember</strong> context from your entire conversation</li>
        </ul>
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

