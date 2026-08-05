import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health_check():
    """GET /health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_fluidos_propriedades_sucesso():
    """T8.1 — POST /api/v1/fluidos/propriedades (Sucesso 200 OK)"""
    payload = {
        "fluido": "agua_doce",
        "temperatura_c": 20.0,
        "vazao_m3h": 118.5,
        "diametro_mm": 150.0
    }
    response = client.post("/api/v1/fluidos/propriedades", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reynolds" in data
    assert "regime" in data
    assert data["regime"] == "turbulento"
    assert data["reynolds"] > 4000

def test_api_fluidos_propriedades_oleo_diesel():
    """POST /api/v1/fluidos/propriedades com oleo_diesel"""
    payload = {
        "fluido": "oleo_diesel",
        "temperatura_c": 25.0,
        "vazao_m3h": 50.0,
        "diametro_mm": 100.0
    }
    response = client.post("/api/v1/fluidos/propriedades", json=payload)
    assert response.status_code == 200
    assert response.json()["massa_especifica_kgm3"] == 850.0

def test_api_fluidos_propriedades_validacao_422():
    """T8.1 — POST /api/v1/fluidos/propriedades (Erro 422 Unprocessable Entity)"""
    payload = {
        "fluido": "agua_doce",
        "temperatura_c": 20.0,
        "vazao_m3h": -50.0,
        "diametro_mm": 150.0
    }
    response = client.post("/api/v1/fluidos/propriedades", json=payload)
    assert response.status_code == 422
