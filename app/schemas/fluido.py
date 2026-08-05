from pydantic import BaseModel, Field

class PropriedadesFluidoRequest(BaseModel):
    fluido: str = Field(default="agua_doce", description="Nome/Identificador do fluido")
    temperatura_c: float = Field(default=20.0, ge=0.0, le=300.0, description="Temperatura em °C")
    vazao_m3h: float = Field(gt=0.0, description="Vazão em m³/h")
    diametro_mm: float = Field(gt=0.0, description="Diâmetro em mm")

class PropriedadesFluidoResponse(BaseModel):
    fluido: str
    temperatura_c: float
    massa_especifica_kgm3: float
    viscosidade_dinamica_pas: float
    viscosidade_cinematica_m2s: float
    velocidade_ms: float
    reynolds: float
    regime: str
    alpha_cinetico: float
