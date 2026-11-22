
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import Base, engine, get_db
from app import models
from app.schemas import (
    VehicleCreate,
    VehicleResponse,
    RentalCreate,
    RentalResponse
)


# Crear las tablas de la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Arriendo de Autos",
    description="API para administrar vehículos y sus arriendos",
    version="1.0.0"
)


@app.get("/", tags=["Inicio"])
def inicio():
    return {
        "mensaje": "Bienvenido al Sistema de Arriendo de Autos",
        "estado": "API funcionando correctamente",
        "documentacion": "/docs"
    }


@app.get("/health", tags=["Sistema"])
def health():
    return {
        "status": "ok",
        "mensaje": "El sistema está operativo"
    }


# ------------------------------
# VEHICULOS
# ------------------------------

@app.post(
    "/vehicles",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Vehículos"]
)
def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db)
):
    existing_vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.plate == vehicle.plate)
        .first()
    )

    if existing_vehicle:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un vehículo con esa patente"
        )

    new_vehicle = models.Vehicle(
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        plate=vehicle.plate,
        daily_price=vehicle.daily_price,
        status="AVAILABLE"
    )

    db.add(new_vehicle)

    try:
        db.commit()
        db.refresh(new_vehicle)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar el vehículo"
        )

    return new_vehicle


@app.get(
    "/vehicles",
    response_model=list[VehicleResponse],
    tags=["Vehículos"]
)
def get_vehicles(db: Session = Depends(get_db)):
    return db.query(models.Vehicle).order_by(models.Vehicle.id).all()


@app.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleResponse,
    tags=["Vehículos"]
)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    return vehicle


# ------------------------------
# ARRIENDOS
# ------------------------------

@app.post(
    "/rentals",
    response_model=RentalResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Arriendos"]
)
def create_rental(
    rental: RentalCreate,
    db: Session = Depends(get_db)
):
    # Validar que la fecha de devolución sea posterior
    if rental.end_date <= rental.start_date:
        raise HTTPException(
            status_code=422,
            detail="La fecha de devolución debe ser posterior a la fecha de inicio"
        )

    # Buscar el vehículo
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == rental.vehicle_id
    ).first()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    # Comprobar disponibilidad
    if vehicle.status != "AVAILABLE":
        raise HTTPException(
            status_code=409,
            detail="El vehículo ya se encuentra arrendado"
        )

    # Crear el arriendo
    new_rental = models.Rental(
        vehicle_id=vehicle.id,
        customer_name=rental.customer_name,
        start_date=rental.start_date,
        end_date=rental.end_date,
        status="ACTIVE"
    )

    # Cambiar el estado del vehículo
    vehicle.status = "RENTED"

    db.add(new_rental)

    try:
        db.commit()
        db.refresh(new_rental)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar el arriendo"
        )

    return new_rental


# Consultar el historial de arriendos
@app.get(
    "/rentals",
    response_model=list[RentalResponse],
    tags=["Arriendos"]
)
def get_rentals(db: Session = Depends(get_db)):
    return db.query(models.Rental).order_by(models.Rental.id).all()


# ------------------------------
# DEVOLUCIONES
# ------------------------------

@app.put(
    "/vehicles/{vehicle_id}/return",
    response_model=RentalResponse,
    tags=["Devoluciones"]
)
def return_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    # Buscar el arriendo activo del vehículo
    active_rental = (
        db.query(models.Rental)
        .filter(
            models.Rental.vehicle_id == vehicle_id,
            models.Rental.status == "ACTIVE"
        )
        .order_by(models.Rental.id.desc())
        .first()
    )

    if active_rental is None:
        raise HTTPException(
            status_code=409,
            detail="El vehículo no tiene un arriendo activo"
        )

    # Finalizar el arriendo y liberar el vehículo
    active_rental.status = "COMPLETED"
    vehicle.status = "AVAILABLE"

    try:
        db.commit()
        db.refresh(active_rental)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar la devolución"
        )

    return active_rental
