"""Log & manage workouts."""
from __future__ import annotations

from datetime import date

import streamlit as st

from ..db import add_workout, delete_workout, list_workouts
from ..models import User

WORKOUT_TYPES = ["Run", "Walk", "Cycle", "Swim", "Strength", "Yoga", "HIIT", "Other"]


def render(user: User) -> None:
    st.header("Log a workout")

    with st.form("log_workout", clear_on_submit=True):
        col1, col2 = st.columns(2)
        w_date = col1.date_input("Date", value=date.today())
        w_type = col2.selectbox("Type", WORKOUT_TYPES)
        col3, col4 = st.columns(2)
        duration = col3.number_input("Duration (min)", min_value=1, max_value=600, value=30)
        calories = col4.number_input("Calories", min_value=0, max_value=5000, value=200)
        notes = st.text_area("Notes", placeholder="How did it feel?", height=80)
        submitted = st.form_submit_button("Save workout", type="primary", width='stretch')

    if submitted:
        add_workout(user.id, w_date.isoformat(), w_type, int(duration), int(calories), notes.strip())
        st.success("Workout logged.")
        st.rerun()

    st.divider()
    st.header("History")
    workouts = list_workouts(user.id)
    if not workouts:
        st.info("No workouts logged yet.")
        return

    for w in workouts:
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.markdown(f"**{w.type}**  \n<span style='color:#8a8275'>{w.date}</span>", unsafe_allow_html=True)
            c2.markdown(f"{w.duration_min} min")
            c3.markdown(f"{w.calories} kcal")
            if c4.button("🗑", key=f"del_{w.id}", help="Delete"):
                delete_workout(user.id, w.id)
                st.rerun()
            if w.notes:
                st.caption(w.notes)
            st.divider()
