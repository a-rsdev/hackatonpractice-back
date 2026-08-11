from typing import Annotated

from fastapi import APIRouter, Depends

from contracts.requests.auth import Credentials
from contracts.responses.auth import AuthResponse
from core.result import Result
from dependencies import get_auth_service
from handlers.dependencies import handles_result
from services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
@handles_result
def register(body: Credentials, service: Annotated[AuthService, Depends(get_auth_service)]) -> Result[AuthResponse]:
    return service.register(body.nickname, body.password)


@router.post("/login", response_model=AuthResponse)
@handles_result
def login(body: Credentials, service: Annotated[AuthService, Depends(get_auth_service)]) -> Result[AuthResponse]:
    return service.login(body.nickname, body.password)
