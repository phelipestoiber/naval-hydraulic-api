# Referencial Matemático — Núcleo Físico e Hidráulico

**Versão:** 2.1 | **Base:** REFERENCIAL_v2.0.md + ARQUITETURA_v2.1.md

---

## 0. Fluidos Cobertos (Referência de Valores Típicos)

| Fluido | ρ (kg/m³) | μ dinâmica (mPa·s) | Observações |
|---|---|---|---|
| Água doce (20°C) | 998 | 1,002 | Referência base |
| Água do mar (15°C) | 1025 | 1,08 | Corrosão acelerada |
| Óleo diesel (MDO/DO) | 820–860 | 3–5 | Combustível naval |
| Óleo lubrificante | 860–900 | 100–500 | Variável com temperatura |
| Óleo hidráulico | 850–900 | 15–100 | Sistemas de governo |
| HFO (heavy fuel oil) | 950–1010 | 380–700 cSt a 50°C | Pré-aquecimento necessário |
| Esgoto / águas cinzas | ~1000 | ~1,1 | Sistemas de esgoto naval |
| Glicol (solução 50%) | 1060 | 6 | Sistemas de refrigeração |
| Água de lastro | 1010–1025 | ~1,1 | Sistema de lastro naval |

---

## 1. Propriedades dos Fluidos Newtonianos

### 1.1 Classificação Newtoniana

O fluido deve satisfazer: **τ = μ · (dv/dy)**

Fluidos não-Newtonianos (polímeros fundidos, lamas, fluidos de Bingham) estão fora do escopo. Rejeitar com `FLUIDO_NAO_NEWTONIANO`.

### 1.2 Parâmetros de Entrada Obrigatórios

```
ρ   — Massa específica        [kg/m³]
μ   — Viscosidade dinâmica    [Pa·s]
ν   — Viscosidade cinemática  [m²/s]  ν = μ/ρ
Pv  — Pressão de vapor        [Pa]
T   — Temperatura             [°C] → convertida para K em unit_casting.py
```

### 1.3 Modelos de Viscosidade por Temperatura

**ATENÇÃO:** `alpha_viscos` (coeficiente do modelo Linear) ≠ `alpha_cinetico` (Bernoulli). Usar nomes distintos em todo o código.

**Modelo de Andrade** *(padrão para água e óleos)*:
```
ln(μ) = A + B/T     [μ em Pa·s, T em Kelvin]
```

Constantes padrão *(⚠️ estimativas para desenvolvimento — substituir com fontes primárias em produção)*:

| Fluido | A | B | Faixa | Fonte de referência |
|---|---|---|---|---|
| Água doce | −3,7188 | 578,919 | 0–100°C | Perry's 8th ed., Tab. 2-313 |
| Água do mar | −3,5645 | 555,200 | 0–80°C | Aproximação — ajustar ITS-90 |
| Óleo diesel | −4,5 | 1600 | 20–80°C | Estimativa — ajustar fabricante |
| Óleo lubrificante SAE 40 | −5,2 | 2500 | 40–100°C | Estimativa — ajustar ASTM D341 |
| Glicol 50% | −4,1 | 1200 | −20–60°C | Estimativa — ajustar Dow Chemical |

**Modelo de Walther** *(óleos minerais — ASTM D341)*:
```
log log(ν + 0,7) = A − B · log(T)     [ν em cSt, T em Kelvin]
```

| Fluido | A | B | Faixa | Fonte |
|---|---|---|---|---|
| Óleo lubrificante SAE 40 | 10,5 | 3,9 | 40–100°C | Estimativa ASTM D341 |
| HFO 380 cSt | 12,1 | 4,2 | 50–150°C | Estimativa — ajustar fabricante |

**Modelo Linear** *(faixas estreitas de temperatura)*:
```
μ(T) = μ_ref · [1 + alpha_viscos · (T − T_ref)]
```

---

## 2. Número de Reynolds e Regime de Escoamento

```
Re = ρ · v · D / μ  =  v · D / ν

Regimes:
  Re < 2.300          → Laminar
  2.300 ≤ Re ≤ 4.000 → Transição  (evitar em projeto)
  Re > 4.000          → Turbulento
```

### 2.1 Coeficiente de Energia Cinética (α)

```
alpha_cinetico:
  Laminar    (Re < 2.300): alpha_cinetico = 2,0
  Turbulento (Re > 4.000): alpha_cinetico = 1,0
```

**Atenção de nomenclatura:** variável deve se chamar `alpha_cinetico` — nunca `alpha` sozinho. Não confundir com `alpha_viscos` do modelo Linear de viscosidade.

---

## 3. Equação de Bernoulli Generalizada

```
Z₁ + P₁/(ρg) + alpha_cinetico₁·v₁²/(2g)
  = Z₂ + P₂/(ρg) + alpha_cinetico₂·v₂²/(2g) + Hf_total − Hb

g = 9,81 m/s²
```

