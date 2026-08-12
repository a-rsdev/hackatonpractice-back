from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.result import Result
from database import SessionFactory
from models.entities import Question, Resource, Roadmap, Unit, UserUnitProgress


class ContentRepository:
    def list_roadmaps(self) -> Result[list[Roadmap]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(select(Roadmap).order_by(Roadmap.title))))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def list_units(self, roadmap_id: str) -> Result[list[Unit] | None]:
        with SessionFactory() as session:
            try:
                if session.get(Roadmap, roadmap_id) is None:
                    return Result.success(None)
                units = session.scalars(
                    select(Unit).where(Unit.roadmap_id == roadmap_id).order_by(Unit.order)
                ).all()
                return Result.success(list(units))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def get_unit(self, unit_id: str) -> Result[Unit | None]:
        with SessionFactory() as session:
            try:
                return Result.success(session.get(Unit, unit_id))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def list_resources(self, unit_id: str) -> Result[list[Resource]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(Resource).where(Resource.unit_id == unit_id).order_by(Resource.id)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def list_questions(self, unit_id: str) -> Result[list[Question]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(Question).where(Question.unit_id == unit_id).order_by(Question.id)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def completed_unit_ids(self, user_id: str, roadmap_id: str) -> Result[set[str]]:
        with SessionFactory() as session:
            try:
                rows = session.scalars(
                    select(UserUnitProgress.unit_id)
                    .join(Unit, Unit.id == UserUnitProgress.unit_id)
                    .where(
                        UserUnitProgress.user_id == user_id,
                        UserUnitProgress.completed == True,  # noqa: E712
                        Unit.roadmap_id == roadmap_id,
                    )
                )
                return Result.success(set(rows))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)