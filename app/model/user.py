from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class User(Base):
    """SQLAlchemy User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(100), default="user")  # Role can be 'admin' or 'user'
    link_product = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# Pydantic models for request/response validation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    link_product: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None
    is_active: bool = None
    role: str = None
    link_product: str = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