---

## 4. Fator de Atrito f

### 4.1 Hierarquia de Uso

1. **Churchill** → cálculo operacional (todos os regimes, sem condicionais)
2. **Colebrook** → validação cruzada e testes de regressão
3. **Haaland / Swamee-Jain** → verificação adicional em testes unitários

### 4.2 Escoamento Laminar

```
f = 64 / Re
```

### 4.3 Churchill (1977) — implementação principal

```
f = 8 · [ (8/Re)¹² + (A + B)^(−1,5) ]^(1/12)

A = { −2,457 · ln[ (7/Re)^0,9 + 0,27·ε/D ] }¹⁶
B = (37.530/Re)¹⁶
```

Válido para todos os regimes com uma única expressão — sem condicionais de regime.

### 4.4 Colebrook-White — validação cruzada

```
1/√f = −2 · log₁₀( ε/(3,71·D) + 2,51/(Re·√f) )
```

Iterativa. Convergência com `TOLERANCIA_CONVERGENCIA_ATRITO = 1e-6` (adimensional). Tipicamente 3–5 iterações.

### 4.5 Swamee-Jain — explícita (erro < 3% vs Colebrook)

```
f = 0,25 / [ log₁₀( ε/(3,71·D) + 5,74/Re^0,9 ) ]²

Validade: 10⁻⁶ ≤ ε/D ≤ 10⁻² e 5.000 ≤ Re ≤ 10⁸
```

### 4.6 Haaland — explícita (erro < 2% vs Colebrook)

```
1/√f = −1,8 · log₁₀[ (ε/D / 3,7)^1,11 + 6,9/Re ]

Validade: 4.000 < Re < 10⁸;  0 ≤ ε/D ≤ 0,05
```

Fora da faixa: emitir aviso e usar fallback (f=64/Re para laminar; Colebrook para ε/D > 0,05).

---

## 5. Perdas de Carga Distribuídas

### 5.1 Darcy-Weisbach — equação principal

```
hf = f · (L/D) · (v²/2g)     [m]
```

### 5.2 Hazen-Williams — alternativa para água

```
hf = 10,646 · Q^1,852 · L / (C^1,852 · D^4,87)

[hf em m; Q em m³/s; L em m; D em m; C adimensional]
```

**Trava de validação obrigatória** — rejeitar automaticamente e usar Darcy-Weisbach se qualquer condição falhar:

| Condição | Critério | Código de rejeição |
|---|---|---|
| Tipo de fluido | Apenas água (doce, salgada, potável, lastro, incêndio) | `HW_FLUIDO_INVALIDO` |
| Temperatura | 5°C ≤ T ≤ 30°C | `HW_TEMPERATURA_INVALIDA` |
| Regime | Re > 4.000 | `HW_REGIME_INVALIDO` |
| Diâmetro | 12 mm ≤ D ≤ 3.600 mm | `HW_DIAMETRO_INVALIDO` |

A validação e o fallback vivem **dentro de `hazen_williams.py`** — nunca no pipeline ou no endpoint. O chamador sempre recebe `{hf_m, metodo_usado, aviso, codigo_rejeicao}`.

**Coeficientes C por material:**

| Material | C (novo) | C (usado) |
|---|---|---|
| PVC / CPVC | 140–150 | 130–140 |
| Aço inoxidável 304/316 | 140–150 | 120–140 |
| Cobre / Cu-Ni | 130–140 | 120–130 |
| Aço carbono | 120–130 | 80–100 |
| Ferro galvanizado | 120 | 100 |

---

## 6. Perdas de Carga Localizadas (Singularidades)

### 6.1 Método dos Coeficientes K

```
hL = K · v²/2g     [m]
```

### 6.2 Comprimento Equivalente

```
Le = K · D / f     [m]
hL = f · (Le/D) · v²/2g
```

### 6.3 Coeficientes K de Referência

**Curvas:**

| Tipo | K | Le/D |
|---|---|---|
| Curva 90° raio longo (R/D = 1,5) | 0,6 | 16 |
| Curva 90° raio curto (R/D = 1,0) | 1,5 | 30 |
| Curva 45° raio longo | 0,4 | 10 |
| Curva 45° raio curto | 0,8 | 16 |
| Curva 180° (retorno) | 2,2 | 50 |

**Válvulas:**

| Tipo | K (aberta) | Le/D |
|---|---|---|
| Gaveta (gate) | 0,1–0,2 | 7 |
| Globo (globe) | 6–10 | 350 |
| Borboleta | 0,6–2,0 | 45 |
| Esfera — passagem total | 0,05–0,1 | 3 |
| Retenção de disco (swing check) | 2,0–3,5 | 100 |
| Retenção de pistão (lift check) | 6–12 | 400 |
| Kingston (sea chest) | 0,5–1,5 | — |

