from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class PurchaseCreate(BaseModel):
    product_id: int
    supplier_id: Optional[int] = None
    quantity: int
    cost_price: Decimal
    invoice_number: Optional[str] = None
    note: Optional[str] = None