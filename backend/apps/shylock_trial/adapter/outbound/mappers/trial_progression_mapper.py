from shylock_trial.adapter.outbound.orm.trial_orm import TrialChoiceHistoryOrm, TrialOrm
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.confidence_score_vo import ConfidenceScore
from shylock_trial.domain.value_objects.dignity_score_vo import DignityScore


def to_entity(orm: TrialOrm) -> Trial:
    return Trial(
        trial_id=orm.trial_id,
        scene_index=orm.scene_index,
        dignity=DignityScore(orm.dignity),
        confidence=ConfidenceScore(orm.confidence),
        choice_history=[row.choice_id for row in orm.choice_history],
        phase=TrialPhase(orm.phase),
        narration_text=orm.narration_text,
    )


def to_orm(entity: Trial) -> TrialOrm:
    orm = TrialOrm(
        trial_id=entity.trial_id,
        scene_index=entity.scene_index,
        dignity=entity.dignity.value,
        confidence=entity.confidence.value,
        phase=entity.phase.value,
        narration_text=entity.narration_text,
    )
    orm.choice_history = [
        TrialChoiceHistoryOrm(trial_id=entity.trial_id, choice_id=choice_id)
        for choice_id in entity.choice_history
    ]
    return orm
