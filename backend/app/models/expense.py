from sqlalchemy import Column, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(DateTime(timezone=True), server_default=func.now())

    category = Column(String(100), nullable=False)

    description = Column(String(255), nullable=True)

    amount = Column(Numeric(12, 2), nullable=False)

    payment_method = Column(String(30), nullable=False)

    notes = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )