from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shylock_trial.adapter.outbound.mappers.trial_progression_mapper import to_entity, to_orm
from shylock_trial.adapter.outbound.orm.trial_orm import TrialChoiceHistoryOrm, TrialOrm
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.domain.entities.trial_entity import Trial


class TrialProgressionPgRepository(TrialProgressionPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, trial: Trial) -> Trial:
        orm = to_orm(trial)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm, attribute_names=["choice_history"])
        return to_entity(orm)

    async def save(self, trial: Trial) -> Trial:
        existing = await self._session.get(
            TrialOrm,
            trial.trial_id,
            options=[selectinload(TrialOrm.choice_history)],
        )
        if existing is None:
            return await self.create(trial)

        existing.scene_index = trial.scene_index
        existing.dignity = trial.dignity.value
        existing.confidence = trial.confidence.value
        existing.phase = trial.phase.value
        existing.narration_text = trial.narration_text
        existing.choice_history.clear()
        for choice_id in trial.choice_history:
            existing.choice_history.append(
                TrialChoiceHistoryOrm(trial_id=trial.trial_id, choice_id=choice_id)
            )

        await self._session.commit()
        await self._session.refresh(existing, attribute_names=["choice_history"])
        return to_entity(existing)

    async def find_by_id(self, trial_id: UUID) -> Trial | None:
        result = await self._session.execute(
            select(TrialOrm)
            .where(TrialOrm.trial_id == trial_id)
            .options(selectinload(TrialOrm.choice_history))
        )
        orm = result.scalar_one_or_none()
        return to_entity(orm) if orm else None
