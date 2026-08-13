from datetime import date, datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    nickname: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    knowledge_points: Mapped[int] = mapped_column(Integer, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    topics_completed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Roadmap(Base):
    __tablename__ = "roadmaps"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)


class Unit(Base):
    __tablename__ = "units"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    roadmap_id: Mapped[str] = mapped_column(ForeignKey("roadmaps.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(Integer)


class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    unit_id: Mapped[str] = mapped_column(ForeignKey("units.id"), index=True)
    url: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    unit_id: Mapped[str] = mapped_column(ForeignKey("units.id"), index=True)
    text: Mapped[str] = mapped_column(String)
    options: Mapped[list[str]] = mapped_column(JSON)
    correct_option_index: Mapped[int] = mapped_column(Integer)


class UserUnitProgress(Base):
    __tablename__ = "user_unit_progress"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    unit_id: Mapped[str] = mapped_column(ForeignKey("units.id"), primary_key=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    player1_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    player2_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    roadmap_id: Mapped[str] = mapped_column(ForeignKey("roadmaps.id"))
    question_ids: Mapped[list[str]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    player1_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    player2_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    player1_points_earned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    player2_points_earned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class MatchAnswer(Base):
    __tablename__ = "match_answers"
    __table_args__ = (UniqueConstraint("match_id", "user_id", "question_id"),)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), primary_key=True)
    selected_option_index: Mapped[int] = mapped_column(Integer)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="running")


class WaitingPlayer(Base):
    __tablename__ = "waiting_pool"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    roadmap_id: Mapped[str] = mapped_column(ForeignKey("roadmaps.id"), index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)