from typing import Annotated

from fastapi import Depends

from repositories.content import ContentRepository
from repositories.matches import MatchRepository
from repositories.pomodoro import PomodoroRepository
from repositories.progress import ProgressRepository
from repositories.users import UserRepository
from services.auth import AuthService
from services.content import ContentService
from services.matches import MatchService
from services.pomodoro import PomodoroService
from services.progress import ProgressService
from services.streak import StreakService


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_content_repository() -> ContentRepository:
    return ContentRepository()


def get_progress_repository() -> ProgressRepository:
    return ProgressRepository()


def get_match_repository() -> MatchRepository:
    return MatchRepository()


def get_pomodoro_repository() -> PomodoroRepository:
    return PomodoroRepository()


def get_auth_service(users: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(users)


def get_content_service(content: Annotated[ContentRepository, Depends(get_content_repository)]) -> ContentService:
    return ContentService(content)


def get_progress_service(
    progress: Annotated[ProgressRepository, Depends(get_progress_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> ProgressService:
    return ProgressService(progress, users)


def get_match_service(
    matches: Annotated[MatchRepository, Depends(get_match_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> MatchService:
    return MatchService(matches, users)


def get_streak_service(users: Annotated[UserRepository, Depends(get_user_repository)]) -> StreakService:
    return StreakService(users)


def get_pomodoro_service(
    sessions: Annotated[PomodoroRepository, Depends(get_pomodoro_repository)],
) -> PomodoroService:
    return PomodoroService(sessions)
