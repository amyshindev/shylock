from fastapi import APIRouter

from shylock_trial.adapter.inbound.api.v1.docs_admin_auth_router import docs_admin_auth_router
from shylock_trial.adapter.inbound.api.v1.evidence_search_router import evidence_search_router
from shylock_trial.adapter.inbound.api.v1.present_evidence_router import present_evidence_router
from shylock_trial.adapter.inbound.api.v1.trial_dev_router import trial_dev_router
from shylock_trial.adapter.inbound.api.v1.trial_progression_router import trial_progression_router
from shylock_trial.adapter.inbound.api.v1.tubal_skill_router import tubal_skill_router
from shylock_trial.adapter.inbound.api.v1.user_auth_router import user_auth_router

# Root-level /docs gate (no /shylock-trial prefix). Mount separately in main.
__all__ = ["shylock_trial_router", "docs_admin_auth_router"]

shylock_trial_router = APIRouter(prefix="/shylock-trial")
shylock_trial_router.include_router(user_auth_router)
shylock_trial_router.include_router(trial_progression_router)
shylock_trial_router.include_router(trial_dev_router)
shylock_trial_router.include_router(evidence_search_router)
shylock_trial_router.include_router(tubal_skill_router)
shylock_trial_router.include_router(present_evidence_router)
