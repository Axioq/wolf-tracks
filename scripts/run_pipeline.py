import sys
sys.path.insert(0, "/app")

from prefect import flow, task
from extract.tautulli_client import get_all_history
from load.loader import load_records

@task
def extract_task():
    print("Extracting from Tautulli...")
    records = get_all_history()
    print(f"Pulled {len(records)} records from API")
    return records

@task
def load_task(records):
    print("Loading to DuckDB...")
    new_count = load_records(records)
    print(f"Loaded {new_count} new records")

@flow(name="wolf-tracks")
def pipeline():
    records = extract_task()
    load_task(records)
    print("Pipeline Complete!")

if __name__ == "__main__":
    pipeline()