import logging
import os
import pandas as pd
from utils import fetch_data, fetch_managers_ids, get_player_gw_data

# ------------------ CONFIG ------------------ #
BASE_URL        = "https://draft.premierleague.com/api"
TEAMS_URL       = f"{BASE_URL}/entry/"
GAME_STATUS_URL = f"{BASE_URL}/game"
PLAYERS_CSV     = "Data/players_data.csv"
GW_FOLDER       = "Data/gameweeks_parquet"
MERGED_OUTPUT   = "Data/gw_data.parquet"
STANDINGS_CSV   = "Data/league_standings.csv"


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

def load_players() -> pd.DataFrame:
    """Load player IDs and names from CSV."""
    df = pd.read_csv(PLAYERS_CSV)
    df = df.astype({"ID": int})
    return df

def fetch_manager_picks(manager_id: int, gw: int) -> pd.DataFrame:
    """Fetch a managers team picks for a given gameweek."""
    url = f"{TEAMS_URL}/{manager_id}/event/{gw}"
    data = fetch_data(url)
    if not data or "picks" not in data:
        return pd.DataFrame()

    picks = pd.DataFrame(data["picks"])
    picks.rename(columns={"element": "ID", "position": "team_position"}, inplace=True)
    picks["manager_id"] = manager_id
    picks["gameweek"] = gw
    return picks[["ID", "manager_id", "gameweek", "team_position"]]

def build_gameweek_data(gw: int, managers: list[int], players_df: pd.DataFrame) -> pd.DataFrame:
    """Build a single gameweek DataFrame."""
    logging.info(f"Processing Gameweek {gw}...")

    gw_stats = get_player_gw_data(gw)
    if gw_stats.empty:
        logging.warning(f"No player stats found for GW{gw}")
        return pd.DataFrame()

    gw_stats.rename(columns={"id": "ID"}, inplace=True)
    gw_stats["gameweek"] = gw
    gw_stats = gw_stats.merge(players_df, on="ID", how="left")

    # Collect all manager picks for the GW
    picks = [fetch_manager_picks(mid, gw) for mid in managers]
    picks = [p for p in picks if not p.empty]

    if picks:
        picks_df = pd.concat(picks, ignore_index=True)
        gw_stats = gw_stats.merge(picks_df, on=["ID", "gameweek"], how="left")
        gw_stats["team_id"] = gw_stats["manager_id"]

    return gw_stats

def save_gameweek(gw_df: pd.DataFrame, gw: int, standings_csv="Data/league_standings.csv"):
    """Save a single gameweek file."""
    os.makedirs(GW_FOLDER, exist_ok=True)
    output_path = f"{GW_FOLDER}/gw_data_gw{gw}.parquet"

    # ✅ Read the CSV first
    standings_df = pd.read_csv(standings_csv)

    # Merge team names
    gw_df = gw_df.merge(
        standings_df[['manager_id', 'team_name']],
        left_on='team_id',
        right_on='manager_id',
        how='left'
    )
    
    gw_df.to_parquet(output_path, index=False, engine="pyarrow")
    logging.info(f"✅ Saved Gameweek {gw} as Parquet: {output_path}")

def merge_all_gameweeks():
    """Combine all GW CSVs into one big file."""
    files = sorted([f for f in os.listdir(GW_FOLDER) if f.startswith("gw_data_gw") and f.endswith(".parquet")])
    if not files:
        logging.warning("No gameweek Parquet files found to merge.")
        return

    dfs = [pd.read_parquet(os.path.join(GW_FOLDER, f)) for f in files]
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_parquet(MERGED_OUTPUT, index=False, engine="pyarrow")
    logging.info(f"📦 Merged all gameweeks into {MERGED_OUTPUT}")


# ------------------ MAIN PROCESSING ------------------ #
def main():
    logging.info("🏁 Starting incremental FPL gameweek data extraction...")

    current_gw = fetch_current_gameweek()
    if current_gw == 0:
        logging.error("Aborting: could not fetch current gameweek.")
        return

    managers = fetch_managers_ids()
    if not managers:
        logging.error("Aborting: no manager IDs found.")
        return

    players_df = load_players()

    # Identify already processed GWs
    os.makedirs(GW_FOLDER, exist_ok=True)
    existing_gws = {
        int(f.split("gw")[-1].split(".")[0])
        for f in os.listdir(GW_FOLDER)
        if f.startswith("gw_data_gw")
    }

    logging.info(f"Already have data for GWs: {sorted(existing_gws)}")

    # Fetch only missing GWs
    for gw in range(1, current_gw + 1):
        if gw in existing_gws:
            logging.info(f"Skipping Gameweek {gw} (already saved)")
            continue

        gw_df = build_gameweek_data(gw, managers, players_df)
        if not gw_df.empty:
            save_gameweek(gw_df, gw)

    # Rebuild master dataset
    merge_all_gameweeks()

    logging.info("🏁 Incremental data extraction completed successfully.")
