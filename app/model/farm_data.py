from typing import Optional

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    String,
    text,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.services.database import Base


class FarmData(BaseModel):
    product_id: Optional[str] = None
    farm_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    water_level: Optional[float] = None
    light_level: Optional[float] = None


class Product(Base):
    __tablename__ = "products"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    is_harvested = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.current_timestamp(),
    )


class Farm(Base):
    __tablename__ = "farms"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.current_timestamp(),
    )

    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship with User
    user = relationship("User", back_populates="farms")


class FarmReport(Base):
    __tablename__ = "farm_reports"

    id = Column(String(255), primary_key=True, index=True)
    farm_id = Column(String(255), nullable=False)
    product_id = Column(String(255), nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    water_level = Column(Float, nullable=False)
    light_level = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.current_timestamp(),
    )
