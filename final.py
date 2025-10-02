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
    """Build a player-centric dataset for all gameweeks including team positions."""
    logging.info("🏁 Starting final player-centric dataset with team positions...")

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

        # 2️⃣ Assign manager IDs and team positions
        all_picks = []
        for manager_id in managers:
            team_data = fetch_data(f"{TEAMS_URL}{manager_id}/event/{gw}")
            if not team_data or "picks" not in team_data:
                continue

            picks = pd.DataFrame(team_data["picks"])
            picks["manager_id"] = manager_id
            picks["gameweek"] = gw

            # Rename columns: 'element' = player ID, 'position' = team position
            picks.rename(columns={"element": "ID", "position": "team_position"}, inplace=True)

            # Keep only relevant columns
            all_picks.append(picks[["ID", "manager_id", "gameweek", "team_position"]])

        # Merge picks with gameweek stats
        if all_picks:
            picks_df = pd.concat(all_picks, ignore_index=True)
            gw_stats = gw_stats.merge(picks_df, on=["ID", "gameweek"], how="left")
            # Fill team_id for backward compatibility
            gw_stats["team_id"] = gw_stats["manager_id"]

        final_records.append(gw_stats)

    # Concatenate all gameweeks
    if not final_records:
        logging.error("No data processed for final dataset.")
        return

    final_df = pd.concat(final_records, ignore_index=True)

    # Save CSV
    final_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    logging.info(f"✅ Player-centric final dataset saved: {output_file}")
    logging.info("🏁 Process completed.")