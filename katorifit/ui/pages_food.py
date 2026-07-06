"""Hand & Katori portion-based food tracker."""
from __future__ import annotations

from datetime import date

import streamlit as st

from ..calculations import CAL_PER_UNIT, calories_from_log
from ..db import get_log, save_log
from ..models import User

TODAY = date.today().isoformat()


def _counter_row(label: str, cal_each: int, value: int, key: str, cap=None, extra_note: str = "") -> int:
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.markdown(f"**{label}**  \n<span style='color:#8a8275; font-size:0.85rem;'>"
                    f"{cal_each} cal / unit {extra_note}</span>", unsafe_allow_html=True)
    with col2:
        if st.button("➖", key=f"minus_{key}"):
            value = max(0, value - 1)
    with col3:
        st.markdown(f"<div style='text-align:center; font-size:1.3rem; font-weight:700;'>{value}</div>",
                     unsafe_allow_html=True)
    with col4:
        limit_hit = cap is not None and value >= cap
        if st.button("➕", key=f"plus_{key}", disabled=limit_hit):
            value += 1
    if cap is not None and value >= cap:
        st.caption(f"⚠️ Daily cap of {cap} reached for {label}.")
    return value


def render(user: User) -> None:
    st.header("🍽️ Hand & Katori Food Tracker")
    st.caption("Log meals with visual portion units instead of weighing grams.")

    log = get_log(user.id, TODAY)

    with st.container():
        st.markdown('<div class="kf-card">', unsafe_allow_html=True)
        log.roti = _counter_row("🫓 Roti (palm-sized, ungreased)", CAL_PER_UNIT["roti"],
                                 log.roti, "roti", cap=2, extra_note="(max 2/meal)")
        st.divider()
        log.protein = _counter_row("🍗 Protein (hand-sized chicken/fish/paneer/dal)", CAL_PER_UNIT["protein"],
                                    log.protein, "protein", extra_note="(target 1/meal)")
        st.divider()
        log.katori = _counter_row("🥕 Carotenoid Katori (greens/carrots/pumpkin)", CAL_PER_UNIT["katori"],
                                   log.katori, "katori")
        st.divider()
        log.eggs = _counter_row("🥚 Eggs (whole, boiled)", CAL_PER_UNIT["eggs"], log.eggs, "eggs")
        st.divider()
        log.fats = _counter_row("🧈 Fats (tsp ghee/mustard oil)", CAL_PER_UNIT["fats"],
                                 log.fats, "fats", cap=3, extra_note="(cap 2-3/day)")
        st.markdown("</div>", unsafe_allow_html=True)

    save_log(user.id, TODAY, roti=log.roti, protein=log.protein, katori=log.katori,
              eggs=log.eggs, fats=log.fats)

    if log.katori < 2:
        st.error("⚠️ Less than 2 katoris of greens/veg logged today — aim higher for antioxidants!")
    else:
        st.success("✅ Great carotenoid intake today!")

    st.caption(f"Today's total: **{calories_from_log(log):.0f} kcal** — saved automatically.")
