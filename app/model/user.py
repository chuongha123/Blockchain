from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.services.database import Base
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
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
    link_product = Column(String(255), nullable=True)  # Legacy field
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship with Farm
    farms = relationship("Farm", back_populates="user")


# Pydantic models for request/response validation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class FarmLinkRequest(BaseModel):
    farm_id: str


class FarmResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_harvested: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    link_product: Optional[str] = None
    created_at: datetime
    farms: Optional[List[FarmResponse]] = []
    
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    link_product: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user_role: str


class TokenData(BaseModel):
    username: Optional[str] = None
