"""Global layout: PWA head injection, responsive CSS, sidebar nav."""
from __future__ import annotations

import streamlit as st

from ..models import User

_PWA_HEAD = """
<link rel="manifest" href="app/static/manifest.webmanifest">
<link rel="apple-touch-icon" sizes="180x180" href="app/static/apple-touch-icon-180.png">
<link rel="icon" type="image/png" sizes="192x192" href="app/static/icon-192.png">
<link rel="icon" type="image/png" sizes="512x512" href="app/static/icon-512.png">
<link rel="shortcut icon" href="app/static/favicon.ico">
<meta name="theme-color" content="#e05a2b">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="KatoriFit">
<meta name="mobile-web-app-capable" content="yes">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
"""

_CSS = """
<style>
:root { --kf-accent: #e05a2b; }
.block-container {
  padding-top: 1.2rem;
  padding-bottom: 5rem;
  max-width: 780px;
}
h1, h2, h3 { letter-spacing: -0.01em; }
.stButton>button { border-radius: 12px; padding: 0.55rem 1rem; }
.stButton>button[kind="primary"] { background: var(--kf-accent); border-color: var(--kf-accent); }
.kf-hero { text-align:center; padding: 1.5rem 0 0.5rem; }
.kf-hero img { width: 96px; height: 96px; border-radius: 22px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
.kf-hero h1 { margin: 0.6rem 0 0.2rem; font-size: 2rem; }
.kf-hero p  { color: #6b6257; margin: 0; }
.kf-card {
  background: #fff; border: 1px solid #ece5d7; border-radius: 16px;
  padding: 1rem 1.1rem; margin-bottom: 0.7rem;
}
.kf-metric-row { display: flex; gap: 0.6rem; flex-wrap: wrap; } [data-testid="InputInstructions"] { display: none !important; }
@media (max-width: 640px) {
  .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
  h1 { font-size: 1.6rem; }
  section[data-testid="stSidebar"] { width: 240px !important; }
}
/* Safe-area for iOS home-screen install */
@supports (padding: max(0px)) {
  .block-container {
    padding-left: max(0.9rem, env(safe-area-inset-left));
    padding-right: max(0.9rem, env(safe-area-inset-right));
    padding-bottom: max(5rem, env(safe-area-inset-bottom));
  }
}
</style>
"""


def apply_layout() -> None:
    st.markdown(_PWA_HEAD, unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)


def hero_header() -> None:
    st.markdown(
        """
        <div class="kf-hero">
          <img src="app/static/icon-192.png" alt="KatoriFit"/>
          <h1>KatoriFit</h1>
          <p>Log workouts. Track progress. Stay consistent.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_nav(user: User) -> str:
    st.sidebar.markdown(
        f"""
        <div style="text-align:center; padding: 0.5rem 0 1rem;">
          <img src="app/static/icon-192.png" width="56" style="border-radius:14px"/>
          <div style="font-weight:600; margin-top:0.4rem;">KatoriFit</div>
          <div style="font-size:0.8rem; color:#8a8275;">{user.email}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.sidebar.radio(
        "Navigate",
        ["Home", "Food Tracker", "Fasting", "Activity", "Workouts", "Cheat Day", "Progress", "Profile"],
        label_visibility="collapsed",
    )
