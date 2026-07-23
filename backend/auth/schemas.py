from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"provider": "google"}]}
    )

    provider: str = Field(description="OAuth provider id, e.g. google")


class LoginResponse(BaseModel):
    authorization_url: str


class RefreshRequest(BaseModel):
    refresh_token: str | None = Field(
        default=None,
        description="Optional body refresh token; cookie is preferred.",
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str | None = None
