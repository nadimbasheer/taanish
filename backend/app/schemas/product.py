from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    cost: Decimal
    mrp: Decimal
    selling: Decimal
    stock: int = 0
    min_stock: int = 0

class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True