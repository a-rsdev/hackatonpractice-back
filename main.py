from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import initialize_database
from handlers.auth import router as auth_router
from handlers.matches import router as matches_router
from handlers.pomodoro import router as pomodoro_router
from handlers.progress import router as progress_router
from handlers.roadmaps import router as roadmaps_router
from handlers.streak import router as streak_router
from middleware.auth import AuthenticationMiddleware
from repositories.users import UserRepository
from services.auth import AuthService


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Learning Quest API", version="2.0.0", lifespan=lifespan)
app.add_middleware(AuthenticationMiddleware, auth_service=AuthService(UserRepository()))
app.include_router(auth_router)
app.include_router(roadmaps_router)
app.include_router(progress_router)
app.include_router(matches_router)
app.include_router(streak_router)
app.include_router(pomodoro_router)


@app.get("/", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


initialize_database()
