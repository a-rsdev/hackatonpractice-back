from typing import Annotated

from fastapi import APIRouter, Depends

from contracts.responses.matches import (
    AnswerAcceptedResponse, MatchmakingResponse, MatchResponse, MatchResultResponse,
)
from contracts.requests.matches import MatchAnswerSubmission
from core.result import Result
from dependencies import get_match_service
from handlers.dependencies import current_user_id, handles_result
from services.matches import MatchService


router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/find", response_model=MatchmakingResponse)
@handles_result
def find_match(
    service: Annotated[MatchService, Depends(get_match_service)],
    user_id: str = Depends(current_user_id),
) -> Result[MatchmakingResponse]:
    return service.find_match(user_id)


@router.get("/{match_id}", response_model=MatchResponse)
@handles_result
def get_match(
    match_id: str,
    service: Annotated[MatchService, Depends(get_match_service)],
    user_id: str = Depends(current_user_id),
) -> Result[MatchResponse]:
    return service.get_match(user_id, match_id)


@router.post("/{match_id}/answer", response_model=AnswerAcceptedResponse)
@handles_result
def answer(
    match_id: str,
    body: MatchAnswerSubmission,
    service: Annotated[MatchService, Depends(get_match_service)],
    user_id: str = Depends(current_user_id),
) -> Result[AnswerAcceptedResponse]:
    return service.submit_answer(user_id, match_id, body.question_id, body.selected_option_index)


@router.post("/{match_id}/finish", response_model=MatchResultResponse)
@handles_result
def finish(
    match_id: str,
    service: Annotated[MatchService, Depends(get_match_service)],
    user_id: str = Depends(current_user_id),
) -> Result[MatchResultResponse]:
    return service.finish_match(user_id, match_id)
