import duckdb
from datetime import datetime

DB_PATH = "data/wolf_tracks.duckdb"

def init_db(db_path: str = DB_PATH):
    """Create schema and table if they don't exist."""
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.raw_play_history (
                play_id                 BIGINT PRIMARY KEY,
                started_at              TIMESTAMP,
                stopped_at              TIMESTAMP,
                song_duration_seconds   INTEGER,
                play_duration_seconds   INTEGER,
                paused_seconds          INTEGER,
                percent_complete        INTEGER,
                title                   VARCHAR,
                album                   VARCHAR,
                artist                  VARCHAR,
                release_year            INTEGER,
                player                  VARCHAR,
                product                 VARCHAR,
                platform                VARCHAR,
                media_type              VARCHAR,
                transcode_decision      VARCHAR,
                username                VARCHAR,
                user_id                 INTEGER,
                loaded_at               TIMESTAMP DEFAULT now()
                )
        """)
    con.close()

def transform_record(raw: dict) -> dict:
    """Map Tautulli API fields to schema created in init_db"""
    return {
        "play_id": raw.get("reference_id") or raw.get("id"),
        "started_at": datetime.fromtimestamp(int(raw["started"])),
        "stopped_at": datetime.fromtimestamp(int(raw["stopped"])),
        "song_duration_seconds": int(raw.get("duration", 0)),
        "play_duration_seconds": int(raw.get("play_duration", 0)),
        "paused_seconds": int(raw.get("paused_counter", 0)),
        "percent_complete": int(raw.get("percent_complete", 0)),
        "title": raw.get("title"),
        "album": raw.get("parent_title"),
        "artist": raw.get("grandparent_title"),
        "release_year": int(raw["year"]) if raw.get("year") else None,
        "player": raw.get("player"),
        "product": raw.get("product"),
        "platform": raw.get("platform"),
        "media_type": raw.get("media_type"),
        "transcode_decision": raw.get("transcode_decision"),
        "username": raw.get("user"),
        "user_id": int(raw["user_id"]) if raw.get("user_id") else None,
    }

def load_records(records: list[dict], db_path: str = DB_PATH) -> int:
    """Load records into DuckDB with deduplication. Returns count of new records."""
    init_db(db_path)
    con = duckdb.connect(db_path)

    transformed = [transform_record(r) for r in records]

    # Get existing IDs to avoid duplication
    existing_ids = set(
        row[0] for row in
        con.execute("SELECT play_id FROM raw.raw_play_history").fetchall()
    )

    new_records = [r for r in transformed if r["play_id"] not in existing_ids]

    if new_records:
        # Using executemany for clarity
        con.executemany(
            """INSERT INTO raw.raw_play_history 
               (play_id, started_at, stopped_at, song_duration_seconds,
                play_duration_seconds, paused_seconds, percent_complete,
                title, album, artist, release_year, player, product,
                platform, media_type, transcode_decision, username, user_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [tuple(r.values()) for r in new_records]
        )

    con.close()
    return len(new_records)