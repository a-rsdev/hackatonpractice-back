from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    status_code: int


class Result(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: T | None = None
    error: ErrorDetail | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        return cls(value=value)

    @classmethod
    def failure(cls, code: str, status_code: int) -> "Result[T]":
        return cls(error=ErrorDetail(code=code, status_code=status_code))
