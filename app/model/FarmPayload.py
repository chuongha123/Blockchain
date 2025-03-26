from typing import Optional

from pydantic import BaseModel


class FarmData(BaseModel):
    product_id: Optional[str] = None
    farm_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    water_level: Optional[float] = None
    light_level: Optional[float] = None
