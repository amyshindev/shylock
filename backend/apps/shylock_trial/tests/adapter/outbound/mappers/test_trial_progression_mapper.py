from uuid import uuid4

from shylock_trial.adapter.outbound.mappers.trial_progression_mapper import to_entity, to_orm
from shylock_trial.adapter.outbound.orm.trial_orm import TrialOrm
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.hp_score_vo import HpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore


def test_trial_mapper_roundtrip() -> None:
    entity = Trial(
        trial_id=uuid4(),
        scene_index=2,
        dp=DpScore(55),
        hp=HpScore(80),
        portia_hp=PortiaHpScore(72),
        choice_history=["appeal_mercy"],
        phase=TrialPhase.IN_PROGRESS,
        portia_reactions=["법정은 증서 위에 서 있노라."],
    )
    orm = to_orm(entity)
    restored = to_entity(orm)

    assert restored.trial_id == entity.trial_id
    assert restored.scene_index == 2
    assert restored.dp.value == 55
    assert restored.hp.value == 80
    assert restored.portia_hp.value == 72
    assert restored.choice_history == ["appeal_mercy"]
    assert restored.portia_reactions == ["법정은 증서 위에 서 있노라."]


def test_trial_orm_entity_fields() -> None:
    orm = TrialOrm(
        trial_id=uuid4(),
        scene_index=0,
        dp=50,
        hp=100,
        portia_hp=100,
        phase="in_progress",
    )
    entity = to_entity(orm)
    assert entity.dp.value == 50
    assert entity.hp.value == 100
