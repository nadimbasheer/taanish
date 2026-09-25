from pydantic import BaseModel
from typing import Optional


class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: str = "Active"
    notes: Optional[str] = None


class CustomerResponse(CustomerCreate):
    id: int

    class Config:
        from_attributes = True