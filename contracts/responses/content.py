from pydantic import BaseModel


class RoadmapResponse(BaseModel):
    id: str
    title: str


class UnitResponse(BaseModel):
    id: str
    roadmap_id: str
    title: str
    order: int
    locked: bool = False
    completed: bool = False


class ResourceResponse(BaseModel):
    id: str
    url: str
    title: str


class QuestionResponse(BaseModel):
    id: str
    text: str
    options: list[str]


class UnitDetailsResponse(UnitResponse):
    resources: list[ResourceResponse]
    test_available: bool
    questions: list[QuestionResponse]
