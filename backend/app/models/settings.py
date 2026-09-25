from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class ShopSettings(Base):
    __tablename__ = "shop_settings"

    id = Column(Integer, primary_key=True, index=True)

    shop_name = Column(
        String(150),
        nullable=False,
        default="Fancy Shop"
    )

    phone = Column(
        String(30),
        nullable=True
    )

    email = Column(
        String(150),
        nullable=True
    )

    address = Column(
        String(500),
        nullable=True
    )

    currency = Column(
        String(10),
        nullable=False,
        default="₹"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )