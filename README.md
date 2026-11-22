# AutoRent - Sistema de Arriendo de Autos

## Descripción

AutoRent es un sistema web básico para administrar el arriendo de vehículos.
Permite registrar clientes, administrar vehículos, realizar arriendos y
gestionar las devoluciones.

El sistema cuenta con dos tipos de usuarios: CLIENTE y DUEÑO.

## Funcionalidades

### Cliente
- Registrarse e iniciar sesión.
- Consultar el catálogo de vehículos.
- Realizar arriendos de vehículos disponibles.
- Consultar su historial personal de arriendos.
- Cerrar sesión.

### Dueño
- Iniciar sesión con una cuenta de dueño.
- Registrar vehículos.
- Consultar el inventario.
- Consultar el historial completo de arriendos.
- Registrar la devolución de vehículos.

## Tecnologías utilizadas

- Python
- FastAPI
- SQLite
- SQLAlchemy
- HTML, CSS y JavaScript
- Pytest

## Instalación

Clonar el repositorio y abrir la carpeta del proyecto.

Crear el entorno virtual:

    python -m venv .venv

Activar el entorno virtual en Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

Instalar las dependencias:

    pip install -r requirements.txt

## Crear una cuenta de dueño

Ejecutar:

    python -m app.create_owner

El programa solicitará nombre de usuario, correo y contraseña.

## Cargar vehículos de demostración

Ejecutar:

    python -m app.seed

Este comando registra vehículos de prueba y evita duplicar las
patentes que ya existan.

## Ejecutar el sistema

En PowerShell, configurar una clave de sesión aleatoria para el entorno local:

    $env:SESSION_SECRET = python -c "import secrets; print(secrets.token_urlsafe(32))"

Iniciar el servidor:

    python -m uvicorn app.main:app --reload

Abrir en el navegador:

    http://127.0.0.1:8000

La documentación interactiva de la API está disponible en:

    http://127.0.0.1:8000/docs

## Ejecutar las pruebas

Con el entorno virtual activado, ejecutar:

    python -m pytest tests/ -v

## Resultado de pruebas

Se ejecutaron 21 casos de prueba automatizados.

- Total de casos: 21
- Aprobados: 21
- Fallidos: 0
- Bloqueados: 0
- Porcentaje de aprobación: 100 %

La evidencia de ejecución se encuentra en:

    docs/evidencias/test.png

## Estructura del proyecto

    ejercicio4/
    ├── app/
    │   ├── main.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── database.py
    │   ├── security.py
    │   ├── create_owner.py
    │   └── seed.py
    ├── docs/
    │   └── evidencias/
    │       └── test.png
    ├── static/
    │   ├── index.html
    │   ├── login.html
    │   ├── cliente.html
    │   └── dueno.html
    ├── tests/
    │   ├── conftest.py
    │   └── test_vehicles.py
    ├── requirements.txt
    └── README.md

## Consideraciones

Este proyecto está preparado como aplicación de demostración local.
Antes de publicarlo en internet se deben configurar correctamente
los secretos de sesión y el uso obligatorio de HTTPS.