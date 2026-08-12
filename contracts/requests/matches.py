from pydantic import BaseModel, Field


class MatchFindRequest(BaseModel):
    roadmap_id: str


class MatchAnswerSubmission(BaseModel):
    question_id: str
    selected_option_index: int = Field(ge=0)