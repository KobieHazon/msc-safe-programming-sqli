# Blind SQL Injection Exercise

This repository preserves and documents a 2023 Safe Programming coursework exercise on SQL injection. It includes the supplied deliberately vulnerable PHP/MySQL lab, my Python solution for blind data extraction, the submitted report, and a result file.

> [!CAUTION]
> The lab is intentionally vulnerable. Run it only on a trusted local machine. The maintained Compose configuration binds the web service to `127.0.0.1` and does not expose MySQL to the host.

## Included materials

- `assignment/`: supplied Safe Programming exercise material.
- `lab/web/`: supplied vulnerable application; its embedded pages credit Appsecco and Riyaz Walikar.
- `lab/database/docker-entrypoint-initdb.d/`: initialization files from the supplied database image.
- `docker-compose.original.yml` and `scripts/`: original exercise launcher and image references.
- `solution/` and `results/`: my solution and submission output.
- `compose.yaml`, Dockerfiles, and tests: the reproducible local environment and validation helpers.

The Dockerfiles build the local web application and database from official base images.

## Requirements

- Docker with Compose support
- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/)

## Run the lab

Start a clean local environment:

```bash
docker compose up --build --detach
```

Open `http://127.0.0.1:8000`, or run the blind-SQLi solver:

```bash
uv sync
uv run python -m solution.exercise_solver
```

The solver answers the exercise's database-discovery and file-extraction tasks. It writes the newly extracted flag to `flag.txt`; that generated file is ignored by Git. `results/flag.bin` is the historical output.

Stop the lab and delete its generated database volume:

```bash
docker compose down --volumes
```

## Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
docker compose config --quiet
```

The automated tests cover the solver's binary-search logic and do not attack an external target. Full end-to-end validation requires the local Compose lab.

## Contents

- `assignment/exercise.pdf`: supplied exercise brief.
- `lab/`: vulnerable web application and database initialization files.
- `solution/exercise_solver.py`: blind-SQLi database and file extraction implementation.
- `solution/misc.py`: binary-search helpers used by the solver.
- `results/report.pdf`: my submitted report.
- `docker-compose.original.yml`: original environment description for reference.
- `compose.yaml`: locally reproducible environment.
