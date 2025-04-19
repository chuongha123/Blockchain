from typing import List, Optional
from sqlalchemy.orm import Session
from app.model.farm_data import Product


class ProductService:
    @staticmethod
    def create_product(
        db: Session,
        product_id: str,
        name: str,
        description: Optional[str] = None,
        is_harvested: bool = False,
    ) -> Product:
        """Tạo sản phẩm mới"""
        product = Product(
            id=product_id, name=name, description=description, is_harvested=is_harvested
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_product(db: Session, product_id: str) -> Optional[Product]:
        """Lấy thông tin sản phẩm theo ID"""
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """Lấy danh sách tất cả sản phẩm"""
        return db.query(Product).offset(skip).limit(limit).all()

    @staticmethod
    def get_harvested_products(
        db: Session, is_harvested: bool = True, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Lấy danh sách sản phẩm theo trạng thái thu hoạch"""
        return (
            db.query(Product)
            .filter(Product.is_harvested == is_harvested)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_product(
        db: Session,
        product_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_harvested: Optional[bool] = None,
    ) -> Optional[Product]:
        """Cập nhật thông tin sản phẩm"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            if name:
                product.name = name
            if description is not None:
                product.description = description
            if is_harvested is not None:
                product.is_harvested = is_harvested
            db.commit()
            db.refresh(product)
        return product

    @staticmethod
    def update_product_harvest_status(
        db: Session, product_id: str, is_harvested: bool
    ) -> Optional[Product]:
        """Cập nhật trạng thái thu hoạch của sản phẩm"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.is_harvested = is_harvested
            db.commit()
            db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: str) -> bool:
        """Xóa sản phẩm"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            db.delete(product)
            db.commit()
            return True
        return False
