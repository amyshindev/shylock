from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "shylock@venice.it",
                    "password": "pound-of-flesh",
                    "nickname": "샤일록",
                }
            ]
        }
    )

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)
    nickname: str = Field(min_length=1, max_length=32)


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "shylock@venice.it",
                    "password": "pound-of-flesh",
                }
            ]
        }
    )

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_id": "9b2f8f0a-0000-4000-8000-000000000000",
                    "email": "shylock@venice.it",
                    "nickname": "샤일록",
                }
            ]
        }
    )

    user_id: UUID
    email: str
    nickname: str
