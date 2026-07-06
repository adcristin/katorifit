"""KatoriFit — Streamlit entry point."""
from __future__ import annotations

import streamlit as st

from katorifit.auth import current_user, ensure_session, sign_in_view, sign_out
from katorifit.db import init_db
from katorifit.ui.layout import apply_layout, sidebar_nav
from katorifit.ui import (
    pages_home,
    pages_food,
    pages_fasting,
    pages_activity,
    pages_workout,
    pages_cheat,
    pages_progress,
    pages_profile,
)


st.set_page_config(
    page_title="KatoriFit",
    page_icon="app/static/icon-192.png",
    layout="centered",
    initial_sidebar_state="auto",
)

apply_layout()
init_db()
ensure_session()

user = current_user()
if not user:
    sign_in_view()
    st.stop()

page = sidebar_nav(user)

if st.sidebar.button("Sign out", width='stretch'):
    sign_out()
    st.rerun()

if page == "Home":
    pages_home.render(user)
elif page == "Food Tracker":
    pages_food.render(user)
elif page == "Fasting":
    pages_fasting.render(user)
elif page == "Activity":
    pages_activity.render(user)
elif page == "Workouts":
    pages_workout.render(user)
elif page == "Cheat Day":
    pages_cheat.render(user)
elif page == "Progress":
    pages_progress.render(user)
elif page == "Profile":
    pages_profile.render(user)
