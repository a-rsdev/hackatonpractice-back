from contracts.responses.content import (
    QuestionResponse, ResourceResponse, RoadmapResponse, UnitDetailsResponse, UnitResponse,
)
from core.result import Result
from models.entities import Question, Unit
from repositories.content import ContentRepository


class ContentService:
    def __init__(self, content: ContentRepository):
        self.content = content

    def roadmaps(self) -> Result[list[RoadmapResponse]]:
        found = self.content.list_roadmaps()
        if not found.is_success:
            return Result(error=found.error)
        return Result.success([
            RoadmapResponse(id=roadmap.id, title=roadmap.title) for roadmap in found.value
        ])

    def units(self, roadmap_id: str) -> Result[list[UnitResponse]]:
        found = self.content.list_units(roadmap_id)
        if not found.is_success:
            return Result(error=found.error)
        if found.value is None:
            return Result.failure("roadmap_not_found", 404)
        return Result.success([self._unit_response(unit) for unit in found.value])

    def unit(self, unit_id: str) -> Result[UnitDetailsResponse]:
        found = self.content.get_unit(unit_id)
        if not found.is_success:
            return Result(error=found.error)
        if found.value is None:
            return Result.failure("unit_not_found", 404)
        resources = self.content.list_resources(unit_id)
        questions = self.content.list_questions(unit_id)
        if not resources.is_success:
            return Result(error=resources.error)
        if not questions.is_success:
            return Result(error=questions.error)
        unit = found.value
        return Result.success(UnitDetailsResponse(
            **self._unit_response(unit).model_dump(),
            resources=[ResourceResponse(id=item.id, url=item.url, title=item.title) for item in resources.value],
            test_available=bool(questions.value),
            questions=[self._question_response(item) for item in questions.value],
        ))

    @staticmethod
    def _unit_response(unit: Unit) -> UnitResponse:
        return UnitResponse(id=unit.id, roadmap_id=unit.roadmap_id, title=unit.title, order=unit.order)

    @staticmethod
    def _question_response(question: Question) -> QuestionResponse:
        return QuestionResponse(id=question.id, text=question.text, options=question.options)
