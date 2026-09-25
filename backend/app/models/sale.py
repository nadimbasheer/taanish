from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(
        String(100),
        unique=True,
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True
    )

    subtotal = Column(
        Numeric(12, 2),
        nullable=False
    )

    discount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    tax = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    total = Column(
        Numeric(12, 2),
        nullable=False
    )

    payment_method = Column(
        String(30),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="Completed"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)

    sale_id = Column(
        Integer,
        ForeignKey("sales.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    price = Column(
        Numeric(10, 2),
        nullable=False
    )

    cost = Column(
        Numeric(10, 2),
        nullable=False
    )

    total = Column(
        Numeric(12, 2),
        nullable=False
    )