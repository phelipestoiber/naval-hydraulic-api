import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_t10_1_roundtrip_http_golden_values(payload_referencia):
    """T10.1 — Round-trip HTTP: validação completa dos Golden Values via POST /api/v1/calcular"""
    response = client.post("/api/v1/calcular", json=payload_referencia)
    assert response.status_code == 200

    data = response.json()
    assert "id_calculo" in data
    assert len(data["id_calculo"]) == 36  # UUID v4 string length
    assert data["status"] == "OK"

    prumo = data["resultados_prumo"]
    assert prumo["velocidade_succao_m_s"] == pytest.approx(1.87, rel=0.02)
    assert prumo["velocidade_descarga_m_s"] == pytest.approx(2.69, rel=0.02)
    assert prumo["reynolds_succao"] == pytest.approx(287000.0, rel=0.05)
    assert prumo["h_geo_m"] == pytest.approx(3.40, rel=0.02)
    assert prumo["altura_manometrica_m"] == pytest.approx(8.45, rel=0.05)
    assert prumo["npsh_disponivel_m"] == pytest.approx(4.82, rel=0.05)
    assert prumo["velocidade_especifica_ns"] == pytest.approx(63.7, rel=0.05)
    assert prumo["tipo_bomba"] == "centrifuga_mista"
    assert prumo["motor_selecionado_cv"] == 7.5

def test_t10_3_rejeicao_entradas_invalidas(payload_referencia):
    """T10.3 — Rejeição de entradas inválidas com status e códigos apropriados"""
    # A: Q negativa -> 422 VAZAO_NEGATIVA
    p_vazao_neg = dict(payload_referencia)
    p_vazao_neg["sistema"] = dict(payload_referencia["sistema"])
    p_vazao_neg["sistema"]["vazao"] = -5.0
    res_a = client.post("/api/v1/calcular", json=p_vazao_neg)
    assert res_a.status_code == 422
    assert "VAZAO_NEGATIVA" in res_a.text

    # H: Malha fechada (F1) -> 422 TOPOLOGIA_MALHA_NAO_SUPORTADA
    p_malha = dict(payload_referencia)
    p_malha["trechos"] = [
        {"id": "S1", "id_destino": "D1"},
        {"id": "D1", "id_destino": "S1"}
    ]
    res_h = client.post("/api/v1/calcular", json=p_malha)
    assert res_h.status_code == 422
    assert "TOPOLOGIA_MALHA_NAO_SUPORTADA" in res_h.text

    # I: H_geo > H_shut_off (F3) -> 400 SEM_PONTO_OPERACAO_SHUT_OFF
    p_shutoff = dict(payload_referencia)
    p_shutoff["sistema"] = dict(payload_referencia["sistema"])
    p_shutoff["sistema"]["pontos_sistema"] = {
        "succao":   {"x_m": -12.5, "y_m": 1.2, "z_m": 0.8},
        "bomba":    {"x_m": -11.0, "y_m": 1.2, "z_m": 1.5},
        "descarga": {"x_m":   5.0, "y_m": 1.2, "z_m": 50.0}
    }
    res_i = client.post("/api/v1/calcular", json=p_shutoff)
    assert res_i.status_code in [400, 422]
    assert "SEM_PONTO_OPERACAO_SHUT_OFF" in res_i.text

def test_t10_5_middleware_erro_interno(monkeypatch):
    """T10.5 — Exceção não tratada disparando HTTP 500 ERRO_INTERNO sem stack trace"""
    client_no_raise = TestClient(app, raise_server_exceptions=False)

    import app.api.v1.endpoints.pipeline as pipeline_ep
    def mock_broken_pipeline(payload):
        raise RuntimeError("Unexpected internal crash")

    monkeypatch.setattr(pipeline_ep, "executar_pipeline_calculo", mock_broken_pipeline)

    res = client_no_raise.post("/api/v1/calcular", json={"sistema": {"vazao": 10.0}})
    assert res.status_code == 500
    data = res.json()
    assert data.get("codigo") == "ERRO_INTERNO"
