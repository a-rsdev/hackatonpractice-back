from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from services.auth import AuthService


PUBLIC_PATHS = {"/", "/docs", "/docs/oauth2-redirect", "/openapi.json", "/redoc"}


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_service: AuthService):
        super().__init__(app)
        self.auth_service = auth_service

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/auth/"):
            return await call_next(request)
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return self._unauthorized("missing_bearer_token")
        authenticated = self.auth_service.authenticate(authorization[7:].strip())
        if not authenticated.is_success:
            return self._unauthorized(authenticated.error.code)
        request.state.user_id = authenticated.value
        return await call_next(request)

    @staticmethod
    def _unauthorized(code: str) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": code},
            headers={"WWW-Authenticate": "Bearer"},
        )
