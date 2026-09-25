from pydantic import BaseModel
from typing import Literal, Optional


class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: Literal["IN", "OUT", "ADJUSTMENT"]
    quantity: int
    note: Optional[str] = None