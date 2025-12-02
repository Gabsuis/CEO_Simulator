
"""
CEO Simulator - Streamlit Web Interface (Welcome Page)

Deploy to Streamlit Cloud: https://share.streamlit.io/
Local: streamlit run streamlit_app.py
"""

import streamlit as st

from app_state import ensure_api_key, initialize_session_state
from app_styles import BASE_CSS
from character_utils import (
    get_character_avatar,
    get_character_image_path,
    normalize_character_key,
)

st.set_page_config(
    page_title="CEO Simulator",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ensure shared session state and API key are available
initialize_session_state()
ensure_api_key()

st.markdown(BASE_CSS, unsafe_allow_html=True)

# Page navigation state
if "current_page" not in st.session_state:
    st.session_state.current_page = "welcome"

# Page navigation header
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.current_page == "welcome":
        st.button("🏠 Welcome", disabled=True, width='stretch')
    else:
        if st.button("🏠 Welcome", width='stretch'):
            st.session_state.current_page = "welcome"
            st.rerun()
with col2:
    if st.session_state.current_page == "simulation":
        st.button("🎮 Simulation", disabled=True, width='stretch')
    else:
        if st.button("🎮 Simulation", width='stretch'):
            st.session_state.current_page = "simulation"
            st.rerun()

# Page content rendering
if st.session_state.current_page == "welcome":
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
            .welcome-body {max-width: 900px; margin: 0 auto;}
            .welcome-body h2, .welcome-body h3 {text-align: center;}
            .welcome-body p {text-align: justify;}
        </style>
        """,
        unsafe_allow_html=True,
    )


DEFAULT_BACKSTORIES = {
    "sarai": "Can do all, evaluates you, and sees every thread."
}


@st.dialog("Character Introduction", width="large")
def show_character_modal(character_id: str):
    """Display a full character brief in a modal."""
    try:
        from engine.character_loader import CharacterLoader

        loader = CharacterLoader()
        char_spec = loader.load_character(normalize_character_key(character_id))
        st.session_state.selected_characters.add(character_id)

        identity = char_spec.get_identity()
        image_path = get_character_image_path(character_id)

        # Centered portrait
        left, center, right = st.columns([1, 2, 1])
        with center:
            try:
                st.image(image_path, use_container_width=True)
            except Exception:
                st.markdown(
                    f"<div style='font-size: 96px; text-align: center; margin: 30px 0;'>{get_character_avatar(character_id)}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            f"## {identity.get('name', character_id.title())}\n"
            f"**{identity.get('in_world_title', 'AI Agent')}**\n\n"
            f"*{identity.get('tagline', 'Guides the CEO')}*"
        )

        st.divider()

        backstory = identity.get("backstory") or DEFAULT_BACKSTORIES.get(
            character_id, "Details coming soon."
        )
        with st.expander("📖 Quick Background", expanded=True):
            st.markdown(backstory)
    except Exception as exc:
        st.error(f"Could not load character introduction: {exc}")


def render_character_grid(characters):
    """Show the character cards with CTA buttons."""
    cols = st.columns(3)
    for idx, char in enumerate(characters):
        with cols[idx % 3]:
            st.markdown(f"### {char['emoji']} {char['name']}")
            st.caption(char["title"])
            st.write(char["desc"])
            if st.button(
                f"Meet {char['name']}",
                key=f"meet_{char['id']}",
                width='stretch',
            ):
                st.session_state.show_character_modal = char["id"]
                st.session_state.show_character_modal_source = "welcome"
                st.rerun()


st.markdown("<div class='welcome-body'>", unsafe_allow_html=True)
st.markdown("## 🎮 Welcome to CEO Simulator")
st.markdown(
    "*Step into the shoes of Mentalyc's CEO and navigate tough calls with your executive team.*"
)

has_met_character = len(st.session_state.selected_characters) > 0
st.markdown("### 🚀 Ready to Lead?")
st.write(
    "Meet at least one character, then jump into the simulation whenever you're ready."
)
if st.button(
    "Start Simulation",
    type="primary",
    width='stretch',
    disabled=not has_met_character,
):
    st.session_state.show_character_modal = None
    st.session_state.show_character_modal_source = None
    st.session_state.current_page = "simulation"
    st.rerun()
if not has_met_character:
    st.caption("Meet a character first to unlock the simulation.")

st.markdown(
    """
<div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); padding: 16px; border-radius: 12px; margin: 30px 0; border-left: 4px solid #f39c12;">
    <h4 style="color: #d68910; margin-top: 0; text-align:center;">📊 Current Scenario</h4>
    <p style="margin-bottom: 0; color: #8b4513;">
        <strong>Company:</strong> Mentalyc (AI therapy platform)<br>
        <strong>Runway:</strong> 2.4 months<br>
        <strong>Challenge:</strong> First 30 days as CEO – stabilize, align, and make decisions fast.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("### 🧭 How It Works")
