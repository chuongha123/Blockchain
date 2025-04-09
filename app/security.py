from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.database import get_db
from app.model.user import User, TokenData

# Security configurations
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Debug tokenUrl calculation
auth_token_url = "/auth/token"
print(f"Using token URL: {auth_token_url}")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Custom OAuth2 scheme that can extract token from cookie
class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, token_url: str, auto_error: bool = True):
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": {}})
        super().__init__(flows=flows, scheme_name="Bearer", auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # First try to get the token from the Authorization header
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            # If not in header, try to get from cookies
            access_token = request.cookies.get("access_token")
            if access_token:
                return access_token

            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param


# Use our custom OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearerWithCookie(
    token_url=auth_token_url, auto_error=False
)


def verify_password(plain_password, hashed_password):
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Get the current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_optional_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Get the current user without raising an exception if not authenticated"""
    if token is None:
        print("Token is None, returning None")
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("No username in payload")
            return None
        print(f"Username from token: {username}")
        token_data = TokenData(username=username)
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        return None

    user = db.query(User).filter(User.username == token_data.username).first()
    if user:
        print(f"Found user: {user.username}")
    else:
        print("No user found in database")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Check if the current user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def check_admin_role(current_user: User = Depends(get_current_active_user)):
    """Check if the current user has admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource",
        )
    return current_user
