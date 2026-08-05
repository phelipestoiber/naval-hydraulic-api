import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_t10_2_persistencia_e_recuperacao(payload_referencia):
    """T10.2 — POST /api/v1/calcular e posterior GET /api/v1/resultado/{id_calculo}"""
    # 1. Calcular
    res_post = client.post("/api/v1/calcular", json=payload_referencia)
    assert res_post.status_code == 200
    data_post = res_post.json()
    id_calculo = data_post["id_calculo"]

    # 2. Recuperar
    res_get = client.get(f"/api/v1/resultado/{id_calculo}")
    assert res_get.status_code == 200
    data_get = res_get.json()

    assert data_get["id_calculo"] == id_calculo
    assert data_get["resultado"]["status"] == "OK"
    assert data_get["resultado"]["resultados_prumo"]["h_geo_m"] == pytest.approx(3.40, rel=0.02)

def test_t10_2_resultado_nao_encontrado():
    """T10.2 — GET /api/v1/resultado/{id_inexistente} -> 404 RESULTADO_NAO_ENCONTRADO"""
    uuid_fake = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/api/v1/resultado/{uuid_fake}")
    assert res.status_code == 404
    data = res.json()
    detail = data.get("detail", {})
    if isinstance(detail, dict):
        assert detail.get("codigo") == "RESULTADO_NAO_ENCONTRADO"
    else:
        assert "RESULTADO_NAO_ENCONTRADO" in str(detail)