st.markdown(
    """
1. **Meet the Team** – Each character brings a unique perspective.
2. **Learn the Context** – Understand Mentalyc's situation.
3. **Start Simulation** – Switch to the Simulation page for the live chat.
4. **Navigate Decisions** – Bounce between characters, gather insight, and lead.
"""
)

st.markdown("### 👥 Meet Your Team")
st.markdown(
    "Click any teammate to open their dossier, personality traits, and backstory."
)

CHARACTERS = [
    {
        "id": "sarai",
        "name": "Sarai",
        "emoji": "🧠",
        "title": "Meta-Orchestrator",
        "desc": "Can do all, evaluates you, and sees every thread.",
    },
    {
        "id": "tech_cofounder",
        "name": "Omer",
        "emoji": "👨‍💻",
        "title": "Tech Cofounder",
        "desc": "Knows the engineering realities, technical debt, and delivery constraints.",
    },
    {
        "id": "advisor",
        "name": "Strategy Advisor",
        "emoji": "🎯",
        "title": "Strategic Advisor",
        "desc": "Connects market dots, pressure-tests focus, and spots blind spots.",
    },
    {
        "id": "marketing_cofounder",
        "name": "Marketing Cofounder",
        "emoji": "📈",
        "title": "Head of Marketing",
        "desc": "Obsessed with GTM, ICP clarity, and customer research.",
    },
    {
        "id": "vc",
        "name": "VC Investor",
        "emoji": "💰",
        "title": "Lead Investor",
        "desc": "Focuses on runway, fundraising appetite, and board-level alignment.",
    },
    {
        "id": "coach",
        "name": "Leadership Coach",
        "emoji": "🏆",
        "title": "Executive Coach",
        "desc": "Helps you stay grounded, prioritize energy, and grow as a leader.",
    },
]

render_character_grid(CHARACTERS)

st.markdown("### 💡 Pro Tips")
st.markdown(
    """
- 🧠 **Start with Sarai** for a systems view, then dive deep with specialists.
- 🔄 **Switch characters anytime** – your transcript stays intact.
- 🗂️ **Characters remember context** from the entire session.
- 📝 **Use the Simulation page** for the actual conversation once you're ready.
"""
)

st.markdown("</div>", unsafe_allow_html=True)

if (
    st.session_state.show_character_modal
    and st.session_state.show_character_modal_source == "welcome"
):
    show_character_modal(st.session_state.show_character_modal)

