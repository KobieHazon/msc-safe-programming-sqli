# Blind SQL Injection Exercise

This repository preserves and documents a 2023 Safe Programming coursework exercise on SQL injection. It includes the supplied deliberately vulnerable PHP/MySQL lab, my Python solution for blind data extraction, the submitted report, and a recovered result file.

> [!CAUTION]
> The lab is intentionally vulnerable. Run it only on a trusted local machine. The maintained Compose configuration binds the web service to `127.0.0.1` and does not expose MySQL to the host.

## Authorship and provenance

| Path | Classification | Author or source |
| --- | --- | --- |
| `assignment/` | Course-supplied | Safe Programming exercise material |
| `lab/web/` | Course-supplied framework | Supplied vulnerable application; embedded pages credit Appsecco and Riyaz Walikar |
| `lab/database/docker-entrypoint-initdb.d/` | Course-supplied framework | Recovered from the supplied database image |
| `docker-compose.original.yml`, `scripts/` | Course-supplied framework | Original exercise launcher and image references |
| `solution/` | Authored solution | Me |
| `results/` | Authored submission output | Me |
| `compose.yaml`, Dockerfiles, tests, and repository documentation | Tests and tooling | Me |

The original Docker image exports were about 303 MB and were not suitable repository source. Their small final application and initialization layers were recovered without changing their historical commits. The current Dockerfiles reconstruct equivalent local services from official base images, with a two-line `mysqli_connect_errno` compatibility update for current PHP.

## Requirements

- Docker with Compose support
- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/)

## Run the lab

Start a clean local environment:

```bash
docker compose up --build --detach
```

Open `http://127.0.0.1:8000`, or run the recovered blind-SQLi solver:

```bash
uv sync
uv run python -m solution.exercise_solver
```

The solver answers the exercise's database-discovery and file-extraction tasks. It writes the newly extracted flag to `flag.txt`; that generated file is ignored by Git. `results/flag.bin` is the historical recovered output.

Stop the lab and delete its generated database volume:

```bash
docker compose down --volumes
```

The original launcher is preserved for historical completeness, but it expects course-provided image archives that are not included. Use `compose.yaml` for the reproducible setup.

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
- `lab/`: recovered vulnerable web application and database initialization files.
- `solution/exercise_solver.py`: blind-SQLi database and file extraction implementation.
- `solution/misc.py`: binary-search helpers used by the solver.
- `results/report.pdf`: sanitized submitted report; personal details other than the author's name were removed.
- `docker-compose.original.yml`: original environment description for provenance.
- `compose.yaml`: locally reproducible environment.

## License

No blanket license is asserted over the supplied course framework. The repository keeps file-level provenance explicit so the authored solution and supplied material are not confused.
