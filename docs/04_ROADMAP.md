# Roadmap — Backlog do Agente

**Versão:** 2.1 | **Base:** VERSIONAMENTO_v2.1.md

---

## Regras de Avanço

1. **TDD obrigatório:** escrever o teste, executar (deve falhar), implementar o módulo, executar novamente (deve passar).
2. **Cobertura antes de avançar:** `core/` ≥ 95% | `api/` ≥ 85% | global ≥ 90%.
3. **Golden values obrigatórios:** os valores da tabela em `INSTRUCOES_AGENTE.md` devem ser reproduzidos dentro das tolerâncias antes de avançar da v0.9.0 para a v1.0.0.
4. **Falha explícita:** testes de rejeição (F1, F3) devem confirmar via spy/mock que **zero iterações** de cálculo ocorrem antes da falha.
5. **Atualizar estado:** ao encerrar cada versão, atualizar o bloco de estado em `INSTRUCOES_AGENTE.md`.

---

## Golden Values de Regressão

| Grandeza | Condição | Valor | Tolerância | Fixado em |
|---|---|---|---|---|
| Reynolds sucção | Prumo | 287.000 | ±2% | v0.1.0 |
| Velocidade sucção | Prumo | 1,87 m/s | ±2% | v0.9.0 |
| Velocidade descarga | Prumo | 2,69 m/s | ±2% | v0.9.0 |
| H_geo | Prumo (0°, 0°) | 3,40 m | ±2% | v0.7.0 |
| H_s | Prumo (0°, 0°) | 0,70 m | ±2% | v0.7.0 |
| Altura manométrica | Prumo | 8,45 m | ±5% | v0.9.0 |
| NPSHd | Prumo (0°, 0°) | 4,82 m | ±5% | v0.9.0 |
| NPSHd integrado | Avaria BB (+10°, +22,5°) | 4,40 m | ±5% | v0.9.0 |
| H_geo integrado | Avaria BB (+10°, +22,5°) | 2,98 m | ±5% | v0.9.0 |
| Velocidade específica Ns | Ponto de operação | ≈ 63,7 | ±5% | v0.4.0 |
| Tipo de bomba | Ponto de operação | centrifuga_mista | exato | v0.4.0 |
| Motor selecionado | Caso de referência | 7,5 CV | exato | v0.6.0 |

> **Nota H_geo avaria:** o valor 2,98 m refere-se ao resultado do pipeline integrado, não à diferença de cotas brutas (0,285 m do cálculo matricial isolado). Validar via teste de integração v0.9.0.

---

## FASE 1 — Núcleo Hidráulico

---

### v0.1.0 — Fundação Matemática e Propriedades de Fluidos

**Módulos a criar:**
```
app/utils/math_utils.py          PchipInterpolator, bisseção, NR, verificar_envelope
app/utils/csv_utils.py           Parser e validador CSV (10 regras do schema D2)
app/schemas/si.py                SistemaSI, RastreabilidadeUnidades
app/core/unit_casting.py         Casting SI + validators + detectar_malha_fechada (F1)
app/core/fluidos/reynolds.py     Re, regime, alpha_cinetico
app/core/fluidos/viscosidade.py  Andrade, Walther, Linear; alpha_viscos
app/data/materiais.json          Schema v2.0
app/data/singularidades_k.json   Schema v1.0 + suporta_metodo_A
app/data/potencias_abnt.json     Schema v2.0 (elétrico, diesel, gasolina)
app/data/classificadoras.json    Schema v2.0 (BV, LR, ABS separados)
```

**Testes a criar (TDD — nesta ordem):**
```
tests/unit/test_math_utils.py
tests/unit/test_csv_utils.py
tests/unit/test_unit_casting.py
tests/unit/test_viscosidade.py
tests/unit/test_reynolds.py
```

**Testes obrigatórios:**

**T1.1 — Casting: água do mar**
```
Entrada: Q=118,5 m³/h; D=150 mm; T=32°C; ρ=1025 kg/m³; μ=0,001 Pa·s
  Q_m3s  = 0,032917 m³/s  (tolerância < 0,01%)
  D_m    = 0,150 m
  T_k    = 305,15 K
  nu_m2s = 9,756e-7 m²/s
RastreabilidadeUnidades contém {"campo":"vazao","fator":"/ 3600",...}
```

