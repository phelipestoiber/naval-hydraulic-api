from typing import Any
from fastapi import APIRouter, HTTPException
from app.core.pipeline import executar_pipeline_calculo
from app.db.crud import create_calculo, get_calculo
from app.schemas.erro import ErroCalculo, ErrorResponse

router = APIRouter()

@router.post("/calcular")
def calcular_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Executa o pipeline completo de cálculo hidráulico naval integrando todas as camadas (1 a 6).
    Salva o resultado no banco de dados e retorna o ID único (UUID v4) gerado.
    """
    vazao = payload.get("sistema", {}).get("vazao", 0.0)
    if vazao < 0:
        raise ErroCalculo(codigo="VAZAO_NEGATIVA", mensagem="A vazão do sistema deve ser estritamente não-negativa.", campo="vazao")

    resultado = executar_pipeline_calculo(payload)
    id_calculo = create_calculo(payload, resultado)

    return {
        "id_calculo": id_calculo,
        **resultado
    }

@router.get("/resultado/{id_calculo}")
def obter_resultado_calculo(id_calculo: str) -> dict[str, Any]:
    """
    Recupera um resultado de cálculo hidráulico prévio pelo seu UUID v4.
    """
    item = get_calculo(id_calculo)
    if not item:
        raise HTTPException(
            status_code=404,
            detail={
                "codigo": "RESULTADO_NAO_ENCONTRADO",
                "mensagem": f"Nenhum cálculo hidráulico encontrado para o ID '{id_calculo}'.",
                "campo": "id_calculo"
            }
        )
    return item
