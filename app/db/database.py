import uuid
from typing import Any

# Armazenamento em memória (simulando BD / ORM) para persistência dos cálculos
_CALCULOS_DB: dict[str, dict[str, Any]] = {}

def get_db():
    return _CALCULOS_DB

def reset_db():
    _CALCULOS_DB.clear()
