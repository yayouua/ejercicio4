
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    plate = Column(String(20), unique=True, index=True, nullable=False)
    daily_price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="AVAILABLE")


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    customer_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # ACTIVE = arriendo vigente
    # COMPLETED = vehículo devuelto
    status = Column(String(20), nullable=False, default="ACTIVE")
