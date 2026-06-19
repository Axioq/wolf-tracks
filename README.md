# Wolf Tracks

Wolf Tracks is a personal data engineering project that extracts Plex music listening history from the Tautulli API, loads it into DuckDB, and prepares analytics-ready models with dbt. The goal is to turn raw listening events into a local, reproducible dataset that can power a self-hosted music analytics dashboard.

## Why I Built This

I wanted a hands-on project that mirrors a real analytics engineering workflow: API ingestion, schema design, incremental loading, transformation, orchestration, and containerized local development. Music listening data is personal enough to stay interesting while still having the same challenges as production data pipelines, including pagination, deduplication, typed storage, transformation logic, and scheduled jobs.

## Architecture

```text
Tautulli API
    |
    v
Python extraction
    |
    v
DuckDB raw schema
    |
    v
dbt analytics models
    |
    v
Dashboard-ready listening metrics
```

## Tech Stack

- Python for API extraction and load logic
- Requests for Tautulli API communication
- DuckDB as the local analytical database
- dbt-duckdb for transformation and modeling
- Prefect 3 for flow orchestration and scheduling
- Docker Compose for reproducible local services

## Current Features

- Extracts paginated track-level listening history from Tautulli
- Loads data into a typed `raw.raw_play_history` DuckDB table
- Deduplicates records by `play_id` before insert
- Tracks ingestion metadata with `loaded_at`
- Creates a dbt staging model with cleaned column names and derived fields
- Filters out very short plays from the staged analytics layer
- Defines a daily Prefect deployment for scheduled pipeline runs

## Repository Structure

```text
.
|-- extract/                 # Tautulli API client and extraction logic
|-- load/                    # DuckDB schema creation and load logic
|-- scripts/                 # Prefect flow entrypoint
|-- transform/               # dbt project, profiles, sources, and models
|-- docker-compose.yml       # Prefect server, worker, and pipeline services
|-- dockerfile               # Python runtime image
|-- prefect.yaml             # Prefect deployment configuration
`-- requirements.txt         # Python dependencies
```

## Data Model

The raw DuckDB table captures one row per listening event with fields such as:

- Playback identifiers: `play_id`, `user_id`, `username`
- Time fields: `started_at`, `stopped_at`, `loaded_at`
- Track metadata: `title`, `album`, `artist`, `release_year`
- Playback metrics: `song_duration_seconds`, `play_duration_seconds`, `paused_seconds`, `percent_complete`
- Client metadata: `player`, `product`, `platform`, `media_type`, `transcode_decision`

The dbt staging model renames raw fields into analytics-friendly names, derives `listen_duration_seconds`, and flags listens where at least 50% of the track was completed.

## Running Locally

### Prerequisites

- Docker and Docker Compose
- A running Tautulli instance connected to Plex
- A Tautulli API key

### Environment Variables

Create a local `.env` file with:

```bash
TAUTULLI_API_KEY=your_api_key
TAUTULLI_BASE_URL=http://host.docker.internal:8181/api/v2
```

The `.env` file is ignored by git so API credentials stay local.

### Start Services

```bash
docker compose up --build
```

This starts:

- A Prefect server at `http://localhost:4200`
- A Prefect worker for scheduled runs
- A development pipeline container with the project mounted into `/app`

### Run the Pipeline Manually

```bash
docker compose exec pipeline python scripts/run_pipeline.py
```

### Run dbt Models

```bash
docker compose exec pipeline dbt run --project-dir transform --profiles-dir transform
```

## Orchestration

The Prefect deployment in `prefect.yaml` defines a daily schedule for the `wolf-tracks` flow:

```text
0 16 * * * UTC
```

The flow currently runs extraction and loading. dbt transformations can be run separately and are intended to become part of the scheduled workflow as the project matures.

## Project Status

This project is actively evolving. The core ingestion and local warehouse pieces are in place. Planned improvements include:

- Add dbt tests and documentation for model quality checks
- Add aggregate marts for artist, album, track, and listening-session analysis
- Include dbt execution in the Prefect flow
- Build a lightweight dashboard on top of the DuckDB analytics layer
- Add automated validation for pipeline runs

## What This Demonstrates

- Building an end-to-end ELT pipeline from an external API
- Designing a local analytical schema in DuckDB
- Handling paginated extraction and deduplicated loads
- Separating raw ingestion from transformed analytics models
- Using dbt for repeatable SQL transformations
- Running and scheduling data workflows with Prefect
- Containerizing a data project for reproducible local development
