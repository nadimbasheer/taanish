from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ExpenseCreate(BaseModel):
    date: Optional[datetime] = None
    category: str
    description: Optional[str] = None
    amount: Decimal
    payment_method: str = "Cash"
    notes: Optional[str] = None


class ExpenseResponse(ExpenseCreate):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True