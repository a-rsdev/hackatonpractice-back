from pydantic import BaseModel, Field


class MatchAnswerSubmission(BaseModel):
    question_id: str
    selected_option_index: int = Field(ge=0)