**Tês e transições:**

| Tipo | K | Le/D |
|---|---|---|
| Tê — passagem direta | 0,3–0,6 | 20 |
| Tê — saída lateral 90° | 1,5–2,0 | 60 |
| Entrada borda viva | 0,5 | — |
| Entrada bem arredondada | 0,03–0,05 | — |
| Saída (em reservatório) | 1,0 | — |
| Ampliação brusca | (1 − D₁²/D₂²)² | — |
| Redução brusca | 0,5·(1 − D₂²/D₁²) | — |

### 6.4 Perda Total no Sistema

```
Hf_total = Σ hf_trechos + Σ hL_singularidades

Curva de resistência do sistema:
H_sistema = H_geo + R · Q²
```

---

## 7. Interpolação de Curvas de Bomba

### 7.1 PCHIP — obrigatório

```python
from scipy.interpolate import PchipInterpolator

# CORRETO — monotonicidade garantida
interp_hq = PchipInterpolator(Q_points, H_points)

# PROIBIDO — não garante monotonicidade
# from scipy.interpolate import CubicSpline
```

**Por que PCHIP:** CubicSpline pode gerar overshoot em curvas planas (ex: diferença de 0,2 m entre pontos consecutivos → H interpolada pode exceder H_shut_off). PCHIP preserva monotonicidade local entre pontos consecutivos.

### 7.2 Verificação de Envelope

```python
def verificar_envelope(interp, Q_min, Q_max, H_min, H_max, n=1000):
    """H(Q) ∈ [H_min, H_max] para n pontos uniformes no intervalo."""
    import numpy as np
    Q_test = np.linspace(Q_min, Q_max, n)
    H_test = interp(Q_test)
    return bool(np.all(H_test >= H_min) and np.all(H_test <= H_max))
```

---

## 8. Ponto de Operação

### 8.1 Boundary Check — obrigatório antes do loop

```python
g_min = H_bom(Q_min) - H_sis(Q_min)
g_max = H_bom(Q_max) - H_sis(Q_max)

if g_min < 0:
    raise ErroCalculo(
        codigo="SEM_PONTO_OPERACAO_SHUT_OFF",
        mensagem=f"H_shut_off ({H_bom(Q_min):.2f} m) < H_sistema_Q0 ({H_sis(Q_min):.2f} m)",
        dados_diagnostico={
            "H_shut_off_m": H_bom(Q_min),
            "H_sistema_Q0_m": H_sis(Q_min),
            "deficit_m": H_sis(Q_min) - H_bom(Q_min)
        }
    )

if g_max > 0:
    raise ErroCalculo(
        codigo="SEM_PONTO_OPERACAO_FORA_CURVA",
        mensagem=f"Q_op > Q_max ({Q_max*3600:.1f} m³/h) — bomba superdimensionada",
        dados_diagnostico={"Q_max_curva_m3h": Q_max * 3600}
    )

# g_min > 0 e g_max < 0 → raiz garantida → iniciar bisseção
```

### 8.2 Algoritmo — bisseção + NR

```
Critério: |H_bom(Q) − H_sis(Q)| < TOLERANCIA_CONVERGENCIA_PONTO_OP (1e-4 m)
Máximo:   MAX_ITERACOES_PONTO_OP (100)
Fallback: TOLERANCIA_CONVERGENCIA_PONTO_OP e MAX_ITERACOES_PONTO_OP são
          configuráveis via .env
```

### 8.3 Três códigos de erro para não-convergência

| Código | Quando |
|---|---|
| `SEM_PONTO_OPERACAO_SHUT_OFF` | H_shut_off < H_sistema(Q=0) |
| `SEM_PONTO_OPERACAO_FORA_CURVA` | Q_op > Q_max da curva fornecida |
| `SEM_PONTO_OPERACAO` | bisseção não convergiu (residual — casos raros) |

---

## 9. Altura Manométrica Total (AMT)

```
Hb = H_geo + Hf_total + ΔP_processo/(ρ·g)

H_geo = z_descarga − z_succao
```

---

## 10. Velocidade Específica e Tipo de Bomba

```
Ns = N · Q^0,5 / Hb^0,75

[N em rpm; Q em m³/s; Hb em m]

Classificação (SI):
  Ns < 50        → "centrifuga_radial"
  50 ≤ Ns ≤ 200 → "centrifuga_mista"
  Ns > 200       → "axial_helice"
```

---

## 11. NPSH

### 11.1 NPSHd — forma adotada

```
NPSHd = (P_atm − P_v)/(ρ·g) + H_s − hf_succao

H_s > 0 quando reservatório está ACIMA da bomba (sucção afogada)
H_s < 0 quando bomba está ACIMA do reservatório (bomba aspirante)
```

