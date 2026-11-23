
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey
)

from app.database import Base


# =====================================================
# USUARIOS
# =====================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    # CUSTOMER = cliente
    # OWNER = dueño
    role = Column(
        String(20),
        nullable=False,
        default="CUSTOMER"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# =====================================================
# VEHICULOS
# =====================================================

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    brand = Column(String(50), nullable=False)

    model = Column(String(50), nullable=False)

    year = Column(Integer, nullable=False)

    plate = Column(
        String(20),
        unique=True,
        index=True,
        nullable=False
    )

    daily_price = Column(Float, nullable=False)

    # AVAILABLE = disponible
    # RENTED = arrendado
    status = Column(
        String(20),
        nullable=False,
        default="AVAILABLE"
    )


# =====================================================
# ARRIENDOS
# =====================================================

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    customer_name = Column(
        String(100),
        nullable=False
    )

    start_date = Column(Date, nullable=False)

    end_date = Column(Date, nullable=False)

    # ACTIVE = arriendo vigente
    # COMPLETED = vehículo devuelto
    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )
