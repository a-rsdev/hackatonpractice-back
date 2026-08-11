from typing import Annotated

from fastapi import APIRouter, Depends

from contracts.responses.activity import StreakResponse
from core.result import Result
from dependencies import get_streak_service
from handlers.dependencies import current_user_id, handles_result
from services.streak import StreakService


router = APIRouter(prefix="/streak", tags=["streak"])


@router.post("/ping", response_model=StreakResponse)
@handles_result
def ping(
    service: Annotated[StreakService, Depends(get_streak_service)],
    user_id: str = Depends(current_user_id),
) -> Result[StreakResponse]:
    return service.ping(user_id)
