# menu.py
import streamlit as st
from datetime import datetime, timezone
from data_utils import (
    load_data,
    get_next_gameweek,
    get_upcoming_fixtures,
    get_starting_lineup,
    get_team_total_points
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="FPL Draft Menu", layout="wide")

# --- HEADER ---
st.title("⚽ Fantasy Premier League Draft Dashboard")
st.markdown("### Select a page to view detailed stats")

# --- LOAD DATA ---
df, standings, gameweeks, fixtures = load_data(
    gw_data_path="Data/gw_data.parquet",
    standings_path="Data/league_standings.csv",
    gameweeks_path="Data/gameweeks.csv",
    fixtures_path="Data/fixtures.csv"
)

# --- NEXT GAMEWEEK & UPCOMING FIXTURES ---
now = datetime.now(timezone.utc)
next_gw = get_next_gameweek(gameweeks, now)
upcoming = get_upcoming_fixtures(fixtures, next_gw)

# --- MANAGER BUTTONS ---
st.markdown("### 📋 Select a Page")

manager_list = sorted(standings["team_name"].unique().tolist())
buttons = ["Overall"] + manager_list

# Overall button
if st.button("🌟 Overall", use_container_width=True, type="primary"):
    st.session_state["current_page"] = "Overall"
    st.switch_page("pages/Overall.py")

st.markdown("---")

# Manager buttons (4 per row)
cols_per_row = 4
manager_buttons = [b for b in buttons if b != "Overall"]

for i in range(0, len(manager_buttons), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, name in enumerate(manager_buttons[i:i + cols_per_row]):
        with cols[j]:
            if st.button(name, use_container_width=True):
                st.session_state["current_page"] = name
                st.switch_page(f"pages/{name}.py")

st.divider()

# --- NEXT DEADLINE INFO ---
if not next_gw.empty:
    gw_name = next_gw.iloc[0]["name"]
    deadline = next_gw.iloc[0]["deadline_time"]
    time_left = deadline - now
    st.markdown(
        f"### ⏰ Next Deadline: **{gw_name}** — {deadline.strftime('%A, %d %B %Y %H:%M %Z')}"
    )
    st.write(
        f"Time remaining: **{time_left.days} days, {time_left.seconds // 3600} hours, "
        f"{time_left.seconds % 3600 // 60} minutes**"
    )
else:
    st.info("🏁 The season might be finished — no upcoming deadlines found.")

# --- MAIN CONTENT ---
left_col, right_col = st.columns([1.5, 1])

with left_col:
    st.subheader("🏆 League Table / Total Team Points")
    starting_players = get_starting_lineup(df)
    team_total_points = get_team_total_points(starting_players)
    st.dataframe(team_total_points, hide_index=True, use_container_width=True)

with right_col:
    st.subheader("⚔️ Upcoming Fixtures")
    if not upcoming.empty:
        st.dataframe(
            upcoming[["Home", "Away", "Kickoff"]],
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("No fixtures available.")
