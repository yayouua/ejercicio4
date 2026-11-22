
import os
import re

from pathlib import Path

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Request
)

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import Base, engine, get_db
from app import models

from app.schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    VehicleCreate,
    VehicleResponse,
    RentalCreate,
    RentalResponse
)

from app.security import hash_password, verify_password


# =====================================================
# CONFIGURACION GENERAL
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Crear las tablas de la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AutoRent - Sistema de Arriendo de Autos",
    description="Sistema de administración y arriendo de vehículos",
    version="1.0.0"
)

# Configuración de sesiones
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SESSION_SECRET",
        "autorrent-local-development-secret-change-before-deployment"
    ),
    same_site="lax",
    https_only=False,
    max_age=28800
)

# Archivos estáticos
app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


# =====================================================
# AUTENTICACION Y PERMISOS
# =====================================================

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Debes iniciar sesión."
        )

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        request.session.clear()

        raise HTTPException(
            status_code=401,
            detail="La sesión no es válida."
        )

    return user


def require_owner(
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "OWNER":
        raise HTTPException(
            status_code=403,
            detail="Esta función es exclusiva del dueño."
        )

    return current_user


def require_customer(
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=403,
            detail="Esta función es exclusiva de los clientes."
        )

    return current_user


# =====================================================
# PAGINAS WEB
# =====================================================

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/cliente", include_in_schema=False)
def customer_page(
    current_user: models.User = Depends(require_customer)
):
    return FileResponse(STATIC_DIR / "cliente.html")


@app.get("/dueno", include_in_schema=False)
def owner_page(
    current_user: models.User = Depends(require_owner)
):
    return FileResponse(STATIC_DIR / "dueno.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard(
    current_user: models.User = Depends(require_owner)
):
    return FileResponse(STATIC_DIR / "dueno.html")


# =====================================================
# REGISTRO DE CLIENTES
# =====================================================

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticación"]
)
def register_customer(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    username = user_data.username.strip().lower()
    email = user_data.email.strip().lower()

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", username):
        raise HTTPException(
            status_code=422,
            detail="El nombre de usuario contiene caracteres no permitidos."
        )

    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email
    ):
        raise HTTPException(
            status_code=422,
            detail="El correo electrónico no es válido."
        )

    existing_user = db.query(models.User).filter(
        (models.User.username == username) |
        (models.User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="El usuario o correo electrónico ya está registrado."
        )

    new_user = models.User(
        username=username,
        email=email,
        password_hash=hash_password(user_data.password),
        role="CUSTOMER"
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar la cuenta."
        )

    return new_user


# =====================================================
# INICIO DE SESION
# =====================================================

@app.post(
    "/auth/login",
    tags=["Autenticación"]
)
def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    username = credentials.username.strip().lower()

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if user is None or not verify_password(
        credentials.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos."
        )

    request.session.clear()
    request.session["user_id"] = user.id

    return {
        "message": "Inicio de sesión correcto.",
        "username": user.username,
        "role": user.role
    }


# =====================================================
# CERRAR SESION
# =====================================================

@app.post(
    "/auth/logout",
    tags=["Autenticación"]
)
def logout(request: Request):
    request.session.clear()

    return {
        "message": "Sesión cerrada correctamente."
    }


# =====================================================
# USUARIO ACTUAL
# =====================================================

@app.get(
    "/auth/me",
    response_model=UserResponse,
    tags=["Autenticación"]
)
def current_account(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# =====================================================
# ESTADO DEL SISTEMA
# =====================================================

@app.get("/health", tags=["Sistema"])
def health():
    return {
        "status": "ok",
        "mensaje": "El sistema está operativo"
    }


# =====================================================
# VEHICULOS
# =====================================================

# Solo el dueño puede registrar vehículos
@app.post(
    "/vehicles",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Vehículos"]
)
def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_owner)
):
    existing_vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.plate == vehicle.plate
    ).first()

    if existing_vehicle:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un vehículo con esa patente."
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
            detail="No se pudo registrar el vehículo."
        )

    return new_vehicle


# Consultar vehículos del catálogo
@app.get(
    "/vehicles",
    response_model=list[VehicleResponse],
    tags=["Vehículos"]
)
def get_vehicles(
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Vehicle)
        .order_by(models.Vehicle.id)
        .all()
    )


# Consultar un vehículo por ID
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
            detail="Vehículo no encontrado."
        )

    return vehicle


# =====================================================
# ARRIENDOS
# =====================================================

# Registrar arriendo: solo clientes
@app.post(
    "/rentals",
    response_model=RentalResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Arriendos"]
)
def create_rental(
    rental: RentalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_customer)
):
    if rental.end_date <= rental.start_date:
        raise HTTPException(
            status_code=422,
            detail="La fecha de devolución debe ser posterior a la fecha de inicio."
        )

    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == rental.vehicle_id
    ).first()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado."
        )

    if vehicle.status != "AVAILABLE":
        raise HTTPException(
            status_code=409,
            detail="El vehículo ya se encuentra arrendado."
        )

    new_rental = models.Rental(
        vehicle_id=vehicle.id,
        customer_name=current_user.username,
        start_date=rental.start_date,
        end_date=rental.end_date,
        status="ACTIVE"
    )

    vehicle.status = "RENTED"
    db.add(new_rental)

    try:
        db.commit()
        db.refresh(new_rental)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar el arriendo."
        )

    return new_rental


# Historial completo: solo dueño
@app.get(
    "/rentals",
    response_model=list[RentalResponse],
    tags=["Arriendos"]
)
def get_rentals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_owner)
):
    return (
        db.query(models.Rental)
        .order_by(models.Rental.id.desc())
        .all()
    )


# =====================================================
# HISTORIAL PERSONAL DEL CLIENTE
# =====================================================

@app.get(
    "/my-rentals",
    response_model=list[RentalResponse],
    tags=["Arriendos"]
)
def get_my_rentals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_customer)
):
    return (
        db.query(models.Rental)
        .filter(
            models.Rental.customer_name == current_user.username
        )
        .order_by(models.Rental.id.desc())
        .all()
    )


# =====================================================
# DEVOLUCIONES
# =====================================================

# Solo el dueño puede registrar devoluciones
@app.put(
    "/vehicles/{vehicle_id}/return",
    response_model=RentalResponse,
    tags=["Devoluciones"]
)
def return_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_owner)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado."
        )

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
            detail="El vehículo no tiene un arriendo activo."
        )

    active_rental.status = "COMPLETED"
    vehicle.status = "AVAILABLE"

    try:
        db.commit()
        db.refresh(active_rental)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar la devolución."
        )

    return active_rental
