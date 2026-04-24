"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Initialize password hashing with multiple fallback options
# Priority: passlib bcrypt > direct bcrypt > SHA256 with salt
pwd_context = None
BCRYPT_AVAILABLE = False
DIRECT_BCRYPT_AVAILABLE = False

# Try passlib bcrypt first
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test if passlib bcrypt is working
    test_hash = pwd_context.hash("test")
    pwd_context.verify("test", test_hash)
    BCRYPT_AVAILABLE = True
    print("✅ Using passlib bcrypt for password hashing")
except Exception as e:
    print(f"⚠️  passlib bcrypt initialization failed: {e}")

    # Try direct bcrypt as fallback
    try:
        import bcrypt

        # Test direct bcrypt functionality
        test_password = b"test"
        test_hash = bcrypt.hashpw(test_password, bcrypt.gensalt())
        bcrypt.checkpw(test_password, test_hash)
        DIRECT_BCRYPT_AVAILABLE = True
        print("✅ Using direct bcrypt for password hashing")
    except Exception as bcrypt_error:
        print(f"⚠️  Direct bcrypt also failed: {bcrypt_error}")
        print("✅ Falling back to SHA256 with salt")

    pwd_context = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: The data to encode in the token

    Returns:
        The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token to verify

    Returns:
        The decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    if BCRYPT_AVAILABLE:
        # Use passlib bcrypt
        # Ensure password doesn't exceed bcrypt's 72-byte limit
        if len(password.encode("utf-8")) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    elif DIRECT_BCRYPT_AVAILABLE:
        # Use direct bcrypt
        import bcrypt

        # Ensure password doesn't exceed bcrypt's 72-byte limit
        if len(password.encode("utf-8")) > 72:
            password = password[:72]
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")
    else:
        # Fallback to SHA256 with salt
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"sha256${salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    try:
        if BCRYPT_AVAILABLE and not hashed_password.startswith("sha256$"):
            # Use passlib bcrypt
            # Ensure password doesn't exceed bcrypt's 72-byte limit
            if len(plain_password.encode("utf-8")) > 72:
                plain_password = plain_password[:72]
            return pwd_context.verify(plain_password, hashed_password)
        elif DIRECT_BCRYPT_AVAILABLE and not hashed_password.startswith("sha256$"):
            # Use direct bcrypt
            import bcrypt

            # Ensure password doesn't exceed bcrypt's 72-byte limit
            if len(plain_password.encode("utf-8")) > 72:
                plain_password = plain_password[:72]
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        elif hashed_password.startswith("sha256$"):
            # Handle SHA256 fallback
            parts = hashed_password.split("$")
            if len(parts) != 3:
                return False
            salt = parts[1]
            stored_hash = parts[2]
            password_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
            return password_hash == stored_hash
        else:
            return False
    except Exception:
        return False


def generate_password_reset_token() -> str:
    """
    Generate a secure random token for password reset.

    Returns:
        A secure random token
    """
    return secrets.token_urlsafe(32)


def generate_email_verification_token() -> str:
    """
    Generate a secure random token for email verification.

    Returns:
        A secure random token
    """
    return secrets.token_urlsafe(32)


def create_password_reset_token(email: str) -> str:
    """
    Create a JWT token for password reset.

    Args:
        email: The user's email address

    Returns:
        The encoded JWT token for password reset
    """
    delta = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email.

    Args:
        token: The password reset token

    Returns:
        The email address if token is valid, None otherwise
    """
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if decoded_token.get("type") != "password_reset":
            return None
        return decoded_token.get("sub")
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """
    Create a JWT token for email verification.

    Args:
        email: The user's email address

    Returns:
        The encoded JWT token for email verification
    """
    delta = timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "email_verification"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify an email verification token and return the email.

    Args:
        token: The email verification token

    Returns:
        The email address if token is valid, None otherwise
    """
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if decoded_token.get("type") != "email_verification":
            return None
        return decoded_token.get("sub")
    except JWTError:
        return None
