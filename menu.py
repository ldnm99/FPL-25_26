import streamlit as st
import pandas as pd
from visuals import get_starting_lineup, get_team_total_points

# --- PAGE CONFIG ---
st.set_page_config(page_title="FPL Draft Menu", layout="wide")

# --- HEADER ---
st.title("⚽ Fantasy Premier League Draft Dashboard")
st.markdown("### Select a page to view detailed stats")

# --- LOAD DATA ---
standings = pd.read_csv("Data/league_standings.csv")

# --- EXTRACT UNIQUE MANAGER NAMES ---
manager_list = sorted(standings["team_name"].unique().tolist())

# Add "Overall" button 
buttons = ["Overall"] + manager_list 

# --- BUTTON LAYOUT ---
cols = st.columns(4)  # 4 buttons per row 

for i, name in enumerate(buttons):
    with cols[i % 4]:
        if st.button(name, use_container_width=True):
            # Store selected page in session
            st.session_state["current_page"] = name
            # Navigate to the page
            st.switch_page(f"pages/{name}.py")

# ---------------- Main points table ----------------
# Load dataset
df = pd.read_parquet("Data/gw_data.parquet")
standings = pd.read_csv("Data/league_standings.csv")

# Get starting lineup
starting_players = get_starting_lineup(df)

# Calculate total team gameweek points
team_gw_points = get_team_total_points(starting_players)

# Display team points
st.subheader("Total Team Points")
st.dataframe(team_gw_points)