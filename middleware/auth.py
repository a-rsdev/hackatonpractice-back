from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from services.auth import AuthService


PUBLIC_PATHS = {"/", "/docs", "/docs/oauth2-redirect", "/openapi.json", "/redoc"}


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_service: AuthService):
        super().__init__(app)
        self.auth_service = auth_service

    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()

        request.state.user_id = None
        if token:
            result = self.auth_service.authenticate(token)
            if result.is_success:
                request.state.user_id = result.value

        return await call_next(request)
