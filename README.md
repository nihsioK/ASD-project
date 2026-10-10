# SciStats - Teacher CRM

[![CI/CD](https://github.com/nihsioK/ASD-project/actions/workflows/ci.yml/badge.svg)](https://github.com/nihsioK/ASD-project/actions/workflows/ci.yml)

A small teacher CRM with descriptive statistics of student results.
A teacher manages students and subjects, records scores, sees summary statistics and the distribution of marks, and generates short-term lesson plans (KSP) with an AI service.
It was built for Assignment 3 (Software Development and Integration) to demonstrate Git, GitHub, automated testing and a CI/CD pipeline.

## Features

- Registration and login with bearer tokens.
- Students: full name, class, parent phone, notes.
- Subjects with student scores in percent.
- Statistics per subject: count, mean, median, standard deviation, min, max, marks 5/4/3/2 and pass rate.
- Statistics for any series of measurements (`POST /stats`).
- Short-term lesson plan (KSP) generation through OpenRouter, with a mock generator by default.
- Web interface served at `/`, OpenAPI documentation at `/docs`.

Scores are converted to marks with the criteria-based scale: 85-100 % is 5, 65-84 % is 4, 40-64 % is 3, below 40 % is 2.
Marks 3 and higher count as passed.

## Run with Docker Compose

```bash
docker compose up --build
```

Open http://localhost:8000 and log in with the demo account `demo@school.kz` / `demo12345`.
Compose starts PostgreSQL, fills it with demo data (8 students, 3 subjects, 24 scores, 1 lesson plan) and starts the API.

KSP generation uses a mock by default.
To use OpenRouter, put `OPENROUTER_API_KEY=...` (and optionally `OPENROUTER_MODEL=...`) into a `.env` file next to `docker-compose.yml`.

## Run locally without Docker

Requires [uv](https://docs.astral.sh/uv/).
Without `DATABASE_URL` the app uses a local SQLite file `app.db`.

```bash
uv sync
uv run python -m app.seed
uv run uvicorn app.main:app --reload
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/auth/register` | Create a user (`email`, `password`) |
| POST | `/auth/login` | Get a bearer token |
| POST | `/auth/logout` | Invalidate the current token |
| GET | `/auth/me` | Current user |
| POST, GET | `/students` | Create, list students |
| GET, PATCH, DELETE | `/students/{id}` | Get, update, delete a student |
| POST, GET | `/subjects` | Create (unique name and grade), list subjects |
| GET, PATCH, DELETE | `/subjects/{id}` | Get, update, delete a subject |
| POST, GET | `/subjects/{id}/scores` | Add a score (`student_id`, `value` 0-100), list scores |
| DELETE | `/subjects/{id}/scores/{score_id}` | Delete a score |
| GET | `/subjects/{id}/stats` | Subject statistics, marks and pass rate |
| POST, GET | `/subjects/{id}/plans` | Generate a KSP (`topic`, `objectives`), list plans |
| DELETE | `/subjects/{id}/plans/{plan_id}` | Delete a plan |
| POST | `/stats` | Statistics for `{"values": [...]}` |

All endpoints except `/health`, `/stats`, `/auth/register` and `/auth/login` require `Authorization: Bearer <token>`.
Every teacher sees only their own students, subjects, scores and plans.

## Project structure

```
app/
  main.py          FastAPI app, routers, frontend mount
  db.py            SQLAlchemy engine and session (PostgreSQL or SQLite)
  security.py      password hashing, tokens, current user
  dependencies.py  shared dependencies: session, user, own subject or student
  seed.py          demo data
  models/          SQLAlchemy tables: User, Student, Subject, Score, LessonPlan
  schemas/         Pydantic request and response models
  repositories/    database queries
  services/        statistics logic and the AI (OpenRouter / mock) client
  routers/         HTTP endpoints
  static/          teacher CRM frontend (HTML, CSS, JavaScript)
tests/             unit tests for services, API tests
```

## Test and lint

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=app --cov-report=term-missing
```

Tests use an in-memory SQLite database by default.
Set `TEST_DATABASE_URL` to run them against PostgreSQL, as CI does.
The OpenRouter client is tested with a fake HTTP response, so tests never call the real API.

## CI/CD

The pipeline is defined in [.github/workflows/ci.yml](.github/workflows/ci.yml) and has four jobs, shown as separate blocks in GitHub Actions:

1. **Lint & format (Ruff)**: install locked dependencies with uv, `ruff check`, `ruff format --check`.
2. **Tests (pytest + PostgreSQL)**: run all tests against a PostgreSQL service, require at least 90 % coverage.
3. **Build Docker image**: build the image and save it as a workflow artifact.
4. **Publish to GHCR** (only on `main`): push the same image to GitHub Container Registry as `ghcr.io/nihsiok/asd-project:latest` and `:<commit SHA>`.

Jobs 1-3 run on every push and pull request (CI); job 4 is continuous delivery.

## Technology choices

- **Python** is the standard language for scientific computing and data processing.
- **FastAPI** gives request validation and OpenAPI docs with very little code.
- **PostgreSQL + SQLAlchemy** store the CRM data; SQLite is used for quick local runs and tests.
- **Plain HTML, CSS and JavaScript** for the frontend: no build step, served by FastAPI from the same Docker image.
- **OpenRouter** gives access to many LLMs through one OpenAI-compatible API; a mock keeps development and CI free and deterministic.
- **uv** manages Python, dependencies and a lock file, so local and CI environments match.
- **pytest** and **Ruff** are the most common testing and linting tools in the Python ecosystem.
- **GitHub Actions** is built into GitHub, so no external CI service is needed.

## License

[MIT](LICENSE)
