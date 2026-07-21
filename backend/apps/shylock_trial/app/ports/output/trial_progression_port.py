from abc import ABC, abstractmethod
from uuid import UUID

from shylock_trial.domain.entities.trial_entity import Trial


class TrialProgressionPort(ABC):
    @abstractmethod
    async def create(self, trial: Trial) -> Trial: ...

    @abstractmethod
    async def save(self, trial: Trial) -> Trial: ...

    @abstractmethod
    async def find_by_id(self, trial_id: UUID) -> Trial | None: ...

    @abstractmethod
    async def list_by_user_id(self, user_id: UUID) -> list[Trial]: ...
