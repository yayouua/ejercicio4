
from app.database import Base, engine, SessionLocal
from app.models import Vehicle


# Crear las tablas si todavía no existen
Base.metadata.create_all(bind=engine)


# Vehículos de demostración
vehicles = [
    {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "plate": "DEMO-001",
        "daily_price": 35000
    },
    {
        "brand": "Hyundai",
        "model": "Accent",
        "year": 2021,
        "plate": "DEMO-002",
        "daily_price": 28000
    },
    {
        "brand": "Suzuki",
        "model": "Swift",
        "year": 2023,
        "plate": "DEMO-003",
        "daily_price": 25000
    },
    {
        "brand": "Kia",
        "model": "Rio",
        "year": 2022,
        "plate": "DEMO-004",
        "daily_price": 30000
    },
    {
        "brand": "Nissan",
        "model": "Versa",
        "year": 2023,
        "plate": "DEMO-005",
        "daily_price": 32000
    },
    {
        "brand": "Chevrolet",
        "model": "Onix",
        "year": 2022,
        "plate": "DEMO-006",
        "daily_price": 29000
    },
    {
        "brand": "Mazda",
        "model": "Mazda 3",
        "year": 2023,
        "plate": "DEMO-007",
        "daily_price": 40000
    },
    {
        "brand": "Hyundai",
        "model": "Tucson",
        "year": 2022,
        "plate": "DEMO-008",
        "daily_price": 45000
    },
    {
        "brand": "Kia",
        "model": "Sportage",
        "year": 2023,
        "plate": "DEMO-009",
        "daily_price": 45000
    },
    {
        "brand": "Toyota",
        "model": "Yaris",
        "year": 2021,
        "plate": "DEMO-010",
        "daily_price": 27000
    }
]


def seed_vehicles():
    db = SessionLocal()
    inserted = 0

    try:
        for data in vehicles:

            # No repetir vehículos si ejecutamos el archivo otra vez
            existing = (
                db.query(Vehicle)
                .filter(Vehicle.plate == data["plate"])
                .first()
            )

            if existing:
                continue

            vehicle = Vehicle(
                **data,
                status="AVAILABLE"
            )

            db.add(vehicle)
            inserted += 1

        db.commit()

        total = db.query(Vehicle).count()

        print("Proceso de generación finalizado.")
        print(f"Vehículos nuevos registrados: {inserted}")
        print(f"Total de vehículos en la base de datos: {total}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_vehicles()
