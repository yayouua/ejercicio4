import os

from sqlalchemy import or_

from app.database import Base, engine, SessionLocal
from app.models import User
from app.security import hash_password
from app.seed import seed_vehicles


def bootstrap_demo():
    # Crear las tablas de la base de datos
    Base.metadata.create_all(bind=engine)

    # Datos de la cuenta de demostración
    username = os.getenv(
        "DEMO_OWNER_USERNAME",
        "dueno_demo"
    ).strip().lower()

    email = os.getenv(
        "DEMO_OWNER_EMAIL",
        "dueno@autorrent.demo"
    ).strip().lower()

    password = os.getenv("DEMO_OWNER_PASSWORD", "")

    if len(password) < 8:
        raise RuntimeError(
            "Configura DEMO_OWNER_PASSWORD en Render "
            "con al menos 8 caracteres."
        )

    db = SessionLocal()

    try:
        owner = db.query(User).filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

        if owner is None:
            owner = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role="OWNER"
            )

            db.add(owner)
            db.commit()

            print("Cuenta de dueño de demostración creada.")

        elif owner.role != "OWNER":
            raise RuntimeError(
                "La cuenta de demostración no tiene rol OWNER."
            )

        else:
            print("Cuenta de dueño disponible.")

    finally:
        db.close()

    # Registrar vehículos de demostración sin duplicarlos
    seed_vehicles()


if __name__ == "__main__":
    bootstrap_demo()