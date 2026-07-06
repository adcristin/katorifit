"""Progress charts: workouts, weight trend, calorie adherence, steps."""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from ..calculations import calc_bmr, calc_fat_loss_target, calc_tdee, calories_from_log
from ..db import get_log_history, get_profile, get_weight_history, list_workouts
from ..models import User


def render(user: User) -> None:
    st.header("Progress")

    profile = get_profile(user.id)

    # ---------------------------------------------------------- weight trend
    weight_history = get_weight_history(user.id, 90)
    if len(weight_history) >= 2:
        df_w = pd.DataFrame([w.__dict__ for w in weight_history])
        st.subheader("Weight trend")
        st.line_chart(df_w.set_index("log_date")["weight_kg"])
    else:
        st.caption("Log your weight on the **Profile** page on at least 2 different "
                   "days to see a weight trend here.")

    # ---------------------------------------------------- calorie adherence
    if profile.age and profile.height_cm and profile.weight_kg:
        bmr = calc_bmr(profile.gender, profile.weight_kg, profile.height_cm, profile.age)
        tdee = calc_tdee(bmr, profile.activity_label)
        target = profile.calorie_target_override or calc_fat_loss_target(tdee)

        log_history = get_log_history(user.id, 30)
        if log_history:
            df_l = pd.DataFrame([h.__dict__ for h in log_history])
            df_l["calories"] = [calories_from_log(h) for h in log_history]

            st.subheader("Calorie adherence (last 30 days)")
            st.caption(f"Target: {target:.0f} kcal/day")
            st.bar_chart(df_l.set_index("log_date")["calories"])

            st.subheader("Steps (last 30 days)")
            st.line_chart(df_l.set_index("log_date")["steps"])

            st.markdown('<div class="kf-card">', unsafe_allow_html=True)
            st.markdown("**Last 7 Days Summary**")
            last7 = df_l.tail(7)
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Calories", f"{last7['calories'].mean():.0f} kcal")
            c2.metric("Avg Steps", f"{last7['steps'].mean():.0f}")
            on_target_days = (last7["calories"] <= target).sum()
            c3.metric("On-Target Days", f"{on_target_days}/{len(last7)}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("Log food and activity for a few days to unlock calorie/step charts.")

    st.divider()

    # ------------------------------------------------------- workout charts
    st.subheader("Workouts")
    workouts = list_workouts(user.id)
    if not workouts:
        st.info("Log a few workouts to see charts here.")
        return

    df = pd.DataFrame([w.__dict__ for w in workouts])
    df["date"] = pd.to_datetime(df["date"])

    period = st.selectbox("Range", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"], index=1)
    if period != "All time":
        days = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}[period]
        cutoff = pd.Timestamp(date.today() - timedelta(days=days))
        df = df[df["date"] >= cutoff]

    if df.empty:
        st.info("No workouts in this range.")
        return

    daily = (
        df.groupby(df["date"].dt.date)
        .agg(minutes=("duration_min", "sum"), calories=("calories", "sum"), sessions=("id", "count"))
        .reset_index()
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total sessions", int(daily["sessions"].sum()))
    c2.metric("Total minutes", int(daily["minutes"].sum()))
    c3.metric("Total calories", int(daily["calories"].sum()))

    st.markdown("##### Minutes per day")
    st.bar_chart(daily.set_index("date")["minutes"])

    st.markdown("##### Calories per day")
    st.bar_chart(daily.set_index("date")["calories"])

    st.markdown("##### By workout type")
    by_type = df.groupby("type").agg(sessions=("id", "count"), minutes=("duration_min", "sum")).sort_values("minutes", ascending=False)
    st.dataframe(by_type, width="stretch")
