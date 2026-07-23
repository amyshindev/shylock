"""Auth-only FastAPI entrypoint (auth.shylock-trial.xyz → auth:9000)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import router as auth_router

app = FastAPI(
    title="Shylock Auth Gateway",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shylock-trial.xyz",
        "https://www.shylock-trial.xyz",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}
