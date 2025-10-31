# data_utils.py
import pandas as pd
from datetime import datetime, timezone

# ---------------- DATA LOADING ----------------
def load_data(
    gw_data_path  ="Data/gw_data.parquet",
    standings_path="Data/league_standings.csv",
    gameweeks_path="Data/gameweeks.csv",
    fixtures_path ="Data/fixtures.csv"
):
    """
    Load all necessary FPL data.
    Returns:
        df: player GW data
        standings: league standings
        gameweeks: GW deadlines
        fixtures: fixtures data
    """
    df = pd.read_parquet(gw_data_path)
    standings = pd.read_csv(standings_path)
    gameweeks = pd.read_csv(gameweeks_path)
    fixtures  = pd.read_csv(fixtures_path)

    # Convert date columns to UTC datetime
    gameweeks["deadline_time"] = pd.to_datetime(gameweeks["deadline_time"], utc=True)
    fixtures["kickoff_time"]   = pd.to_datetime(fixtures["kickoff_time"], utc=True)

    return df, standings, gameweeks, fixtures


# ---------------- NEXT GAMEWEEK ----------------
def get_next_gameweek(gameweeks: pd.DataFrame, now: datetime = None) -> pd.DataFrame:
    """
    Return the next gameweek row based on current UTC time.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    next_gw = gameweeks[gameweeks["deadline_time"] > now].sort_values("deadline_time").head(1)
    return next_gw


# ---------------- UPCOMING FIXTURES ----------------
def get_upcoming_fixtures(fixtures: pd.DataFrame, next_gw: pd.DataFrame) -> pd.DataFrame:
    """
    Return formatted fixtures for the next gameweek.
    """
    if next_gw.empty:
        return pd.DataFrame()

    next_gw_id = next_gw.iloc[0]["id"]
    upcoming = fixtures[fixtures["event"] == next_gw_id][
        ["team_h_name", "team_a_name", "kickoff_time", "team_h_difficulty", "team_a_difficulty"]
    ].copy()

    upcoming = upcoming.sort_values("kickoff_time")
    upcoming["kickoff_time"] = upcoming["kickoff_time"].dt.strftime('%A, %d %B %Y %H:%M %Z')

    upcoming.rename(columns={
        "team_h_name": "Home",
        "team_a_name": "Away",
        "kickoff_time": "Kickoff"
    }, inplace=True)

    return upcoming


# ---------------- MANAGER FILTER ----------------
def get_manager_data(df: pd.DataFrame, manager_name: str) -> pd.DataFrame:
    """Filter dataframe for a specific manager."""
    if manager_name not in df['manager_team_name'].unique():
        return pd.DataFrame()  # return empty for safety
    return df[df['manager_team_name'] == manager_name]


# ---------------- STARTING LINEUP ----------------
def get_starting_lineup(df: pd.DataFrame) -> pd.DataFrame:
    """Get starting XI (positions 1-11)."""
    return df[df['team_position'] <= 11].copy()


# ---------------- TEAM GAMEWEEK POINTS ----------------
def calculate_team_gw_points(starting_players: pd.DataFrame) -> pd.DataFrame:
    team_gw_points = starting_players.pivot_table(
        index='manager_team_name',
        columns='gw',
        values='gw_points',
        aggfunc='sum',
        fill_value=0
    )
    if team_gw_points.empty:
        return team_gw_points
    team_gw_points['Total'] = team_gw_points.sum(axis=1)
    cols = [c for c in team_gw_points.columns if c != 'Total'] + ['Total']
    return team_gw_points[cols].sort_values(by='Total', ascending=False)


# ---------------- TEAM AVERAGE POINTS ----------------
def get_teams_avg_points(team_gw_points: pd.DataFrame) -> pd.DataFrame:
    if team_gw_points.empty:
        return pd.DataFrame(columns=['team_name', 'avg_points'])
    gw_cols = [c for c in team_gw_points.columns if c != 'Total']
    team_avg_points = team_gw_points[gw_cols].mean(axis=1).reset_index().rename(columns={0:'avg_points'})
    team_avg_points.columns = ['team_name', 'avg_points']
    return team_avg_points.sort_values(by='avg_points', ascending=False)


# ---------------- TOTAL POINTS BY TEAM ----------------
def get_team_total_points(starting_players: pd.DataFrame) -> pd.DataFrame:
    if starting_players.empty:
        return pd.DataFrame(columns=['manager_team_name','Total Points'])
    team_total_points = (
        starting_players.groupby('manager_team_name')['gw_points']
        .sum()
        .reset_index()
        .rename(columns={'manager_team_name':'Team','gw_points':'Total Points'})
        .sort_values('Total Points', ascending=False)
        .reset_index(drop=True)
    )
    return team_total_points


# ---------------- POINTS BY POSITION ----------------
def points_per_player_position(starting_players: pd.DataFrame) -> pd.DataFrame:

    print(starting_players['position'])

    if starting_players.empty:
        return pd.DataFrame(columns=['position','gw_points'])
    
    return starting_players.groupby('position')['gw_points'].sum().reset_index()


# ---------------- TOP PERFORMERS ----------------
def get_top_performers(manager_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    agg_df = (
        manager_df.groupby(['gw','full_name','real_team'], as_index=False)
        .agg(
            total_points=('gw_points','sum'),
            Benched=('team_position', lambda x: (x>11).any())
        )
    )
    top_df = agg_df.sort_values('total_points', ascending=False).head(top_n)
    top_df.rename(columns={'gw':'Gameweek','full_name':'Player','real_team':'Team','total_points':'Points'}, inplace=True)
    return top_df


# ---------------- PLAYER PROGRESSION ----------------
def get_player_progression(manager_df: pd.DataFrame) -> pd.DataFrame:
    return manager_df.pivot_table(
        index='gw',
        columns='full_name',
        values='gw_points',
        fill_value=0
    )