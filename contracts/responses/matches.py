from typing import Literal

from pydantic import BaseModel

from contracts.responses.content import QuestionResponse


class WaitingMatchResponse(BaseModel):
    status: Literal["waiting"] = "waiting"


class MatchedResponse(BaseModel):
    status: Literal["matched"] = "matched"
    match_id: str


MatchmakingResponse = WaitingMatchResponse | MatchedResponse


class MatchResponse(BaseModel):
    id: str
    player1_id: str
    player2_id: str
    roadmap_id: str
    status: str
    questions: list[QuestionResponse]


class AnswerAcceptedResponse(BaseModel):
    status: Literal["accepted"] = "accepted"


class MatchResultResponse(BaseModel):
    player1_score: int
    player2_score: int
    player1_points_earned: int
    player2_points_earned: int
