from datetime import datetime

from sqlalchemy import select, update
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
                    update(PomodoroSession)
                    .where(PomodoroSession.user_id == user_id, PomodoroSession.status == "running")
                    .values(status="cancelled")
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
                return Result.failure("database_error", 500)

    def stop_running(self, user_id: str) -> Result[None]:
        with SessionFactory() as session:
            try:
                session.execute(
                    update(PomodoroSession)
                    .where(PomodoroSession.user_id == user_id, PomodoroSession.status == "running")
                    .values(status="cancelled")
                )
                session.commit()
                return Result.success(None)
            except SQLAlchemyError:
                session.rollback()
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
                return Result.failure("database_error", 500)

    def finish(self, session_id: str) -> Result[PomodoroSession | None]:
        with SessionFactory() as session:
            try:
                current = session.get(PomodoroSession, session_id)
                if current:
                    current.status = "finished"
                    session.commit()
                    session.refresh(current)
                return Result.success(current)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)
