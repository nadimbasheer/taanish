from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class SaleReturn(Base):
    __tablename__ = "sale_returns"

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

    refund_amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    reason = Column(
        String(255),
        nullable=True
    )

    refund_method = Column(
        String(30),
        nullable=False,
        default="Cash"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )