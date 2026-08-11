from pydantic import BaseModel, Field, field_validator


class Credentials(BaseModel):
    nickname: str = Field(min_length=1, max_length=40, pattern=r"^[\w-]+$")
    password: str = Field(min_length=1, max_length=128)

    @field_validator("nickname")
    @classmethod
    def clean_nickname(cls, value: str) -> str:
        return value.strip()
