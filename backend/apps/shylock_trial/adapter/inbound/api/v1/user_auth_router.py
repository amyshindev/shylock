import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response

from infrastructure.config import get_settings
from shylock_trial.adapter.inbound.api.schemas.user_auth_schema import (
    LoginRequest,
    SignupRequest,
    UserResponse,
)
from shylock_trial.app.constants.user_auth import USER_SESSION_COOKIE, USER_SESSION_TTL_SECONDS
from shylock_trial.app.dtos.user_auth_dto import AuthResultDto, LoginInputDto, SignupInputDto, UserDto
from shylock_trial.app.ports.input.user_auth_use_case import UserAuthUseCase
from shylock_trial.app.ports.output.google_oauth_port import GoogleOAuthPort
from shylock_trial.app.ports.output.user_session_port import UserSessionPort
from shylock_trial.dependencies.user_auth_provider import (
    get_current_user_optional,
    get_google_oauth_client,
    get_user_auth_use_case,
    get_user_session_repository,
)

logger = logging.getLogger(__name__)

user_auth_router = APIRouter(prefix="/auth", tags=["user-auth"])

GOOGLE_STATE_COOKIE = "shylock_google_state"


def _auth_response(result: AuthResultDto, session_port: UserSessionPort) -> JSONResponse:
    assert result.user is not None and result.session_token is not None
    response = JSONResponse(
        {
            "user_id": str(result.user.user_id),
            "email": result.user.email,
            "nickname": result.user.nickname,
        }
    )
    response.set_cookie(
        key=USER_SESSION_COOKIE,
        value=result.session_token,
        httponly=True,
        samesite="lax",
        secure=session_port.cookie_secure(),
        max_age=USER_SESSION_TTL_SECONDS,
        path="/",
    )
    return response


@user_auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: SignupRequest,
    use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
    session_port: UserSessionPort = Depends(get_user_session_repository),
) -> Response:
    result = await use_case.signup(
        SignupInputDto(email=body.email, password=body.password, nickname=body.nickname)
    )
    if not result.success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=result.error)
    response = _auth_response(result, session_port)
    response.status_code = status.HTTP_201_CREATED
    return response


@user_auth_router.post("/login", response_model=UserResponse)
async def login(
    body: LoginRequest,
    use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
    session_port: UserSessionPort = Depends(get_user_session_repository),
) -> Response:
    result = await use_case.login(LoginInputDto(email=body.email, password=body.password))
    if not result.success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.error)
    return _auth_response(result, session_port)


@user_auth_router.get("/google/login", include_in_schema=False)
async def google_login_start(
    google: GoogleOAuthPort = Depends(get_google_oauth_client),
    session_port: UserSessionPort = Depends(get_user_session_repository),
) -> Response:
    if not google.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="구글 로그인이 설정되지 않았습니다.",
        )
    state = secrets.token_urlsafe(16)
    response = RedirectResponse(url=google.authorize_url(state))
    response.set_cookie(
        key=GOOGLE_STATE_COOKIE,
        value=state,
        httponly=True,
        samesite="lax",
        secure=session_port.cookie_secure(),
        max_age=600,
        path="/",
    )
    return response


@user_auth_router.get("/google/callback", include_in_schema=False)
async def google_login_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
    google: GoogleOAuthPort = Depends(get_google_oauth_client),
    session_port: UserSessionPort = Depends(get_user_session_repository),
) -> Response:
    frontend = get_settings().frontend_base_url.rstrip("/")

    def _fail() -> RedirectResponse:
        response = RedirectResponse(url=f"{frontend}/login?error=google")
        response.delete_cookie(GOOGLE_STATE_COOKIE, path="/")
        return response

    expected_state = request.cookies.get(GOOGLE_STATE_COOKIE)
    if error or not code or not state or not expected_state or state != expected_state:
        return _fail()

    try:
        access_token = await google.exchange_code(code)
        profile = await google.fetch_profile(access_token)
    except Exception:
        logger.exception("Google OAuth exchange failed")
        return _fail()

    result = await use_case.login_with_google(profile)
    if not result.success or not result.session_token:
        return _fail()

    response = RedirectResponse(url=f"{frontend}/")
    response.delete_cookie(GOOGLE_STATE_COOKIE, path="/")
    response.set_cookie(
        key=USER_SESSION_COOKIE,
        value=result.session_token,
        httponly=True,
        samesite="lax",
        secure=session_port.cookie_secure(),
        max_age=USER_SESSION_TTL_SECONDS,
        path="/",
    )
    return response


@user_auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(USER_SESSION_COOKIE, path="/")
    return response


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
