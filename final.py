import logging
import pandas as pd
from utils import fetch_data, fetch_managers_ids, get_player_gw_data

# ------------------ CONFIG ------------------ #
BASE_URL        = "https://draft.premierleague.com/api"
TEAMS_URL       = f"{BASE_URL}/entry/"
GAME_STATUS_URL = f"{BASE_URL}/game"
PLAYERS_CSV     = "Data/players_data.csv"
OUTPUT_FILE     = "Data/gw_data.csv"


# ------------------ LOGGING ------------------ #
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ------------------ HELPERS ------------------ #
def fetch_current_gameweek() -> int:
    """Fetch the current gameweek number from API."""
    data = fetch_data(GAME_STATUS_URL)
    if not data or "current_event" not in data:
        logging.error("Failed to fetch current gameweek.")
        return 0
    return data["current_event"]

def load_players(players_csv=PLAYERS_CSV) -> pd.DataFrame:
    """Load player IDs and names from CSV."""
    df = pd.read_csv(players_csv)
    df["player_name"] = df["first_name"].fillna("") + " " + df["second_name"].fillna("")
    return df[["id", "player_name"]].astype({"id": int})

# ------------------ MAIN PROCESSING ------------------ #
def main(output_file=OUTPUT_FILE):
    """Build a player-centric dataset for all gameweeks."""
    logging.info("🏁 Starting final player-centric dataset...")

    current_gw = fetch_current_gameweek()
    if current_gw == 0:
        logging.error("Aborting: could not fetch current gameweek.")
        return

    managers = fetch_managers_ids()
    if not managers:
        logging.error("Aborting: no manager IDs found.")
        return

    players_df = load_players()
    players_df = players_df.rename(columns={"id": "ID"})

    final_records = []

    # Loop through each gameweek
    for gw in range(1, current_gw + 1):
        logging.info(f"Processing Gameweek {gw}/{current_gw}...")

        # 1️⃣ Fetch all player stats for this gameweek
        gw_stats = get_player_gw_data(gw)
        if gw_stats.empty:
            logging.warning(f"No stats for GW{gw}, skipping...")
            continue

        # Standardize column names
        gw_stats = gw_stats.rename(columns={"id": "ID"})
        gw_stats["gameweek"] = gw

        # Merge player names
        gw_stats = gw_stats.merge(players_df, on="ID", how="left")

        # Initialize team_id column
        gw_stats["team_id"] = pd.NA

        # 2️⃣ Assign manager IDs for players
        for manager_id in managers:
            team_data = fetch_data(f"{TEAMS_URL}{manager_id}/event/{gw}")
            if not team_data or "picks" not in team_data:
                continue

            picks = pd.DataFrame(team_data["picks"])
            picked_ids = picks["element"].astype(int).tolist()

            # Set team_id for players picked by this manager
            gw_stats.loc[gw_stats["ID"].isin(picked_ids), "team_id"] = manager_id

        final_records.append(gw_stats)

    # Concatenate all gameweeks
    if not final_records:
        logging.error("No data processed for final dataset.")
        return

    final_df = pd.concat(final_records, ignore_index=True)

    # Save CSV
    final_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    logging.info(f"✅ Player-centric final dataset saved: {output_file}")











#combined_data = []
#current_gameweek = fetch_data(GAME_STATUS_URL)['current_event']
#
## Get managers IDs from the CSV file
#managers_ids = fetch_managers_ids()
#
## Load player names from CSV
#players_df = pd.read_csv("Data/players_data.csv")
#players_df['player_name'] = players_df['First_Name'] + ' ' + players_df['Last_Name']
#players_df = players_df[['ID', 'player_name']]
#players_df['ID'] = players_df['ID'].astype(int)  # Ensure ID type matches for merge
#
#def main():
#    """Main function to fetch player stats and merge with managers' teams."""
#    print("Starting final data processing...")
#    print('----------------------------------------------------------------------')
#
#    # Loop through each gameweek
#    for gw in range(1, current_gameweek + 1):
#        """Fetch player stats and merge them with each manager's team picks for each gameweek."""
#        gw_stats = get_player_gw_data(gw)
#        gw_stats['gameweek'] = gw
#        gw_stats = gw_stats[['ID', 'gameweek', 'minutes', 'goals_scored', 'assists', 'bonus',
#                             'clean_sheets', 'expected_goals', 'expected_assists',
#                             'expected_goal_involvements', 'expected_goals_conceded', 'total_points']]
#
#        gw_stats['ID'] = gw_stats['ID'].astype(int)
#        gw_stats['gameweek'] = gw_stats['gameweek'].astype(int)
#
#        # Merge player names
#        gw_stats = gw_stats.merge(players_df, on='ID', how='left')
#
#        # Fetch each manager's team picks for each gameweek
#        for manager_id in managers_ids:
#            team_data = fetch_data(f"{TEAMS_URL}{manager_id}/event/{gw}")
#            if not team_data or 'picks' not in team_data:
#                continue
#            
#            picks = pd.DataFrame(team_data['picks'])
#            picks['manager_id'] = manager_id
#            picks['gameweek'] = gw
#            picks.rename(columns={'element': 'ID', 'position': 'team_position'}, inplace=True)
#
#            picks['ID'] = picks['ID'].astype(int)
#            picks['gameweek'] = picks['gameweek'].astype(int)
#
#            # Merge gameweek picks with stats + player name
#            merged = picks.merge(gw_stats, on=['ID', 'gameweek'], how='left')
#            combined_data.append(merged)
#
#    # Concatenate all manager-team-player-gameweek data
#    final_df = pd.concat(combined_data, ignore_index=True)
#
#    # Save to CSV
#    final_df.to_csv("Data/final_data.csv", index=False)
#    print("Saved final_data.csv")
