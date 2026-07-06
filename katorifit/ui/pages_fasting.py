"""16:8 intermittent fasting daily schedule."""
from __future__ import annotations

from datetime import date, datetime, time as dtime

import streamlit as st

from ..db import get_log, save_log
from ..models import User

TODAY = date.today().isoformat()


def _is_now(target_time: dtime, window_min: int = 30) -> bool:
    now = datetime.now().time()
    t = datetime.combine(datetime.today(), target_time)
    n = datetime.combine(datetime.today(), now)
    return abs((t - n).total_seconds()) <= window_min * 60


def render(user: User) -> None:
    st.header("⏱️ 16:8 Daily Schedule")
    st.caption("A late-rise routine timeline: fast until 10am, eat within an 8-hour window.")

    log = get_log(user.id, TODAY)

    st.markdown('<div class="kf-card">', unsafe_allow_html=True)

    st.markdown("**10:00 AM — Wake & Break Fast**  \nHydration check before your first meal.")
    hydration_done = st.checkbox("💧 Hydration done", value=log.hydration_done)

    st.markdown("**12:30 PM — Meal 1 (Power Lunch)**")
    meal1_done = st.checkbox("🍽️ Meal 1 logged", value=log.meal1_done)

    st.markdown("**04:30 PM — Mid-day Anchor**  \nGreen tea + roasted makhana.")
    anchor_done = st.checkbox("🍵 Anchor snack done", value=log.anchor_done)

    st.markdown("**08:00 PM — Meal 2 (Light Dinner)**")
    meal2_done = st.checkbox("🍽️ Meal 2 logged", value=log.meal2_done)

    st.markdown("**08:30 PM — Fasting Window Locks**")
    fast_locked = st.toggle("🔒 Lock fasting window", value=log.fast_locked)

    st.markdown("</div>", unsafe_allow_html=True)

    save_log(user.id, TODAY, hydration_done=hydration_done, meal1_done=meal1_done,
              anchor_done=anchor_done, meal2_done=meal2_done, fast_locked=fast_locked)

    if _is_now(dtime(12, 30)):
        st.info("⏰ It's around Meal 1 time — Power Lunch!")
    if _is_now(dtime(20, 0)):
        st.info("⏰ It's around Meal 2 time — keep it light.")

    completed = sum([hydration_done, meal1_done, anchor_done, meal2_done, fast_locked])
    st.progress(completed / 5)
    st.caption(f"{completed}/5 checkpoints done today.")
