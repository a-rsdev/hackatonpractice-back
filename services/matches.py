from config import MATCH_BONUS, POINTS_PER_CORRECT
from contracts.responses.content import QuestionResponse
from contracts.responses.matches import (
    AnswerAcceptedResponse, MatchedResponse, MatchmakingResponse,
    MatchResponse, MatchResultResponse, WaitingMatchResponse,
)
from core.result import Result
from models.entities import Match
from repositories.matches import MatchRepository
from repositories.users import UserRepository


class MatchService:
    def __init__(self, matches: MatchRepository, users: UserRepository):
        self.matches = matches
        self.users = users

    def find_match(self, user_id: str) -> Result[MatchmakingResponse]:
        found = self.users.get_by_id(user_id)
        if not found.is_success:
            return Result(error=found.error)
        user = found.value
        if user is None or user.topics_completed < 5:
            return Result.failure("need_5_units_completed", 403)
        claimed = self.matches.claim_opponent_or_enqueue(user_id)
        if not claimed.is_success:
            return Result(error=claimed.error)
        opponent = claimed.value
        if opponent is None:
            return Result.success(WaitingMatchResponse())

        less_advanced_id = user_id if user.topics_completed <= opponent.topics_completed else opponent.id
        units = self.matches.list_units()
        completed = self.matches.list_completed_progress(less_advanced_id)
        if not units.is_success:
            return Result(error=units.error)
        if not completed.is_success:
            return Result(error=completed.error)
        completed_ids = {progress.unit_id for progress in completed.value}
        candidates = [unit for unit in units.value if unit.id not in completed_ids]
        selected_unit = (candidates or units.value)[-1]
        questions = self.matches.questions_for_unit(selected_unit.id)
        if not questions.is_success:
            return Result(error=questions.error)
        created = self.matches.create(
            opponent.id, user_id, selected_unit.id, [question.id for question in questions.value],
        )
        if not created.is_success:
            return Result(error=created.error)
        return Result.success(MatchedResponse(match_id=created.value.id))

    def get_match(self, user_id: str, match_id: str) -> Result[MatchResponse]:
        checked = self._participant(user_id, match_id)
        if not checked.is_success:
            return Result(error=checked.error)
        match = checked.value
        questions = self.matches.questions_by_ids(match.question_ids)
        if not questions.is_success:
            return Result(error=questions.error)
        return Result.success(MatchResponse(
            id=match.id, player1_id=match.player1_id, player2_id=match.player2_id,
            unit_id=match.unit_id, status=match.status,
            questions=[QuestionResponse(id=q.id, text=q.text, options=q.options) for q in questions.value],
        ))

    def submit_answer(self, user_id: str, match_id: str, question_id: str,
                      selected: int) -> Result[AnswerAcceptedResponse]:
        checked = self._participant(user_id, match_id)
        if not checked.is_success:
            return Result(error=checked.error)
        match = checked.value
        if match.status != "active":
            return Result.failure("match_not_active", 409)
        if question_id not in match.question_ids:
            return Result.failure("question_not_in_match", 400)
        found = self.matches.question(question_id)
        if not found.is_success:
            return Result(error=found.error)
        question = found.value
        if question is None or selected >= len(question.options):
            return Result.failure("selected_option_index_out_of_range", 422)
        saved = self.matches.add_answer(
            match_id, user_id, question_id, selected, selected == question.correct_option_index,
        )
        if not saved.is_success:
            return Result(error=saved.error)
        return Result.success(AnswerAcceptedResponse())

    def finish_match(self, user_id: str, match_id: str) -> Result[MatchResultResponse]:
        checked = self._participant(user_id, match_id)
        if not checked.is_success:
            return Result(error=checked.error)
        match = checked.value
        if match.status == "finished":
            return Result.success(self._result_response(match))
        found = self.matches.list_answers(match.id)
        if not found.is_success:
            return Result(error=found.error)
        answers = found.value
        required = len(match.question_ids)
        player1_answers = [answer for answer in answers if answer.user_id == match.player1_id]
        player2_answers = [answer for answer in answers if answer.user_id == match.player2_id]
        if len(player1_answers) < required or len(player2_answers) < required:
            return Result.failure("both_players_must_answer_all_questions", 409)
        score1 = sum(answer.is_correct for answer in player1_answers)
        score2 = sum(answer.is_correct for answer in player2_answers)
        points1, points2 = score1 * POINTS_PER_CORRECT, score2 * POINTS_PER_CORRECT
        if score1 > score2:
            points1 += MATCH_BONUS
        elif score2 > score1:
            points2 += MATCH_BONUS
        finished = self.matches.finish_and_award(match.id, score1, score2, points1, points2)
        if not finished.is_success:
            return Result(error=finished.error)
        return Result.success(self._result_response(finished.value))

    def _participant(self, user_id: str, match_id: str) -> Result[Match]:
        found = self.matches.get(match_id)
        if not found.is_success:
            return Result(error=found.error)
        match = found.value
        if match is None:
            return Result.failure("match_not_found", 404)
        if user_id not in (match.player1_id, match.player2_id):
            return Result.failure("not_a_match_participant", 403)
        return Result.success(match)

    @staticmethod
    def _result_response(match: Match) -> MatchResultResponse:
        return MatchResultResponse(
            player1_score=match.player1_score or 0,
            player2_score=match.player2_score or 0,
            player1_points_earned=match.player1_points_earned or 0,
            player2_points_earned=match.player2_points_earned or 0,
        )
