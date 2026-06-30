from pydantic import BaseModel, ConfigDict


class PortiaResponseSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"text": "Speak your plea before the Duke.", "fallback_used": False}]
        }
    )

    text: str
    fallback_used: bool = False