**T1.2 — Sanity checks (7 casos)**
```
Q=-5 m³/h          → 422; "VAZAO_NEGATIVA"
ρ=2500 kg/m³       → 422; "DENSIDADE_INVALIDA"
T=-10°C = 263,15 K → 422; "TEMPERATURA_FORA_DO_RANGE"
μ=0 Pa·s           → 422; "VISCOSIDADE_INVALIDA"
Pv=-100 Pa         → 422; "PRESSAO_VAPOR_INVALIDA"
ε=-0,01 mm         → 422; "RUGOSIDADE_INVALIDA"
unidade="gal/h"    → 422; "UNIDADE_INVALIDA"
Nunca AssertionError — sempre ErrorResponse estruturado
```

**T1.3 — Reynolds laminar (Exemplo 2.12 — Silva Telles)**
```
Q=200 m³/h; D=255 mm; ν=550 cSt
  Re ≈ 504; Regime: LAMINAR; alpha_cinetico = 2,0  (±2%)
```

**T1.4 — Reynolds turbulento (Exemplo 2.13 — Silva Telles)**
```
Q=9 l/s; D=102,2 mm; ν=6 cSt
  Re = 18.679; Regime: TURBULENTO; alpha_cinetico = 1,0  (±2%)
```

**T1.5 — Andrade: água doce (constantes padrão D1)**
```
A=-3,7188; B=578,919
  T=20°C → μ ≈ 1,002e-3 Pa·s  (±2% vs CRC Handbook)
  T=60°C → μ ≈ 4,67e-4 Pa·s   (±2%)
  T=90°C → μ ≈ 3,15e-4 Pa·s   (±2%)
```

**T1.6 — Walther: óleo SAE 40**
```
A=10,5; B=3,9
  T=40°C  → ν ≈ 110 cSt  (±5%)
  T=100°C → ν ≈ 14,5 cSt (±5%)
```

**T1.7 — Distinção alpha_viscos ≠ alpha_cinetico**
```
Modelo Linear: μ(T)=μ_ref·[1+alpha_viscos·(T−T_ref)]
  μ_ref=0,001 Pa·s; T_ref=293,15 K; alpha_viscos=−0,02 /K
  T=313,15 K → μ = 6e-4 Pa·s
Verificar que "alpha_viscos" e "alpha_cinetico" são variáveis distintas
```

**T1.8 — Schemas JSON (schema v2.0)**
```
materiais.json:       versao_schema="2.0"; "aco_inox_304" rugosidade_mm=0,02
singularidades_k.json:"curva_90_rl" K=0,6; "valvula_gaveta" suporta_metodo_A=true
potencias_abnt.json:  margens_por_tipo com "eletrico","diesel","gasolina"
classificadoras.json: BV/LR/ABS separados; LR com nota_divergencia
```

**T1.9 — csv_utils: 10 casos do schema D2**
```
CSV válido → (True, [])
header errado          → "CURVA_CSV_HEADER_INVALIDO"
2 pontos               → "CURVA_CSV_PONTOS_INSUFICIENTES"
Q decrescente          → "CURVA_CSV_Q_NAO_CRESCENTE"
H crescente            → "CURVA_CSV_H_INVALIDO"
decimal vírgula        → "CURVA_CSV_FORMATO_DECIMAL"
51 pontos              → "CURVA_CSV_PONTOS_EXCEDIDOS"
sem coluna Q_m3h       → "CURVA_CSV_HEADER_INVALIDO"
arquivo vazio          → "CURVA_CSV_ARQUIVO_INVALIDO"
encoding latin-1       → "CURVA_CSV_ENCODING_INVALIDO"
valor ausente em H_m   → "CURVA_CSV_VALOR_AUSENTE"
```

**T1.10 — Detecção de malha fechada (F1)**
```
Cenário A: trechos em série sem retorno → detectar_malha=False → passa
Cenário B: D1.id_destino = S1.id → detectar_malha=True
  → "TOPOLOGIA_MALHA_NAO_SUPORTADA"
  → ZERO cálculos hidráulicos executados (verificar via mock)
Cenário C: tê sem ciclo → False → passa
Cenário D: anel [A→B, B→C, C→A] → True
  → "TOPOLOGIA_MALHA_NAO_SUPORTADA"
  → mensagem menciona "sistemas em anel"
```

**T1.11 — PCHIP: monotonicidade e envelope**
```
Curva plana: Q=[0,50,100,150,180]; H=[42,41.8,36,28,18]
  verificar_envelope(interp, 0, 180, 18, 42, n=1000) → True
  H(25) ∈ [41.8, 42.0]  (PCHIP garante; CubicSpline pode violar)
```

