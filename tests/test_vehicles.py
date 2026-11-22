
from app.models import Vehicle


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def register_customer(client, username="cliente_test"):
    return client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "CustomerPass123!"
        }
    )


def login_customer(client, username="cliente_test"):
    return client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "CustomerPass123!"
        }
    )


def login_owner(client):
    return client.post(
        "/auth/login",
        json={
            "username": "admin_test",
            "password": "OwnerPass123!"
        }
    )


def create_vehicle_in_db(db_session, plate="TEST-001"):
    vehicle = Vehicle(
        brand="Toyota",
        model="Corolla",
        year=2022,
        plate=plate,
        daily_price=35000,
        status="AVAILABLE"
    )

    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)

    return vehicle


def create_vehicle_api(client, plate="API-001"):
    return client.post(
        "/vehicles",
        json={
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2022,
            "plate": plate,
            "daily_price": 35000
        }
    )


def create_rental(client, vehicle_id):
    return client.post(
        "/rentals",
        json={
            "vehicle_id": vehicle_id,
            "start_date": "2026-11-23",
            "end_date": "2026-11-26"
        }
    )


# =====================================================
# CP-01: COMPROBAR ESTADO DEL SISTEMA
# =====================================================

def test_CP_01_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# =====================================================
# CP-02: REGISTRAR CLIENTE
# =====================================================

def test_CP_02_register_customer(client):
    response = register_customer(client)

    assert response.status_code == 201
    assert response.json()["username"] == "cliente_test"
    assert response.json()["role"] == "CUSTOMER"


# =====================================================
# CP-03: IMPEDIR USUARIOS DUPLICADOS
# =====================================================

def test_CP_03_duplicate_customer(client):
    register_customer(client)

    response = register_customer(client)

    assert response.status_code == 409


# =====================================================
# CP-04: RECHAZAR CONTRASEÑA INCORRECTA
# =====================================================

