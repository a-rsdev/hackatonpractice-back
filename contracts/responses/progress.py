from pydantic import BaseModel


class TestResultResponse(BaseModel):
    passed: bool
    score: int
    topics_completed: int
