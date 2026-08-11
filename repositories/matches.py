from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.result import Result
from database import SessionFactory
from models.entities import Match, MatchAnswer, Question, Unit, User, UserUnitProgress, WaitingPlayer


class MatchRepository:
    def claim_opponent_or_enqueue(self, user_id: str) -> Result[User | None]:
        with SessionFactory() as session:
            try:
                opponent_id = session.scalar(
                    select(WaitingPlayer.user_id)
                    .join(User, User.id == WaitingPlayer.user_id)
                    .where(WaitingPlayer.user_id != user_id, User.topics_completed >= 5)
                    .order_by(WaitingPlayer.joined_at).limit(1)
                )
                if opponent_id is None:
                    waiting = session.get(WaitingPlayer, user_id)
                    if waiting:
                        waiting.joined_at = datetime.now(timezone.utc)
                    else:
                        session.add(WaitingPlayer(user_id=user_id))
                    session.commit()
                    return Result.success(None)
                opponent = session.get(User, opponent_id)
                session.execute(delete(WaitingPlayer).where(WaitingPlayer.user_id.in_([user_id, opponent_id])))
                session.commit()
                return Result.success(opponent)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)

    def list_units(self) -> Result[list[Unit]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(select(Unit).order_by(Unit.order))))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def list_completed_progress(self, user_id: str) -> Result[list[UserUnitProgress]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(UserUnitProgress).where(
                        UserUnitProgress.user_id == user_id,
                        UserUnitProgress.completed.is_(True),
                    )
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def questions_for_unit(self, unit_id: str) -> Result[list[Question]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(Question).where(Question.unit_id == unit_id).order_by(Question.id).limit(5)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def create(self, player1_id: str, player2_id: str, unit_id: str,
               question_ids: list[str]) -> Result[Match]:
        with SessionFactory() as session:
            try:
                match = Match(
                    player1_id=player1_id, player2_id=player2_id,
                    unit_id=unit_id, question_ids=question_ids, status="active",
                )
                session.add(match)
                session.commit()
                session.refresh(match)
                return Result.success(match)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)

    def get(self, match_id: str) -> Result[Match | None]:
        with SessionFactory() as session:
            try:
                return Result.success(session.get(Match, match_id))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def questions_by_ids(self, question_ids: list[str]) -> Result[list[Question]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(Question).where(Question.id.in_(question_ids)).order_by(Question.id)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def question(self, question_id: str) -> Result[Question | None]:
        with SessionFactory() as session:
            try:
                return Result.success(session.get(Question, question_id))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def add_answer(self, match_id: str, user_id: str, question_id: str,
                   selected: int, is_correct: bool) -> Result[MatchAnswer]:
        with SessionFactory() as session:
            try:
                answer = MatchAnswer(
                    match_id=match_id, user_id=user_id, question_id=question_id,
                    selected_option_index=selected, is_correct=is_correct,
                )
                session.add(answer)
                session.commit()
                session.refresh(answer)
                return Result.success(answer)
            except IntegrityError:
                session.rollback()
                return Result.failure("question_already_answered", 409)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)

    def list_answers(self, match_id: str) -> Result[list[MatchAnswer]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(MatchAnswer).where(MatchAnswer.match_id == match_id)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def finish_and_award(self, match_id: str, score1: int, score2: int,
                         points1: int, points2: int) -> Result[Match]:
        with SessionFactory() as session:
            try:
                match = session.get(Match, match_id)
                if match.status != "finished":
                    player1 = session.get(User, match.player1_id)
                    player2 = session.get(User, match.player2_id)
                    player1.knowledge_points += points1
                    player2.knowledge_points += points2
                    match.status = "finished"
                    match.finished_at = datetime.now(timezone.utc)
                    match.player1_score = score1
                    match.player2_score = score2
                    match.player1_points_earned = points1
                    match.player2_points_earned = points2
                    session.commit()
                    session.refresh(match)
                return Result.success(match)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)
