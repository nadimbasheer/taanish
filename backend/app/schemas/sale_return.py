from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class SaleReturnCreate(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    refund_amount: Decimal
    reason: Optional[str] = None
    refund_method: str = "Cash"


class SaleReturnResponse(SaleReturnCreate):
    id: int

    class Config:
        from_attributes = True