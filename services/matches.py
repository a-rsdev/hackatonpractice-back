from datetime import datetime, timedelta, timezone

from config import (
    ANSWER_TIME_SECONDS, MAX_STREAK_MULTIPLIER, POINTS_PER_CORRECT, ROUNDS_PER_MATCH,
    STREAK_MULTIPLIER_STEP, WIN_MULTIPLIER, REVEAL_DURATION_SECONDS,
)
from contracts.responses.content import QuestionResponse
from contracts.responses.matches import (
    AnswerAcceptedResponse, EligibleRoadmapResponse, MatchedResponse, MatchmakingResponse,
    MatchResponse, MatchResultResponse, RoundResultResponse, WaitingMatchResponse,
)
from core.result import Result
from models.entities import Match, MatchAnswer
from repositories.matches import MatchRepository
from repositories.users import UserRepository


def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


class MatchService:
    def __init__(self, matches: MatchRepository, users: UserRepository):
        self.matches = matches
        self.users = users

    def eligible_roadmaps(self, user_id: str) -> Result[list[EligibleRoadmapResponse]]:
        found = self.matches.roadmaps_with_progress(user_id)
        if not found.is_success:
            return Result(error=found.error)
        return Result.success([
            EligibleRoadmapResponse(
                id=roadmap.id, title=roadmap.title,
                completed_units=count, eligible=count >= 5,
            )
            for roadmap, count in found.value
        ])

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

        questions = self.matches.questions_for_units(weaker_unit_ids, limit=ROUNDS_PER_MATCH)
        if not questions.is_success:
            return Result(error=questions.error)
        if len(questions.value) < ROUNDS_PER_MATCH:
            return Result.failure("not_enough_questions_for_match", 409)

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

        loaded = self._load_state(match)
        if not loaded.is_success:
            return Result(error=loaded.error)
        answers, questions_by_id = loaded.value

        revealed_rounds, current_round = self._round_state(match, answers, questions_by_id)
        total_rounds = len(match.question_ids)

        if match.status == "active" and current_round < total_rounds:
            forfeited = self._expire_current_round_if_needed(match, answers, current_round)
            if not forfeited.is_success:
                return Result(error=forfeited.error)
            if forfeited.value:
                loaded = self._load_state(match)
                if not loaded.is_success:
                    return Result(error=loaded.error)
                answers, questions_by_id = loaded.value
                revealed_rounds, current_round = self._round_state(match, answers, questions_by_id)

        current_question = None
        answer_deadline = None
        you_answered = False
        opponent_answered = False
        opponent_id = match.player2_id if user_id == match.player1_id else match.player1_id

        if current_round < total_rounds:
            current_question_id = match.question_ids[current_round]
            question = questions_by_id.get(current_question_id)
            if question is not None:
                current_question = QuestionResponse(id=question.id, text=question.text, options=question.options)
            you_answered = any(a.question_id == current_question_id and a.user_id == user_id for a in answers)
            opponent_answered = any(
                a.question_id == current_question_id and a.user_id == opponent_id for a in answers
            )
            answer_deadline = self._round_deadline(match, answers, current_round)

        return Result.success(MatchResponse(
            id=match.id, player1_id=match.player1_id, player2_id=match.player2_id,
            roadmap_id=match.roadmap_id, status=match.status,
            total_rounds=total_rounds, current_round=current_round,
            current_question=current_question, answer_deadline=answer_deadline,
            you_answered_current=you_answered, opponent_answered_current=opponent_answered,
            rounds=revealed_rounds,
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

        found_answers = self.matches.list_answers(match.id)
        if not found_answers.is_success:
            return Result(error=found_answers.error)
        _, current_round = self._round_state(match, found_answers.value, {})
        total_rounds = len(match.question_ids)
        if current_round >= total_rounds:
            return Result.failure("all_rounds_completed", 409)
        if match.question_ids[current_round] != question_id:
            return Result.failure("not_current_round", 409)

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

        loaded = self._load_state(match)
        if not loaded.is_success:
            return Result(error=loaded.error)
        answers, questions_by_id = loaded.value

        revealed_rounds, current_round = self._round_state(match, answers, questions_by_id)
        total_rounds = len(match.question_ids)

        if current_round < total_rounds:
            forfeited = self._expire_current_round_if_needed(match, answers, current_round)
            if not forfeited.is_success:
                return Result(error=forfeited.error)
            if forfeited.value:
                loaded = self._load_state(match)
                if not loaded.is_success:
                    return Result(error=loaded.error)
                answers, questions_by_id = loaded.value
                revealed_rounds, current_round = self._round_state(match, answers, questions_by_id)

        if current_round < total_rounds:
            return Result.failure("not_all_rounds_completed", 409)

        score1 = sum(round_.player1_correct for round_ in revealed_rounds)
        score2 = sum(round_.player2_correct for round_ in revealed_rounds)

        found_p1 = self.users.get_by_id(match.player1_id)
        found_p2 = self.users.get_by_id(match.player2_id)
        if not found_p1.is_success:
            return Result(error=found_p1.error)
        if not found_p2.is_success:
            return Result(error=found_p2.error)
        player1, player2 = found_p1.value, found_p2.value

        base1, base2 = score1 * POINTS_PER_CORRECT, score2 * POINTS_PER_CORRECT
        streak_mult1 = min(1 + player1.streak_count * STREAK_MULTIPLIER_STEP, MAX_STREAK_MULTIPLIER)
        streak_mult2 = min(1 + player2.streak_count * STREAK_MULTIPLIER_STEP, MAX_STREAK_MULTIPLIER)
        win_mult1 = WIN_MULTIPLIER if score1 > score2 else 1.0
        win_mult2 = WIN_MULTIPLIER if score2 > score1 else 1.0

        points1 = round(base1 * streak_mult1 * win_mult1)
        points2 = round(base2 * streak_mult2 * win_mult2)

        breakdown = {
            "player1_base_points": base1, "player2_base_points": base2,
            "player1_streak_multiplier": streak_mult1, "player2_streak_multiplier": streak_mult2,
            "player1_win_multiplier": win_mult1, "player2_win_multiplier": win_mult2,
        }

        finished = self.matches.finish_and_award(match.id, score1, score2, points1, points2, breakdown)
        if not finished.is_success:
            return Result(error=finished.error)
        return Result.success(self._result_response(finished.value))

    def _load_state(self, match: Match) -> Result[tuple[list[MatchAnswer], dict]]:
        found_answers = self.matches.list_answers(match.id)
        if not found_answers.is_success:
            return Result(error=found_answers.error)
        found_questions = self.matches.questions_by_ids(match.question_ids)
        if not found_questions.is_success:
            return Result(error=found_questions.error)
        questions_by_id = {q.id: q for q in found_questions.value}
        return Result.success((found_answers.value, questions_by_id))

    def _expire_current_round_if_needed(self, match: Match, answers: list[MatchAnswer],
                                        current_round: int) -> Result[bool]:
        deadline = self._round_deadline(match, answers, current_round)
        if datetime.now(timezone.utc) < deadline:
            return Result.success(False)

        question_id = match.question_ids[current_round]
        answered_users = {a.user_id for a in answers if a.question_id == question_id}
        forfeited = False
        for player_id in (match.player1_id, match.player2_id):
            if player_id not in answered_users:
                result = self.matches.force_miss_answer(match.id, player_id, question_id)
                if not result.is_success:
                    return Result(error=result.error)
                forfeited = True
        return Result.success(forfeited)

    @staticmethod
    def _round_deadline(match: Match, answers: list[MatchAnswer], current_round: int) -> datetime:
        if current_round == 0:
            start = _as_utc(match.created_at)
        else:
            prev_question_id = match.question_ids[current_round - 1]
            prev_times = [_as_utc(a.answered_at) for a in answers if a.question_id == prev_question_id]
            reveal_time = max(prev_times) if prev_times else _as_utc(match.created_at)
            start = reveal_time + timedelta(seconds=REVEAL_DURATION_SECONDS)
        return start + timedelta(seconds=ANSWER_TIME_SECONDS)

    @staticmethod
    def _round_state(match: Match, answers: list[MatchAnswer],
                     questions_by_id: dict) -> tuple[list[RoundResultResponse], int]:
        by_question: dict[str, dict[str, MatchAnswer]] = {}
        for answer in answers:
            by_question.setdefault(answer.question_id, {})[answer.user_id] = answer

        revealed_rounds: list[RoundResultResponse] = []
        current_round = len(match.question_ids)
        for index, question_id in enumerate(match.question_ids):
            pair = by_question.get(question_id, {})
            p1_answer = pair.get(match.player1_id)
            p2_answer = pair.get(match.player2_id)
            if p1_answer is not None and p2_answer is not None:
                question = questions_by_id.get(question_id)
                revealed_rounds.append(RoundResultResponse(
                    question_id=question_id,
                    correct_option_index=question.correct_option_index if question else -1,
                    player1_selected_index=p1_answer.selected_option_index,
                    player1_correct=p1_answer.is_correct,
                    player2_selected_index=p2_answer.selected_option_index,
                    player2_correct=p2_answer.is_correct,
                ))
            else:
                current_round = index
                break
        return revealed_rounds, current_round

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
        breakdown = match.score_breakdown or {}
        return MatchResultResponse(
            player1_score=match.player1_score or 0,
            player2_score=match.player2_score or 0,
            player1_base_points=breakdown.get("player1_base_points", 0),
            player2_base_points=breakdown.get("player2_base_points", 0),
            player1_streak_multiplier=breakdown.get("player1_streak_multiplier", 1.0),
            player2_streak_multiplier=breakdown.get("player2_streak_multiplier", 1.0),
            player1_win_multiplier=breakdown.get("player1_win_multiplier", 1.0),
            player2_win_multiplier=breakdown.get("player2_win_multiplier", 1.0),
            player1_points_earned=match.player1_points_earned or 0,
            player2_points_earned=match.player2_points_earned or 0,
        )