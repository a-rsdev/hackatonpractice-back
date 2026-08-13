from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from contracts.responses.content import QuestionResponse


class WaitingMatchResponse(BaseModel):
    status: Literal["waiting"] = "waiting"


class MatchedResponse(BaseModel):
    status: Literal["matched"] = "matched"
    match_id: str


MatchmakingResponse = WaitingMatchResponse | MatchedResponse


class RoundResultResponse(BaseModel):
    question_id: str
    correct_option_index: int
    player1_selected_index: int
    player1_correct: bool
    player2_selected_index: int
    player2_correct: bool


class EligibleRoadmapResponse(BaseModel):
    id: str
    title: str
    completed_units: int
    eligible: bool


class MatchResponse(BaseModel):
    id: str
    player1_id: str
    player2_id: str
    roadmap_id: str
    status: str
    total_rounds: int
    current_round: int
    current_question: Optional[QuestionResponse] = None
    answer_deadline: Optional[datetime] = None
    you_answered_current: bool
    opponent_answered_current: bool
    rounds: list[RoundResultResponse]


class AnswerAcceptedResponse(BaseModel):
    status: Literal["accepted"] = "accepted"


class MatchResultResponse(BaseModel):
    player1_score: int
    player2_score: int
    player1_base_points: int
    player2_base_points: int
    player1_streak_multiplier: float
    player2_streak_multiplier: float
    player1_win_multiplier: float
    player2_win_multiplier: float
    player1_points_earned: int
    player2_points_earned: int