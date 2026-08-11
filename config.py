import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "learning_quest.db")))
JWT_SECRET = os.getenv("JWT_SECRET", "development-secret-change-me")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "86400"))
PASSING_SCORE = 70
POINTS_PER_CORRECT = 10
MATCH_BONUS = 20
