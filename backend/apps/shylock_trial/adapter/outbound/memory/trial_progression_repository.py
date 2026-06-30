from uuid import UUID

from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.domain.entities.trial_entity import Trial


class InMemoryTrialProgressionRepository(TrialProgressionPort):
    _instance: "InMemoryTrialProgressionRepository | None" = None

    def __init__(self) -> None:
        self._store: dict[UUID, Trial] = {}

    @classmethod
    def get_instance(cls) -> "InMemoryTrialProgressionRepository":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def create(self, trial: Trial) -> Trial:
        self._store[trial.trial_id] = trial
        return trial

    async def save(self, trial: Trial) -> Trial:
        self._store[trial.trial_id] = trial
        return trial

    async def find_by_id(self, trial_id: UUID) -> Trial | None:
        return self._store.get(trial_id)
