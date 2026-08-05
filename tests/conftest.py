import pytest

@pytest.fixture
def payload_referencia():
    """
    Payload de Teste Realista Completo — Sistema de Resfriamento ME Principal.
    Usado para validação dos Golden Values no pipeline completo (v0.9.0 / v1.0.0).
    """
    return {
        "projeto": {
            "nome": "Sistema de Resfriamento — ME Principal",
            "navio": "MV Example",
            "classificadora": "BV",
            "norma": "NR467",
            "revisao": "0"
        },
        "fluido": {
            "tipo": "agua_salgada",
            "nome": "Água do mar",
            "temperatura_C": 32,
            "densidade_kg_m3": 1025,
            "viscosidade_dinamica_Pa_s": 0.001,
            "pressao_vapor_Pa": 4800,
            "modelo_viscosidade": "andrade"
        },
        "sistema": {
            "unidade_vazao": "m3h",
            "vazao": 118.5,
            "pressao_succao_Pa": 101325,
            "pressao_descarga_Pa": 101325,
            "pressao_atm_Pa": 101325,
            "altitude_m": 0,
            "pontos_sistema": {
                "succao":   {"x_m": -12.5, "y_m": 1.2, "z_m": 0.8},
                "bomba":    {"x_m": -11.0, "y_m": 1.2, "z_m": 1.5},
                "descarga": {"x_m":   5.0, "y_m": 1.2, "z_m": 4.2}
            },
            "condicoes_inclinacao": "BV_operacao_e_avaria",
            "sistema_essencial": True,
            "numero_bombas": 2,
            "alimentacoes_independentes": True
        },
        "trechos": [
            {
                "id": "S1",
                "descricao": "Sucção — kingston a bomba",
                "diametro_interno_mm": 150,
                "comprimento_m": 8.5,
                "material": "aco_inox_304",
                "rugosidade_mm": 0.02,
                "perda_equipamento_m": 3.62,
                "metodo_perda": "darcy_weisbach",
                "singularidades": [
                    {"tipo": "valvula_gaveta",   "quantidade": 1},
                    {"tipo": "curva_90_rl",      "quantidade": 2},
                    {"tipo": "valvula_retencao", "quantidade": 1}
                ]
            },
            {
                "id": "D1",
                "descricao": "Descarga — bomba ao resfriador",
                "diametro_interno_mm": 125,
                "comprimento_m": 15.2,
                "material": "aco_inox_304",
                "rugosidade_mm": 0.02,
                "metodo_perda": "darcy_weisbach",
                "singularidades": [
                    {"tipo": "curva_90_rl",         "quantidade": 3},
                    {"tipo": "tee_passagem_direta", "quantidade": 1}
                ]
            }
        ],
        "bomba": {
            "fabricante": "Grundfos",
            "modelo": "NK 100-315",
            "rotacao_rpm": 1450,
            "metodo_margem_npsh": "combinado",
            "curva_hq": [
                {"Q_m3h": 0, "H_m": 42},
                {"Q_m3h": 50, "H_m": 40},
                {"Q_m3h": 118.5, "H_m": 36},
                {"Q_m3h": 150, "H_m": 28},
                {"Q_m3h": 180, "H_m": 18}
            ],
            "curva_npsh": [
                {"Q_m3h": 0, "NPSH_m": 1.5},
                {"Q_m3h": 50, "NPSH_m": 2.0},
                {"Q_m3h": 118.5, "NPSH_m": 3.2},
                {"Q_m3h": 150, "NPSH_m": 4.5},
                {"Q_m3h": 180, "NPSH_m": 6.5}
            ],
            "curva_eta": [
                {"Q_m3h": 0, "eta_pct": 0},
                {"Q_m3h": 50, "eta_pct": 55},
                {"Q_m3h": 118.5, "eta_pct": 79},
                {"Q_m3h": 150, "eta_pct": 75},
                {"Q_m3h": 180, "eta_pct": 60}
            ]
        }
    }
