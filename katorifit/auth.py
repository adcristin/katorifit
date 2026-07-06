"""Supabase-backed authentication for Streamlit."""
from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from .models import User

load_dotenv()


@st.cache_resource(show_spinner=False)
def _client():
    from supabase import create_client

    url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)


def ensure_session() -> None:
    st.session_state.setdefault("user", None)


def current_user() -> Optional[User]:
    return st.session_state.get("user")


def sign_out() -> None:
    client = _client()
    if client:
        try:
            client.auth.sign_out()
        except Exception:
            pass
    st.session_state["user"] = None


def _handle_auth_response(res) -> Optional[str]:
    user = getattr(res, "user", None)
    if not user:
        return "Invalid credentials or unconfirmed email."
    st.session_state["user"] = User(id=user.id, email=user.email or "")
    return None


def sign_in_view() -> None:
    from .ui.layout import hero_header

    hero_header()
    client = _client()
    if client is None:
        st.error(
            "Supabase is not configured. Copy `.env.example` to `.env` and fill in "
            "`SUPABASE_URL` and `SUPABASE_ANON_KEY`, then restart the app."
        )
        st.stop()

    tab_signin, tab_signup = st.tabs(["Sign in", "Create account"])

    with tab_signin:
        with st.form("signin"):
            email = st.text_input("Email", key="si_email")
            password = st.text_input("Password", type="password", key="si_pw")
            submitted = st.form_submit_button("Sign in", width='stretch')
        if submitted:
            try:
                res = client.auth.sign_in_with_password({"email": email, "password": password})
            except Exception as exc:  # noqa: BLE001
                st.error(f"Sign in failed: {exc}")
                return
            err = _handle_auth_response(res)
            if err:
                st.error(err)
            else:
                st.rerun()

    with tab_signup:
        with st.form("signup"):
            email = st.text_input("Email", key="su_email")
            password = st.text_input("Password (min 6 chars)", type="password", key="su_pw")
            submitted = st.form_submit_button("Create account", width='stretch')
        if submitted:
            try:
                res = client.auth.sign_up({"email": email, "password": password})
            except Exception as exc:  # noqa: BLE001
                st.error(f"Sign up failed: {exc}")
                return
            if getattr(res, "user", None):
                st.success(
                    "Account created. Check your email to confirm, then sign in."
                )
            else:
                st.error("Could not create account.")
