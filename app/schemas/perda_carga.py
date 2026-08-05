from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DarcyWeisbachRequest(BaseModel):
    vazao_m3h: float = Field(gt=0.0, description="Vazão em m³/h")
    diametro_mm: float = Field(gt=0.0, description="Diâmetro interno em mm")
    comprimento_m: float = Field(gt=0.0, description="Comprimento da tubulação em metros")
    rugosidade_mm: float = Field(ge=0.0, default=0.045, description="Rugosidade absoluta em mm")
    fluido: str = Field(default="agua_doce")
    temperatura_c: float = Field(default=20.0)
    metodo_fator_atrito: str = Field(default="churchill")

class DarcyWeisbachResponse(BaseModel):
    hf_m: float
    fator_atrito: float
    reynolds: float
    regime: str
    velocidade_ms: float

class HazenWilliamsRequest(BaseModel):
    vazao_m3h: float = Field(gt=0.0)
    diametro_mm: float = Field(gt=0.0)
    comprimento_m: float = Field(gt=0.0)
    coeficiente_c: float = Field(default=140.0, gt=0.0)
    fluido: str = Field(default="agua_doce")
    temperatura_c: float = Field(default=20.0)

class HazenWilliamsResponse(BaseModel):
    hf_m: float
    metodo_usado: str
    aviso: Optional[str] = None
    codigo_rejeicao: Optional[str] = None

class SingularidadeItem(BaseModel):
    id: str
    quantidade: int = Field(default=1, gt=0)
    K: Optional[float] = Field(default=0.0, ge=0.0)
    Le_sobre_D: Optional[float] = Field(default=0.0, ge=0.0)

class PerdaSingularidadesRequest(BaseModel):
    singularidades: List[SingularidadeItem]
    diametro_mm: float = Field(gt=0.0)
    velocidade_ms: float = Field(ge=0.0)
    fator_atrito: float = Field(default=0.02, gt=0.0)
    metodo: str = Field(default="k")

class PerdaSingularidadesResponse(BaseModel):
    hl_total_m: float
    le_total_m: float
