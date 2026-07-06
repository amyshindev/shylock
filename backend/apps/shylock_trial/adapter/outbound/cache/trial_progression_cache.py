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
from shylock_trial.domain.value_objects.hp_score_vo import HpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore


class TrialProgressionRedisCache(TrialProgressionCachePort):
    def __init__(self, redis_client) -> None:
        self._redis = redis_client

    def _key(self, trial_id: UUID) -> str:
        return f"shylock:trial:{trial_id}"

    def _serialize_scene_dialogues(self, trial: Trial) -> dict:
        return {
            str(idx): {
                "lines": [
                    {
                        "text": line.text,
                        "kind": line.kind.value,
                        **({"speaker": line.speaker} if line.speaker else {}),
                    }
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
                        speaker=line.get("speaker"),
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
            dp=DpScore(data["dp"]),
            hp=HpScore(data.get("hp", 100)),
            portia_hp=PortiaHpScore(data.get("portia_hp", 100)),
            choice_history=data["choice_history"],
            phase=TrialPhase(data["phase"]),
            narration_text=data.get("narration_text"),
            scene_dialogues=self._deserialize_scene_dialogues(data.get("scene_dialogues")),
            tubal_used_scenes=tuple(data.get("tubal_used_scenes", [])),
            presented_evidence=tuple(data.get("presented_evidence", [])),
            tubal_enhanced_choices=data.get("tubal_enhanced_choices", {}),
            venice_dp_shield=data.get("venice_dp_shield", False),
            venice_paradox_used=data.get("venice_paradox_used", False),
        )

    async def set(self, trial: Trial, ttl_seconds: int = 3600) -> None:
        payload = json.dumps(
            {
                "trial_id": str(trial.trial_id),
                "scene_index": trial.scene_index,
                "dp": trial.dp.value,
                "hp": trial.hp.value,
                "portia_hp": trial.portia_hp.value,
                "choice_history": trial.choice_history,
                "phase": trial.phase.value,
                "narration_text": trial.narration_text,
                "scene_dialogues": self._serialize_scene_dialogues(trial),
                "tubal_used_scenes": list(trial.tubal_used_scenes),
                "presented_evidence": list(trial.presented_evidence),
                "tubal_enhanced_choices": trial.tubal_enhanced_choices,
                "venice_dp_shield": trial.venice_dp_shield,
                "venice_paradox_used": trial.venice_paradox_used,
            }
        )
        await self._redis.set(self._key(trial.trial_id), payload, ex=ttl_seconds)

    async def delete(self, trial_id: UUID) -> None:
        await self._redis.delete(self._key(trial_id))
