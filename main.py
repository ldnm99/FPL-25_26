import os
import logging

from league  import get_league_standings
from players import get_player_data
import final 

###########################################################Endpoints###########################################################
# Define URLs
BASE_URL            = "https://draft.premierleague.com/api"

#Our league ID 
LEAGUE_ID           = '24636'

#Endpoint to get league data info like standings
LEAGUE_DETAILS_URL  = f"{BASE_URL}/league/"f"{LEAGUE_ID}/details"

#Endpoint to get the managers teams for each gameweek
TEAMS_URL           = f"{BASE_URL}/entry/"

#Endpoint to get the current gameweek
GAME_STATUS_URL     = f"{BASE_URL}/game"

#Player data from the gameweek endpoint
GW_URL              = f"{BASE_URL}/event/"

#Player data endpoint
PLAYER_DATA_URL     = f"{BASE_URL}/bootstrap-static"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
#################################################################################################################################

# Main function to execute the data extraction script
def run_pipeline(league_id: int):
    """
    Main function to execute the data extraction script.
    This function performs the following tasks:
    1. Prints a starting message.
    2. Ensures the 'Data' directory exists.
    3. Fetches and saves league standings data.
    4. Fetches and saves player data.
    5. Prints a completion message.
    6. Saves the data as CSV files in the 'Data' folder.
    Returns:
        None
    """

    logging.info("🚀 Starting FPL Draft data extraction pipeline...")
    

    # Ensure the data directory exists
    if not os.path.exists('Data'):
        os.makedirs('Data', exist_ok=True)

    # Fetch and save league standings data with just managers' information
    logging.info("Fetching league standings...")
    get_league_standings(league_id, output_file="Data/league_standings.csv")

    # Player data
    logging.info("Fetching player data...")
    get_player_data(output_file="Data/players_data.csv")

    logging.info("✅ Data extraction completed successfully.")
    logging.info("Running final data processing...")
    final.main()

    logging.info("✅ Pipeline completed successfully.")

# Main function
if __name__ == "__main__":
    # Ask user for league ID
    try:
        league_id = int(input("Enter your League ID: "))
    except ValueError:
        print("❌ Invalid input. Please enter a numeric League ID.")
        exit(1)

    run_pipeline(league_id) 