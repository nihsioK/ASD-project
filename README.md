# SciStats API

[![CI/CD](https://github.com/nihsioK/sci-stats-api/actions/workflows/ci.yml/badge.svg)](https://github.com/nihsioK/sci-stats-api/actions/workflows/ci.yml)

A small FastAPI service with user login, a basic CRUD for school subjects and an endpoint that returns descriptive statistics for a series of experimental measurements.
It was built for Assignment 3 (Software Development and Integration) to demonstrate Git, GitHub, automated testing and a CI/CD pipeline.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/auth/register` | Create a user (`email`, `password`) |
| POST | `/auth/login` | Get a bearer token |
| GET | `/auth/me` | Current user (token required) |
| POST | `/subjects` | Create a subject (`name`, `grade` 1-11) |
| GET | `/subjects` | List own subjects |
| GET | `/subjects/{id}` | Get own subject |
| DELETE | `/subjects/{id}` | Delete own subject |
| POST | `/stats` | Count, mean, median, sample standard deviation, min and max |
| GET | `/docs` | Interactive OpenAPI documentation |

Subject endpoints require the header `Authorization: Bearer <token>` from `/auth/login`.

Example statistics request:

```bash
curl -X POST localhost:8000/stats -H "content-type: application/json" -d '{"values": [9.8, 9.7, 9.9, 9.81]}'
```

Example response:

```json
{"count": 4, "mean": 9.8025, "median": 9.805, "stdev": 0.0818, "min": 9.7, "max": 9.9}
```

At least two values are required, otherwise the API returns `422`.

## Run locally

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Data is stored in a local SQLite file `app.db`, tables are created on startup.

## Project structure

```
app/
  main.py          FastAPI app, routers, table creation
  db.py            SQLAlchemy engine and session
  security.py      password hashing, tokens, current user
  models/          SQLAlchemy tables: User, Subject
  schemas/         Pydantic request and response models
  repositories/    database queries
  routers/         HTTP endpoints: auth, subjects, stats
tests/             pytest tests with an in-memory database
```

## Test and lint

```bash
uv run ruff check .
uv run pytest
```

## Run with Docker

```bash
docker run -p 8000:8000 ghcr.io/nihsiok/sci-stats-api:latest
```

## CI/CD

The pipeline is defined in [.github/workflows/ci.yml](.github/workflows/ci.yml).

- **CI** runs on every push and pull request: install locked dependencies with uv, lint with Ruff, test with pytest.
- **CD** runs only on `main` after CI passes: build the Docker image and publish it to GitHub Container Registry.

## Technology choices

- **Python** is the standard language for scientific computing.
- **FastAPI** gives request validation and OpenAPI docs with very little code.
- **SQLAlchemy + SQLite** store users and subjects with zero setup; the same code can move to PostgreSQL.
- **uv** manages Python, dependencies and a lock file, so local and CI environments match.
- **pytest** and **Ruff** are the most common testing and linting tools in the Python ecosystem.
- **GitHub Actions** is built into GitHub, so no external CI service is needed.

## License

[MIT](LICENSE)
