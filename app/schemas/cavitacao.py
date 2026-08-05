from pydantic import BaseModel, Field
from typing import Optional

class NPSHRequest(BaseModel):
    p_atm_pa: float = Field(default=101325.0, gt=0.0)
    temperatura_c: float = Field(default=20.0)
    z_suc_m: float
    hf_suc_m: float = Field(ge=0.0)
    npshr_m: float = Field(gt=0.0)

class NPSHResponse(BaseModel):
    npsha_m: float
    npshr_m: float
    margem_m: float
    margem_requerida_m: float
    cavitacao_detectada: bool
    status_cavitacao: str
