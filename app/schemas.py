
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# USUARIOS
# =====================================================

class UserRegister(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: str = Field(
        min_length=5,
        max_length=100
    )

    password: str = Field(
        min_length=8,
        max_length=100
    )


class UserLogin(BaseModel):

    username: str

    password: str


class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str


# =====================================================
# VEHICULOS
# =====================================================

class VehicleCreate(BaseModel):

    brand: str = Field(min_length=1, max_length=50)

    model: str = Field(min_length=1, max_length=50)

    year: int = Field(ge=1900, le=2100)

    plate: str = Field(min_length=1, max_length=20)

    daily_price: float = Field(gt=0)


class VehicleResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    year: int
    plate: str
    daily_price: float
    status: str


# =====================================================
# ARRIENDOS
# =====================================================

class RentalCreate(BaseModel):

    vehicle_id: int = Field(gt=0)

    customer_name: str = Field(
        min_length=2,
        max_length=100
    )

    start_date: date

    end_date: date


class RentalResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    customer_name: str
    start_date: date
    end_date: date
    status: str
