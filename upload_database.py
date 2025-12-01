import pandas as pd
import io
import os
from supabase import create_client
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_csv(file_path, bucket="data"):
    df = pd.read_csv(file_path)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    supabase.storage.from_(bucket).upload(os.path.basename(file_path), buffer.getvalue(), content_type="text/csv")

def upload_parquet(file_path, bucket="data"):
    df = pd.read_parquet(file_path)
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    supabase.storage.from_(bucket).upload(os.path.basename(file_path), buffer.getvalue(), content_type="application/octet-stream")

if __name__ == "__main__":
    # CSV files
    upload_csv("Data/league_standings.csv")
    upload_csv("Data/players_data.csv")
    
    # Parquet files
    upload_parquet("Data/gw_data.parquet")
    # Optional: upload individual gameweek files
    import os
    for f in os.listdir("Data"):
        if f.startswith("gw") and f.endswith(".parquet") and f != "gw_data.parquet":
            upload_parquet(f)

with open("last_updated.txt", "w") as f:        
    f.write(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
