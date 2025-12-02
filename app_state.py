import os
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# Ensure environment variables are available
load_dotenv()

# Make sure project root is on sys.path so simulation_engine imports work
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ENGINE_VERSION = "2.0"


@st.cache_resource
def get_simulation_engine(_version: str):
    """Initialize simulation engine (cached across reruns)."""
    from simulation_engine_adk import SimulationEngine

    return SimulationEngine()


def initialize_session_state():
    """Ensure all session state defaults exist."""
    if "engine" not in st.session_state:
        st.session_state.engine = get_simulation_engine(ENGINE_VERSION)

    # Refresh engine if it is missing new methods (backward compatibility)
    if not hasattr(st.session_state.engine, "get_debug_logs"):
        get_simulation_engine.clear()
        st.session_state.engine = get_simulation_engine(ENGINE_VERSION)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_agent" not in st.session_state:
        agents = [a["name"] for a in st.session_state.engine.list_agents()]
        st.session_state.current_agent = agents[0] if agents else "sarai"

    if "user_id" not in st.session_state:
        st.session_state.user_id = f"streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    if "selected_characters" not in st.session_state:
        st.session_state.selected_characters = set()

    if "show_character_modal" not in st.session_state:
        st.session_state.show_character_modal = None

    if "show_character_modal_source" not in st.session_state:
        st.session_state.show_character_modal_source = None

    if "previous_agent" not in st.session_state:
        st.session_state.previous_agent = None


def ensure_api_key():
    """Stop the app with instructions if the API key is missing."""
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("❌ API Key not found!")
        st.info(
            """
            ### Setup Instructions:

            **Local Development:**
            1. Create `.streamlit/secrets.toml`
            2. Add: `GOOGLE_API_KEY = "your-key-here"`
            3. Restart the app

            **Streamlit Cloud:**
            1. Deploy your repo to GitHub
            2. Go to app settings → Secrets
            3. Add your `GOOGLE_API_KEY`
            """
        )
        st.stop()

