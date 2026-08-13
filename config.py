import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "learning_quest.db")))
JWT_SECRET = os.getenv("JWT_SECRET", "development-secret-change-me")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "86400"))


PASSING_SCORE = 60

ANSWER_TIME_SECONDS = 15
REVEAL_DURATION_SECONDS = 3
ROUNDS_PER_MATCH = 3
POINTS_PER_CORRECT = 10
WIN_MULTIPLIER = 1.5
STREAK_MULTIPLIER_STEP = 0.1     # +10% за каждый день стрика
MAX_STREAK_MULTIPLIER = 2.0      # потолок множителя
