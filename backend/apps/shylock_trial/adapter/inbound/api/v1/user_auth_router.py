from fastapi import APIRouter, Depends, HTTPException, status

from shylock_trial.adapter.inbound.api.schemas.user_auth_schema import UserResponse
from shylock_trial.app.dtos.user_auth_dto import UserDto
from shylock_trial.dependencies.user_auth_provider import get_current_user_optional

user_auth_router = APIRouter(prefix="/auth", tags=["user-auth"])


@user_auth_router.get("/me", response_model=UserResponse)
async def me(
    current_user: UserDto | None = Depends(get_current_user_optional),
) -> UserResponse:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
        )
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        nickname=current_user.nickname,
    )
