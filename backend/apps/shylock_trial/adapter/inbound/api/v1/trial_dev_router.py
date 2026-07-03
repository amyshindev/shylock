from fastapi import APIRouter, Depends, HTTPException, status

from infrastructure.config import get_settings
from shylock_trial.adapter.inbound.api.schemas.trial_progression_schema import (
    SceneDialogueLineResponse,
    SceneDialogueResponse,
    StartTrialResponse,
)
from shylock_trial.app.constants.game_balance import DP_JESSICA_EPILOGUE_THRESHOLD
from shylock_trial.app.constants.scene_progression import (
    JESSICA_DUET_SCENE_INDEX,
    JESSICA_INTERVENTION_SCENE_INDEX,
)
from shylock_trial.app.ports.input.trial_progression_use_case import TrialProgressionUseCase
from shylock_trial.dependencies.trial_progression_provider import get_trial_progression_use_case

trial_dev_router = APIRouter(prefix="/dev/trials", tags=["trial-dev"])


def _require_development() -> None:
    if get_settings().app_env != "development":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


def _start_trial_response(result) -> StartTrialResponse:
    return StartTrialResponse(
        trial_id=result.trial_id,
        scene_index=result.scene_index,
        dp=result.dp,
        phase=result.phase,
        scene_dialogue=SceneDialogueResponse(
            lines=[
                SceneDialogueLineResponse(text=line.text, kind=line.kind.value, speaker=line.speaker)
                for line in result.scene_dialogue.lines
            ],
            challenge_header=result.scene_dialogue.challenge_header,
            challenge_text=result.scene_dialogue.challenge_text,
            choice_texts=result.scene_dialogue.choice_text_map(),
        ),
    )


@trial_dev_router.post(
    "/jessica-duet",
    response_model=StartTrialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def dev_jessica_duet(
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> StartTrialResponse:
    _require_development()
    result = await use_case.start_dev_scene(
        scene_index=JESSICA_DUET_SCENE_INDEX,
        dp=DP_JESSICA_EPILOGUE_THRESHOLD,
    )
    return _start_trial_response(result)


@trial_dev_router.post(
    "/jessica-intervention",
    response_model=StartTrialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def dev_jessica_intervention(
    use_case: TrialProgressionUseCase = Depends(get_trial_progression_use_case),
) -> StartTrialResponse:
    _require_development()
    result = await use_case.start_dev_scene(
        scene_index=JESSICA_INTERVENTION_SCENE_INDEX,
        dp=DP_JESSICA_EPILOGUE_THRESHOLD,
    )
    return _start_trial_response(result)
