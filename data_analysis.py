import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Data/gw_data.csv")

# Overview
print(df.info())
print(df.describe())

# Check missing values
print(df.isna().sum())

# Unique values in categorical columns
print(df['player_name'].nunique(), "players")
print(df['team_id'].nunique(), "managers")
print(df['gameweek'].nunique(), "gameweeks")


# Total points per player across all gameweeks
top_players = df.groupby('player_name')['total_points'].sum().sort_values(ascending=False)
print(top_players.head(10))


# Which players does each manager own most consistently?
manager_players = df.dropna(subset=['team_id']).groupby(['team_id','player_name']).size().unstack(fill_value=0)
print(manager_players)

#Total points contribution per manager per gameweek
manager_points = df.dropna(subset=['team_id']).groupby(['team_id','gameweek'])['total_points'].sum().unstack()
print(manager_points)

#Best performing manager overall
manager_total = df.dropna(subset=['team_id']).groupby('team_id')['total_points'].sum()
print(manager_total.sort_values(ascending=False))


