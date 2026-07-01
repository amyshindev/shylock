from uuid import uuid4

from shylock_trial.adapter.outbound.mappers.trial_progression_mapper import to_entity, to_orm
from shylock_trial.app.dtos.scene_dialogue_dto import (
    DialogueLineKind,
    SceneDialogueContent,
    SceneDialogueLine,
)
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore
from shylock_trial.domain.value_objects.shylock_hp_score_vo import ShylockHpScore


def test_trial_mapper_roundtrip() -> None:
    trial = Trial(
        trial_id=uuid4(),
        scene_index=2,
        shylock_hp=ShylockHpScore(45),
        dp=DpScore(60),
        portia_hp=PortiaHpScore(100),
        alien_law_executed=True,
        choice_history=["bond", "mercy"],
        phase=TrialPhase.IN_PROGRESS,
        narration_text="Test narration",
        scene_dialogues={
            0: SceneDialogueContent(
                lines=(
                    SceneDialogueLine(
                        text="line one",
                        kind=DialogueLineKind.SPEECH,
                    ),
                ),
                challenge_text="choose",
                choice_texts={"a": "A"},
            ),
        },
    )
    orm = to_orm(trial)
    restored = to_entity(orm)

    assert restored.trial_id == trial.trial_id
    assert restored.scene_index == trial.scene_index
    assert restored.shylock_hp.value == 45
    assert restored.dp.value == 60
    assert restored.portia_hp.value == 100
    assert restored.alien_law_executed is True
    assert restored.choice_history == ["bond", "mercy"]
    assert restored.phase == TrialPhase.IN_PROGRESS
    assert restored.narration_text == "Test narration"
    assert 0 in restored.scene_dialogues
    assert restored.scene_dialogues[0].lines[0].text == "line one"
    assert restored.scene_dialogues[0].lines[0].kind == DialogueLineKind.SPEECH