**Critério de avanço:** T1.1–T1.11 passando; cobertura ≥ 95%

---

### v0.2.0 — Fator de Atrito e Perdas Distribuídas

**Módulos a criar:**
```
app/core/perda_carga/fator_atrito.py    Churchill, Colebrook, Swamee-Jain, Haaland, f=64/Re
app/core/perda_carga/darcy_weisbach.py  hf = f·(L/D)·(v²/2g)
```

**Testes a criar:**
```
tests/unit/test_fator_atrito.py
tests/unit/test_darcy_weisbach.py
```

**T2.1 — Laminar: Churchill = Poiseuille (Exemplo 2.12 — Silva Telles)**
```
Re≈504; D=255 mm; L'=215 m; ν=550 cSt
  f_Poiseuille = 64/504 = 0,1270
  f_Churchill  → mesmo valor (tolerância < 0,1%)
  j = 3,0 m/100m  (livro: 3,01 ✓ ±2%)
```

**T2.2 — Turbulento: quatro equações vs Colebrook (Exemplo 2.13 — Silva Telles)**
```
Re=18.679; ε/D=0,00043
  f_Colebrook (ref): ≈ 0,028  (livro: 0,028 ✓)
  f_Churchill:    |f−f_ref| < 0,1%
  f_Swamee-Jain:  |f−f_ref| < 3%
  f_Haaland:      |f−f_ref| < 2%
  j = 0,0167 m/m (livro ✓); J = 1,35 m (livro ✓)
```

**T2.3 — Consistência cruzada 5 pontos**
```
(Re=1.000, ε/D=0):       laminar   → Churchill=Poiseuille    (< 0,01%)
(Re=10.000, ε/D=0,0001): turb.liso → Churchill vs Colebrook  (< 0,1%)
(Re=100.000, ε/D=0,001): turbulento→ Churchill (< 0,1%); Swamee (< 3%); Haaland (< 2%)
(Re=1e6, ε/D=0,005):     rug.      → Churchill vs Colebrook  (< 0,1%)
(Re=1e8, ε/D=0,05):      zona rug. → Churchill vs Colebrook  (< 0,1%)
```

**T2.4 — Convergência Colebrook**
```
Re=50.000; ε/D=0,001; f_0=0,02
  ≤ 5 iterações com TOLERANCIA_CONVERGENCIA_ATRITO=1e-6
```

**T2.5 — Haaland: faixa e fallback**
```
Dentro (Re=50.000; ε/D=0,001): executa; erro vs Colebrook < 2%
Fora (Re=1.000 laminar): aviso + f=64/Re
Fora (ε/D=0,1): aviso + Colebrook
```

**Critério de avanço:** T2.1–T2.5 passando; Exemplos 2.12 e 2.13 reproduzidos ±2%; cobertura ≥ 95%

---

### v0.3.0 — Perdas Localizadas e Sistema Completo

**Módulos a criar:**
```
app/core/perda_carga/hazen_williams.py
app/core/perda_carga/singularidades.py
app/core/perda_carga/sistema.py
app/core/bernoulli.py
```

**Testes a criar:**
```
tests/unit/test_hazen_williams.py
tests/unit/test_singularidades.py
tests/unit/test_bernoulli.py
```

**T3.1 — Comprimento equivalente (Exemplo 2.12 — Silva Telles)**
```
2 gavetas:3,50 m | 1 retenção:21,00 m | 4 curvas:7,00 m | 1 entrada:10,00 m
Soma = 41,50 m (livro: 41,5 ✓); L'=215,5 m (±5%)
```

**T3.2 — HW: 4 casos rejeição/aceitação**
```
oleo_diesel, T=20°C, Re=50k → HW_FLUIDO_INVALIDO → Darcy
agua_doce, T=85°C, Re=50k   → HW_TEMPERATURA_INVALIDA → Darcy
agua_doce, T=20°C, Re=50k, D=150mm → aceita; metodo_usado="hazen_williams"
agua_salgada, T=15°C, Re=1500 → HW_REGIME_INVALIDO → Darcy
```

**T3.3 — alpha_cinetico no Bernoulli**
```
Laminar (Re=504):   alpha=2,0; termo cinético=0,1206 m
Turbulento (Re=18k):alpha=1,0; termo cinético=0,0614 m
Variável chamada "alpha_cinetico" — nunca "alpha" sozinho
```

