from fastapi import APIRouter, HTTPException, status

from app.dependencies import DbSession, OwnSubject
from app.models import LessonPlan
from app.repositories import plan as plan_repo
from app.schemas.plan import PlanCreate, PlanOut
from app.services import ai

router = APIRouter(prefix="/subjects/{subject_id}/plans", tags=["lesson plans"])


@router.post("", status_code=status.HTTP_201_CREATED)
def generate_plan(data: PlanCreate, subject: OwnSubject, db: DbSession) -> PlanOut:
    # ponytail: generation runs inside the request; move to a queue worker for real AI latency
    try:
        content, source = ai.generate_plan(
            subject.name, subject.grade, data.topic, data.objectives
        )
    except ai.AIServiceError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error)) from error
    plan = LessonPlan(
        subject_id=subject.id,
        topic=data.topic,
        objectives=data.objectives,
        content=content,
        source=source,
    )
    return plan_repo.create(db, plan)


@router.get("")
def list_plans(subject: OwnSubject, db: DbSession) -> list[PlanOut]:
    return plan_repo.list_for_subject(db, subject.id)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, subject: OwnSubject, db: DbSession) -> None:
    plan = plan_repo.get_for_subject(db, subject.id, plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plan not found")
    plan_repo.delete(db, plan)
