import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="FPL Fixtures", layout="wide")

# --- LOAD DATA ---
fixtures = pd.read_csv("Data/fixtures.csv")

# Map team IDs to names
teams = {
    1: "Arsenal", 2: "Aston Villa", 3: "Brentford", 4: "Bournemouth",
    5: "Brighton", 6: "Burnley", 7: "Chelsea", 8: "Crystal Palace",
    9: "Everton", 10: "Fulham", 11: "Leeds United", 12: "Liverpool",
    13: "Manchester City", 14: "Manchester United", 15: "Newcastle United",
    16: "Nottingham Forest", 17: "Sunderland", 18: "Tottenham",
    19: "West Ham", 20: "Wolverhampton"
}

# Map badges
team_badges = {team: f"assets/badges/{team}.png" for team in teams.values()}

fixtures["team_h_name"] = fixtures["team_h"].map(teams)
fixtures["team_a_name"] = fixtures["team_a"].map(teams)
fixtures["kickoff_time"] = pd.to_datetime(fixtures["kickoff_time"])

# --- SELECT GAMEWEEK ---
gameweeks = sorted(fixtures["event"].dropna().unique())
selected_gw = st.selectbox("Select Gameweek", gameweeks)

# --- FILTER FIXTURES ---
gw_fixtures = fixtures[fixtures["event"] == selected_gw].copy()  # avoid SettingWithCopyWarning
gw_fixtures["Kickoff"] = gw_fixtures["kickoff_time"].dt.strftime("%A, %d %B %H:%M")

# --- DIFFICULTY COLOR FUNCTION ---
def difficulty_color(difficulty):
    if difficulty <= 2: return "🟢"
    elif difficulty == 3: return "🟡"
    else: return "🔴"

# --- DISPLAY FIXTURES ---
st.title(f"⚽ Fixtures – Gameweek {selected_gw}")

for _, row in gw_fixtures.iterrows():
    # Layout: Home badge | Home team | VS | Away team | Away badge
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 1])
    
    with col1:  # Home badge
        st.image(team_badges[row['team_h_name']], width=80)
    with col2:  # Home name + difficulty
        st.markdown(f"**{row['team_h_name']}** {difficulty_color(row['team_h_difficulty'])}")
    with col3:
        st.markdown("**vs**")
    with col4:  # Away name + difficulty
        st.markdown(f"{difficulty_color(row['team_a_difficulty'])} **{row['team_a_name']}**")
    with col5:  # Away badge
        st.image(team_badges[row['team_a_name']], width=80)
    
    # Kickoff time below
    st.write(f"🕒 Kickoff: {row['Kickoff']}")
    st.markdown("---")
