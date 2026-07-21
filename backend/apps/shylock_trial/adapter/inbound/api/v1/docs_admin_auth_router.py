from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from shylock_trial.adapter.inbound.api.templates.docs_admin_auth_login import LOGIN_HTML
from shylock_trial.app.dtos.docs_admin_auth_dto import DocsAdminLoginInputDto
from shylock_trial.app.ports.input.docs_admin_auth_use_case import DocsAdminAuthUseCase
from shylock_trial.app.ports.output.docs_admin_auth_port import DocsAdminAuthPort
from shylock_trial.dependencies.docs_admin_auth_provider import (
    get_docs_admin_auth_repository,
    get_docs_admin_auth_use_case,
)

DOCS_COOKIE_NAME = "shylock_docs_session"

docs_admin_auth_router = APIRouter(include_in_schema=False)


def _login_page(*, error: str | None = None) -> HTMLResponse:
    error_html = f'<p class="error">{error}</p>' if error else ""
    return HTMLResponse(
        content=LOGIN_HTML.replace("__ERROR__", error_html),
        status_code=status.HTTP_401_UNAUTHORIZED if error else status.HTTP_200_OK,
    )


def _set_docs_cookie(
    response: Response,
    *,
    session_token: str,
    port: DocsAdminAuthPort,
) -> None:
    response.set_cookie(
        key=DOCS_COOKIE_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=port.cookie_secure(),
        max_age=60 * 60 * 12,
        path="/",
    )


@docs_admin_auth_router.get("/docs")
async def docs(
    request: Request,
    use_case: DocsAdminAuthUseCase = Depends(get_docs_admin_auth_use_case),
) -> Response:
    if not use_case.is_session_valid(request.cookies.get(DOCS_COOKIE_NAME)):
        return _login_page()
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Shylock Trial API - Swagger UI",
    )


@docs_admin_auth_router.get("/redoc")
async def redoc(
    request: Request,
    use_case: DocsAdminAuthUseCase = Depends(get_docs_admin_auth_use_case),
) -> Response:
    if not use_case.is_session_valid(request.cookies.get(DOCS_COOKIE_NAME)):
        return _login_page()
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Shylock Trial API - ReDoc",
    )


@docs_admin_auth_router.get("/openapi.json")
async def openapi_json(
    request: Request,
    use_case: DocsAdminAuthUseCase = Depends(get_docs_admin_auth_use_case),
) -> Response:
    if not use_case.is_session_valid(request.cookies.get(DOCS_COOKIE_NAME)):
        return JSONResponse(
            {"detail": "Authentication required"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return JSONResponse(request.app.openapi())


@docs_admin_auth_router.post("/docs/login")
async def docs_login(
    username: str = Form(...),
    password: str = Form(...),
    use_case: DocsAdminAuthUseCase = Depends(get_docs_admin_auth_use_case),
    port: DocsAdminAuthPort = Depends(get_docs_admin_auth_repository),
) -> Response:
    result = await use_case.login(
        DocsAdminLoginInputDto(username=username, password=password),
    )
    if not result.success or not result.session_token:
        return _login_page(error="관리자 계정 정보가 올바르지 않습니다.")

    response = RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)
    _set_docs_cookie(response, session_token=result.session_token, port=port)
    return response


@docs_admin_auth_router.post("/docs/logout")
async def docs_logout() -> Response:
    response = RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(DOCS_COOKIE_NAME, path="/")
    return response
