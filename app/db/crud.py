import uuid
from datetime import datetime, timezone
from typing import Any
from app.db.database import get_db

def create_calculo(payload: dict[str, Any], resultado: dict[str, Any]) -> str:
    """
    Persiste um registro de cálculo hidráulico e retorna o UUID v4 gerado.
    """
    id_calculo = str(uuid.uuid4())
    registro = {
        "id": id_calculo,
        "id_calculo": id_calculo,
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "resultado": resultado
    }
    db = get_db()
    db[id_calculo] = registro
    return id_calculo

def get_calculo(id_calculo: str) -> dict[str, Any] | None:
    """
    Recupera um registro de cálculo por seu UUID. Retorna None se não encontrado.
    """
    db = get_db()
    return db.get(id_calculo)
