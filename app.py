import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- LOAD DATA ----------------
st.set_page_config(layout="wide")  # Full width layout

# Load dataset
df = pd.read_csv("Data/gw_data.csv")
standings = pd.read_csv("Data/league_standings.csv")

# Merge team names
df = df.merge(
    standings[['manager_id', 'team_name']],
    left_on='team_id',
    right_on='manager_id',
    how='left'
)

# ---------------- DASHBOARD TITLE ----------------
st.title("FPL Draft Data Dashboard")
st.write("Explore players, managers, and gameweek stats.")

# ---------------- FILTERS ----------------
# Gameweek slider
min_gameweek, max_gameweek = st.slider(
    "Select Gameweek", 
    min_value=int(df['gameweek'].min()), 
    max_value=int(df['gameweek'].max()), 
    value=(int(df['gameweek'].min()), int(df['gameweek'].max()))
)

# Manager filter
teams = df['team_name'].dropna().unique()
selected_team = st.selectbox("Select Manager (Optional)", options=[None] + list(teams))

# Checkbox for owned players only
owned_only = st.checkbox("Show only owned players")

# ---------------- FILTER DATA ----------------
filtered_df = df[(df['gameweek'] >= min_gameweek) & (df['gameweek'] <= max_gameweek)]

if selected_team:
    filtered_df = filtered_df[filtered_df['team_name'] == selected_team]

if owned_only:
    filtered_df = filtered_df[filtered_df['team_name'].notnull()]

# Display filtered dataframe
selected_columns = st.sidebar.multiselect(
    "Select columns to display",
    options=list(filtered_df.columns),
    default=list(filtered_df.columns)
)
st.subheader(f"Players Data from Gameweek {min_gameweek} to {max_gameweek}")
st.dataframe(filtered_df[selected_columns])

# ---------------- VISUALIZATIONS ----------------
starting_players = filtered_df[filtered_df['team_position'] <= 11]

# Pivot table
team_gw_points = starting_players.pivot_table(
    index='team_name',
    columns='gameweek',
    values='total_points',
    aggfunc='sum',
    fill_value=0
)

if not team_gw_points.empty:
    team_gw_points['Total'] = team_gw_points.sum(axis=1)
    cols = list(team_gw_points.columns)
    cols.remove('Total')
    cols.append('Total')
    team_gw_points = team_gw_points[cols]

# Reorder columns to have Total at the end
cols = list(team_gw_points.columns)
if 'Total' in cols:
    cols.remove('Total')
    cols.append('Total')
team_gw_points = team_gw_points[cols]

# Sort by Total descending
team_gw_points = team_gw_points.sort_values(by='Total', ascending=False)

# Display pivot table in Streamlit
st.subheader("Team Points by Gameweek (Starting XI)")
st.dataframe(team_gw_points)

# Melt for scatter & line charts
team_gw_points_melted = team_gw_points.reset_index().melt(
    id_vars='team_name',
    var_name='gameweek',
    value_name='points'
) if not team_gw_points.empty else pd.DataFrame(columns=['team_name', 'gameweek', 'points'])

# Remove 'Total' and convert gameweek to int
team_gw_points_melted = team_gw_points_melted[team_gw_points_melted['gameweek'] != 'Total']
team_gw_points_melted['gameweek'] = team_gw_points_melted['gameweek'].astype(int) if not team_gw_points_melted.empty else pd.Series(dtype=int)

# Filter by gameweek
team_gw_points_melted = team_gw_points_melted[
    (team_gw_points_melted['gameweek'] >= min_gameweek) &
    (team_gw_points_melted['gameweek'] <= max_gameweek)
] if not team_gw_points_melted.empty else team_gw_points_melted

# ---------------- DASHBOARD ----------------
st.title("Current League Standings")

# Top Row: Line Charts
st.subheader("Line Charts")
col1, col2 = st.columns(2)

with col1:
    if not team_gw_points_melted.empty:
        fig_line = px.line(
            team_gw_points_melted,
            x='gameweek',
            y='points',
            color='team_name',
            markers=True,
            title="Team Points per Gameweek"
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data for the selected gameweek/manager.")

with col2:
    if not team_gw_points_melted.empty:
        team_cumsum = team_gw_points_melted.copy()
        team_cumsum['cum_points'] = team_cumsum.groupby('team_name')['points'].cumsum()
        fig_cumsum = px.line(
            team_cumsum,
            x='gameweek',
            y='cum_points',
            color='team_name',
            markers=True,
            title="Cumulative Team Points"
        )
        st.plotly_chart(fig_cumsum, use_container_width=True)
    else:
        st.info("No data for the selected gameweek/manager.")

# Bottom Row: Heatmap & Scatter
st.subheader("Heatmap & Scatter")
col3, col4 = st.columns(2)

# Filter pivot table columns by gameweek slider
heatmap_data = team_gw_points.loc[:, [col for col in team_gw_points.columns if col != 'Total']]
heatmap_data = heatmap_data.loc[:, heatmap_data.columns[(heatmap_data.columns >= min_gameweek) & (heatmap_data.columns <= max_gameweek)]] if not heatmap_data.empty else heatmap_data

with col3:
    if not heatmap_data.empty:
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Gameweek", y="Team", color="Points"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No data for the selected gameweek/manager.")

with col4:
    if not team_gw_points_melted.empty:
        fig_scatter = px.scatter(
            team_gw_points_melted,
            x='gameweek',
            y='team_name',
            size='points',
            color='points',
            color_continuous_scale='Viridis',
            hover_data=['points'],
            title="Team Points per Gameweek (Scatter)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No data for the selected gameweek/manager.")
