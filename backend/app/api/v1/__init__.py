from fastapi import APIRouter
from app.api.v1 import auth, users, admin, collections, documents, search, chat

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(collections.router, prefix="/collections", tags=["collections"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
