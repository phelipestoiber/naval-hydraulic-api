import pytest
from app.core.unit_casting import realizar_unit_casting, ErroCalculo

def test_casting_agua_do_mar():
    """T1.1 — Casting: água do mar"""
    payload = {
        "vazao": 118.5,
        "unidade_vazao": "m3h",
        "diametro_mm": 150.0,
        "temperatura_C": 32.0,
        "densidade_kg_m3": 1025.0,
        "viscosidade_dinamica_Pa_s": 0.001,
        "pressao_vapor_Pa": 4800.0,
        "pressao_atm_Pa": 101325.0,
        "comprimento_m": 8.5,
        "rugosidade_mm": 0.02,
        "altitude_m": 0.0,
        "rotacao_rpm": 1450.0
    }

    sistema_si, rastreabilidade = realizar_unit_casting(payload)

    assert sistema_si.Q_m3s == pytest.approx(0.032916666, rel=1e-4)
    assert sistema_si.D_m == pytest.approx(0.150, abs=1e-5)
    assert sistema_si.T_k == pytest.approx(305.15, abs=1e-3)
    assert sistema_si.nu_m2s == pytest.approx(0.001 / 1025.0, rel=1e-4)

    campos_rastreados = {item["campo"]: item for item in rastreabilidade.campos}
    assert "vazao" in campos_rastreados
    assert campos_rastreados["vazao"]["fator"] == "/ 3600"

def test_casting_unidades_alternativas():
    """Testa conversão para l/min e l/s."""
    payload_lmin = {
        "vazao": 600.0,
        "unidade_vazao": "l/min",
        "diametro_mm": 100.0,
        "temperatura_C": 20.0
    }
    si_lmin, _ = realizar_unit_casting(payload_lmin)
    assert si_lmin.Q_m3s == pytest.approx(0.01, abs=1e-6)

    payload_ls = {
        "vazao": 10.0,
        "unidade_vazao": "l/s",
        "diametro_mm": 100.0,
        "temperatura_C": 20.0
    }
    si_ls, _ = realizar_unit_casting(payload_ls)
    assert si_ls.Q_m3s == pytest.approx(0.01, abs=1e-6)

    payload_m3s = {
        "vazao": 0.01,
        "unidade_vazao": "m3s",
        "diametro_mm": 100.0,
        "temperatura_C": 20.0
    }
    si_m3s, _ = realizar_unit_casting(payload_m3s)
    assert si_m3s.Q_m3s == pytest.approx(0.01, abs=1e-6)

def test_sanity_checks_7_casos():
    """T1.2 — Sanity checks (7 casos) com ErrorResponse estruturado"""
    def check_erro(modificacao, codigo_esperado):
        base_payload = {
            "vazao": 118.5,
            "unidade_vazao": "m3h",
            "diametro_mm": 150.0,
            "temperatura_C": 32.0,
            "densidade_kg_m3": 1025.0,
            "viscosidade_dinamica_Pa_s": 0.001,
            "pressao_vapor_Pa": 4800.0,
            "pressao_atm_Pa": 101325.0,
            "comprimento_m": 8.5,
            "rugosidade_mm": 0.02,
            "altitude_m": 0.0,
            "rotacao_rpm": 1450.0
        }
        base_payload.update(modificacao)
        with pytest.raises(ErroCalculo) as exc_info:
            realizar_unit_casting(base_payload)
        assert exc_info.value.codigo == codigo_esperado

    check_erro({"vazao": -5.0}, "VAZAO_NEGATIVA")
    check_erro({"diametro_mm": -10.0}, "DIAMETRO_INVALIDO")
    check_erro({"densidade_kg_m3": 2500.0}, "DENSIDADE_INVALIDA")
    check_erro({"temperatura_C": -10.0}, "TEMPERATURA_FORA_DO_RANGE")
    check_erro({"viscosidade_dinamica_Pa_s": 0.0}, "VISCOSIDADE_INVALIDA")
    check_erro({"pressao_vapor_Pa": -100.0}, "PRESSAO_VAPOR_INVALIDA")
    check_erro({"rugosidade_mm": -0.01}, "RUGOSIDADE_INVALIDA")
    check_erro({"unidade_vazao": "gal/h"}, "UNIDADE_INVALIDA")

def test_deteccao_malha_fechada_f1():
    """T1.10 — Detecção de malha fechada (F1)"""
    trechos_serie = [
        {"id": "S1", "id_destino": "BOMBA"},
        {"id": "D1", "id_destino": "DESCARGA"}
    ]
    payload_serie = {
        "vazao": 100.0, "unidade_vazao": "m3h", "diametro_mm": 100.0,
        "temperatura_C": 20.0, "densidade_kg_m3": 998.0, "viscosidade_dinamica_Pa_s": 0.001,
        "pressao_vapor_Pa": 2340.0, "pressao_atm_Pa": 101325.0, "comprimento_m": 10.0,
        "rugosidade_mm": 0.045, "altitude_m": 0.0, "rotacao_rpm": 1450.0,
        "trechos": trechos_serie
    }
    sistema_si, _ = realizar_unit_casting(payload_serie)
    assert sistema_si is not None

    trechos_ciclo = [
        {"id": "S1", "id_destino": "D1"},
        {"id": "D1", "id_destino": "S1"}
    ]
    payload_ciclo = dict(payload_serie, trechos=trechos_ciclo)
    with pytest.raises(ErroCalculo) as exc_info:
        realizar_unit_casting(payload_ciclo)
    assert exc_info.value.codigo == "TOPOLOGIA_MALHA_NAO_SUPORTADA"
    assert "malha fechada" in exc_info.value.mensagem.lower() or "anel" in exc_info.value.mensagem.lower()
