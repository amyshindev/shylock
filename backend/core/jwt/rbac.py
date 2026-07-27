from enum import StrEnum


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"


class Permission(StrEnum):
    PLAY_GAME = "play_game"
    READ_RECORDS = "read_records"
    MANAGE_USERS = "manage_users"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.USER: frozenset({Permission.PLAY_GAME, Permission.READ_RECORDS}),
    Role.ADMIN: frozenset(
        {Permission.PLAY_GAME, Permission.READ_RECORDS, Permission.MANAGE_USERS}
    ),
}


def permissions_for(roles: list[str]) -> set[Permission]:
    out: set[Permission] = set()
    for name in roles:
        try:
            role = Role(name)
        except ValueError:
            continue
        out |= ROLE_PERMISSIONS.get(role, frozenset())
    return out
