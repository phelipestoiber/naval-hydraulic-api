import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_cavitacao_npsh_sucesso():
    """T8.4 — POST /api/v1/cavitacao/npsh (Sucesso 200 OK)"""
    payload = {
        "p_atm_pa": 101325.0,
        "temperatura_c": 20.0,
        "z_suc_m": 3.0,
        "hf_suc_m": 1.5,
        "npshr_m": 3.2
    }
    response = client.post("/api/v1/cavitacao/npsh", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "npsha_m" in data
    assert "margem_m" in data
    assert data["status_cavitacao"] == "OK"
