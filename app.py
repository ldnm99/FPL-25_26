import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("Data/final_player_centric.csv")

st.title("FPL Draft Data Dashboard")
st.write("Explore players, managers, and gameweek stats.")

# ---------------- FILTERS ----------------
# Select Gameweek
gameweek = st.slider("Select Gameweek", min_value=int(df['gameweek'].min()), max_value=int(df['gameweek'].max()), value=int(df['gameweek'].max()))

# Select Manager (optional)
managers = df['team_id'].dropna().unique()
manager = st.selectbox("Select Manager (optional)", options=[None] + list(managers))

# Filter dataframe
filtered_df = df[df['gameweek'] == gameweek]
if manager:
    filtered_df = filtered_df[filtered_df['team_id'] == manager]

st.subheader(f"Players Data for Gameweek {gameweek}")
st.dataframe(filtered_df)

# ---------------- VISUALIZATIONS ----------------
st.subheader("Top Players by Total Points")
top_players = filtered_df.groupby("player_name")["total_points"].sum().sort_values(ascending=False).head(10)
fig = px.bar(top_players, x=top_players.index, y=top_players.values, labels={"x":"Player","y":"Total Points"})
st.plotly_chart(fig)

st.subheader("Minutes vs Total Points")
fig2 = px.scatter(filtered_df, x="minutes", y="total_points", hover_data=["player_name", "team_id"])
st.plotly_chart(fig2)
