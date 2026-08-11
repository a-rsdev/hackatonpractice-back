from datetime import date, timedelta

from contracts.responses.activity import StreakResponse
from core.result import Result
from repositories.users import UserRepository


class StreakService:
    def __init__(self, users: UserRepository):
        self.users = users

    def ping(self, user_id: str) -> Result[StreakResponse]:
        found = self.users.get_by_id(user_id)
        if not found.is_success:
            return Result(error=found.error)
        user, today = found.value, date.today()
        if user is None:
            return Result.failure("user_not_found", 404)
        if user.last_active_date == today:
            streak = user.streak_count
        elif user.last_active_date == today - timedelta(days=1):
            streak = user.streak_count + 1
        else:
            streak = 1
        updated = self.users.update_streak(user_id, streak, today)
        if not updated.is_success:
            return Result(error=updated.error)
        return Result.success(StreakResponse(streak_count=updated.value.streak_count))
