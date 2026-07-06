"""Activity & habit tracker: steps, walk alerts, bodyweight circuit, plank timer."""
from __future__ import annotations

from datetime import date

import streamlit as st

from ..db import get_log, save_log
from ..models import User

TODAY = date.today().isoformat()


def _plank_timer(seconds: int = 45) -> None:
    st.iframe(
        f"""
        <div style="font-family:sans-serif; text-align:center;">
          <div id="display" style="font-size:2.4rem; font-weight:800; color:#e05a2b;">{seconds}s</div>
          <button id="startBtn" style="background:#2f8a4d; color:white; border:none;
              border-radius:10px; padding:8px 18px; font-weight:700; cursor:pointer;">
            Start Plank
          </button>
        </div>
        <script>
          const display = document.getElementById('display');
          const btn = document.getElementById('startBtn');
          let total = {seconds};
          let interval = null;
          btn.onclick = function() {{
            if (interval) clearInterval(interval);
            let remaining = total;
            display.innerText = remaining + "s";
            interval = setInterval(function() {{
              remaining -= 1;
              if (remaining <= 0) {{
                clearInterval(interval);
                display.innerText = "Done! \\ud83d\\udcaa";
                display.style.color = "#2f8a4d";
              }} else {{
                display.innerText = remaining + "s";
              }}
            }}, 1000);
          }};
        </script>
        """,
        height=110,
        width="stretch",
    )


def render(user: User) -> None:
    st.header("🏃 Activity & Habit Tracker")

    log = get_log(user.id, TODAY)

    st.markdown('<div class="kf-card">', unsafe_allow_html=True)
    st.subheader("Step Counter")
    steps = st.slider("Steps today", 0, 15000, log.steps, step=100)
    st.progress(min(steps / 9000, 1.0))
    st.caption(f"{steps:,} / 9,000 step goal")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="kf-card">', unsafe_allow_html=True)
    st.subheader("Walk Alerts")
    walk1_done = st.checkbox("🚶 Post-Lunch Walk (15 mins)", value=log.walk1_done)
    walk2_done = st.checkbox("🚶 Post-Dinner Walk (30 mins)", value=log.walk2_done)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="kf-card">', unsafe_allow_html=True)
    st.subheader("In-Room Circuit (4 rounds)")
    st.caption("Each round: 15 Squats · 12 Knee Push-ups · 20 Lunges · 45s Plank")
    cols = st.columns(4)
    rounds_done = []
    for i in range(4):
        with cols[i]:
            rounds_done.append(st.checkbox(f"Round {i+1}", value=(log.circuit_rounds > i), key=f"round_{i}"))
    circuit_rounds = sum(rounds_done)
    st.progress(circuit_rounds / 4)
    _plank_timer(45)
    st.markdown("</div>", unsafe_allow_html=True)

    save_log(user.id, TODAY, steps=steps, walk1_done=walk1_done, walk2_done=walk2_done,
              circuit_rounds=circuit_rounds)
