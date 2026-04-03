import requests
import os
import time 

def _make_request(cmd: str, **kwargs) -> dict:
    """Make a request to the Tautilli API."""
    params = {
        "apikey": os.environ["TAUTULLI_API_KEY"],
        "cmd": cmd,
        **kwargs
    }
    response = requests.get(os.environ["TAUTULLI_BASE_URL"], params=params)
    response.raise_for_status()
    return response.json()["response"]["data"]

def get_all_history() -> list[dict]:
    """Pull all music play history with pagination."""
    all_records = []
    start = 0
    length = 100

    while True:
        data = _make_request(
            "get_history",
            media_type="track",
            length=str(length),
            start=str(start),
            order_column="date",
            order_dir="desc"
        )

        batch = data["data"]
        all_records.extend(batch)
        
        if len(batch) < length:
            break

        start += length
        time.sleep(0.2) # polite pause between pages

    return all_records
