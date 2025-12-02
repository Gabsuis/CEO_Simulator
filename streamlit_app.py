
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


def render_top_nav(active: str):
    """Render top navigation tabs."""
    nav = st.container()
    with nav:
        col1, col2 = st.columns([1, 1])
        with col1:
            if active == "welcome":
                st.button(
                    "🏠 Welcome",
                    disabled=True,
                    width='stretch',
                )
            else:
                if st.button("🏠 Welcome", width='stretch'):
                    st.switch_page("streamlit_app.py")
        with col2:
            if active == "simulation":
                st.button(
                    "🎮 Simulation",
                    disabled=True,
                    width='stretch',
                )
            else:
                if st.button("🎮 Simulation", width='stretch'):
                    st.switch_page("pages/simulation.py")


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


render_top_nav("welcome")

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
    st.switch_page("simulation")
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
