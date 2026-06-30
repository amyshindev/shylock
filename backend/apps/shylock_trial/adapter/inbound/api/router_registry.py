from fastapi import APIRouter

from shylock_trial.adapter.inbound.api.v1.evidence_search_router import evidence_search_router
from shylock_trial.adapter.inbound.api.v1.trial_progression_router import trial_progression_router

shylock_trial_router = APIRouter(prefix="/shylock-trial")
shylock_trial_router.include_router(trial_progression_router)
shylock_trial_router.include_router(evidence_search_router)
