from shylock_trial.adapter.outbound.orm.trial_orm import TrialChoiceHistoryOrm, TrialOrm
from shylock_trial.app.utils.scene_dialogue_store import (
    deserialize_scene_dialogues,
    serialize_scene_dialogues,
)
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore
from shylock_trial.domain.value_objects.shylock_hp_score_vo import ShylockHpScore


def to_entity(orm: TrialOrm) -> Trial:
    return Trial(
        trial_id=orm.trial_id,
        scene_index=orm.scene_index,
        shylock_hp=ShylockHpScore(orm.shylock_hp),
        dp=DpScore(orm.dp),
        portia_hp=PortiaHpScore(orm.portia_hp),
        alien_law_executed=orm.alien_law_executed,
        choice_history=[row.choice_id for row in orm.choice_history],
        phase=TrialPhase(orm.phase),
        narration_text=orm.narration_text,
        scene_dialogues=deserialize_scene_dialogues(orm.scene_dialogues_json),
    )


def to_orm(entity: Trial) -> TrialOrm:
    orm = TrialOrm(
        trial_id=entity.trial_id,
        scene_index=entity.scene_index,
        shylock_hp=entity.shylock_hp.value,
        dp=entity.dp.value,
        portia_hp=entity.portia_hp.value,
        alien_law_executed=entity.alien_law_executed,
        phase=entity.phase.value,
        narration_text=entity.narration_text,
        scene_dialogues_json=serialize_scene_dialogues(entity.scene_dialogues)
        if entity.scene_dialogues
        else None,
    )
    orm.choice_history = [
        TrialChoiceHistoryOrm(trial_id=entity.trial_id, choice_id=choice_id)
        for choice_id in entity.choice_history
    ]
    return orm
