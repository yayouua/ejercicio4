
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Archivo donde se almacenará la base de datos
DATABASE_URL = "sqlite:///./arriendo_autos.db"

# Crear la conexión con SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Crear las sesiones para consultar y guardar información
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para crear los modelos de la base de datos
Base = declarative_base()


# Administrar las sesiones de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
