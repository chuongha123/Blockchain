from typing import List, Optional
from sqlalchemy.orm import Session
from app.model.farm_data import Farm


class FarmService:
    @staticmethod
    def create_farm(
        db: Session, farm_id: str, name: str, description: Optional[str] = None
    ) -> Farm:
        """Tạo nông trại mới"""
        farm = Farm(id=farm_id, name=name, description=description)
        db.add(farm)
        db.commit()
        db.refresh(farm)
        return farm

    @staticmethod
    def get_farm(db: Session, farm_id: str) -> Optional[Farm]:
        """Lấy thông tin nông trại theo ID"""
        return db.query(Farm).filter(Farm.id == farm_id).first()

    @staticmethod
    def get_farms(db: Session, skip: int = 0, limit: int = 100) -> List[Farm]:
        """Lấy danh sách tất cả nông trại"""
        return db.query(Farm).offset(skip).limit(limit).all()

    @staticmethod
    def update_farm(
        db: Session,
        farm_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Farm]:
        """Cập nhật thông tin nông trại"""
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if farm:
            if name:
                farm.name = name
            if description is not None:
                farm.description = description
            db.commit()
            db.refresh(farm)
        return farm

    @staticmethod
    def delete_farm(db: Session, farm_id: str) -> bool:
        """Xóa nông trại"""
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if farm:
            db.delete(farm)
            db.commit()
            return True
        return False
