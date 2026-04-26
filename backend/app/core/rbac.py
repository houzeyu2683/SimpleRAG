from __future__ import annotations
from enum import Enum


class Permission(str, Enum):
    # Document permissions
    document_upload = "document:upload"
    document_delete = "document:delete"
    document_read = "document:read"

    # Collection permissions
    collection_manage = "collection:manage"
    collection_read = "collection:read"

    # Chat permissions
    chat_create = "chat:create"
    chat_read = "chat:read"

    # Admin permissions
    user_manage = "user:manage"
    role_manage = "role:manage"
    system_read = "system:read"


# Role → allowed permissions
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "admin": set(Permission),  # all permissions
    "user": {
        Permission.document_upload,
        Permission.document_delete,
        Permission.document_read,
        Permission.collection_manage,
        Permission.collection_read,
        Permission.chat_create,
        Permission.chat_read,
    },
    "viewer": {
        Permission.document_read,
        Permission.collection_read,
        Permission.chat_read,
    },
}


def has_permission(role_name: str, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role_name, set())
