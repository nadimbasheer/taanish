from pydantic import BaseModel
from typing import Optional


class SettingsUpdate(BaseModel):
    shop_name: str = "Fancy Shop"
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    currency: str = "₹"


class SettingsResponse(SettingsUpdate):
    id: int

    class Config:
        from_attributes = True