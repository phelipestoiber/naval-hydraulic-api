import uuid
import pytest
from app.db import crud
from app.db.database import reset_db

def test_db_crud_operacoes(payload_referencia):
    """T9.4 — Banco de dados: criação, UUID v4 e consulta por ID"""
    reset_db()

    resultado_mock = {"status": "OK", "altura_manometrica_m": 8.45}
    id_calculo = crud.create_calculo(payload_referencia, resultado_mock)

    # Verificar que é um UUID v4 válido
    val_uuid = uuid.UUID(id_calculo, version=4)
    assert str(val_uuid) == id_calculo

    # Recuperar cálculo existente
    reg = crud.get_calculo(id_calculo)
    assert reg is not None
    assert reg["id"] == id_calculo
    assert reg["resultado"]["status"] == "OK"

    # Buscar UUID inexistente -> None
    assert crud.get_calculo("00000000-0000-0000-0000-000000000000") is None
