import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from visuals import get_starting_lineup, get_team_total_points

# --- PAGE CONFIG ---
st.set_page_config(page_title="FPL Draft Menu", layout="wide")

# --- HEADER ---
st.title("⚽ Fantasy Premier League Draft Dashboard")
st.markdown("### Select a page to view detailed stats")

# --- LOAD DATA ---
standings = pd.read_csv("Data/league_standings.csv")
df = pd.read_parquet("Data/gw_data.parquet")

# --- DEADLINE & FIXTURES DATA ---
gameweeks = pd.read_csv("Data/gameweeks.csv")
fixtures = pd.read_csv("Data/fixtures.csv")

# Convert to datetime
gameweeks["deadline_time"] = pd.to_datetime(gameweeks["deadline_time"], utc=True)
fixtures["kickoff_time"]   = pd.to_datetime(fixtures["kickoff_time"], utc=True)

# Find next deadline
now = datetime.now(timezone.utc)
next_gw = gameweeks[gameweeks["deadline_time"] > now].sort_values("deadline_time").head(1)

# --- MANAGER BUTTONS ---

st.markdown("### 📋 Select a Page")

manager_list = sorted(standings["team_name"].unique().tolist())
buttons = ["Overall"] + manager_list

if st.button("🌟 Overall", use_container_width=True, type="primary"):
    st.session_state["current_page"] = "Overall"
    st.switch_page("pages/Overall.py")

st.markdown("---")

# --- Manager buttons below ---
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

if not next_gw.empty:
    gw_name = next_gw.iloc[0]["name"]
    deadline = next_gw.iloc[0]["deadline_time"]
    time_left = deadline - now
    next_gw_id = next_gw.iloc[0]["id"]

    # Deadline Info (Full Width)
    st.markdown(f"### ⏰ Next Deadline: **{gw_name}** — {deadline.strftime('%A, %d %B %Y %H:%M %Z')}")
    st.write(f"Time remaining: **{time_left.days} days, {time_left.seconds // 3600} hours, {time_left.seconds % 3600 // 60} minutes**")

    # Filter upcoming fixtures
    upcoming = fixtures[fixtures["event"] == next_gw_id][
        ["team_h_name", "team_a_name", "kickoff_time", "team_h_difficulty", "team_a_difficulty"]
    ]
    upcoming["kickoff_time"] = pd.to_datetime(upcoming["kickoff_time"], utc=True)
    upcoming = upcoming.sort_values("kickoff_time")
    upcoming["kickoff_time"] = upcoming["kickoff_time"].dt.strftime('%A, %d %B %Y %H:%M %Z')

    upcoming.rename(columns={
        "team_h_name": "Home",
        "team_a_name": "Away",
            "kickoff_time": "Kickoff"
        }, inplace=True)
    
else:
    upcoming = pd.DataFrame()
    st.info("🏁 The season might be finished — no upcoming deadlines found.")


# --- MAIN CONTENT AREA ---
left_col, right_col = st.columns([1.5, 1])  # Wider left column for points table

with left_col:
    # Calculate and display team totals
    starting_players = get_starting_lineup(df)
    team_gw_points = get_team_total_points(starting_players)

    st.subheader("🏆 League Table / Total Team Points")
    st.dataframe(team_gw_points, hide_index=True, use_container_width=True)

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



