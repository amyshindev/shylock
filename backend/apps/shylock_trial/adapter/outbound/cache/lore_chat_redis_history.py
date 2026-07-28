import json

from shylock_trial.app.dtos.lore_chat_dto import LoreChatTurnDto
from shylock_trial.app.ports.output.lore_chat_history_port import LoreChatHistoryPort

# Keep at most 10 round trips (20 turns) per session in Redis — same idea as
# trial_progression_cache.py's ttl_seconds, but bounded by count instead of
# only by time, since a single long-lived session could otherwise grow the
# stored history (and therefore every future LLM call's token cost) without
# limit.
MAX_STORED_TURNS = 20
DEFAULT_TTL_SECONDS = 3600


class LoreChatRedisHistory(LoreChatHistoryPort):
    def __init__(self, redis_client, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    def _key(self, session_id: str) -> str:
        return f"shylock:lore_chat:{session_id}"

    async def get(self, session_id: str) -> tuple[LoreChatTurnDto, ...]:
        raw_turns = await self._redis.lrange(self._key(session_id), 0, -1)
        return tuple(
            LoreChatTurnDto(role=data["role"], content=data["content"])
            for data in (json.loads(raw) for raw in raw_turns)
        )

    async def append(self, session_id: str, turn: LoreChatTurnDto) -> None:
        key = self._key(session_id)
        payload = json.dumps({"role": turn.role, "content": turn.content}, ensure_ascii=False)
        await self._redis.rpush(key, payload)
        await self._redis.ltrim(key, -MAX_STORED_TURNS, -1)
        await self._redis.expire(key, self._ttl_seconds)
