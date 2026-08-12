# services/content.py
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

    def units(self, roadmap_id: str, user_id: str) -> Result[list[UnitResponse]]:
        found = self.content.list_units(roadmap_id)
        if not found.is_success:
            return Result(error=found.error)
        if found.value is None:
            return Result.failure("roadmap_not_found", 404)

        completed = self.content.completed_unit_ids(user_id, roadmap_id)
        if not completed.is_success:
            return Result(error=completed.error)

        units = found.value
        result = []
        unlocked_so_far = True
        for unit in sorted(units, key=lambda u: u.order):
            is_completed = unit.id in completed.value
            locked = not unlocked_so_far
            result.append(self._unit_response(unit, locked=locked, completed=is_completed))
            if not is_completed:
                unlocked_so_far = False
        return Result.success(result)

    def unit(self, unit_id: str, user_id: str) -> Result[UnitDetailsResponse]:
        found = self.content.get_unit(unit_id)
        if not found.is_success:
            return Result(error=found.error)
        if found.value is None:
            return Result.failure("unit_not_found", 404)
        unit = found.value

        completed = self.content.completed_unit_ids(user_id, unit.roadmap_id)
        if not completed.is_success:
            return Result(error=completed.error)

        prior_units = self.content.list_units(unit.roadmap_id)
        if not prior_units.is_success:
            return Result(error=prior_units.error)

        for other in prior_units.value:
            if other.order < unit.order and other.id not in completed.value:
                return Result.failure("unit_locked", 403)

        resources = self.content.list_resources(unit_id)
        questions = self.content.list_questions(unit_id)
        if not resources.is_success:
            return Result(error=resources.error)
        if not questions.is_success:
            return Result(error=questions.error)

        return Result.success(UnitDetailsResponse(
            **self._unit_response(unit, locked=False, completed=unit.id in completed.value).model_dump(),
            resources=[ResourceResponse(id=item.id, url=item.url, title=item.title) for item in resources.value],
            test_available=bool(questions.value),
            questions=[self._question_response(item) for item in questions.value],
        ))

    @staticmethod
    def _unit_response(unit: Unit, locked: bool = False, completed: bool = False) -> UnitResponse:
        return UnitResponse(
            id=unit.id, roadmap_id=unit.roadmap_id, title=unit.title,
            order=unit.order, locked=locked, completed=completed,
        )

    @staticmethod
    def _question_response(question: Question) -> QuestionResponse:
        return QuestionResponse(id=question.id, text=question.text, options=question.options)