from pydantic import BaseModel, Field


class TestAnswer(BaseModel):
    question_id: str
    selected_option_index: int = Field(ge=0)


class TestSubmission(BaseModel):
    answers: list[TestAnswer]
