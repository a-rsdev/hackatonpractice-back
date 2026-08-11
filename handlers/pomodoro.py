from typing import Annotated

from fastapi import APIRouter, Depends

from contracts.responses.activity import (
    PomodoroStartedResponse, PomodoroStatusResponse, PomodoroStoppedResponse,
)
from contracts.requests.pomodoro import PomodoroStart
from core.result import Result
from dependencies import get_pomodoro_service
from handlers.dependencies import current_user_id, handles_result
from services.pomodoro import PomodoroService


router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


@router.post("/start", response_model=PomodoroStartedResponse)
@handles_result
def start(
    body: PomodoroStart,
    service: Annotated[PomodoroService, Depends(get_pomodoro_service)],
    user_id: str = Depends(current_user_id),
) -> Result[PomodoroStartedResponse]:
    return service.start(user_id, body.duration_seconds)


@router.post("/stop", response_model=PomodoroStoppedResponse)
@handles_result
def stop(
    service: Annotated[PomodoroService, Depends(get_pomodoro_service)],
    user_id: str = Depends(current_user_id),
) -> Result[PomodoroStoppedResponse]:
    return service.stop(user_id)


@router.get("/status/{requested_user_id}", response_model=PomodoroStatusResponse)
@handles_result
def status(
    requested_user_id: str,
    service: Annotated[PomodoroService, Depends(get_pomodoro_service)],
    user_id: str = Depends(current_user_id),
) -> Result[PomodoroStatusResponse]:
    if requested_user_id != user_id:
        return Result.failure("cannot_view_another_users_session", 403)
    return service.status(user_id)
