import logging
from utils import fetch_data,save_csv
import pandas as pd

# Define URLs
BASE_URL            = "https://draft.premierleague.com/api"
PLAYER_DATA_URL     = f"{BASE_URL}/bootstrap-static"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

#Gets all the players data and saves into a CSV file called players_data.csv in data folder
def get_player_data(output_file: str = "Data/players_data.csv"):
    """
    Fetches player data, processes it, and saves it to a CSV file.
    This function performs the following steps:
    1. Fetches player data from a specified URL.
    2. Extracts relevant fields from the player data.
    3. Saves the processed player data to a CSV file.
    4. Returns the player data as a pandas DataFrame.
    Returns:
        pd.DataFrame: A DataFrame containing player data with columns:
                      ['ID', 'First_Name', 'Last_Name', 'Team', 'Position', 'Assists', 'bonus', 'Total points',
                       'xA', 'CS', 'Gc', 'Goals Scored', 'minutes', 'red_cards', 'starts', 'xG',
                       'xGi','xGc','code','PpG']
    """

    data = fetch_data(PLAYER_DATA_URL)
    if not data or "elements" not in data:
        logging.error("No player data retrieved from API.")
        return []
    
    players = data["elements"]

    # Convert list of dicts to DataFrame (includes all fields)
    df = pd.DataFrame(players)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    logging.info(f"✅ Full player dataset saved to {output_file}")

    #
    #if data:
    #    players = data.get('elements', [])
    #    player_data = [
    #        [player['id'], player['first_name'], player['second_name'], player['team'], player['element_type'],
    #         player['assists'],player['bonus'],  player['total_points'],player['expected_assists'],   player['clean_sheets'],
    #         player['goals_conceded'], player['goals_scored'], player['minutes'], player['red_cards'],player['starts'],
    #         player['expected_goals'],player['expected_goal_involvements'], player['expected_goals_conceded'],
    #         player['code'], player['points_per_game']]
    #        for player in players
    #    ]
    #    headers = ['ID', 'First_Name', 'Last_Name', 'Team', 'Position', 'Assists', 'bonus', 'Total points', 'xA', 'CS', 'Gc', 'Goals Scored', 'minutes',
    #               'red_cards', 'starts', 'xG', 'xGi','xGc','code','PpG']
    #    save_csv('Data/players_data.csv', headers, player_data)
    #    print("Player data successfully retrieved.")
        