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

    def find_match(self, user_id: str, roadmap_id: str) -> Result[MatchmakingResponse]:
        roadmap = self.matches.get_roadmap(roadmap_id)
        if not roadmap.is_success:
            return Result(error=roadmap.error)
        if roadmap.value is None:
            return Result.failure("roadmap_not_found", 404)

        own_progress = self.matches.completed_units_count_in_roadmap(user_id, roadmap_id)
        if not own_progress.is_success:
            return Result(error=own_progress.error)
        if own_progress.value < 5:
            return Result.failure("need_5_units_completed", 403)

        claimed = self.matches.claim_opponent_or_enqueue(user_id, roadmap_id)
        if not claimed.is_success:
            return Result(error=claimed.error)
        opponent = claimed.value
        if opponent is None:
            return Result.success(WaitingMatchResponse())

        my_completed = self.matches.completed_unit_ids_in_roadmap(user_id, roadmap_id)
        opp_completed = self.matches.completed_unit_ids_in_roadmap(opponent.id, roadmap_id)
        if not my_completed.is_success:
            return Result(error=my_completed.error)
        if not opp_completed.is_success:
            return Result(error=opp_completed.error)

        weaker_completed = (
            my_completed.value if len(my_completed.value) <= len(opp_completed.value) else opp_completed.value
        )

        units = self.matches.units_for_roadmap(roadmap_id)
        if not units.is_success:
            return Result(error=units.error)

        weaker_unit_ids = [unit.id for unit in units.value if unit.id in weaker_completed]
        if not weaker_unit_ids:
            weaker_unit_ids = [units.value[0].id]

        questions = self.matches.questions_for_units(weaker_unit_ids, limit=5)
        if not questions.is_success:
            return Result(error=questions.error)

        created = self.matches.create(
            opponent.id, user_id, roadmap_id, [question.id for question in questions.value],
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
            roadmap_id=match.roadmap_id, status=match.status,
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