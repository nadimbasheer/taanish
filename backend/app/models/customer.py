from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False
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
        String(255),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="Active"
    )

    notes = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )