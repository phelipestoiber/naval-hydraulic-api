from dataclasses import dataclass

@dataclass
class SistemaSI:
    """Todas as grandezas em SI — produzida por unit_casting.py."""
    Q_m3s: float       # Vazão [m³/s]
    D_m: float         # Diâmetro interno [m]
    L_m: float         # Comprimento [m]
    rho_kgm3: float    # Massa específica [kg/m³]
    mu_pas: float      # Viscosidade dinâmica [Pa·s]
    nu_m2s: float      # Viscosidade cinemática [m²/s]
    Pv_pa: float       # Pressão de vapor [Pa]
    Patm_pa: float     # Pressão atmosférica [Pa]
    T_k: float         # Temperatura [K]
    epsilon_m: float   # Rugosidade absoluta [m]
    altitude_m: float  # Altitude [m]
    N_rpm: float       # Rotação da bomba [rpm]

@dataclass
class RastreabilidadeUnidades:
    """Registra cada conversão de unidade para auditoria."""
    campos: list[dict]
