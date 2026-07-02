import json
from uuid import UUID

from shylock_trial.app.dtos.scene_dialogue_dto import (
    DialogueLineKind,
    SceneDialogueContent,
    SceneDialogueLine,
)
from shylock_trial.app.ports.output.trial_progression_cache_port import TrialProgressionCachePort
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.shylock_hp_score_vo import ShylockHpScore


class TrialProgressionRedisCache(TrialProgressionCachePort):
    def __init__(self, redis_client) -> None:
        self._redis = redis_client

    def _key(self, trial_id: UUID) -> str:
        return f"shylock:trial:{trial_id}"

    def _serialize_scene_dialogues(self, trial: Trial) -> dict:
        return {
            str(idx): {
                "lines": [
                    {"text": line.text, "kind": line.kind.value}
                    for line in content.lines
                ],
                "challenge_header": content.challenge_header,
                "challenge_text": content.challenge_text,
                "choice_texts": content.choice_texts,
            }
            for idx, content in trial.scene_dialogues.items()
        }

    def _deserialize_scene_dialogues(self, data: dict | None) -> dict[int, SceneDialogueContent]:
        if not data:
            return {}
        result: dict[int, SceneDialogueContent] = {}
        for idx_str, raw in data.items():
            result[int(idx_str)] = SceneDialogueContent(
                lines=[
                    SceneDialogueLine(
                        text=line["text"],
                        kind=DialogueLineKind(line["kind"]),
                    )
                    for line in raw.get("lines", [])
                ],
                challenge_header=raw.get("challenge_header"),
                challenge_text=raw.get("challenge_text"),
                choice_texts=raw.get("choice_texts", {}),
            )
        return result

    async def get(self, trial_id: UUID) -> Trial | None:
        raw = await self._redis.get(self._key(trial_id))
        if not raw:
            return None
        data = json.loads(raw)
        return Trial(
            trial_id=UUID(data["trial_id"]),
            scene_index=data["scene_index"],
            shylock_hp=ShylockHpScore(data["shylock_hp"]),
            dp=DpScore(data["dp"]),
            alien_law_executed=data.get("alien_law_executed", True),
            choice_history=data["choice_history"],
            phase=TrialPhase(data["phase"]),
            narration_text=data.get("narration_text"),
            scene_dialogues=self._deserialize_scene_dialogues(data.get("scene_dialogues")),
            tubal_used_scenes=tuple(data.get("tubal_used_scenes", [])),
            presented_evidence=tuple(data.get("presented_evidence", [])),
        )

    async def set(self, trial: Trial, ttl_seconds: int = 3600) -> None:
        payload = json.dumps(
            {
                "trial_id": str(trial.trial_id),
                "scene_index": trial.scene_index,
                "shylock_hp": trial.shylock_hp.value,
                "dp": trial.dp.value,
                "alien_law_executed": trial.alien_law_executed,
                "choice_history": trial.choice_history,
                "phase": trial.phase.value,
                "narration_text": trial.narration_text,
                "scene_dialogues": self._serialize_scene_dialogues(trial),
                "tubal_used_scenes": list(trial.tubal_used_scenes),
                "presented_evidence": list(trial.presented_evidence),
            }
        )
        await self._redis.set(self._key(trial.trial_id), payload, ex=ttl_seconds)

    async def delete(self, trial_id: UUID) -> None:
        await self._redis.delete(self._key(trial_id))
