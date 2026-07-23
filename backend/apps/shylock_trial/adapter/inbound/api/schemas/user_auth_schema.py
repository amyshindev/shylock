from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
    email: str | None
    nickname: str
