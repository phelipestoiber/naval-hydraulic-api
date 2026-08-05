import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_motores_dimensionamento_eletrico_sucesso():
    """T8.4 — POST /api/v1/motores/dimensionamento (Sucesso 200 OK — Elétrico)"""
    payload = {
        "vazao_m3h": 118.5,
        "h_op_m": 8.45,
        "eta_bomba": 0.79,
        "eta_motor": 0.92,
        "eta_transmissao": 1.0,
        "tensao_volts": 380.0,
        "fator_potencia": 0.85,
        "tipo_acionador": "eletrico"
    }
    response = client.post("/api/v1/motores/dimensionamento", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "potencia_hidraulica_kw" in data
    assert "potencia_eletrica_kw" in data
    assert "corrente_nominal_a" in data
    assert data["corrente_nominal_a"] == pytest.approx(6.71, rel=0.05)

def test_api_motores_dimensionamento_diesel_sucesso():
    """T8.4 — POST /api/v1/motores/dimensionamento (Sucesso 200 OK — Diesel)"""
    payload = {
        "vazao_m3h": 118.5,
        "h_op_m": 8.45,
        "eta_bomba": 0.79,
        "tipo_acionador": "diesel",
        "sfc_g_kwh": 210.0
    }
    response = client.post("/api/v1/motores/dimensionamento", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "consumo_lh" in data
    assert data["consumo_lh"] > 0
