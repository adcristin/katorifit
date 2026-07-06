"""Home dashboard."""
from __future__ import annotations

import random
from datetime import date, timedelta

import streamlit as st

from ..calculations import (
    MYTH_TIPS, calc_bmr, calc_fat_loss_target, calc_tdee, calories_from_log,
)
from ..db import (
    compute_streak, get_log, get_profile, katori_days_hit, list_workouts, total_steps,
)
from ..models import User
from .layout import hero_header

TODAY = date.today().isoformat()


def _badge(label: str, earned: bool) -> None:
    if earned:
        st.markdown(
            f"<span style='display:inline-block; background:#eaf5ee; color:#1f5c3a; "
            f"border:1px solid #2f8a4d; border-radius:999px; padding:4px 12px; "
            f"font-size:0.8rem; margin:3px 5px 3px 0;'>✅ {label}</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<span style='display:inline-block; background:transparent; color:#8a8275; "
            f"border:1px dashed #ccc; border-radius:999px; padding:4px 12px; "
            f"font-size:0.8rem; margin:3px 5px 3px 0;'>🔒 {label}</span>",
            unsafe_allow_html=True,
        )


def render(user: User) -> None:
    hero_header()
    profile = get_profile(user.id)
    greeting = profile.name.strip() or user.email.split("@")[0]
    st.subheader(f"Hi, {greeting} 👋")

    # ------------------------------------------------------- myth-buster tip
    st.session_state.setdefault("kf_tip_index", random.randint(0, len(MYTH_TIPS) - 1))
    title, tip = MYTH_TIPS[st.session_state["kf_tip_index"]]
    st.markdown(
        f"<div class='kf-card' style='border-left:4px solid #e05a2b;'>"
        f"<b>{title}:</b> {tip}</div>",
        unsafe_allow_html=True,
    )
    if st.button("💡 Show another tip"):
        st.session_state["kf_tip_index"] = (st.session_state["kf_tip_index"] + 1) % len(MYTH_TIPS)
        st.rerun()

    # -------------------------------------------------- BMR/TDEE/target/gauge
    if profile.age and profile.height_cm and profile.weight_kg:
        bmr = calc_bmr(profile.gender, profile.weight_kg, profile.height_cm, profile.age)
        tdee = calc_tdee(bmr, profile.activity_label)
        target = profile.calorie_target_override or calc_fat_loss_target(tdee)

        c1, c2, c3 = st.columns(3)
        c1.metric("BMR", f"{bmr:.0f}", help="kcal/day")
        c2.metric("TDEE", f"{tdee:.0f}", help="kcal/day")
        c3.metric("Fat-Loss Target", f"{target:.0f}", help="kcal/day")

        today_log = get_log(user.id, TODAY)
        calories_logged = calories_from_log(today_log)
        st.progress(min(calories_logged / target, 1.0) if target else 0.0)
        if calories_logged > target:
            st.warning(f"You're {calories_logged - target:.0f} kcal over your fat-loss target today.")
        elif calories_logged == 0:
            st.info("Nothing logged yet today — head to **Food Tracker** in the sidebar.")
        else:
            st.success(f"{target - calories_logged:.0f} kcal remaining in today's budget "
                       f"({calories_logged:.0f}/{target:.0f} kcal logged).")

        # ---------------------------------------------------------- streaks
        current_streak, best_streak = compute_streak(user.id, target)
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("🔥 Day Streak", current_streak, help="Consecutive on-target days")
        sc2.metric("Best Streak", best_streak, help="days")
        sc3.metric("Steps (90d)", f"{total_steps(user.id, 90):,}")

        # ---------------------------------------------------------- badges
        st.markdown('<div class="kf-card">', unsafe_allow_html=True)
        st.markdown("**Achievements**")
        katori_days = katori_days_hit(user.id, 90)
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            _badge("3-Day Streak", current_streak >= 3 or best_streak >= 3)
        with b2:
            _badge("7-Day Streak", best_streak >= 7)
        with b3:
            _badge("Carotenoid Champ", katori_days >= 10)
        with b4:
            _badge("Century Walker", total_steps(user.id, 90) >= 100000)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Fill in your age, height, and weight on the **Profile** page to "
                "unlock your BMR/TDEE calorie target and daily gauge.")

    # ---------------------------------------------------- recent workouts
    workouts = list_workouts(user.id)
    today = date.today()
    week_ago = today - timedelta(days=7)
    week = [w for w in workouts if w.date >= week_ago.isoformat()]
    total_min = sum(w.duration_min for w in week)
    total_cal = sum(w.calories for w in week)
    sessions = len(week)

    st.markdown("### This week's workouts")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sessions (7d)", sessions)
    c2.metric("Minutes (7d)", total_min)
    c3.metric("Calories (7d)", total_cal)

    st.markdown("### Recent workouts")
    if not workouts:
        st.info("No workouts yet. Head to **Workouts** to log your first session.")
        return
    for w in workouts[:5]:
        st.markdown(
            f"""
            <div class="kf-card">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-weight:600;">{w.type}</div>
                  <div style="color:#8a8275; font-size:0.85rem;">{w.date}</div>
                </div>
                <div style="text-align:right;">
                  <div>{w.duration_min} min</div>
                  <div style="color:#8a8275; font-size:0.85rem;">{w.calories} kcal</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