else:  # Simulation page
    # Import simulation-specific modules
    import asyncio
    import os
    import streamlit.components.v1 as components

    from app_state import (
        ENGINE_VERSION,
        get_simulation_engine,
    )

    # Initialize simulation-specific state
    st.session_state.show_character_modal = None
    st.session_state.show_character_modal_source = None

    def render_sidebar_controls():
        with st.sidebar:
            st.markdown("### 🎮 Simulation Controls")
            agents = [a["name"] for a in st.session_state.engine.list_agents()]
            agent_display = []
            agent_map = {}
            for agent in agents:
                title = agent.replace("_", " ").title()
                is_new = agent not in st.session_state.selected_characters
                label = f"🆕 {title}" if is_new else f"👤 {title}"
                agent_display.append(label)
                agent_map[label] = agent

            current_title = st.session_state.current_agent.replace("_", " ").title()
            current_label = (
                f"🆕 {current_title}"
                if st.session_state.current_agent not in st.session_state.selected_characters
                else f"👤 {current_title}"
            )
            try:
                idx = agent_display.index(current_label)
            except ValueError:
                idx = 0

            selected_display = st.selectbox(
                "Select Character", agent_display, index=idx, key="simulation_agent_select"
            )
            st.session_state.current_agent = agent_map.get(
                selected_display, st.session_state.current_agent
            )

            if st.session_state.current_agent not in st.session_state.selected_characters:
                st.session_state.selected_characters.add(st.session_state.current_agent)

            st.markdown("**⚡ Quick Switches**")
            quick_chars = ["sarai", "tech_cofounder", "advisor", "vc"]
            for char in quick_chars:
                label = char.replace("_", " ").title()
                if st.button(
                    f"→ {label}",
                    key=f"sim_quick_{char}",
                    width='stretch',
                ):
                    if st.session_state.current_agent != char:
                        st.session_state.previous_agent = st.session_state.current_agent
                        st.session_state.current_agent = char
                        st.session_state.selected_characters.add(char)
                        # Add system notification for character switch
                        char_display = char.replace('_', ' ').title()
                        st.session_state.messages.append({
                            "role": "system",
                            "content": f"🔄 Switched to {char_display}"
                        })
                        st.session_state.message_count += 1
                    st.rerun()

            st.markdown("---")
            AGENT_INFO = {
                "sarai": "Can do all, evaluates you, and sees every thread.",
                "tech_cofounder": "Pragmatic engineer. Focuses on feasibility, trade-offs, and technical reality.",
                "advisor": "Strategic thinker. Asks probing questions and connects dots across domains.",
                "marketing_cofounder": "Customer-obsessed marketer. Focuses on GTM and customer research.",
                "vc": "Board-level investor. High-level strategy and market opportunity focus.",
                "coach": "Executive coach. Leadership development and personal growth focus.",
            }
            st.markdown("**ℹ️ About This Character**")
            st.caption(AGENT_INFO.get(st.session_state.current_agent, "AI Agent"))

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Clear Chat", width='stretch'):
                    st.session_state.engine.reset_session(
                        user_id=st.session_state.user_id,
                        session_id=st.session_state.session_id,
                    )
                    st.session_state.session_id = (
                        f"session_{st.session_state.user_id.split('_')[-1]}"
                    )
                    st.session_state.messages = []
                    st.session_state.message_count = 0
                    st.rerun()
            with col2:
                if st.session_state.messages:
                    transcript = []
                    transcript.append("=" * 60)
                    transcript.append("CEO SIMULATOR - CHAT TRANSCRIPT")
                    transcript.append("=" * 60)
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            transcript.append(f"You: {msg['content']}")
                        elif msg["role"] == "system":
                            transcript.append(f"[{msg['content']}]")
                        else:
                            transcript.append(f"{msg['agent']}: {msg['content']}")
                        transcript.append("")
                    transcript_text = "\n".join(transcript)
                    st.download_button(
                        "📥 Export",
                        data=transcript_text,
                        file_name="ceo_sim_transcript.txt",
                        mime="text/plain",
                        width='stretch',
                    )
                else:
                    st.button("📥 Export", width='stretch', disabled=True)

    def render_message_stream():
        message_container = st.container()
        with message_container:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(
                        f"""
                <div class="chat-message message-user">
                    <div style="display: flex; align-items: flex-start; margin-bottom: 8px;">
                        <div class="agent-avatar" style="background: #2196F3; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white;">👤</div>
                        <div style="flex: 1;">
                            <strong style="color: #1976D2;">You</strong>
                            <div style="color: #424242; margin-top: 4px;">{msg["content"]}</div>
                        </div>
                    </div>
                </div>
                """,
                        unsafe_allow_html=True,
                    )
                elif msg["role"] == "system":
                    st.markdown(
                        f"""
                <div class="chat-message message-system">
                    {msg["content"]}
                </div>
                """,
                        unsafe_allow_html=True,
                    )
                else:
                    key = msg["agent"].lower().replace(" ", "_")
                    avatar = get_character_avatar(key)
                    st.markdown(
                        f"""
                <div class="chat-message message-assistant">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                        <div class="agent-avatar" style="background: #667eea; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white;">{avatar}</div>
                        <div style="flex: 1;">
                            <strong style="color: #667eea;">{msg["agent"]}</strong>
                            <div style="color: #424242; margin-top: 4px;">{msg["content"]}</div>
                        </div>
                    </div>
                </div>
                """,
                        unsafe_allow_html=True,
                    )
        # Auto-scroll to newest message
        components.html(
            """
            <script>
            setTimeout(function () {
                const section = window.parent.document.querySelector('section.main');
                if (section) {
                    section.scrollTo({top: section.scrollHeight, behavior: 'smooth'});
                } else {
                    window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
                }
            }, 100);
            </script>
            """,
            height=0,
        )

    def handle_chat_input():
        st.divider()
        user_input = st.chat_input(
            f"Type your message to {st.session_state.current_agent.replace('_', ' ').title()}..."
        )
        if not user_input:
            return

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.message_count += 1

        with st.spinner(
            f"✨ {st.session_state.current_agent.replace('_', ' ').title()} is thinking..."
        ):
            try:
                async def get_response():
                    return await st.session_state.engine.handle_input(
                        user_id=st.session_state.user_id,
                        session_id=st.session_state.session_id,
                        speaker=st.session_state.current_agent,
                        message=user_input,
                    )

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                responses = loop.run_until_complete(get_response())
                loop.close()

                if not responses:
                    st.error("❌ No response received from the agent. Try again.")
                    return

                for response in responses:
                    agent_name = response.speaker.replace("_", " ").title()
                    st.session_state.messages.append(
                        {"role": "assistant", "agent": agent_name, "content": response.text}
                    )
                    st.session_state.message_count += 1
            except Exception as exc:
                st.error(f"❌ Error: {exc}")
                st.info("💡 Check that your GOOGLE_API_KEY is set correctly.")
        st.rerun()

    def render_debug_panel():
        with st.expander("🔧 Debug Panel", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("User ID", st.session_state.user_id[-8:])
            with col2:
                st.metric("Session ID", st.session_state.session_id[-15:])
            with col3:
                st.metric("Messages", st.session_state.message_count)
            with col4:
                st.metric("API Key", "✅" if os.getenv("GOOGLE_API_KEY") else "❌")

            has_debug = hasattr(st.session_state.engine, "get_debug_logs")
            has_reset = hasattr(st.session_state.engine, "reset_session")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Debug Available", "✅" if has_debug else "❌")
            with col2:
                st.metric("Reset Available", "✅" if has_reset else "❌")
            with col3:
                if st.button("🔄 Force Refresh", width='stretch'):
                    get_simulation_engine.clear()
                    st.session_state.engine = get_simulation_engine(ENGINE_VERSION)
                    st.success("Engine refreshed! Refreshing page...")
                    st.rerun()

            st.divider()
            st.markdown("### 📋 Engine Debug Logs")
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                log_limit = st.slider("Show last N logs", 5, 50, 15)
            with col2:
                if st.button("🗑️ Clear Logs"):
                    if hasattr(st.session_state.engine, "clear_debug_logs"):
                        st.session_state.engine.clear_debug_logs()
                        st.success("Logs cleared!")

            logs = []
            if has_debug:
                debug_logs = st.session_state.engine.get_debug_logs()
                if debug_logs:
                    # Show most recent logs
                    recent_logs = debug_logs[-log_limit:] if log_limit > 0 else debug_logs
                    for log_entry in recent_logs:
                        timestamp = log_entry.get('timestamp', 'Unknown')
                        level = log_entry.get('level', 'info').upper()
                        message = log_entry.get('message', 'No message')

                        # Color code by level
                        if level == 'ERROR':
                            level_icon = '🔴'
                        elif level == 'WARNING':
                            level_icon = '🟡'
                        else:
                            level_icon = '🔵'

                        logs.append(f"{level_icon} **{level}** {timestamp}")
                        logs.append(f"   {message}")

                        # Show details if available
                        details = log_entry.get('details', {})
                        if details:
                            for key, value in details.items():
                                logs.append(f"   • {key}: {value}")
                        logs.append("")

            if logs:
                st.code("\n".join(logs), language=None)
            else:
                st.info("No debug logs yet. Send a message to generate logs.")

    # Render the simulation page
    current_title = st.session_state.current_agent.replace("_", " ").title()
    emoji = get_character_avatar(st.session_state.current_agent)
    st.markdown(
        f"""
    <div class="dream-header" style="display: flex; align-items: center; justify-content: center; gap: 16px;">
        <div style="font-size: 48px;">{emoji}</div>
        <div>
            <h4 style="margin: 0; color: rgba(255,255,255,0.8); letter-spacing: 1px;">THE MEETING ROOM</h4>
            <h1 style="margin: 0;">{current_title}</h1>
            <p style="margin: 4px 0 0 0; opacity: 0.9;">Live conversation channel</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_message_stream()
    handle_chat_input()
    render_debug_panel()
