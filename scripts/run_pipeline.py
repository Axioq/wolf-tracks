import sys
sys.path.insert(0, "/app")

from extract.tautulli_client import get_all_history
from load.loader import load_records

if __name__ == "__main__":
    print("Extracting from Tautulli...")
    records = get_all_history()
    print(f"Pulled {len(records)} records from API")

    print("Loading to DuckDB...")
    new_count = load_records(records)
    print(f"Loaded {new_count} new records")

    print("Pipeline Complete!")