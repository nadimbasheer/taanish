from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=True
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    cost_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    total = Column(
        Numeric(12, 2),
        nullable=False
    )

    invoice_number = Column(
        String(100),
        nullable=True
    )

    note = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )