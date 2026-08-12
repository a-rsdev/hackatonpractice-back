from datetime import datetime
import traceback

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from core.result import Result
from database import SessionFactory
from models.entities import PomodoroSession


class PomodoroRepository:
    def replace_running(self, user_id: str, duration_seconds: int,
                        started_at: datetime) -> Result[PomodoroSession]:
        with SessionFactory() as session:
            try:
                session.execute(
                    delete(PomodoroSession)
                    .where(PomodoroSession.user_id == user_id, PomodoroSession.status == "running")
                )
                current = PomodoroSession(
                    user_id=user_id, duration_seconds=duration_seconds,
                    started_at=started_at, status="running",
                )
                session.add(current)
                session.commit()
                session.refresh(current)
                return Result.success(current)
            except SQLAlchemyError:
                session.rollback()
                traceback.print_exc()
                return Result.failure("database_error", 500)

    def delete_running(self, user_id: str) -> Result[None]:
        with SessionFactory() as session:
            try:
                session.execute(
                    delete(PomodoroSession)
                    .where(PomodoroSession.user_id == user_id, PomodoroSession.status == "running")
                )
                session.commit()
                return Result.success(None)
            except SQLAlchemyError:
                session.rollback()
                traceback.print_exc()
                return Result.failure("database_error", 500)

    def current(self, user_id: str) -> Result[PomodoroSession | None]:
        with SessionFactory() as session:
            try:
                return Result.success(session.scalar(
                    select(PomodoroSession)
                    .where(PomodoroSession.user_id == user_id, PomodoroSession.status == "running")
                    .order_by(PomodoroSession.started_at.desc()).limit(1)
                ))
            except SQLAlchemyError:
                traceback.print_exc()
                return Result.failure("database_error", 500)

    def finish(self, session_id: str) -> Result[None]:
        with SessionFactory() as session:
            try:
                current = session.get(PomodoroSession, session_id)
                if current:
                    current.status = "finished"
                    session.commit()
                return Result.success(None)
            except SQLAlchemyError:
                session.rollback()
                traceback.print_exc()
                return Result.failure("database_error", 500)