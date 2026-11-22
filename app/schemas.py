
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


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


class RentalCreate(BaseModel):
    vehicle_id: int = Field(gt=0)
    customer_name: str = Field(min_length=2, max_length=100)
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
