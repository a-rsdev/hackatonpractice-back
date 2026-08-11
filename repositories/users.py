from datetime import date

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.result import Result
from database import SessionFactory
from models.entities import User


class UserRepository:
    def create(self, nickname: str, password_hash: str) -> Result[User]:
        with SessionFactory() as session:
            user = User(nickname=nickname, password_hash=password_hash)
            session.add(user)
            try:
                session.commit()
                session.refresh(user)
                return Result.success(user)
            except IntegrityError:
                session.rollback()
                return Result.failure("nickname_taken", 409)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)

    def get_by_nickname(self, nickname: str) -> Result[User | None]:
        with SessionFactory() as session:
            try:
                user = session.scalar(select(User).where(func.lower(User.nickname) == nickname.lower()))
                return Result.success(user)
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def get_by_id(self, user_id: str) -> Result[User | None]:
        with SessionFactory() as session:
            try:
                user = session.get(User, user_id)
                return Result.success(user)
            except SQLAlchemyError:
                return Result.failure("database_error", 500)

    def update_streak(self, user_id: str, streak_count: int, active_date: date) -> Result[User | None]:
        with SessionFactory() as session:
            try:
                user = session.get(User, user_id)
                if user is None:
                    return Result.success(None)
                user.streak_count = streak_count
                user.last_active_date = active_date
                session.commit()
                session.refresh(user)
                return Result.success(user)
            except SQLAlchemyError:
                session.rollback()
                return Result.failure("database_error", 500)
