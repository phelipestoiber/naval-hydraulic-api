import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_darcy_weisbach_sucesso():
    """T8.2 — POST /api/v1/perda-carga/darcy-weisbach (Sucesso 200 OK)"""
    payload = {
        "vazao_m3h": 118.5,
        "diametro_mm": 150.0,
        "comprimento_m": 174.0,
        "rugosidade_mm": 0.045,
        "fluido": "agua_doce",
        "temperatura_c": 20.0,
        "metodo_fator_atrito": "churchill"
    }
    response = client.post("/api/v1/perda-carga/darcy-weisbach", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "hf_m" in data
    assert "fator_atrito" in data
    assert data["hf_m"] > 0

def test_api_hazen_williams_fallback_diesel():
    """T8.2 — POST /api/v1/perda-carga/hazen-williams com óleo diesel -> Fallback 200 OK com aviso"""
    payload = {
        "vazao_m3h": 118.5,
        "diametro_mm": 150.0,
        "comprimento_m": 174.0,
        "coeficiente_c": 140.0,
        "fluido": "oleo_diesel",
        "temperatura_c": 20.0
    }
    response = client.post("/api/v1/perda-carga/hazen-williams", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["metodo_usado"] == "darcy_weisbach"
    assert data["codigo_rejeicao"] == "HW_FLUIDO_INVALIDO"
    assert "Hazen-Williams rejeitada" in data["aviso"]

def test_api_singularidades_sucesso():
    """POST /api/v1/perda-carga/singularidades (Sucesso 200 OK)"""
    payload = {
        "singularidades": [
            {"id": "curva_90", "quantidade": 4, "Le_sobre_D": 7.0}
        ],
        "diametro_mm": 150.0,
        "velocidade_ms": 2.0,
        "fator_atrito": 0.02,
        "metodo": "le"
    }
    response = client.post("/api/v1/perda-carga/singularidades", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "hl_total_m" in data
    assert "le_total_m" in data
