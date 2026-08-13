from config import PASSING_SCORE
from contracts.requests.progress import TestAnswer
from contracts.responses.progress import TestResultResponse
from core.result import Result
from repositories.progress import ProgressRepository
from repositories.users import UserRepository


class ProgressService:
    def __init__(self, progress: ProgressRepository, users: UserRepository):
        self.progress = progress
        self.users = users

    def submit_test(self, user_id: str, unit_id: str, answers: list[TestAnswer]) -> Result[TestResultResponse]:
        fetched = self.progress.get_questions(unit_id)
        if not fetched.is_success:
            return Result(error=fetched.error)
        questions = fetched.value
        if not questions:
            return Result.failure("unit_or_test_not_found", 404)
        answer_map = {answer.question_id: answer.selected_option_index for answer in answers}
        if len(answer_map) != len(answers) or set(answer_map) != {question.id for question in questions}:
            return Result.failure("all_questions_must_be_answered_once", 400)
        incorrect_question_numbers = [
            question_number
            for question_number, question in enumerate(questions, start=1)
            if answer_map[question.id] != question.correct_option_index
        ]
        correct = len(questions) - len(incorrect_question_numbers)
        score = round(correct * 100 / len(questions))
        passed = score >= PASSING_SCORE
        user = self.progress.complete_unit(user_id, unit_id) if passed else self.users.get_by_id(user_id)
        if not user.is_success:
            return Result(error=user.error)
        return Result.success(TestResultResponse(
            passed=passed,
            score=score,
            topics_completed=user.value.topics_completed,
            incorrect_question_numbers=incorrect_question_numbers,
        ))