### 11.2 Correção de P_atm por altitude

```
P_atm/γ = 10,33 − 0,12 · (Z/100)   [mca; Z em metros]

Z = 0 m   → 10,33 mca ≈ 101.325 Pa
Z = 500 m → 9,73 mca
Z = 900 m → 9,25 mca
```

### 11.3 Três métodos de margem

```
Método 1 — Margem fixa normal:   NPSHd ≥ NPSHr + 0,6 m
Método 1b — Margem fixa crítica: NPSHd ≥ NPSHr + 1,0 m
Método 2 — Coeficiente 1,2:      NPSHd ≥ 1,2 · NPSHr
Método 3 — Combinado (padrão):   NPSHd ≥ max(NPSHr + 0,6 m ; 1,2 · NPSHr)
```

### 11.4 NPSHr aproximado (sem dados de fabricante)

```
NPSHr ≈ 0,0012 · n^(4/3) · Q^(2/3)

[n em rpm; Q em m³/s]
Marcar campo "npsh_fonte" = "estimativa_sem_fabricante"
```

### 11.5 Índice de Cavitação Específica

```
Nss = N · Q^0,5 / NPSHr^0,75

Nss < 8.500 (unidades inglesas) → operação segura
```

---

## 12. Potência e Eficiência

```
P_hidráulica = ρ · g · Q · Hb           [W]
P_eixo       = P_hidráulica / η_bomba    [W]
P_motor      = P_eixo / η_motor          [W]
η_global     = η_bomba · η_motor · η_transmissão
```

### 12.1 Margens ABNT por tipo de motor

| Faixa (CV) | Elétrico | Diesel | Gasolina |
|---|---|---|---|
| Até 2,0 CV | 50% | — | — |
| 2,0 a 5,0 CV | 30% | — | — |
| 5,0 a 10,0 CV | 20% | — | — |
| 10,0 a 20,0 CV | 15% | 25% | 50% |
| Acima de 20,0 CV | 10% | 25% | 50% |

### 12.2 Potências nominais ABNT (CV)

```
1/12, 1/8, 1/6, 1/4, 1/3, 1/2, 3/4, 1
1,5, 2, 3, 4, 5, 6, 7,5, 10
12,5, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 200
```

---

## 13. Leis de Afinidade e Métodos de Ajuste

### 13.1 Leis de Afinidade

```
Q₂/Q₁ = N₂/N₁
H₂/H₁ = (N₂/N₁)²
P₂/P₁ = (N₂/N₁)³
```

### 13.2 Método A — Estrangulamento por válvula de gaveta

Incrementar K_gaveta iterativamente até Q_op ≈ Q_alvo.
Emitir aviso: `"Método A dissipa energia; preferir VFD (Método B)"`.

### 13.3 Método B — VFD (inversor de frequência)

```
n₂ = n₁ · (Q₂/Q₁)
H₂ = H₁ · (n₂/n₁)²
Parábola de iso-rendimento: H = (H₁/Q₁²) · Q²
```

### 13.4 Método C — Usinagem do rotor

```
D₂ = D₁ · √(Q₂/Q₁)
Usinagem por lado = (D₁ − D₂) / 2  [mm]
Alerta se usinagem > 10% de D₁ → alerta_fabricante = True
```

### 13.5 Pré-dimensionamento do diâmetro de recalque (ABNT)

```
D_R = 1,3 · (T/24)^0,25 · √Q

[D_R em m; T em h/dia; Q em m³/s]
Marcar campo "tipo" = "estimativa_inicial_abnt"
```

---

## 14. Faixas de Operação BEP (ISO 9906)

```
70% ≤ Q/Q_BEP ≤ 120%  → status_bep = "OK"
50% ≤ Q/Q_BEP ≤ 130%  → status_bep = "AVISO"
Q/Q_BEP < 50% ou > 130% → status_bep = "ALERTA"
```

---

## 15. Materiais e Rugosidades

| Material | ε (mm) | Uso naval típico |
|---|---|---|
| Aço carbono novo | 0,046 | Estrutural, lastro |
| Aço carbono usado | 0,15–0,30 | Após anos de serviço |
| Aço galvanizado | 0,15 | Água doce, lastro |
| Aço inoxidável 304/316 | 0,015–0,025 | Água do mar, alimentos |
| Ferro fundido | 0,26 | Sistemas antigos |
| Cobre | 0,0015 | Refrigeração |
| Liga Cu-Ni 90/10 | 0,0015 | Água do mar (premium) |
| Liga Cu-Ni 70/30 | 0,0015 | Água do mar (alta resist.) |
| PVC / CPVC | 0,0015 | Água potável, esgoto |
| GRP (fibra de vidro) | 0,025 | Lastro moderno |
