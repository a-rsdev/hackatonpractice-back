from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.result import Result
from database import SessionFactory
from models.entities import (
    Match, MatchAnswer, Question, Roadmap, Unit, User, UserRoadmapPoints, UserUnitProgress, WaitingPlayer,
)


class MatchRepository:
    def get_roadmap(self, roadmap_id: str) -> Result[Roadmap | None]:
        with SessionFactory() as session:
            try:
                return Result.success(session.get(Roadmap, roadmap_id))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def completed_units_count_in_roadmap(self, user_id: str, roadmap_id: str) -> Result[int]:
        with SessionFactory() as session:
            try:
                count = session.scalar(
                    select(func.count(UserUnitProgress.unit_id))
                    .join(Unit, Unit.id == UserUnitProgress.unit_id)
                    .where(
                        UserUnitProgress.user_id == user_id,
                        UserUnitProgress.completed.is_(True),
                        Unit.roadmap_id == roadmap_id,
                    )
                )
                return Result.success(count or 0)
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def completed_unit_ids_in_roadmap(self, user_id: str, roadmap_id: str) -> Result[set[str]]:
        with SessionFactory() as session:
            try:
                rows = session.scalars(
                    select(UserUnitProgress.unit_id)
                    .join(Unit, Unit.id == UserUnitProgress.unit_id)
                    .where(
                        UserUnitProgress.user_id == user_id,
                        UserUnitProgress.completed.is_(True),
                        Unit.roadmap_id == roadmap_id,
                    )
                )
                return Result.success(set(rows))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def units_for_roadmap(self, roadmap_id: str) -> Result[list[Unit]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(Unit).where(Unit.roadmap_id == roadmap_id).order_by(Unit.order)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def active_match_for_user(self, user_id: str) -> Result[Match | None]:
        with SessionFactory() as session:
            try:
                match = session.scalar(
                    select(Match)
                    .where(
                        Match.status == "active",
                        (Match.player1_id == user_id) | (Match.player2_id == user_id),
                    )
                    .order_by(Match.created_at.desc())
                    .limit(1)
                )
                return Result.success(match)
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def claim_opponent_or_enqueue(self, user_id: str, roadmap_id: str) -> Result[User | None]:
        with SessionFactory() as session:
            try:
                qualified_users = (
                    select(UserUnitProgress.user_id)
                    .join(Unit, Unit.id == UserUnitProgress.unit_id)
                    .where(Unit.roadmap_id == roadmap_id, UserUnitProgress.completed.is_(True))
                    .group_by(UserUnitProgress.user_id)
                    .having(func.count(UserUnitProgress.unit_id) >= 5)
                )
                opponent_id = session.scalar(
                    select(WaitingPlayer.user_id)
                    .where(
                        WaitingPlayer.roadmap_id == roadmap_id,
                        WaitingPlayer.user_id != user_id,
                        WaitingPlayer.user_id.in_(qualified_users),
                    )
                    .order_by(WaitingPlayer.joined_at).limit(1)
                )
                if opponent_id is None:
                    waiting = session.get(WaitingPlayer, user_id)
                    if waiting:
                        waiting.roadmap_id = roadmap_id
                        waiting.joined_at = datetime.now(timezone.utc)
                    else:
                        session.add(WaitingPlayer(user_id=user_id, roadmap_id=roadmap_id))
                    session.commit()
                    return Result.success(None)
                opponent = session.get(User, opponent_id)
                session.execute(delete(WaitingPlayer).where(WaitingPlayer.user_id.in_([user_id, opponent_id])))
                session.commit()
                return Result.success(opponent)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)

    def questions_for_units(self, unit_ids: list[str], limit: int) -> Result[list[Question]]:
        with SessionFactory() as session:
            try:
                return Result.success(list(session.scalars(
                    select(Question)
                    .where(Question.unit_id.in_(unit_ids))
                    .order_by(func.random())
                    .limit(limit)
                )))
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def create(self, player1_id: str, player2_id: str, roadmap_id: str,
               question_ids: list[str]) -> Result[Match]:
        with SessionFactory() as session:
            try:
                match = Match(
                    player1_id=player1_id, player2_id=player2_id,
                    roadmap_id=roadmap_id, question_ids=question_ids, status="active",
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

    def finish_and_award(self, match_id: str, roadmap_id: str, score1: int, score2: int,
                         points1: int, points2: int, breakdown: dict) -> Result[tuple[Match, int, int]]:
        with SessionFactory() as session:
            try:
                match = session.get(Match, match_id)
                if match.status != "finished":
                    player1 = session.get(User, match.player1_id)
                    player2 = session.get(User, match.player2_id)
                    player1.knowledge_points += points1
                    player2.knowledge_points += points2

                    rp1 = session.get(UserRoadmapPoints, {"user_id": match.player1_id, "roadmap_id": roadmap_id})
                    if rp1 is None:
                        rp1 = UserRoadmapPoints(user_id=match.player1_id, roadmap_id=roadmap_id, points=0)
                        session.add(rp1)
                    rp1.points += points1

                    rp2 = session.get(UserRoadmapPoints, {"user_id": match.player2_id, "roadmap_id": roadmap_id})
                    if rp2 is None:
                        rp2 = UserRoadmapPoints(user_id=match.player2_id, roadmap_id=roadmap_id, points=0)
                        session.add(rp2)
                    rp2.points += points2

                    match.status = "finished"
                    match.finished_at = datetime.now(timezone.utc)
                    match.player1_score = score1
                    match.player2_score = score2
                    match.player1_points_earned = points1
                    match.player2_points_earned = points2
                    match.score_breakdown = breakdown
                    session.commit()
                    session.refresh(match)
                    session.refresh(rp1)
                    session.refresh(rp2)
                    return Result.success((match, rp1.points, rp2.points))

                rp1 = session.get(UserRoadmapPoints, {"user_id": match.player1_id, "roadmap_id": roadmap_id})
                rp2 = session.get(UserRoadmapPoints, {"user_id": match.player2_id, "roadmap_id": roadmap_id})
                return Result.success((match, rp1.points if rp1 else 0, rp2.points if rp2 else 0))
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)

    def roadmaps_with_progress(self, user_id: str) -> Result[list[tuple[Roadmap, int, int]]]:
        with SessionFactory() as session:
            try:
                rows = session.execute(
                    select(
                        Roadmap,
                        func.count(UserUnitProgress.unit_id).filter(UserUnitProgress.completed.is_(True)),
                        func.coalesce(UserRoadmapPoints.points, 0),
                    )
                    .select_from(Roadmap)
                    .join(Unit, Unit.roadmap_id == Roadmap.id)
                    .outerjoin(
                        UserUnitProgress,
                        (UserUnitProgress.unit_id == Unit.id) & (UserUnitProgress.user_id == user_id),
                    )
                    .outerjoin(
                        UserRoadmapPoints,
                        (UserRoadmapPoints.roadmap_id == Roadmap.id) & (UserRoadmapPoints.user_id == user_id),
                    )
                    .group_by(Roadmap.id, UserRoadmapPoints.points)
                    .order_by(Roadmap.title)
                ).all()
                return Result.success([(roadmap, count, points) for roadmap, count, points in rows])
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def force_miss_answer(self, match_id: str, user_id: str, question_id: str) -> Result[None]:
        with SessionFactory() as session:
            try:
                existing = session.get(MatchAnswer, {
                    "match_id": match_id, "user_id": user_id, "question_id": question_id,
                })
                if existing is None:
                    session.add(MatchAnswer(
                        match_id=match_id, user_id=user_id, question_id=question_id,
                        selected_option_index=-1, is_correct=False,
                    ))
                    session.commit()
                return Result.success(None)
            except IntegrityError:
                session.rollback()
                return Result.success(None)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)

    def enqueue(self, user_id: str, roadmap_id: str) -> Result[None]:
        with SessionFactory() as session:
            try:
                waiting = session.get(WaitingPlayer, user_id)
                if waiting:
                    waiting.roadmap_id = roadmap_id
                    waiting.joined_at = datetime.now(timezone.utc)
                else:
                    session.add(WaitingPlayer(user_id=user_id, roadmap_id=roadmap_id))
                session.commit()
                return Result.success(None)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)