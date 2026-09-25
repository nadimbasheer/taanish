from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    category = Column(String(100), nullable=True)

    sku = Column(String(100), unique=True, nullable=True, index=True)

    barcode = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )

    cost = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    mrp = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    selling = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    stock = Column(
        Integer,
        nullable=False,
        default=0
    )

    min_stock = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )