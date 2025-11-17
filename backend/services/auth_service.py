"""
Authentication Service
JWT-based authentication with OAuth support (Google, GitHub)
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenData(BaseModel):
    """Token payload data"""

    user_id: int
    email: str
    username: str
    exp: datetime


class AuthService:
    """Authentication service for user management"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash

        Args:
            plain_password: Plain text password to check
            hashed_password: Stored hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token

        Args:
            data: Data to encode in token (user_id, email, etc.)
            expires_delta: Token expiration time (default 30 minutes)

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Create JWT refresh token

        Args:
            data: Data to encode in token

        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and verify JWT token

        Args:
            token: JWT token to decode

        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"JWT decode error: {e}")
            return None

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
        """
        Verify token and check type

        Args:
            token: JWT token
            token_type: Expected token type (access/refresh)

        Returns:
            Token payload if valid, None otherwise
        """
        payload = AuthService.decode_token(token)
        if not payload:
            return None

        if payload.get("type") != token_type:
            logger.warning(
                f"Invalid token type: expected {token_type}, got {payload.get('type')}"
            )
            return None

        return payload

    @staticmethod
    def create_token_pair(user_data: dict) -> dict:
        """
        Create access and refresh token pair

        Args:
            user_data: User data to encode (user_id, email, username)

        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = AuthService.create_access_token(user_data)
        refresh_token = AuthService.create_refresh_token(user_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[dict]:
        """
        Generate new access token from refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token pair or None if refresh token invalid
        """
        payload = AuthService.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return None

        # Create new token pair
        user_data = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
        }

        return AuthService.create_token_pair(user_data)


class OAuthService:
    """OAuth authentication service for social login"""

    @staticmethod
    def verify_google_token(token: str) -> Optional[dict]:
        """
        Verify Google OAuth token

        Args:
            token: Google OAuth token

        Returns:
            User data from Google or None if invalid
        """
        try:
            from google.auth.transport import requests
            from google.oauth2 import id_token

            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID")
            )

            # Extract user info
            return {
                "email": idinfo.get("email"),
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture"),
                "provider": "google",
                "provider_id": idinfo.get("sub"),
            }
        except Exception as e:
            logger.error(f"Google token verification failed: {e}")
            return None

    @staticmethod
    def verify_github_token(token: str) -> Optional[dict]:
        """
        Verify GitHub OAuth token

        Args:
            token: GitHub OAuth token

        Returns:
            User data from GitHub or None if invalid
        """
        try:
            import requests

            # Get user info from GitHub
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers)

            if response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code}")
                return None

            user_data = response.json()

            # Get primary email
            email_response = requests.get(
                "https://api.github.com/user/emails", headers=headers
            )
            emails = email_response.json()
            primary_email = next(
                (e["email"] for e in emails if e["primary"]), user_data.get("email")
            )

            return {
                "email": primary_email,
                "name": user_data.get("name") or user_data.get("login"),
                "username": user_data.get("login"),
                "picture": user_data.get("avatar_url"),
                "provider": "github",
                "provider_id": str(user_data.get("id")),
            }
        except Exception as e:
            logger.error(f"GitHub token verification failed: {e}")
            return None


class RateLimiter:
    """Simple rate limiter for authentication attempts"""

    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        """
        Initialize rate limiter

        Args:
            max_attempts: Maximum attempts allowed
            window_minutes: Time window in minutes
        """
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts = {}  # {identifier: [(timestamp, success), ...]}

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if identifier is allowed to make request

        Args:
            identifier: User identifier (email, IP, etc.)

        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)

        # Clean old attempts
        if identifier in self.attempts:
            self.attempts[identifier] = [
                (ts, success)
                for ts, success in self.attempts[identifier]
                if ts > window_start
            ]

            # Count failed attempts in window
            failed_attempts = sum(
                1 for ts, success in self.attempts[identifier] if not success
            )

            if failed_attempts >= self.max_attempts:
                logger.warning(
                    f"Rate limit exceeded for {identifier}: {failed_attempts} failed attempts"
                )
                return False

        return True

    def record_attempt(self, identifier: str, success: bool):
        """
        Record authentication attempt

        Args:
            identifier: User identifier
            success: Whether attempt was successful
        """
        now = datetime.utcnow()

        if identifier not in self.attempts:
            self.attempts[identifier] = []

        self.attempts[identifier].append((now, success))

        # Keep only last 100 attempts per identifier
        self.attempts[identifier] = self.attempts[identifier][-100:]


# Global rate limiter instance
auth_rate_limiter = RateLimiter()


def get_auth_service() -> AuthService:
    """Get authentication service instance"""
    return AuthService()


def get_oauth_service() -> OAuthService:
    """Get OAuth service instance"""
    return OAuthService()
