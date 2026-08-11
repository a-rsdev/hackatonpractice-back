from typing import Annotated

from fastapi import APIRouter, Depends

from contracts.requests.progress import TestSubmission
from contracts.responses.progress import TestResultResponse
from core.result import Result
from dependencies import get_progress_service
from handlers.dependencies import current_user_id, handles_result
from services.progress import ProgressService


router = APIRouter(tags=["progress"])


@router.post("/units/{unit_id}/test/submit", response_model=TestResultResponse)
@handles_result
def submit_test(
    unit_id: str,
    body: TestSubmission,
    service: Annotated[ProgressService, Depends(get_progress_service)],
    user_id: str = Depends(current_user_id),
) -> Result[TestResultResponse]:
    return service.submit_test(user_id, unit_id, body.answers)
