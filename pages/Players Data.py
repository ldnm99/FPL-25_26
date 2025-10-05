import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- LOAD DATA ----------------
st.set_page_config(layout="wide")  # Full width layout

df        = pd.read_csv("Data/gw_data.csv")
standings = pd.read_csv("Data/league_standings.csv")
players   = pd.read_csv("Data/players_data.csv")

# Merge team names
df = df.merge(
    standings[['manager_id', 'team_name']],
    left_on='team_id',
    right_on='manager_id',
    how='left'
)

# ---------------- DASHBOARD TITLE ----------------
st.title("FPL Draft Players Data")

selected_player = st.selectbox("Select Player", options=[None] + list(df['player_name'].unique()))


selected_player = st.selectbox("Select Player", options=[None] + list(df['name'].unique()))

# Checkbox for owned players only
owned_only = st.checkbox("Show only owned players")

# Checkbox for not owned players only
not_owned_only = st.checkbox("Show not owned players")

if owned_only:
    filtered_df = filtered_df[filtered_df['team_name'].notnull()]

if not_owned_only:
    filtered_df = filtered_df[filtered_df['team_name'].isnull()]
    
if selected_player:
    filtered_df = filtered_df[filtered_df['player_name'] == selected_player]