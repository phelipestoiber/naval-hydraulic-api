from typing import Any
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    campo: str | None = None
    mensagem: str
    codigo: str

class ErrorResponse(BaseModel):
    status: str = "ERRO"
    erros: list[ErrorDetail]
    request_id: str | None = None

class ErroCalculo(Exception):
    """Exceção customizada para erros de cálculo e limites de escopo."""
    def __init__(self, codigo: str, mensagem: str, dados_diagnostico: dict[str, Any] | None = None, campo: str | None = None):
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.dados_diagnostico = dados_diagnostico or {}
        self.campo = campo

    def to_error_detail(self) -> ErrorDetail:
        return ErrorDetail(
            campo=self.campo,
            mensagem=self.mensagem,
            codigo=self.codigo
        )