def test_CP_04_wrong_password(client):
    register_customer(client)

    response = client.post(
        "/auth/login",
        json={
            "username": "cliente_test",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


# =====================================================
# CP-05: IMPEDIR ACCESO SIN SESION
# =====================================================

def test_CP_05_owner_without_session(client):
    response = client.get("/dueno")

    assert response.status_code == 401


# =====================================================
# CP-06: IMPEDIR ACCESO DEL CLIENTE AL PANEL DEL DUEÑO
# =====================================================

def test_CP_06_customer_cannot_access_owner(client):
    register_customer(client)
    login_customer(client)

    response = client.get("/dueno")

    assert response.status_code == 403


# =====================================================
# CP-07: PERMITIR ACCESO DEL DUEÑO
# =====================================================

def test_CP_07_owner_access(client, owner):
    login_owner(client)

    response = client.get("/dueno")

    assert response.status_code == 200


# =====================================================
# CP-08: CONSULTAR VEHICULOS
# =====================================================

def test_CP_08_list_vehicles(client, db_session):
    create_vehicle_in_db(db_session)

    response = client.get("/vehicles")

    assert response.status_code == 200
    assert len(response.json()) == 1


# =====================================================
# CP-09: REGISTRAR VEHICULO COMO DUEÑO
# =====================================================

def test_CP_09_create_vehicle(client, owner):
    login_owner(client)

    response = create_vehicle_api(client)

    assert response.status_code == 201
    assert response.json()["status"] == "AVAILABLE"


# =====================================================
# CP-10: IMPEDIR REGISTRO DE VEHICULO POR CLIENTE
# =====================================================

def test_CP_10_customer_cannot_create_vehicle(client):
    register_customer(client)
    login_customer(client)

    response = create_vehicle_api(client)

    assert response.status_code == 403


# =====================================================
# CP-11: IMPEDIR PATENTES DUPLICADAS
# =====================================================

def test_CP_11_duplicate_vehicle_plate(client, owner):
    login_owner(client)

    first = create_vehicle_api(client, "DUP-001")
    second = create_vehicle_api(client, "DUP-001")

    assert first.status_code == 201
    assert second.status_code == 409


# =====================================================
# CP-12: ARRENDAR VEHICULO DISPONIBLE
# =====================================================

def test_CP_12_create_rental(client, db_session):
    vehicle = create_vehicle_in_db(db_session)

    register_customer(client)
    login_customer(client)

    response = create_rental(client, vehicle.id)

    assert response.status_code == 201
    assert response.json()["status"] == "ACTIVE"

    vehicle_response = client.get(
        f"/vehicles/{vehicle.id}"
    )

    assert vehicle_response.json()["status"] == "RENTED"


# =====================================================
# CP-13: IMPEDIR DOBLE ARRIENDO
# =====================================================

def test_CP_13_prevent_double_rental(client, db_session):
    vehicle = create_vehicle_in_db(db_session)

    register_customer(client)
    login_customer(client)

    first = create_rental(client, vehicle.id)
    second = create_rental(client, vehicle.id)

    assert first.status_code == 201
    assert second.status_code == 409


# =====================================================
# CP-14: RECHAZAR FECHAS INVALIDAS
# =====================================================

def test_CP_14_invalid_rental_dates(client, db_session):
    vehicle = create_vehicle_in_db(db_session)

    register_customer(client)
    login_customer(client)

    response = client.post(
        "/rentals",
        json={
            "vehicle_id": vehicle.id,
            "start_date": "2026-11-26",
            "end_date": "2026-11-23"
        }
    )

    assert response.status_code == 422


# =====================================================
# CP-15: CONSULTAR HISTORIAL PERSONAL
# =====================================================

def test_CP_15_customer_personal_history(client, db_session):
    vehicle = create_vehicle_in_db(db_session)

    # Registrar dos clientes
    register_customer(client, "cliente_uno")
    register_customer(client, "cliente_dos")

    # Primer cliente realiza un arriendo
    login_customer(client, "cliente_uno")

    rental = create_rental(client, vehicle.id)

    assert rental.status_code == 201

    # Cambiar a la cuenta del segundo cliente
    client.post("/auth/logout")
    login_customer(client, "cliente_dos")

    response = client.get("/my-rentals")

    assert response.status_code == 200
    assert response.json() == []

    # Volver a la primera cuenta
    client.post("/auth/logout")
    login_customer(client, "cliente_uno")

    response = client.get("/my-rentals")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["customer_name"] == "cliente_uno"


# =====================================================
# CP-16: CONSULTAR HISTORIAL GENERAL COMO DUEÑO
# =====================================================

def test_CP_16_owner_rental_history(client, db_session, owner):
    vehicle = create_vehicle_in_db(db_session)

    register_customer(client)
    login_customer(client)

    create_rental(client, vehicle.id)

    client.post("/auth/logout")
    login_owner(client)

    response = client.get("/rentals")

    assert response.status_code == 200
    assert len(response.json()) == 1


# =====================================================
# CP-17: IMPEDIR HISTORIAL GENERAL AL CLIENTE
# =====================================================

def test_CP_17_customer_cannot_view_all_rentals(client):
    register_customer(client)
    login_customer(client)

    response = client.get("/rentals")

    assert response.status_code == 403


# =====================================================
# CP-18: REGISTRAR DEVOLUCION COMO DUEÑO
# =====================================================

def test_CP_18_return_vehicle(client, db_session, owner):
    vehicle = create_vehicle_in_db(db_session)

    register_customer(client)
    login_customer(client)

    create_rental(client, vehicle.id)

    client.post("/auth/logout")
    login_owner(client)

    response = client.put(
        f"/vehicles/{vehicle.id}/return"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

    vehicle_response = client.get(
        f"/vehicles/{vehicle.id}"
    )

    assert vehicle_response.json()["status"] == "AVAILABLE"


# =====================================================
# CP-19: IMPEDIR DEVOLUCION POR CLIENTE
# =====================================================

def test_CP_19_customer_cannot_return_vehicle(client, db_session):
    vehicle = create_vehicle_in_db(db_session)

    register_customer(client)
    login_customer(client)

    response = client.put(
        f"/vehicles/{vehicle.id}/return"
    )

    assert response.status_code == 403


# =====================================================
# CP-20: CONSULTAR VEHICULO INEXISTENTE
# =====================================================

def test_CP_20_vehicle_not_found(client):
    response = client.get("/vehicles/99999")

    assert response.status_code == 404


# =====================================================
# CP-21: CERRAR SESION
# =====================================================

def test_CP_21_logout(client):
    register_customer(client)
    login_customer(client)

    before_logout = client.get("/auth/me")

    assert before_logout.status_code == 200

    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 200

    after_logout = client.get("/auth/me")

    assert after_logout.status_code == 401
