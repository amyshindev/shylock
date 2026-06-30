import json
from uuid import UUID

from shylock_trial.app.ports.output.trial_progression_cache_port import TrialProgressionCachePort
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.confidence_score_vo import ConfidenceScore
from shylock_trial.domain.value_objects.dignity_score_vo import DignityScore


class TrialProgressionRedisCache(TrialProgressionCachePort):
    def __init__(self, redis_client) -> None:
        self._redis = redis_client

    def _key(self, trial_id: UUID) -> str:
        return f"shylock:trial:{trial_id}"

    async def get(self, trial_id: UUID) -> Trial | None:
        raw = await self._redis.get(self._key(trial_id))
        if not raw:
            return None
        data = json.loads(raw)
        return Trial(
            trial_id=UUID(data["trial_id"]),
            scene_index=data["scene_index"],
            dignity=DignityScore(data["dignity"]),
            confidence=ConfidenceScore(data["confidence"]),
            choice_history=data["choice_history"],
            phase=TrialPhase(data["phase"]),
            narration_text=data.get("narration_text"),
        )

    async def set(self, trial: Trial, ttl_seconds: int = 3600) -> None:
        payload = json.dumps(
            {
                "trial_id": str(trial.trial_id),
                "scene_index": trial.scene_index,
                "dignity": trial.dignity.value,
                "confidence": trial.confidence.value,
                "choice_history": trial.choice_history,
                "phase": trial.phase.value,
                "narration_text": trial.narration_text,
            }
        )
        await self._redis.set(self._key(trial.trial_id), payload, ex=ttl_seconds)

    async def delete(self, trial_id: UUID) -> None:
        await self._redis.delete(self._key(trial_id))
