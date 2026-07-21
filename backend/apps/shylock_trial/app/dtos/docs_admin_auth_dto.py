from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DocsAdminLoginInputDto:
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class DocsAdminLoginResultDto:
    success: bool
    session_token: str | None = None
