from uuid import uuid4

from shylock_trial.adapter.outbound.mappers.trial_progression_mapper import to_entity, to_orm
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.confidence_score_vo import ConfidenceScore
from shylock_trial.domain.value_objects.dignity_score_vo import DignityScore


def test_trial_mapper_roundtrip() -> None:
    trial = Trial(
        trial_id=uuid4(),
        scene_index=2,
        dignity=DignityScore(60),
        confidence=ConfidenceScore(45),
        choice_history=["bond", "mercy"],
        phase=TrialPhase.IN_PROGRESS,
        narration_text="Test narration",
    )
    orm = to_orm(trial)
    restored = to_entity(orm)

    assert restored.trial_id == trial.trial_id
    assert restored.scene_index == trial.scene_index
    assert restored.dignity.value == 60
    assert restored.confidence.value == 45
    assert restored.choice_history == ["bond", "mercy"]
    assert restored.phase == TrialPhase.IN_PROGRESS
    assert restored.narration_text == "Test narration"