**T3.4 — Balanço energético sem bomba (Exemplo 2.12)**
```
Energia ponto 1: 34,13 m | Energia ponto 2: 30,10 m
Diferença: 4,03 m (livro: 3,95 m ±2% ✓)
J para 12": 3,31 m < 4,03 m → satisfaz ✓
```

**T3.5 — HW vs Darcy**
```
Água doce, 20°C; C=140; D=150 mm; Q=0,032917 m³/s; L=8,5 m
|hf_HW − hf_DW| / hf_DW ≤ 10%
```

**Critério de avanço:** T3.1–T3.5 passando; Exemplo 2.12 end-to-end; cobertura ≥ 95%

---

## FASE 2 — Bombas e Ponto de Operação

---

### v0.4.0 — Interpolação PCHIP, Ponto de Operação e Velocidade Específica

**Módulos a criar:**
```
app/core/bombas/interpolacao.py          PchipInterpolator H×Q, η×Q, NPSHr×Q
app/core/bombas/ponto_operacao.py        Boundary check + bisseção + NR (F3)
app/core/bombas/velocidade_especifica.py Ns; classificação
app/core/bombas/bep.py                   OK/AVISO/ALERTA
```

**Testes a criar:**
```
tests/unit/test_interpolacao.py
tests/unit/test_ponto_operacao.py
tests/unit/test_velocidade_especifica.py
tests/unit/test_bep.py
```

**T4.1 — PCHIP: envelope e monotonicidade (F2)**
```
Curva ref: Q=[0,50,100,150,180]; H=[42,40,36,28,18]
  H(0)=42; H(180)=18 (pontos extremos preservados)
  dH/dQ ≤ 0 em todos os pontos interiores
  verificar_envelope(0, 180, 18, 42, n=1000) → True

Curva plana: Q=[0,50,100,150,180]; H=[42,41.8,36,28,18]
  verificar_envelope(...) → True
  H(25) ∈ [41.8, 42.0]  — não ultrapassa H_shut_off

Regressão PCHIP vs CubicSpline (documentação, não falha):
  CubicSpline(25) pode exceder 42.0 — registrar no log
```

**T4.2 — Boundary check + convergência (F3)**
```
F3-A: H_geo=50 m > H_shut_off=42 m
  g(Q=0) = 42−50 = −8 < 0
  → "SEM_PONTO_OPERACAO_SHUT_OFF" ANTES do loop
  → dados_diagnostico["deficit_m"] = 8.0
  → spy confirma: iteracoes_bisecao = 0

F3-B: sistema muito fácil (bomba sempre acima)
  g(Q_max) > 0
  → "SEM_PONTO_OPERACAO_FORA_CURVA" ANTES do loop
  → spy confirma: iteracoes_bisecao = 0

Normal: H_geo=3,40 m; curva ref
  g(0) > 0 e g(Q_max) < 0 → raiz garantida
  ≤ 100 iterações; |H_sis−H_bom| < 1e-4 m
  resultado["convergiu"] = True

Residual (mock max_iter=1, tol=1e-30):
  → "SEM_PONTO_OPERACAO"  (código genérico)
```

**T4.3 — Série e paralelo**
```
Série:   H_serie(Q) = 2×H_bom(Q); Q_op_serie < Q_op_paralelo
Paralelo:Q_paralelo(H) = 2×Q_bom(H); Q_op_paralelo > Q_op_serie
```

**T4.4 — Velocidade específica Ns (golden value)**
```
N=1450 rpm; Q_op=0,032917 m³/s; H_op=8,45 m
  Ns = 1450 × √0,032917 / 8,45^0,75 ≈ 63,7  (±5%)  ← golden value
  tipo_bomba = "centrifuga_mista"  ← golden value
Limites: Ns=30→"centrifuga_radial"; Ns=250→"axial_helice"
```

**T4.5 — BEP: três status**
```
Q_BEP = 100 m³/h
  Q_op=85  (85%) → "OK"
  Q_op=60  (60%) → "AVISO"
  Q_op=40  (40%) → "ALERTA"
  Q_op=140 (140%)→ "ALERTA"
```

**Critério de avanço:** T4.1–T4.5 passando; spy confirma zero iterações antes de F3-A e F3-B; golden values Ns e tipo_bomba corretos; cobertura ≥ 95%

---

### v0.5.0 — NPSH e Cavitação

**Módulos a criar:**
```
app/core/bombas/npsh.py
```

**Testes a criar:**
```
tests/unit/test_npsh.py
```

