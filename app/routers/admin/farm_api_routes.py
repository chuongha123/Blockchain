from types import NoneType

from fastapi import APIRouter
from pydantic import BaseModel

from app.generate_qr import GenerateQRService

router = APIRouter(prefix="/farms", tags=["farm_api"])
generate_qr_service = GenerateQRService()


class FarmHarvest(BaseModel):
    is_harvest: bool


@router.post("/{farm_id}/harvest", response_model=str)
async def farm_harvest(farm_id: str, body: FarmHarvest):
    qr_url = ''
    if body.is_harvest:
        qr_url = generate_qr_service.generate_qr_code(farm_id, body)

    return qr_url
