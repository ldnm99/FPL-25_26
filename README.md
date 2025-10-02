# ⚽ Fantasy Premier League Draft Data Extractor

This project extracts, processes, and visualizes Fantasy Premier League Draft data for the 2025/26 season.

It pulls data from the FPL Draft API and produces structured .csv files in a local Data/ folder.

The Streamlit dashboard provides interactive visualizations for players, managers, and gameweek performance.

It processes and saves the extracted data into structured `.csv` files stored in a local `Data/` folder.
---

## 📁 Project Structure
FPL-25_26/

├── app.py               # Main Streamlit dashboard
├── extract.py           # Fetches data from the API
├── processing.py        # Processes CSVs and merges player/team data
├── league_classification.py # Creates league tables and HTML outputs
├── utils.py             # Helper functions: fetch API data, save CSV, etc.
├── Data/                # CSV files stored here (league standings, player stats)
├── requirements.txt     # Python dependencies for deployment
└── README.md            # This file


---

## 🚀 Features

- Data Extraction:
  - League standings with manager info
  - Player statistics and metadata
  - Gameweek-specific player performance
- Data Visualizations:
  - Table of all players with filters
  - Pivot table: Teams as rows, Gameweeks as columns, with a Total column
  - Line chart: points per gameweek per team
  - Cumulative line chart: total points over gameweeks
  - Heatmap and scatter plot of team points
  - Interactive filters: Gameweek range, Manager, Owned players
- Data Storage
    - Data Storage
    - Outputs CSV files in Data/
---

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/fpl-draft-dashboard.git
cd fpl-draft-dashboard
```

2. Install dependencies
This project uses standard libraries, but make sure you have the following installed:
```
pip install -r requirements.txt
```
This includes:
```
streamlit
pandas
plotly
requests
```
3. Run the Dashboard
```
streamlit run app.py
```
Open the URL in your browser to explore the dashboard.

## 📦 Output Files
Inside the Data/ folder:

- league_Standings.csv: Manager IDs, names, waiver pick, and team name
- gw_data.csv: Player statistics for each gameweek
- players_data.csv: Static player metadata (optional)

## 📚 API Endpoints Used
https://draft.premierleague.com/api/league/{league_id}/details

https://draft.premierleague.com/api/bootstrap-static

https://draft.premierleague.com/api/event/{gameweek}/live

https://draft.premierleague.com/api/game

## 🛠 Modules Overview
app.py

Streamlit dashboard with 2x2 visualizations and interactive filters

extract.py

Fetches data from the FPL Draft API and saves CSVs in Data/

processing.py

Cleans, merges, and prepares player and team data for analysis

league_classification.py

Generates league tables and HTML reports from processed data

utils.py
## Shared utilities:

- fetch_data(): Handles GET requests

- save_csv(): Saves lists of data to .csv files

- Additional helper functions

📌 Notes

- All output data is saved locally inside the Data/ folder.
- Gameweek data handling (from event/{gameweek}/live) is available via get_player_gw_data(gameweek) in utils.py.
- The dashboard is deployed using Streamlit, with full-page layout and wide 2x2 visualizations.

