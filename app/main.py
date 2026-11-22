
from fastapi import FastAPI

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
