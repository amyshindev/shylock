from pydantic import BaseModel, ConfigDict, Field


class DocsAdminLoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "admin",
                    "password": "change-me-docs-admin-password",
                }
            ]
        }
    )

    username: str = Field(min_length=1, description="Docs admin username")
    password: str = Field(min_length=1, description="Docs admin password")
