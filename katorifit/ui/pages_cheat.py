"""Sunday cheat meal strategy tool."""
from __future__ import annotations

from datetime import date

import streamlit as st

from ..db import get_log, save_log
from ..models import User

TODAY = date.today().isoformat()


def render(user: User) -> None:
    st.header("🎉 Sunday Cheat Meal Strategy")

    log = get_log(user.id, TODAY)

    st.markdown('<div class="kf-card">', unsafe_allow_html=True)
    st.write(
        "Activating this locks in a protein-only light lunch, opens an "
        "unrestricted cheat dinner slot, and requires a full 10,000 steps "
        "before the cheat dinner unlocks."
    )
    if st.button("🎉 Activate Sunday Cheat Meal", type="primary"):
        save_log(user.id, TODAY, cheat_mode=True)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if log.cheat_mode:
        st.markdown('<div class="kf-card">', unsafe_allow_html=True)
        st.subheader("Today's Cheat Template")
        st.write("🥗 **Lunch:** Ultra-light, protein-only (e.g. grilled chicken/paneer + salad)")
        steps_ok = log.steps >= 10000
        if steps_ok:
            st.success("🍕 **Dinner:** Unrestricted — cheat dinner unlocked! Enjoy responsibly.")
        else:
            remaining = 10000 - log.steps
            st.warning(f"🔒 **Dinner locked.** Walk {remaining} more steps (log them on the "
                        f"Activity page) to unlock your cheat dinner.")
        if st.button("↩️ Deactivate for today"):
            save_log(user.id, TODAY, cheat_mode=False)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
