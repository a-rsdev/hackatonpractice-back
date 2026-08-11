from functools import wraps
from typing import Any, Callable, ParamSpec

from fastapi import Request
from fastapi.responses import JSONResponse

from contracts.responses.errors import ApiErrorResponse
from core.result import Result


P = ParamSpec("P")


def current_user_id(request: Request) -> str:
    return request.state.user_id


def handles_result(endpoint: Callable[P, Result[Any]]) -> Callable[P, Any]:
    """Translate an application Result at the HTTP boundary without exceptions."""
    @wraps(endpoint)
    def wrapped(*args: P.args, **kwargs: P.kwargs):
        result = endpoint(*args, **kwargs)
        if result.is_success:
            return result.value
        return JSONResponse(
            status_code=result.error.status_code,
            content=ApiErrorResponse(error=result.error.code).model_dump(),
        )

    return wrapped
