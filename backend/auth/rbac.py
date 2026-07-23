"""Re-export RBAC types from core so auth routers can import from auth.rbac."""

from core.rbac import ROLE_PERMISSIONS, Permission, Role, permissions_for

__all__ = ["Role", "Permission", "ROLE_PERMISSIONS", "permissions_for"]
