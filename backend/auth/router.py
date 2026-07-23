"""Auth gateway HTTP routes (harness §2.1)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from auth.schemas import LoginRequest, LoginResponse, RefreshRequest, TokenResponse
from auth.services import (
    ACCESS_COOKIE,
    FRONTEND_BASE_URL,
    OAUTH_STATE_COOKIE,
    REFRESH_COOKIE,
    REFRESH_TTL_SEC,
    google_authorize_url,
    login_with_google_code,
    logout,
    new_oauth_state,
    rotate_refresh_token,
)
from core.security import COOKIE_KWARGS, public_jwk, verify_token
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth-gateway"])

SERVICE_AUD = os.getenv("SERVICE_AUD", "shylock-api")


def _set_auth_cookies(response: Response, *, access: str, refresh: str, expires_in: int) -> None:
    response.set_cookie(
        ACCESS_COOKIE,
        access,
        max_age=expires_in,
        path="/",
        **COOKIE_KWARGS,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh,
        max_age=REFRESH_TTL_SEC,
        path="/",
        **COOKIE_KWARGS,
    )


def _clear_auth_cookies(response: Response) -> None:
    for name in (ACCESS_COOKIE, REFRESH_COOKIE, OAUTH_STATE_COOKIE):
        response.delete_cookie(name, path="/", domain=COOKIE_KWARGS.get("domain"))


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse | JSONResponse:
    provider = body.provider.strip().lower()
    if provider != "google":
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    state = new_oauth_state()
    try:
        url = await google_authorize_url(state)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    response = JSONResponse({"authorization_url": url})
    response.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        max_age=600,
        path="/",
        **COOKIE_KWARGS,
    )
    return response  # type: ignore[return-value]


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> Response:
    if provider != "google":
        raise HTTPException(status_code=404, detail="Unknown provider")

    expected = request.cookies.get(OAUTH_STATE_COOKIE)
    if error or not code or not state or not expected or state != expected:
        return RedirectResponse(url=f"{FRONTEND_BASE_URL}/login?error=google")

    try:
        tokens = await login_with_google_code(code)
    except Exception:
        logger.exception("Google OAuth callback failed")
        return RedirectResponse(url=f"{FRONTEND_BASE_URL}/login?error=google")

    response = RedirectResponse(url=f"{FRONTEND_BASE_URL}/")
    response.delete_cookie(OAUTH_STATE_COOKIE, path="/", domain=COOKIE_KWARGS.get("domain"))
    _set_auth_cookies(
        response,
        access=tokens.access_token,
        refresh=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )
    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, body: RefreshRequest | None = None) -> Response:
    refresh_token = (body.refresh_token if body else None) or request.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        tokens = await rotate_refresh_token(refresh_token)
    except PermissionError as exc:
        response = JSONResponse({"detail": str(exc)}, status_code=401)
        _clear_auth_cookies(response)
        return response

    payload = {
        "access_token": tokens.access_token,
        "token_type": "bearer",
        "expires_in": tokens.expires_in,
        "refresh_token": tokens.refresh_token,
    }
    response = JSONResponse(payload)
    _set_auth_cookies(
        response,
        access=tokens.access_token,
        refresh=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_route(request: Request) -> Response:
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    access = request.cookies.get(ACCESS_COOKIE)
    access_jti = None
    access_exp = None
    if access:
        try:
            payload = verify_token(access, aud=SERVICE_AUD)
            access_jti = payload.jti
            access_exp = payload.exp
        except Exception:  # noqa: BLE001
            pass
    await logout(refresh_token, access_jti, access_exp)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_auth_cookies(response)
    return response


@router.get("/.well-known/jwks.json")
async def jwks() -> dict:
    try:
        return {"keys": [public_jwk()]}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
