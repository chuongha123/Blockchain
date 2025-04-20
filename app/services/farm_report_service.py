from typing import Optional, Type

from sqlalchemy.orm import Session

from app.model.farm_data import FarmReport


class FarmReportService:
    @staticmethod
    def create_report(
            db: Session,
            report_id: str,
            farm_id: str,
            product_id: str,
            temperature: float,
            humidity: float,
            water_level: float,
            light_level: float,
    ) -> FarmReport:
        """Create a new farm report"""
        report = FarmReport(
            id=report_id,
            farm_id=farm_id,
            product_id=product_id,
            temperature=temperature,
            humidity=humidity,
            water_level=water_level,
            light_level=light_level,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_report(db: Session, report_id: str) -> Optional[FarmReport]:
        """Get report by ID"""
        return db.query(FarmReport).filter(FarmReport.id == report_id).first()

    @staticmethod
    def get_reports(db: Session, skip: int = 0, limit: int = 100) -> list[Type[FarmReport]]:
        """Get list of reports"""
        return db.query(FarmReport).offset(skip).limit(limit).all()

    @staticmethod
    def get_reports_by_farm(
            db: Session, farm_id: str, skip: int = 0, limit: int = 100
    ) -> list[Type[FarmReport]]:
        """Get list of reports by farm"""
        return (
            db.query(FarmReport)
            .filter(FarmReport.farm_id == farm_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_reports_by_product(
            db: Session, product_id: str, skip: int = 0, limit: int = 100
    ) -> list[Type[FarmReport]]:
        """Get list of reports by product"""
        return (
            db.query(FarmReport)
            .filter(FarmReport.product_id == product_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_reports_by_farm_and_product(
            db: Session, farm_id: str, product_id: str, skip: int = 0, limit: int = 100
    ) -> list[Type[FarmReport]]:
        """Get list of reports by farm and product"""
        return (
            db.query(FarmReport)
            .filter(FarmReport.farm_id == farm_id, FarmReport.product_id == product_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_report(
            db: Session,
            report_id: str,
            temperature: Optional[float] = None,
            humidity: Optional[float] = None,
            water_level: Optional[float] = None,
            light_level: Optional[float] = None,
    ) -> Optional[FarmReport]:
        """Update farm report"""
        report = db.query(FarmReport).filter(FarmReport.id == report_id).first()
        if report:
            if temperature is not None:
                report.temperature = temperature
            if humidity is not None:
                report.humidity = humidity
            if water_level is not None:
                report.water_level = water_level
            if light_level is not None:
                report.light_level = light_level
            db.commit()
            db.refresh(report)
        return report

    @staticmethod
    def delete_report(db: Session, report_id: str) -> bool:
        """Delete farm report"""
        report = db.query(FarmReport).filter(FarmReport.id == report_id).first()
        if report:
            db.delete(report)
            db.commit()
            return True
        return False

    @staticmethod
    def delete_farm_reports(db: Session, farm_id: str) -> int:
        """Delete all reports of a farm and return the number of reports deleted"""
        reports = db.query(FarmReport).filter(FarmReport.farm_id == farm_id).all()
        count = len(reports)
        for report in reports:
            db.delete(report)
        db.commit()
        return count
