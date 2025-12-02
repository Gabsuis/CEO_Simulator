"""CEO Simulator - Simulation Page"""

import asyncio
import os

import streamlit as st
import streamlit.components.v1 as components

from app_state import (
    ENGINE_VERSION,
    ensure_api_key,
    get_simulation_engine,
    initialize_session_state,
)
from app_styles import BASE_CSS
from character_utils import (
    get_character_avatar,
    normalize_character_key,
)

st.set_page_config(
    page_title="CEO Simulator – Simulation",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
ensure_api_key()
st.session_state.show_character_modal = None
st.session_state.show_character_modal_source = None

st.markdown(BASE_CSS, unsafe_allow_html=True)


def render_top_nav():
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🏠 Welcome", width='stretch'):
                st.switch_page("streamlit_app.py")
        with col2:
            st.button(
                "🎮 Simulation",
                disabled=True,
                width='stretch',
            )


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


def render_floating_dashboard():
    st.markdown(
        f"""
    <div class="floating-dashboard">
        <h4>📊 Session</h4>
        <div class="metric-row"><span class="metric-label">Messages:</span><span class="metric-value">{st.session_state.message_count}</span></div>
        <div class="metric-row"><span class="metric-label">Characters met:</span><span class="metric-value">{len(st.session_state.selected_characters)}</span></div>
        <div class="metric-row"><span class="metric-label">Current:</span><span class="metric-value">{st.session_state.current_agent.replace('_', ' ').title()}</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )


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
                    <div style="display: flex; align-items: flex-start; margin-bottom: 8px;">
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

            responses = asyncio.run(get_response())

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
        if hasattr(st.session_state.engine, "get_debug_logs"):
            logs = st.session_state.engine.get_debug_logs(limit=log_limit)
        if logs:
            for log in reversed(logs):
                level_icon = {"info": "🔵", "warning": "🟡", "error": "🔴"}.get(
                    log.get("level"), "⚪"
                )
                timestamp = log.get("timestamp", "")
                st.markdown(f"**{level_icon} [{timestamp}] {log.get('message','')}**")
                details = log.get("details", {})
                if details:
                    detail_container = st.container()
                    for key, value in details.items():
                        if key == "traceback":
                            detail_container.code(value, language="python")
                        else:
                            detail_container.write(f"**{key}:** {value}")
                st.markdown("---")
        else:
            st.info("No debug logs yet. Send a message to generate logs.")


render_top_nav()
render_sidebar_controls()
render_floating_dashboard()

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

