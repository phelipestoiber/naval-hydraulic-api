import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_bombas_ponto_operacao_sucesso():
    """T8.3 — POST /api/v1/bombas/ponto-operacao (Sucesso 200 OK)"""
    payload = {
        "curva_hq": [
            {"q_m3h": 0.0, "h_m": 42.0},
            {"q_m3h": 50.0, "h_m": 38.0},
            {"q_m3h": 100.0, "h_m": 28.0},
            {"q_m3h": 150.0, "h_m": 12.0},
            {"q_m3h": 180.0, "h_m": 2.0}
        ],
        "h_geo_m": 3.40,
        "resistencia_sistema_r": 0.0003596
    }
    response = client.post("/api/v1/bombas/ponto-operacao", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Q_op_m3h" in data
    assert "H_op_m" in data
    assert data["Q_op_m3h"] > 0

def test_api_bombas_shut_off_erro_400():
    """T8.3 — POST /api/v1/bombas/ponto-operacao com H_geo > H_shut_off (Erro 400 Bad Request)"""
    payload = {
        "curva_hq": [
            {"q_m3h": 0.0, "h_m": 42.0},
            {"q_m3h": 50.0, "h_m": 38.0},
            {"q_m3h": 100.0, "h_m": 28.0},
            {"q_m3h": 150.0, "h_m": 12.0},
            {"q_m3h": 180.0, "h_m": 2.0}
        ],
        "h_geo_m": 50.0,  # 50 m > H_shut_off (42 m)
        "resistencia_sistema_r": 0.0003596
    }
    response = client.post("/api/v1/bombas/ponto-operacao", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["codigo"] == "SEM_PONTO_OPERACAO_SHUT_OFF"
    assert data["error"]["dados_diagnostico"]["deficit_m"] == 8.0
