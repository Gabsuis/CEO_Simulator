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

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

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

@st.cache_resource
def get_simulation_engine():
    """Initialize simulation engine (cached across reruns)."""
    from simulation_engine_adk import SimulationEngine
    return SimulationEngine()

# Initialize session state
if "engine" not in st.session_state:
    st.session_state.engine = get_simulation_engine()

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
# DEBUG INFO (DEV ONLY)
# ============================================================================

with st.expander("🔧 Debug Info"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("User ID", st.session_state.user_id[-8:])
    with col2:
        st.metric("Session ID", st.session_state.session_id)
    with col3:
        st.metric("API Key Set", "✅" if os.getenv("GOOGLE_API_KEY") else "❌")

