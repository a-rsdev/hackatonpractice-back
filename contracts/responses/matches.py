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
    your_selected_index: int
    your_correct: bool
    opponent_selected_index: int
    opponent_correct: bool


class EligibleRoadmapResponse(BaseModel):
    id: str
    title: str
    completed_units: int
    eligible: bool
    points: int


class MatchResponse(BaseModel):
    id: str
    opponent_id: str
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
    your_score: int
    opponent_score: int
    you_won: bool
    is_draw: bool
    your_base_points: int
    your_streak_multiplier: float
    your_win_multiplier: float
    your_points_earned: int
    your_roadmap_points_total: int
    opponent_base_points: int
    opponent_streak_multiplier: float
    opponent_win_multiplier: float
    opponent_points_earned: int