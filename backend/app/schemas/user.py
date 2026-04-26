from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateMeRequest(BaseModel):
    username: str | None = None


class AdminUpdateUserRequest(BaseModel):
    role: str | None = None
    is_active: bool | None = None