**T5.1 — NPSHd (Exemplo 2.13 — Silva Telles)**
```
P_atm=103.300 Pa; γ=7.800 N/m³; Pv=35.200 Pa; H_s=2,60 m; hf=1,35 m; NPSHr=1,90 m
  NPSHd = 11,92 − (2,60+4,51+1,90) = 2,91 m  (livro: 2,84 m ±3% ✓)
  NPSHd > hf_suc → 4" satisfaz ✓
```

**T5.2 — P_atm por altitude**
```
Z=0 m   → P_atm ≈ 101.325 Pa (±0,02%)
Z=500 m → P_atm ≈ 95.427 Pa
Z=900 m → P_atm ≈ 90.713 Pa
```

**T5.3 — Três métodos de margem**
```
NPSHr=3,20 m; NPSHd=4,82 m (golden value)
Fixo normal (0,6 m):   4,82 ≥ 3,80 ✓  margem=1,02 m
Fixo crítico (1,0 m):  4,82 ≥ 4,20 ✓  margem=0,62 m
Coeficiente 1,2:       4,82 ≥ 3,84 ✓  margem=0,98 m
Combinado:             4,82 ≥ 3,84 ✓
```

**T5.4 — NPSHr aproximado**
```
n=1450 rpm; Q=0,032917 m³/s → NPSHr_aprox ∈ [2, 6] m
campo "npsh_fonte" = "estimativa_sem_fabricante"
```

**T5.5 — Serviço normal vs. crítico**
```
NPSHd=4,00 m; fixo normal  (0,6 m): 4,00 ≥ 3,80 → "OK"
NPSHd=4,00 m; fixo crítico (1,0 m): 4,00 < 4,20 → "REPROVADO"
```

**Critério de avanço:** T5.1–T5.5 passando; Exemplo 2.13 ±3%; cobertura ≥ 95%

---

### v0.6.0 — Potência, Motor e Métodos de Ajuste

**Módulos a criar:**
```
app/core/bombas/potencia.py
app/core/bombas/afinidade.py
app/core/bombas/pre_dimensionamento.py
```

**Testes a criar:**
```
tests/unit/test_potencia.py
tests/unit/test_afinidade.py
```

**T6.1 — Cadeia de potência (golden value)**
```
Q=0,032917 m³/s; H=8,45 m; ρ=1025 kg/m³; η_bomba=0,799; η_motor=0,92
  P_hid  = 2.793 W  (±2%)
  P_eixo = 3.495 W
  P_motor = 3.799 W = 5,16 CV

Elétrico (30% na faixa 2-5 CV): 5,16×1,30=6,71 → motor 7,5 CV  ← golden value
Diesel   (25%):                  5,16×1,25=6,45 → motor 7,5 CV
Gasolina (50%):                  5,16×1,50=7,74 → motor 10 CV
```

**T6.2 — Método B (VFD)**
```
Q₁=150 m³/h; H₁=28 m; n₁=1450 rpm → Q₂=118,5 m³/h
  n₂ = 1146 rpm; H₂ = 17,47 m; P₂/P₁ = 0,495
Ponto homólogo: H(118,5) = 17,47 m ✓  (±1%)
```

**T6.3 — Método C (usinagem + alerta)**
```
D₁=315 mm; Q₂/Q₁=118,5/150 → D₂=280 mm
Usinagem: 17,5 mm/lado = 11,1% > 10% → alerta_fabricante=True
```

**T6.4 — Método A (estrangulamento por gaveta)**
```
Q_op=118,5 → Q_alvo=90 m³/h
Incrementar K_gaveta até |Q_op−Q_alvo| < 1 m³/h em ≤ 50 iterações
Aviso: "Método A dissipa energia; preferir VFD"
```

**T6.5 — Pré-dimensionamento ABNT**
```
Q=0,032917 m³/s; T=20 h/dia → D_R=0,227 m=227 mm
DN acima: 250 mm; tipo="estimativa_inicial_abnt"
```

**Critério de avanço:** T6.1–T6.5 passando; motor 7,5 CV confirmado (golden value); cobertura ≥ 95%

---

## FASE 3 — Módulo Naval

---

### v0.7.0 — Geometria 3D e Varredura de Inclinação

**Módulos a criar:**
```
app/core/naval/geometria.py     R(θ,φ); z_efetivo; docstring convenção D5
app/core/naval/inclinacao.py    9 condições; crítica; OK/AVISO/REPROVADO; condicoes_reprovadas
```

**Testes a criar:**
```
tests/unit/test_geometria_naval.py
tests/unit/test_inclinacao.py
```

