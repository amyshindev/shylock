from abc import ABC, abstractmethod
from uuid import UUID

from shylock_trial.domain.entities.trial_entity import Trial


class TrialProgressionCachePort(ABC):
    """Optional fast lookup for in-progress trials (Redis)."""

    @abstractmethod
    async def get(self, trial_id: UUID) -> Trial | None: ...

    @abstractmethod
    async def set(self, trial: Trial, ttl_seconds: int = 3600) -> None: ...

    @abstractmethod
    async def delete(self, trial_id: UUID) -> None: ...
