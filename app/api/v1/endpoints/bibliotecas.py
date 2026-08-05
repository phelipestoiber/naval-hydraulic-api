import json
from pathlib import Path
from typing import Any
from fastapi import APIRouter

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def _find_data_file(filename: str) -> Path:
    candidates = [
        BASE_DIR / "app" / "data" / filename,
        BASE_DIR / "data" / filename,
        Path.cwd() / "app" / "data" / filename,
        Path.cwd() / "data" / filename,
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]

@router.get("/materiais")
def listar_materiais() -> list[dict[str, Any]]:
    """
    Retorna a biblioteca completa de materiais de tubulação com suas respectivas rugosidades absolutas em mm.
    """
    path_materiais = _find_data_file("materiais.json")
    if path_materiais.exists():
        with open(path_materiais, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("materiais", data)

    return [
        {"id": "aco_comercial", "nome": "Aço comercial limpo", "rugosidade_mm": 0.045},
        {"id": "aco_inox_304", "nome": "Aço inoxidável 304", "rugosidade_mm": 0.020},
        {"id": "ferro_fundido", "nome": "Ferro fundido", "rugosidade_mm": 0.260},
        {"id": "pvc", "nome": "PVC / Plástico", "rugosidade_mm": 0.0015},
        {"id": "cobre", "nome": "Cobre / Latão", "rugosidade_mm": 0.0015},
        {"id": "aco_galvanizado", "nome": "Aço galvanizado", "rugosidade_mm": 0.150},
        {"id": "cuproniquel", "nome": "Cuproníquel (Cu-Ni)", "rugosidade_mm": 0.025},
        {"id": "composite_grp", "nome": "GRP / Fiberglass", "rugosidade_mm": 0.010}
    ]

@router.get("/singularidades/biblioteca")
def listar_singularidades() -> dict[str, Any]:
    """
    Retorna a biblioteca padronizada de coeficientes de perda de carga localizada K e Le/D.
    """
    path_sings = _find_data_file("singularidades_k.json")
    if path_sings.exists():
        with open(path_sings, "r", encoding="utf-8") as f:
            data = json.load(f)
            sings = data.get("singularidades", [])
            if isinstance(sings, list):
                return {item["id"]: item for item in sings}
            return data

    return {
        "curva_90_rl": {"nome": "Curva 90° Raio Longo", "K": 0.6, "Le_sobre_D": 16},
        "valvula_gaveta": {"nome": "Válvula Gaveta Aberta", "K": 0.15, "Le_sobre_D": 7, "suporta_metodo_A": True},
        "valvula_retencao": {"nome": "Válvula de Retenção", "K": 2.5, "Le_sobre_D": 100},
        "tee_passagem_direta": {"nome": "Tê de Passagem Direta", "K": 0.45, "Le_sobre_D": 20}
    }
