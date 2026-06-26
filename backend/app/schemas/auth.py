"""Pydantic Schemas — Auth"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import uuid


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be 3-50 characters")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, _ and -")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_verified: bool
    onboarding_completed: bool = False

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    age_range: Optional[str] = None
    occupation: Optional[str] = None
    timezone: Optional[str] = None
