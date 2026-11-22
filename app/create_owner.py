
from getpass import getpass

from sqlalchemy import or_

from app.database import Base, engine, SessionLocal
from app.models import User
from app.security import hash_password


def create_owner():
    Base.metadata.create_all(bind=engine)

    print("\n=== CREAR CUENTA DEL DUEÑO ===\n")

    username = input("Nombre de usuario: ").strip().lower()
    email = input("Correo electrónico: ").strip().lower()

    password = getpass("Contraseña (mínimo 8 caracteres): ")
    confirmation = getpass("Confirmar contraseña: ")

    if len(username) < 3:
        print("Error: el usuario debe tener al menos 3 caracteres.")
        return

    if len(password) < 8:
        print("Error: la contraseña debe tener al menos 8 caracteres.")
        return

    if password != confirmation:
        print("Error: las contraseñas no coinciden.")
        return

    if "@" not in email or "." not in email.split("@")[-1]:
        print("Error: el correo electrónico no parece válido.")
        return

    db = SessionLocal()

    try:
        existing = db.query(User).filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

        if existing:
            print("Error: ese usuario o correo ya está registrado.")
            return

        owner = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role="OWNER"
        )

        db.add(owner)
        db.commit()

        print("\n¡Cuenta del dueño creada correctamente!")
        print(f"Usuario: {username}")
        print("Rol: OWNER")

    except Exception as error:
        db.rollback()
        print(f"No se pudo crear la cuenta: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    create_owner()
