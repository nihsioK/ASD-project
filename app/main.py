from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401 - registers tables on Base.metadata
from app.db import Base, engine
from app.routers import auth, plans, scores, stats, students, subjects

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # ponytail: create_all instead of migrations, add Alembic when the schema starts changing
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="SciStats Teacher CRM", version="0.4.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(subjects.router)
app.include_router(scores.router)
app.include_router(plans.router)
app.include_router(stats.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Teacher CRM frontend; mounted last so API routes take priority
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
