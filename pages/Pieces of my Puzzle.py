import streamlit as st
import pandas as pd
import plotly.express as px

from visuals import calculate_team_gw_points, get_starting_lineup, get_team_total_points, get_teams_avg_points

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")
GW_DATA_PATH = "Data/gw_data.parquet"
STANDINGS_PATH = "Data/league_standings.csv"

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_parquet(GW_DATA_PATH)
    standings = pd.read_csv(STANDINGS_PATH)
    return df, standings

df, standings = load_data()

# ---------------- MANAGER SELECTION ----------------
# Replace this with session_state if using menu.py
manager_name = "Pieces of my Puzzle"  
if manager_name not in df['team_name'].unique():
    st.error("⚠️ Manager not found in data")
    st.stop()

st.title(f"📊 {manager_name} Dashboard")

# ---------------- OVERVIEW ----------------
st.header("🏆 Season Overview")

# Filter manager data
manager_df = df[df['team_name'] == manager_name]

# Get starting lineup
starting_players = get_starting_lineup(manager_df)

# Calculate team gameweek points
team_gw_points = calculate_team_gw_points(starting_players)

# Calculate average points per gameweek
team_avg_points = get_teams_avg_points(team_gw_points)

# Display team points
st.subheader("Team Points by Gameweek (Starting XI)")
st.dataframe(team_gw_points, use_container_width=True)

# Display average points
st.subheader("Average Points per Gameweek (Starting XI)")
if not team_avg_points.empty:
    avg_points = team_avg_points.loc[team_avg_points['team_name'] == manager_name, 'avg_points'].values[0]
    st.metric("Average Points per Gameweek", f"{avg_points:.2f}")


# ---------------- TEAM PERFORMANCE TREND ------------
st.header("📈 Points Progression")

# Filter manager data
manager_df = df[df['team_name'] == manager_name]

# Get starting lineup
starting_players = get_starting_lineup(manager_df)

# Calculate points per gameweek (pivot table)
team_gw_points = calculate_team_gw_points(starting_players)

# Get manager's points per GW (row of the pivot table)
manager_row = team_gw_points.loc[manager_name].drop('Total')

# Convert Series to DataFrame for merging
manager_points = pd.DataFrame({
    'gameweek': manager_row.index.astype(int),
    'manager_points': manager_row.values
})

# League average (excluding manager)
all_starting_players = get_starting_lineup(df)

# Each manager's total points per GW
all_team_gw_points = (
    all_starting_players.groupby(['team_name', 'gameweek'])['total_points']
    .sum()
    .reset_index()
)

# Exclude the current manager
other_teams = all_team_gw_points[all_team_gw_points['team_name'] != manager_name]

# Calculate average points of other managers per GW
league_avg = (
    other_teams.groupby('gameweek')['total_points']
    .mean()
    .reset_index()
    .rename(columns={'total_points': 'avg_points'})
)

# Merge manager and league averages
comparison_df = manager_points.merge(league_avg, on='gameweek', how='left')

# Melt to long format for Plotly
plot_df = comparison_df.melt(id_vars='gameweek', var_name='Type', value_name='Points')

# Plot line chart
fig = px.line(
    plot_df,
    x='gameweek',
    y='Points',
    color='Type',
    markers=True,
    title=f"{manager_name} – Gameweek Points vs League Average"
)
fig.update_layout(xaxis=dict(dtick=1))
fig.update_traces(line=dict(width=3))
st.plotly_chart(fig, use_container_width=True)

# ---------------- CURRENT GAMEWEEK ----------------
st.header("🎯 Latest Gameweek Lineup")

latest_gw = manager_df['gameweek'].max()
latest_gw_df = manager_df[manager_df['gameweek'] == latest_gw]
latest_gw_df = latest_gw_df.sort_values(by='team_position')


if latest_gw_df.empty:
    st.info("No data for latest gameweek yet.")
else:
    st.markdown(f"**Gameweek {latest_gw}**")
    st.dataframe(
        latest_gw_df[['name', 'team', 'team_position','event_points']],
        use_container_width=True
    )

# ---------------- TOP PERFORMERS ----------------
st.header("⭐ Top Performing Players (Single Gameweek)")

# Aggregate points per player per gameweek
agg_df = (
    manager_df.groupby(['gameweek', 'name', 'team'], as_index=False)
    .agg(
        total_points=('total_points', 'sum'),
        Benched=('team_position', lambda x: (x > 11).any())  # True if player was ever benched in that GW
    )
) 

# Sort by points descending
top_10_gw_performances = agg_df.sort_values('total_points', ascending=False).head(10)

# Display
st.dataframe(
    top_10_gw_performances,
    use_container_width=True
)

# ---------------- PLAYER PROGRESSION ----------------
st.header("📊 Player Points Over Time")

player_progression = manager_df.pivot_table(
    index='gameweek',
    columns='name',
    values='total_points',
    fill_value=0
)

fig2 = px.line(
    player_progression.reset_index(),
    x='gameweek',
    y=player_progression.columns,
    title="Player Points Progression",
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- OTHER STATS ----------------
st.header("📜 Other Stats")

col1, col2, col3 = st.columns(3)

# Best player
best_player = top_10_gw_performances.iloc[0]
col1.metric("Top Scorer", best_player['name'], f"{best_player['total_points']} pts")

# Best & worst Gameweek
# Use manager_points DataFrame instead of undefined gw_points
best_gw_row = manager_points.loc[manager_points['manager_points'].idxmax()]
worst_gw_row = manager_points.loc[manager_points['manager_points'].idxmin()]

col2.metric("Best Gameweek", int(best_gw_row['gameweek']), f"{best_gw_row['manager_points']} pts")
col3.metric("Toughest Gameweek", int(worst_gw_row['gameweek']), f"{worst_gw_row['manager_points']} pts")
