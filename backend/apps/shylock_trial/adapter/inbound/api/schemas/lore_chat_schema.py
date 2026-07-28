from pydantic import BaseModel, ConfigDict, Field


class LoreChatAskRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "session_id": None,
                    "message": "샤일록은 왜 안토니오에게 살 1파운드를 요구했나요?",
                }
            ]
        }
    )

    session_id: str | None = None
    message: str = Field(min_length=1, max_length=1000)


class LoreChatSourceResponse(BaseModel):
    ftln: int
    act_scene: str
    speaker: str
    excerpt: str


class LoreChatAskResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "session_id": "f3c0b2f0-2c9b-4b8a-9b0a-1f2e3d4c5b6a",
                    "answer": "극 중 샤일록은 안토니오와의 채무 계약에서 위약 시 살 1파운드를 조건으로 걸었습니다...",
                    "sources": [
                        {
                            "ftln": 470,
                            "act_scene": "1.3",
                            "speaker": "SHYLOCK",
                            "excerpt": "Let the forfeit / Be nominated for an equal pound / Of your fair flesh...",
                        }
                    ],
                }
            ]
        }
    )

    session_id: str
    answer: str
    sources: list[LoreChatSourceResponse] = Field(default_factory=list)