**T7.1 — Prumo: R(0°,0°) = identidade (golden values)**
```
Pontos ref (D5: X+=proa):
  sucção {x:-12,5; y:1,2; z:0,8}; descarga {x:+5,0; y:1,2; z:4,2}

R(0°,0°) = identidade → z_efetivo = z_original
H_geo = 4,2 − 0,8 = 3,40 m  ← golden value ±2%
H_s   = 1,5 − 0,8 = 0,70 m  ← golden value ±2%
```

**T7.2 — Avaria BB (+10°, +22,5°): matemática da matriz**
```
R[2] = [−0,1604; 0,3827; 0,9096]

Descarga P=[+5,0; 1,2; 4,2]:
  z_efetivo = (−0,1604×5,0)+(0,3827×1,2)+(0,9096×4,2) = 3,477 m

Sucção P=[−12,5; 1,2; 0,8]:
  z_efetivo = (−0,1604×(−12,5))+(0,3827×1,2)+(0,9096×0,8) = 3,192 m

H_geo_bruto = 3,477 − 3,192 = 0,285 m
(Golden value 2,98 m é resultado pipeline integrado — validar em T9.1)
```

**T7.3 — Simetria φ=+15° vs φ=−15°**
```
θ=5°; pontos com y=1,2 m (≠ 0)
H_geo(5°,+15°) ≠ H_geo(5°,−15°)  — calculados independentemente
```

**T7.4 — Status OK/AVISO/REPROVADO (D4)**
```
A: todas 9 aprovadas → "OK"; condicoes_reprovadas=[]
B: 5 operação ok, ≥1 avaria reprovada → "AVISO"
C: ≥1 operação reprovada → "REPROVADO"
   condicoes_reprovadas[0] tem {condicao, theta_deg, phi_deg,
   npsh_disponivel_m, npsh_minimo_m, deficit_m}
```

**T7.5 — Nomes das 9 condições**
```
varredura_inclinacao com 9 entradas, campo "condicao" ∈:
  "prumo","operacao_BB","operacao_EB","operacao_BB_inv","operacao_EB_inv",
  "avaria_BB","avaria_EB","avaria_BB_inv","avaria_EB_inv"
```

**Critério de avanço:** T7.1–T7.5 passando; golden values H_geo e H_s confirmados; 3 status distintos; cobertura ≥ 95%

---

### v0.8.0 — Verificações de Norma de Classificadora

**Módulos a criar:**
```
app/core/naval/normas.py
app/core/naval/redundancia.py
```

**Testes a criar:**
```
tests/unit/test_normas.py
tests/unit/test_redundancia.py
```

**T8.1 — Classes BV/LR/ABS com divergência**
```
P=20 bar, T=350°C → Classe I para BV, LR e ABS
P=18 bar, T=200°C → BV: Classe I (P>16); LR: Classe II (P≤20)
resultado["classificacao_por_norma"]["LR"] tem "nota" sobre divergência
```

**T8.2 — Velocidades fora dos limites (BV)**
```
Água do mar, sucção (0,5–1,2 m/s):
  v=0,3 → ALERTA; v=0,8 → OK; v=2,0 → ALERTA
Alerta inclui nome da classificadora e faixa permitida
```

**T8.3 — MAWP por classe**
```
Classe II BV (≤16 bar): P_op=18 → REPROVADO
Classe III BV (≤7 bar):  P_op=5  → APROVADO
```

**T8.4 — Redundância: 4 cenários obrigatórios**
```
A: essencial, 1 bomba, sem alim.ind. → REPROVADO (2 não-conformidades)
B: essencial, 2 bombas, alim.ind.    → APROVADO
C: não-essencial, 1 bomba            → APROVADO
D: essencial, 2 bombas, sem alim.ind.→ REPROVADO (1 não-conformidade)
```

**Critério de avanço:** T8.1–T8.4 passando; 3 classificadoras com divergência BV/LR reportada; cobertura ≥ 95%

---

### v0.9.0 — Pipeline Completo, Banco de Dados e Status

**Módulos a criar:**
```
app/core/bernoulli.py
app/core/pipeline.py
app/db/database.py
app/db/models.py
app/db/crud.py
app/schemas/erro.py
app/utils/report_utils.py
tests/conftest.py
```

**Testes a criar:**
```
tests/integration/test_pipeline_completo.py
tests/integration/test_inclinacao_varredura.py
tests/integration/test_bomba_sistema.py
```

