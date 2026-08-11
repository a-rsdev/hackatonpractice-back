from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.result import Result
from database import SessionFactory
from models.entities import Question, User, UserUnitProgress


class ProgressRepository:
    def get_questions(self, unit_id: str) -> Result[list[Question]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(Question).where(Question.unit_id == unit_id).order_by(Question.id)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def complete_unit(self, user_id: str, unit_id: str) -> Result[User]:
        with SessionFactory() as session:
            try:
                progress = session.get(UserUnitProgress, (user_id, unit_id))
                user = session.get(User, user_id)
                if progress is None:
                    progress = UserUnitProgress(user_id=user_id, unit_id=unit_id)
                    session.add(progress)
                if not progress.completed:
                    progress.completed = True
                    progress.completed_at = datetime.now(timezone.utc)
                    user.topics_completed += 1
                session.commit()
                session.refresh(user)
                return Result.success(user)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)
