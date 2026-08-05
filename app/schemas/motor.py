from pydantic import BaseModel, Field
from typing import Optional

class DimensionamentoMotorRequest(BaseModel):
    vazao_m3h: float = Field(gt=0.0)
    h_op_m: float = Field(gt=0.0)
    eta_bomba: float = Field(gt=0.0, le=1.0)
    eta_motor: float = Field(default=0.92, gt=0.0, le=1.0)
    eta_transmissao: float = Field(default=1.0, gt=0.0, le=1.0)
    tensao_volts: float = Field(default=380.0, gt=0.0)
    fator_potencia: float = Field(default=0.85, gt=0.0, le=1.0)
    tipo_acionador: str = Field(default="eletrico")
    sfc_g_kwh: float = Field(default=210.0, gt=0.0)

class DimensionamentoMotorResponse(BaseModel):
    potencia_hidraulica_kw: float
    potencia_eixo_kw: float
    potencia_eletrica_kw: float
    corrente_nominal_a: float
    rendimento_global: float
    consumo_lh: Optional[float] = None
