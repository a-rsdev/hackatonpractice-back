from typing import Annotated

from fastapi import APIRouter, Depends

from contracts.responses.content import RoadmapResponse, UnitDetailsResponse, UnitResponse
from core.result import Result
from dependencies import get_content_service
from handlers.dependencies import current_user_id, handles_result
from services.content import ContentService


router = APIRouter(tags=["learning"])


@router.get("/roadmaps", response_model=list[RoadmapResponse])
@handles_result
def roadmaps(
    service: Annotated[ContentService, Depends(get_content_service)],
    _: str = Depends(current_user_id),
) -> Result[list[RoadmapResponse]]:
    return service.roadmaps()


@router.get("/roadmaps/{roadmap_id}/units", response_model=list[UnitResponse])
@handles_result
def units(
    roadmap_id: str,
    service: Annotated[ContentService, Depends(get_content_service)],
    _: str = Depends(current_user_id),
) -> Result[list[UnitResponse]]:
    return service.units(roadmap_id)


@router.get("/units/{unit_id}", response_model=UnitDetailsResponse)
@handles_result
def unit(
    unit_id: str,
    service: Annotated[ContentService, Depends(get_content_service)],
    _: str = Depends(current_user_id),
) -> Result[UnitDetailsResponse]:
    return service.unit(unit_id)
