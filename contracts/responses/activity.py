from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class StreakResponse(BaseModel):
    streak_count: int


class PomodoroStartedResponse(BaseModel):
    session_id: str
    started_at: datetime
    duration_seconds: int


class PomodoroStoppedResponse(BaseModel):
    status: Literal["stopped"] = "stopped"


class PomodoroStatusResponse(BaseModel):
    is_running: bool
