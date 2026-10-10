from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401 - registers tables on Base.metadata
from app.db import Base, engine
from app.routers import auth, stats, subjects


@asynccontextmanager
async def lifespan(_: FastAPI):
    # ponytail: create_all instead of migrations, add Alembic when the schema starts changing
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="SciStats API", version="0.2.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(stats.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