**T9.1 — Pipeline completo: golden values**
```
Payload: payload_referencia do conftest.py

resultados_prumo:
  velocidade_succao_m_s:   1,87   (±2%)  ← golden value
  velocidade_descarga_m_s: 2,69   (±2%)  ← golden value
  reynolds_succao:         287.000 (±2%) ← golden value
  alpha_cinetico_succao:   1,0
  h_geo_m:                 3,40   (±2%)  ← golden value
  altura_manometrica_m:    8,45   (±5%)  ← golden value
  npsh_disponivel_m:       4,82   (±5%)  ← golden value
  velocidade_especifica_ns:≈63,7  (±5%)  ← golden value
  tipo_bomba:              "centrifuga_mista"  ← golden value
  motor_selecionado_cv:    7,5    (exato) ← golden value
  status_npsh:             "OK"
  status_bep:              "OK"

condicao_critica:
  condicao:            "avaria_BB"
  theta_deg:           10,0; phi_deg: 22,5
  npsh_disponivel_m:   4,40   (±5%)  ← golden value
  aprovado:            true

varredura: 9 condições nomeadas
status: "OK"; condicoes_reprovadas: []
```

**T9.2 — Rastreabilidade de unidades**
```
rastreabilidade_unidades contém:
  vazao: {valor_entrada:118.5, unidade:"m3/h", valor_si:0.032917, fator:"/ 3600"}
  diametro_s: {valor_entrada:150.0, unidade:"mm", valor_si:0.150, fator:"/ 1000"}
  temperatura: {valor_entrada:32, unidade:"°C", valor_si:305.15, fator:"+ 273,15"}
```

**T9.3 — Alertas acumulados**
```
Payload: T=85°C + método HW + v_suc=2,5 m/s + Q/Q_BEP=45%
  avisos_equacao: ["HW rejeitada: T=85°C..."]
  alertas: ["Velocidade sucção acima do limite BV...", "BEP fora da faixa aceitável..."]
```

**T9.4 — Banco de dados**
```
sqlite:///:memory → tabela "calculos" com colunas corretas
crud.create_calculo → UUID v4 válido
crud.get_resultado("uuid_invalido") → None
```

**T9.5 — ErrorResponse para erros de cálculo**
```
Curva com 1 ponto         → 422; "CURVA_HQ_INVALIDA"
H crescente na curva      → 422; "CURVA_HQ_H_INVALIDO"
H_shut_off < H_geo        → 422; "SEM_PONTO_OPERACAO_SHUT_OFF"   ← F3
Q_op além da curva        → 422; "SEM_PONTO_OPERACAO_FORA_CURVA" ← F3
Bisseção residual falha   → 422; "SEM_PONTO_OPERACAO"
Nunca HTTP 500 para estes casos
```

**T9.6 — Status REPROVADO: NPSH < critério em operação (D4)**
```
H_s negativo grande → NPSHd baixo em todas as condições
  HTTP 200; status="REPROVADO"
  condicoes_reprovadas não vazia; deficit_m > 0
```

**T9.7 — Status AVISO: falha só em avaria (D4)**
```
NPSHd ok nas 5 de operação/prumo; < critério em ≥1 avaria
  HTTP 200; status="AVISO"
  condicoes_reprovadas contém apenas avarias
```

**T9.8 — Pipeline rejeita malha na Camada 1 (F1)**
```
trechos[1].id_destino = trechos[0].id
  Falha em unit_casting — Camadas 2–6 não executadas (verificar via mock)
  "TOPOLOGIA_MALHA_NAO_SUPORTADA"
```

**Critério de avanço:** TODOS os golden values confirmados em T9.1; T9.2–T9.8 passando; cobertura integração ≥ 90%

---

## FASE 4 — API REST

---

### v1.0.0 — API REST Pública

**Módulos a criar:**
```
app/main.py
app/api/v1/router.py
app/api/v1/dependencies.py
app/api/v1/endpoints/*.py  (todos os 10 endpoints)
README.md
```

**Testes a criar:**
```
tests/conftest.py  (finalizar com fixtures completas)
tests/api/test_endpoint_calcular.py
tests/api/test_endpoint_resultado.py
```

**T10.1 — Round-trip HTTP (golden values)**
```
POST /api/v1/calcular com payload_referencia
  HTTP 200
  Todos os golden values da tabela reproduzidos
  id_calculo é UUID v4 válido
  status = "OK"
```

