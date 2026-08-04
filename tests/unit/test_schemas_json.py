import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "data"

def test_schemas_json_v2_0():
    """T1.8 — Schemas JSON (schema v2.0)"""
    # 1. materiais.json
    with open(DATA_DIR / "materiais.json", "r", encoding="utf-8") as f:
        materiais_data = json.load(f)
    assert materiais_data["versao_schema"] == "2.0"
    mats = {m["id"]: m for m in materiais_data["materiais"]}
    assert "aco_inox_304" in mats
    assert mats["aco_inox_304"]["rugosidade_mm"] == 0.02

    # 2. singularidades_k.json
    with open(DATA_DIR / "singularidades_k.json", "r", encoding="utf-8") as f:
        sing_data = json.load(f)
    assert sing_data["versao_schema"] == "1.0"
    sings = {s["id"]: s for s in sing_data["singularidades"]}
    assert "curva_90_rl" in sings
    assert sings["curva_90_rl"]["K"] == 0.6
    assert "valvula_gaveta" in sings
    assert sings["valvula_gaveta"]["suporta_metodo_A"] is True

    # 3. potencias_abnt.json
    with open(DATA_DIR / "potencias_abnt.json", "r", encoding="utf-8") as f:
        pot_data = json.load(f)
    assert pot_data["versao_schema"] == "2.0"
    assert "eletrico" in pot_data["margens_por_tipo"]
    assert "diesel" in pot_data["margens_por_tipo"]
    assert "gasolina" in pot_data["margens_por_tipo"]

    # 4. classificadoras.json
    with open(DATA_DIR / "classificadoras.json", "r", encoding="utf-8") as f:
        class_data = json.load(f)
    assert class_data["versao_schema"] == "2.0"
    classifs = class_data["classificadoras"]
    assert "BV" in classifs
    assert "LR" in classifs
    assert "ABS" in classifs
    assert "nota_divergencia" in classifs["LR"]
