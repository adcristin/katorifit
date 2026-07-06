"""User profile edit, calorie target override, data export, and reset."""
from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from ..calculations import ACTIVITY_MULTIPLIERS, calc_bmr, calc_fat_loss_target, calc_tdee
from ..db import get_log_history, get_profile, save_log, upsert_profile
from ..models import DailyLog, Profile, User


def render(user: User) -> None:
    st.header("Profile")
    profile = get_profile(user.id)

    with st.form("profile"):
        name = st.text_input("Name", value=profile.name)
        col1, col2 = st.columns(2)
        age = col1.number_input("Age", min_value=0, max_value=120, value=int(profile.age or 0))
        gender = col2.selectbox("Gender", ["Male", "Female"],
                                 index=["Male", "Female"].index(profile.gender))
        col3, col4 = st.columns(2)
        height = col3.number_input("Height (cm)", min_value=0.0, max_value=260.0,
                                    value=float(profile.height_cm or 0), step=0.5)
        weight = col4.number_input("Weight (kg)", min_value=0.0, max_value=400.0,
                                    value=float(profile.weight_kg or 0), step=0.1)
        activity_label = st.selectbox("Activity Level", list(ACTIVITY_MULTIPLIERS.keys()),
                                       index=list(ACTIVITY_MULTIPLIERS.keys()).index(profile.activity_label))
        goal = st.text_area("Goal", value=profile.goal, placeholder="e.g. Run 5k under 25 min")
        submitted = st.form_submit_button("Save", type="primary", width='stretch')

    if submitted:
        upsert_profile(Profile(
            user_id=user.id,
            name=name.strip(),
            age=int(age) or None,
            height_cm=float(height) or None,
            weight_kg=float(weight) or None,
            goal=goal.strip(),
            gender=gender,
            activity_label=activity_label,
            calorie_target_override=profile.calorie_target_override,
        ))
        st.success("Profile saved.")
        st.rerun()

    st.caption(f"Signed in as {user.email}")

    # ------------------------------------------------- calorie target override
    if profile.age and profile.height_cm and profile.weight_kg:
        st.divider()
        st.markdown('<div class="kf-card">', unsafe_allow_html=True)
        st.markdown("**Calorie Target Override**")
        bmr = calc_bmr(profile.gender, profile.weight_kg, profile.height_cm, profile.age)
        tdee = calc_tdee(bmr, profile.activity_label)
        default_target = calc_fat_loss_target(tdee)
        st.caption(f"Auto-calculated target from your profile: **{default_target:.0f} kcal/day**. "
                   "Override it here if your doctor or trainer gave you a different number.")
        use_override = st.toggle("Use custom target", value=profile.calorie_target_override is not None)
        override_val = None
        if use_override:
            override_val = st.number_input(
                "Custom daily calorie target (kcal)", 800, 5000,
                int(profile.calorie_target_override or default_target),
            )
        if st.button("💾 Save Target Setting"):
            profile.calorie_target_override = override_val
            upsert_profile(profile)
            st.success("Saved.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------ data export
    st.divider()
    st.markdown('<div class="kf-card">', unsafe_allow_html=True)
    st.markdown("**Export Your Data**")
    history = get_log_history(user.id, 365)
    if history:
        df = pd.DataFrame([h.__dict__ for h in history])
        st.download_button(
            "⬇️ Download full log history (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name="katorifit_history.csv",
            mime="text/csv",
        )
    else:
        st.caption("No logged history yet.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------ danger zone
    st.markdown('<div class="kf-card">', unsafe_allow_html=True)
    st.markdown("**Danger Zone**")
    st.caption("Wipes today's food/fasting/activity log only. Profile, workouts, and history are untouched.")
    if st.button("🗑️ Reset Today's Log"):
        blank = DailyLog(user_id=user.id, log_date=date.today().isoformat())
        save_log(user.id, date.today().isoformat(), **{
            k: getattr(blank, k) for k in
            ["roti", "protein", "katori", "eggs", "fats", "steps", "walk1_done", "walk2_done",
             "circuit_rounds", "hydration_done", "meal1_done", "meal2_done", "anchor_done",
             "fast_locked", "cheat_mode"]
        })
        st.success("Today's log cleared.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