**T10.2 — Persistência e recuperação**
```
GET /api/v1/resultado/{id_do_T10.1} → HTTP 200; dados coincidem
GET /api/v1/resultado/uuid-invalido  → HTTP 404; "RESULTADO_NAO_ENCONTRADO"
```

**T10.3 — Rejeição de entradas (9 casos)**
```
A: Q=-5 m³/h                       → 422; "VAZAO_NEGATIVA"
B: fluido sem "densidade_kg_m3"     → 422; "CAMPO_OBRIGATORIO"
C: unidade="furlongs_por_fortnight" → 422; "UNIDADE_INVALIDA"
D: T=500°C (773 K)                  → 422; "TEMPERATURA_FORA_DO_RANGE"
E: H×Q com H crescente              → 422; "CURVA_HQ_H_INVALIDO"
F: fluido="lama_nao_newtoniana"     → 422; "FLUIDO_INVALIDO"
G: NPSH reprovado todas as 9        → 200; status="REPROVADO"  (D4)
H: malha fechada (F1)               → 422; "TOPOLOGIA_MALHA_NAO_SUPORTADA"
I: H_geo > H_shut_off (F3)          → 422; "SEM_PONTO_OPERACAO_SHUT_OFF"
   dados_diagnostico["deficit_m"] presente no response
```

**T10.4 — Endpoints de biblioteca**
```
GET /api/v1/materiais
  ≥ 8 materiais; "aco_inox_304" rugosidade_mm ∈ [0,015; 0,025]

GET /api/v1/singularidades/biblioteca
  "curva_90_rl": K=0,6; Le_sobre_D=16
  "valvula_gaveta": suporta_metodo_A=true
```

**T10.5 — Middleware de erro interno**
```
Mock de exceção não tratada → HTTP 500; "ERRO_INTERNO"
Stack trace ausente quando APP_DEBUG=false
```

**Critério de avanço:** T10.1–T10.5 passando; cobertura API ≥ 85%; global ≥ 90%

---

### v1.1.0 — Funcionalidades Avançadas

**Módulos a criar/expandir:**
```
app/api/v1/endpoints/comparar.py   POST /api/v1/comparar
app/schemas/comparacao.py
Expandir: endpoints/bomba.py       suporte a upload CSV multipart
```

**Testes a criar:**
```
tests/api/test_endpoint_comparar.py
```

**T11.1 — Upload CSV**
```
CSV válido via multipart/form-data
  HTTP 200; curva_hq[2] = {"Q_m3h": 100.0, "H_m": 36.0}

CSV inválido (Q decrescente) → 422; "CURVA_CSV_Q_NAO_CRESCENTE"
CSV decimal vírgula          → 422; "CURVA_CSV_FORMATO_DECIMAL"
```

**T11.2 — Comparação série vs. paralelo**
```
Q_op_serie < Q_op_paralelo
H_op_serie > H_op_paralelo
Ambas com status_npsh para 9 condições; velocidade_especifica_ns; tipo_bomba
```

**T11.3 — Modelo de viscosidade no payload**
```
modelo_viscosidade="walther"; T=40°C → ν≈110 cSt → Re<<4000 → laminar
campo "modelo_viscosidade_usado" = "walther"
```

**T11.4 — Consistência de serialização**
```
Serializar → Deserializar → Re-serializar payload_referencia
JSONs idênticos; sem perda de precisão float; campos opcionais preservados
```

**Critério de avanço:** T11.1–T11.4 passando; sem quebra de contrato com v1.0.0

---

## Referência Rápida de Erros por Fase

| Fase | Principais códigos novos |
|---|---|
| v0.1.0 | `TOPOLOGIA_MALHA_NAO_SUPORTADA`, `VAZAO_NEGATIVA`, `HW_*` |
| v0.2.0 | — (sem novos códigos) |
| v0.3.0 | — |
| v0.4.0 | `SEM_PONTO_OPERACAO_SHUT_OFF`, `SEM_PONTO_OPERACAO_FORA_CURVA`, `SEM_PONTO_OPERACAO` |
| v0.5.0 | — |
| v0.6.0 | — |
| v0.7.0 | — (status OK/AVISO/REPROVADO são campos de resultado, não códigos HTTP 422) |
| v0.8.0 | — |
| v0.9.0 | `CURVA_HQ_INVALIDA`, `CURVA_HQ_H_INVALIDO`, `ERRO_INTERNO` |
| v1.0.0 | `RESULTADO_NAO_ENCONTRADO`, `CAMPO_OBRIGATORIO` |
| v1.1.0 | `CURVA_CSV_*` (10 variantes) |
