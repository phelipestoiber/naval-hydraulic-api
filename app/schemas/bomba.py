from pydantic import BaseModel, Field
from typing import List, Optional

class PontoCurvaHQ(BaseModel):
    q_m3h: float = Field(ge=0.0)
    h_m: float = Field(ge=0.0)

class PontoOperacaoRequest(BaseModel):
    curva_hq: List[PontoCurvaHQ] = Field(min_length=3)
    h_geo_m: float = Field(ge=0.0)
    resistencia_sistema_r: float = Field(gt=0.0)

class PontoOperacaoResponse(BaseModel):
    Q_op_m3h: float
    H_op_m: float
    residual_m: float
    iteracoes: int
    convergiu: bool
