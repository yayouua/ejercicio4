from sqlalchemy import Column, Integer, String, Float

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    plate = Column(String(20), unique=True, index=True, nullable=False)
    daily_price = Column(Float, nullable=False)

    # AVAILABLE = disponible
    # RENTED = arrendado
    status = Column(
        String(20),
        nullable=False,
        default="AVAILABLE"
    )
