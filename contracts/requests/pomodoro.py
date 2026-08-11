from pydantic import BaseModel, Field


class PomodoroStart(BaseModel):
    duration_seconds: int = Field(ge=1, le=86400)
