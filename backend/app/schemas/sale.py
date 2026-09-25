from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: Decimal


class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    items: list[SaleItemCreate]
    discount: Decimal = 0
    tax: Decimal = 0
    payment_method: str = "Cash"