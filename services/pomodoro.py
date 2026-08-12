from datetime import datetime, timedelta, timezone

from contracts.responses.activity import (
    PomodoroStartedResponse, PomodoroStatusResponse, PomodoroStoppedResponse,
)
from core.result import Result
from repositories.pomodoro import PomodoroRepository


class PomodoroService:
    def __init__(self, sessions: PomodoroRepository):
        self.sessions = sessions

    def start(self, user_id: str, duration_seconds: int) -> Result[PomodoroStartedResponse]:
        now = datetime.now(timezone.utc)
        created = self.sessions.replace_running(user_id, duration_seconds, now)
        if not created.is_success:
            return Result(error=created.error)
        session = created.value
        return Result.success(PomodoroStartedResponse(
            session_id=session.id, started_at=session.started_at,
            duration_seconds=session.duration_seconds,
        ))

    def stop(self, user_id: str) -> Result[PomodoroStoppedResponse]:
        stopped = self.sessions.delete_running(user_id)
        if not stopped.is_success:
            return Result(error=stopped.error)
        return Result.success(PomodoroStoppedResponse())

    def status(self, user_id: str) -> Result[PomodoroStatusResponse]:
        found = self.sessions.current(user_id)
        if not found.is_success:
            return Result(error=found.error)
        session = found.value
        if session is None:
            return Result.success(PomodoroStatusResponse(is_running=False))
        started_at = session.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        if started_at + timedelta(seconds=session.duration_seconds) <= datetime.now(timezone.utc):
            finished = self.sessions.finish(session.id)
            if not finished.is_success:
                return Result(error=finished.error)
            return Result.success(PomodoroStatusResponse(is_running=False))
        return Result.success(PomodoroStatusResponse(is_running=True))
