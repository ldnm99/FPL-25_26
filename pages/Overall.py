import streamlit as st
import pandas as pd
import plotly.express as px

from visuals import calculate_team_gw_points, get_starting_lineup, get_teams_avg_points

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

selected_player = st.selectbox("Select Player (Optional)", options=[None] + list(df['player_name'].unique()))

# Checkbox for owned players only
owned_only = st.checkbox("Show only owned players")

# Checkbox for not owned players only
not_owned_only = st.checkbox("Show not owned players")

# ---------------- FILTER DATA ----------------
filtered_df = df[(df['gameweek'] >= min_gameweek) & (df['gameweek'] <= max_gameweek)]

if selected_team:
    filtered_df = filtered_df[filtered_df['team_name'] == selected_team]

if owned_only:
    filtered_df = filtered_df[filtered_df['team_name'].notnull()]

if not_owned_only:
    filtered_df = filtered_df[filtered_df['team_name'].isnull()]
    
if selected_player:
    filtered_df = filtered_df[filtered_df['player_name'] == selected_player]
    
# Display filtered dataframe
selected_columns = st.sidebar.multiselect(
    "Select columns to display",
    options=list(filtered_df.columns),
    default=list(filtered_df.columns)
)
st.subheader(f"Players Data from Gameweek {min_gameweek} to {max_gameweek}")
st.dataframe(filtered_df[selected_columns])

# --------------------------------------------------------------------------- VISUALIZATIONS --------------------------------------------------------------------------------
# Get starting lineup
starting_players = get_starting_lineup(filtered_df)

# Calculate team gameweek points
team_gw_points = calculate_team_gw_points(starting_players)

# Display team points
st.subheader("Team Points by Gameweek (Starting XI)")
st.dataframe(team_gw_points)

# ---------------- TEAM AVERAGE POINTS CARDS ----------------
st.subheader("Average Points per Gameweek (Starting XI)")
team_avg_points = get_teams_avg_points(team_gw_points)

# Display cards in 3x2 grid
cols = st.columns(3)
for i, row in team_avg_points.head(7).iterrows():
    with cols[i % 3]:
        st.markdown(
            f"""
            <div style="
                background-color: #1E1E1E;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                text-align: center;
                color: white;
            ">
                <div style="font-size: 2.5rem; font-weight: 600; margin-bottom: 10px;">
                    {row['avg_points']:.1f}
                </div>
                <div style="font-size: 1.2rem; font-weight: 500; opacity: 0.8;">
                    {row['team_name']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


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
