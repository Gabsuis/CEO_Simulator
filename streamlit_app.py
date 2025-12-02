
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
from supabase_client import (
    is_supabase_configured,
    login,
    signup,
    logout,
    list_user_sessions,
    load_game_session,
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

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION (only if Supabase is configured)
# ─────────────────────────────────────────────────────────────
supabase_enabled = is_supabase_configured()

if supabase_enabled and not st.session_state.authenticated:
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    
    # Hide sidebar on login page
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
        <div style="max-width: 400px; margin: 0 auto; padding-top: 50px;">
            <h1 style="text-align: center;">🎮 CEO Simulator</h1>
            <p style="text-align: center; color: #666;">Sign in to save your progress</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "✨ Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if email and password:
                        user = login(email, password)
                        if user:
                            st.session_state.user = user
                            st.session_state.authenticated = True
                            # Clear any previous game state to prevent session bleeding
                            st.session_state.messages = []
                            st.session_state.message_count = 0
                            st.session_state.session_name = None
                            st.session_state.current_game_session_id = None
                            st.session_state.selected_characters = set()
                            st.success("✅ Welcome back!")
                            st.rerun()
                    else:
                        st.warning("Please enter email and password")
        
        with tab2:
            with st.form("signup_form"):
                email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_pass", 
                                        help="Minimum 6 characters")
                password_confirm = st.text_input("Confirm Password", type="password", key="signup_pass_confirm")
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not email or not password:
                        st.warning("Please fill in all fields")
                    elif password != password_confirm:
                        st.error("Passwords don't match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        if signup(email, password):
                            st.success("✅ Account created! Please login.")
        
        st.markdown("---")
        st.caption("Or continue without an account (progress won't be saved)")
        if st.button("🎮 Play as Guest", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    st.stop()

# ─────────────────────────────────────────────────────────────
# MAIN APP (authenticated or guest mode)
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
# USER INFO BAR (if authenticated)
# ─────────────────────────────────────────────────────────────
if st.session_state.authenticated and st.session_state.user:
    user_col1, user_col2 = st.columns([3, 1])
    with user_col1:
        st.markdown(f"👤 Logged in as **{st.session_state.user['email']}**")
    with user_col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Show saved sessions
    sessions = list_user_sessions(st.session_state.user["id"])
    if sessions:
        with st.expander("📂 **Continue a Previous Game**", expanded=False):
            for session in sessions[:5]:  # Show last 5
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{session['session_name']}**")
                    st.caption(f"{session['message_count']} messages • {session['current_agent'].replace('_', ' ').title()}")
                with col2:
                    if st.button("▶️ Resume", key=f"resume_{session['id']}", use_container_width=True):
                        # Load the session
                        session_data = load_game_session(session['id'])
                        if session_data:
                            st.session_state.messages = session_data["messages"]
                            st.session_state.current_agent = session_data["current_agent"]
                            st.session_state.selected_characters = session_data["selected_characters"]
                            st.session_state.session_name = session_data["session_name"]
                            st.session_state.current_game_session_id = session['id']
                            st.session_state.message_count = len(session_data["messages"])
                            st.switch_page("pages/simulation.py")
    st.markdown("---")

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
    st.switch_page("pages/simulation.py")
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
