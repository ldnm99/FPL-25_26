import requests
import pandas as pd

# ---------------- BOOTSTRAP STATIC (for deadlines) ----------------
url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(url).json()

# Create DataFrame for gameweek data
events_df = pd.DataFrame(data["events"])

# Select relevant columns
deadlines = events_df[["id", "name", "deadline_time", "finished", "is_current"]]

# Save to CSV
deadlines.to_csv("Data/gameweeks.csv", index=False)
print("✅ Saved gameweek deadlines to Data/gameweeks.csv")


# ---------------- FIXTURES (for matches & difficulty) ----------------
fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"
fixtures = requests.get(fixtures_url).json()
fixtures_df = pd.DataFrame(fixtures)

# Keep only useful columns
fixtures_df = fixtures_df[
    ["event", "team_h", "team_a", "team_h_difficulty", "team_a_difficulty", "kickoff_time"]
]

# Fetch team data dynamically from the same API (instead of hardcoding)
teams_df = pd.DataFrame(data["teams"])
team_map = dict(zip(teams_df["id"], teams_df["name"]))

# Map team IDs to names
fixtures_df["team_h_name"] = fixtures_df["team_h"].map(team_map)
fixtures_df["team_a_name"] = fixtures_df["team_a"].map(team_map)

# Save to CSV
fixtures_df.to_csv("Data/fixtures.csv", index=False)
print("✅ Saved fixtures to Data/fixtures.csv")

# Preview
print(fixtures_df.head())
