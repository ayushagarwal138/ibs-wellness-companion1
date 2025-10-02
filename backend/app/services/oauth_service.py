"""OAuth service for handling Google and GitHub authentication."""

import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session


class OAuthService:
    """Service for handling OAuth authentication with Google and GitHub."""

    def __init__(self):
        self.auth_service = AuthService()

    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and return user info."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v1/userinfo?"
                    f"access_token={token}"
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    async def verify_github_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify GitHub OAuth token and return user info."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"token {token}"}
                response = await client.get(
                    "https://api.github.com/user", headers=headers
                )
                if response.status_code == 200:
                    user_data = response.json()
                    # Get user email if not public
                    if not user_data.get("email"):
                        email_response = await client.get(
                            "https://api.github.com/user/emails", headers=headers
                        )
                        if email_response.status_code == 200:
                            emails = email_response.json()
                            primary_email = next(
                                (email for email in emails if email["primary"]), None
                            )
                            if primary_email:
                                user_data["email"] = primary_email["email"]
                    return user_data
                return None
        except Exception:
            return None

    async def handle_oauth_login(
        self, provider: str, token: str, db: Session
    ) -> Dict[str, Any]:
        """Handle OAuth login/registration."""
        user_info = None

        if provider == "google":
            user_info = await self.verify_google_token(token)
        elif provider == "github":
            user_info = await self.verify_github_token(token)
        else:
            raise ValueError("Unsupported OAuth provider")

        if not user_info:
            raise ValueError("Invalid OAuth token")

        email = user_info.get("email")
        if not email:
            raise ValueError("Email not provided by OAuth provider")

        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            # User exists, generate tokens
            access_token = self.auth_service.create_access_token(
                data={"sub": existing_user.email}
            )
            refresh_token = self.auth_service.create_refresh_token(
                data={"sub": existing_user.email}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": existing_user.id,
                    "email": existing_user.email,
                    "full_name": existing_user.full_name,
                    "is_verified": existing_user.is_verified,
                },
            }
        else:
            # Create new user
            _full_name = user_info.get("name") or user_info.get("login", "")

            # Create user with OAuth provider info
            user_data = {
                "email": email,
                "first_name": (
                    user_info.get("given_name") or user_info.get("name", "").split()[0]
                    if user_info.get("name")
                    else ""
                ),
                "last_name": (
                    user_info.get("family_name")
                    or " ".join(user_info.get("name", "").split()[1:])
                    if user_info.get("name")
                    and len(user_info.get("name", "").split()) > 1
                    else ""
                ),
                "password_hash": None,  # OAuth users don't have passwords
                "is_verified": True,  # OAuth users are pre-verified
                "avatar_url": (user_info.get("picture") or user_info.get("avatar_url")),
            }

            # Set OAuth provider specific fields
            if provider == "google":
                user_data["google_id"] = str(user_info.get("id", ""))
            elif provider == "github":
                user_data["github_id"] = str(user_info.get("id", ""))

            new_user = User(**user_data)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            # Generate tokens
            access_token = self.auth_service.create_access_token(
                data={"sub": new_user.email}
            )
            refresh_token = self.auth_service.create_refresh_token(
                data={"sub": new_user.email}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "is_verified": new_user.is_verified,
                },
            }
