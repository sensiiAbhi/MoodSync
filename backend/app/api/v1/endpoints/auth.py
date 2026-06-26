"""Auth API Router"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, UserProfile, RefreshToken
from app.schemas.auth import (
    RegisterRequest, LoginRequest, LoginResponse,
    UserResponse, UpdateProfileRequest
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, hash_refresh_token
)
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        is_verified=True,  # Skip email verification in dev
    )
    db.add(user)
    await db.flush()  # get user.id

    # Create profile
    profile = UserProfile(user_id=user.id, gdpr_consent=True, gdpr_consent_at=datetime.now(timezone.utc))
    db.add(profile)

    await db.commit()
    await db.refresh(user)

    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "message": "Account created successfully. Welcome to MoodSync!",
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    # Create tokens
    access_token = create_access_token(str(user.id), user.email)
    raw_refresh, hashed_refresh = create_refresh_token()

    # Store refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh,
        ip_address=request.client.host if request.client else None,
        expires_at=expires_at,
    )
    db.add(db_token)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    # Set HttpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    # Get profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()

    return LoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            is_verified=user.is_verified,
            onboarding_completed=profile.onboarding_completed if profile else False,
        ),
    )


@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    token_hash = hash_refresh_token(raw_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,  # noqa
        )
    )
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Rotate: revoke old, issue new
    db_token.is_revoked = True

    # Get user
    result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token(str(user.id), user.email)
    new_raw, new_hashed = create_refresh_token()

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=new_hashed,
        ip_address=request.client.host if request.client else None,
        expires_at=expires_at,
    )
    db.add(new_db_token)
    await db.commit()

    response.set_cookie(
        key="refresh_token",
        value=new_raw,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {
        "access_token": new_access,
        "token_type": "Bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified,
        onboarding_completed=profile.onboarding_completed if profile else False,
    )


@router.patch("/me")
async def update_me(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()

    if profile:
        if payload.age_range:
            profile.age_range = payload.age_range
        if payload.occupation:
            profile.occupation = payload.occupation
        if payload.timezone:
            profile.timezone = payload.timezone

    await db.commit()
    return {"message": "Profile updated"}


@router.post("/onboarding/complete")
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile:
        profile.onboarding_completed = True
        await db.commit()
    return {"message": "Onboarding completed"}
