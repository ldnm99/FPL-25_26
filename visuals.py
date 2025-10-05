import pandas as pd

def get_starting_lineup(df):
    """
    Get the starting lineup (players with team_position <= 11) from the dataframe.
    Args:
        df (pd.DataFrame): DataFrame containing player data.
    Returns:
        pd.DataFrame: DataFrame containing only starting lineup players.
    """
    return df[df['team_position'] <= 11]

def calculate_team_gw_points(starting_players):
    """
    Calculate the total points for each team per gameweek from the starting players.
    Args:
        starting_players (pd.DataFrame): DataFrame containing starting lineup players.
    Returns:
        pd.DataFrame: Pivot table with teams as rows, gameweeks as columns, and total points as values.
    """
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

    return team_gw_points

def get_teams_avg_points(team_gw_points):
    if not team_gw_points.empty:
        # Remove 'Total' column for average calculation
        gw_cols = [c for c in team_gw_points.columns if c != 'Total']

        # Calculate average points per GW for each team
        team_avg_points = (
            team_gw_points[gw_cols]
            .mean(axis=1)
            .reset_index()
            .rename(columns={0: "avg_points"})
        )
        team_avg_points.columns = ["team_name", "avg_points"]

        # Sort by highest average
        team_avg_points = team_avg_points.sort_values(by="avg_points", ascending=False).reset_index(drop=True)              
        return team_avg_points
    
def get_team_total_points(starting_players):
    """
    Calculate the total points for each team from the starting players.
    Args:
        starting_players (pd.DataFrame): DataFrame containing starting lineup players.
    Returns:
        pd.DataFrame: DataFrame with teams and their total points.
    """
    if not starting_players.empty:
        team_total_points = starting_players.groupby('team_name')['total_points'].sum().reset_index()
        team_total_points.columns = ['Team', 'Total Points']
        team_total_points = team_total_points.sort_values(by='Total Points', ascending=False).reset_index(drop=True)
        return team_total_points
    else:
        return pd.DataFrame(columns=['Team', 'Total Points'])