"""
Supabase client for auth and database operations.

Provides:
- User authentication (login/signup/logout)
- Game session persistence (save/load transcripts)
"""

import os
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Lazy import to avoid errors if supabase not installed
_supabase_client = None


def get_supabase():
    """Get Supabase client (cached). Returns None if not configured."""
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        return None
    
    try:
        from supabase import create_client
        _supabase_client = create_client(url, key)
        return _supabase_client
    except ImportError:
        st.warning("⚠️ Supabase package not installed. Run: pip install supabase")
        return None
    except Exception as e:
        st.error(f"⚠️ Supabase connection failed: {e}")
        return None


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    return get_supabase() is not None


# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────

def login(email: str, password: str) -> Optional[Dict]:
    """
    Login user with email and password.
    
    Returns:
        User dict with 'id' and 'email' on success, None on failure.
    """
    client = get_supabase()
    if not client:
        return None
    
    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email
            }
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            st.error("❌ Invalid email or password")
        else:
            st.error(f"❌ Login failed: {error_msg}")
    return None


def signup(email: str, password: str) -> bool:
    """
    Sign up a new user.
    
    Returns:
        True on success, False on failure.
    """
    client = get_supabase()
    if not client:
        return False
    
    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            return True
        else:
            st.error("❌ Signup failed - please try again")
            return False
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            st.error("❌ This email is already registered")
        elif "password" in error_msg.lower():
            st.error("❌ Password must be at least 6 characters")
        else:
            st.error(f"❌ Signup failed: {error_msg}")
        return False


def logout():
    """Logout current user and clear ALL session state to prevent bleeding."""
    client = get_supabase()
    if client:
        try:
            client.auth.sign_out()
        except:
            pass
    
    # Clear auth-related session state
    st.session_state.user = None
    st.session_state.authenticated = False
    st.session_state.current_game_session_id = None
    st.session_state.session_name = None
    
    # Clear game state to prevent session bleeding between users
    st.session_state.messages = []
    st.session_state.message_count = 0
    st.session_state.selected_characters = set()


# ─────────────────────────────────────────────────────────────
# GAME SESSIONS
# ─────────────────────────────────────────────────────────────

def save_game_session(
    user_id: str,
    session_name: str,
    messages: List[Dict],
    current_agent: str,
    selected_characters: set
) -> Optional[str]:
    """
    Save or update a game session.
    
    Args:
        user_id: Supabase user ID
        session_name: Name for this game session
        messages: List of message dicts (role, content, agent)
        current_agent: Currently selected agent
        selected_characters: Set of characters the user has met
    
    Returns:
        Session ID on success, None on failure.
    """
    client = get_supabase()
    if not client:
        return None
    
    try:
        # Convert set to list for JSON serialization
        characters_list = list(selected_characters) if selected_characters else []
        
        data = {
            "user_id": user_id,
            "session_name": session_name,
            "messages": json.dumps(messages),
            "current_agent": current_agent,
            "selected_characters": json.dumps(characters_list),
            "message_count": len(messages),
            "updated_at": datetime.now().isoformat()
        }
        
        # Upsert: update if exists, insert if not
        response = client.table("game_sessions").upsert(
            data,
            on_conflict="user_id,session_name"
        ).execute()
        
        if response.data:
            return response.data[0].get("id")
        return None
        
    except Exception as e:
        # Silently fail to avoid interrupting gameplay
        print(f"[Supabase] Save failed: {e}")
        return None


def load_game_session(session_id: str) -> Optional[Dict]:
    """
    Load a game session by ID.
    
    Returns:
        Session dict with messages, current_agent, selected_characters, etc.
        None if not found.
    """
    client = get_supabase()
    if not client:
        return None
    
    try:
        response = client.table("game_sessions").select("*").eq("id", session_id).execute()
        
        if response.data:
            session = response.data[0]
            # Parse JSON fields
            session["messages"] = json.loads(session["messages"]) if session.get("messages") else []
            session["selected_characters"] = set(
                json.loads(session["selected_characters"]) if session.get("selected_characters") else []
            )
            return session
        return None
        
    except Exception as e:
        st.error(f"❌ Failed to load session: {e}")
        return None


def list_user_sessions(user_id: str) -> List[Dict]:
    """
    List all game sessions for a user.
    
    Returns:
        List of session summaries (id, session_name, message_count, updated_at)
    """
    client = get_supabase()
    if not client:
        return []
    
    try:
        response = client.table("game_sessions").select(
            "id, session_name, message_count, current_agent, updated_at"
        ).eq("user_id", user_id).order("updated_at", desc=True).execute()
        
        return response.data or []
        
    except Exception as e:
        print(f"[Supabase] List sessions failed: {e}")
        return []


def delete_game_session(session_id: str) -> bool:
    """
    Delete a game session.
    
    Returns:
        True on success, False on failure.
    """
    client = get_supabase()
    if not client:
        return False
    
    try:
        client.table("game_sessions").delete().eq("id", session_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete session: {e}")
        return False

