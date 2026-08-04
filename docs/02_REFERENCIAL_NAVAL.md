# Referencial Naval — Geometria 3D e Normativas

**Versão:** 2.1 | **Base:** REFERENCIAL_v2.0.md + ARQUITETURA_v2.1.md

---

## 1. Convenção de Coordenadas Espaciais Navais

```
Eixo X: longitudinal — PROA POSITIVA (+X = vante; −X = popa/ré)
Eixo Y: transversal  — BOMBORDO POSITIVO (+Y = BB; −Y = EB)
Eixo Z: vertical     — ACIMA DA QUILHA POSITIVO
Origem: interseção da quilha com a meia-nau e o plano de simetria longitudinal
```

**Exemplo dos pontos de referência do caso de referência:**
```json
"pontos_sistema": {
  "succao":   {"x_m": -12.5, "y_m": 1.2, "z_m": 0.8},
  "bomba":    {"x_m": -11.0, "y_m": 1.2, "z_m": 1.5},
  "descarga": {"x_m":   5.0, "y_m": 1.2, "z_m": 4.2}
}
```

Interpretação:
- Sucção: 12,5 m à popa da meia-nau (X negativo), 1,2 m a BB, 0,8 m acima da quilha
- Descarga: 5,0 m à vante da meia-nau (X positivo), 1,2 m a BB, 4,2 m acima da quilha

> Esta convenção deve ser documentada como docstring no topo de `naval/geometria.py`.

---

## 2. Ângulos de Inclinação

```
θ (theta) — Trim (pitch): inclinação longitudinal
  +θ → proa acima (proa alta)
  −θ → proa abaixo (proa baixa)

φ (phi) — Banda (heel/roll): inclinação transversal
  +φ → bombordo desce (banda para BB)
  −φ → estibordo desce (banda para EB)
```

---

## 3. Matrizes de Rotação

### 3.1 Rotação por Trim θ (em torno do eixo Y)

```
R_theta = | cos θ    0    sin θ |
          |   0      1      0   |
          |−sin θ    0    cos θ |
```

### 3.2 Rotação por Banda φ (em torno do eixo X)

```
R_phi = | 1      0         0    |
        | 0    cos φ   −sin φ   |
        | 0    sin φ    cos φ   |
```

### 3.3 Matriz Composta R = R_phi · R_theta

```
R[0] = [  cos θ,        0,       sin θ      ]
R[1] = [ sin φ·sin θ,  cos φ,  −sin φ·cos θ ]
R[2] = [−cos φ·sin θ,  sin φ,   cos φ·cos θ ]
```

### 3.4 Cálculo do z_efetivo

```python
import numpy as np

def calcular_z_efetivo(ponto: dict, theta_rad: float, phi_rad: float) -> float:
    """
    Calcula a altura efetiva de um ponto no referencial inercial
    após inclinação do navio por trim θ e banda φ.

    Args:
        ponto: {"x_m": float, "y_m": float, "z_m": float}
        theta_rad: trim em radianos
        phi_rad:   banda em radianos

    Returns:
        z_efetivo em metros
    """
    ct, st = np.cos(theta_rad), np.sin(theta_rad)
    cp, sp = np.cos(phi_rad),   np.sin(phi_rad)

    # Linha 2 da matriz composta R = R_phi · R_theta
    R2 = np.array([−cp*st, sp, cp*ct])

    P = np.array([ponto["x_m"], ponto["y_m"], ponto["z_m"]])
    return float(R2 @ P)
```

### 3.5 Verificação de Prumo (θ=0°, φ=0°)

```
R(0°, 0°) = identidade
z_efetivo = z_original para todos os pontos

Golden values para prumo:
  z_efetivo_succao   = 0,8 m
  z_efetivo_descarga = 4,2 m
  H_geo = 4,2 − 0,8 = 3,40 m  ← golden value ±2%
  H_s   = 1,5 − 0,8 = 0,70 m
```

### 3.6 Cálculo de H_geo e H_s sob inclinação

```python
def calcular_H_geo_e_Hs(pontos: dict, theta_rad: float, phi_rad: float) -> tuple:
    z_suc = calcular_z_efetivo(pontos["succao"],   theta_rad, phi_rad)
    z_bom = calcular_z_efetivo(pontos["bomba"],    theta_rad, phi_rad)
    z_des = calcular_z_efetivo(pontos["descarga"], theta_rad, phi_rad)

    H_geo = z_des − z_suc
    H_s   = z_bom − z_suc   # positivo = reservatório acima da bomba

    return H_geo, H_s
```

---

## 4. Varredura Obrigatória de 9 Condições

O sistema deve calcular H_geo, H_s e NPSHd para **todas** as 9 condições. A condição crítica é aquela com menor NPSHd.

```python
CONDICOES = [
    {"nome": "prumo",          "theta_deg":   0.0, "phi_deg":   0.0},
    {"nome": "operacao_BB",    "theta_deg":  +5.0, "phi_deg": +15.0},
    {"nome": "operacao_EB",    "theta_deg":  +5.0, "phi_deg": −15.0},
    {"nome": "operacao_BB_inv","theta_deg":  −5.0, "phi_deg": +15.0},
    {"nome": "operacao_EB_inv","theta_deg":  −5.0, "phi_deg": −15.0},
    {"nome": "avaria_BB",      "theta_deg": +10.0, "phi_deg": +22.5},
    {"nome": "avaria_EB",      "theta_deg": +10.0, "phi_deg": −22.5},
    {"nome": "avaria_BB_inv",  "theta_deg": −10.0, "phi_deg": +22.5},
    {"nome": "avaria_EB_inv",  "theta_deg": −10.0, "phi_deg": −22.5},
]
```

### 4.1 Limites por condição (fonte: BV / Lloyd's / ABS)

| Condição | Trim θ | Banda φ |
|---|---|---|
| Normal (prumo) | 0° | 0° |
| Operação | ±5° | ±15° |
| Avaria | ±10° | ±22,5° |

### 4.2 Condições de operação vs. avaria (para status D4)

```
Condições de operação (índices 1–4): operacao_BB, operacao_EB, operacao_BB_inv, operacao_EB_inv
Condições de avaria   (índices 5–8): avaria_BB, avaria_EB, avaria_BB_inv, avaria_EB_inv
Prumo (índice 0): sempre verificado
```

### 4.3 Regra de status (D4)

```
status = "OK"        → NPSHd ≥ critério em TODAS as 9 condições
status = "AVISO"     → NPSHd ≥ critério nas 5 de operação/prumo,
                        mas < critério em ≥1 das 4 de avaria
status = "REPROVADO" → NPSHd < critério em ≥1 das 5 condições de operação/prumo
```

### 4.4 Golden values de avaria (para testes de regressão)

```
Condição: avaria_BB (θ=+10°, φ=+22,5°)

Cálculo da linha R[2] da matriz composta:
  cos(10°) = 0,9848; sin(10°) = 0,1736
  cos(22,5°) = 0,9239; sin(22,5°) = 0,3827

  R[2] = [−cos(22,5°)·sin(10°),  sin(22,5°),  cos(22,5°)·cos(10°)]
       = [−0,1604,               0,3827,       0,9096              ]

Para descarga P = [+5,0; 1,2; 4,2]:
  z_efetivo = (−0,1604×5,0) + (0,3827×1,2) + (0,9096×4,2)
            = −0,802 + 0,459 + 3,820 = 3,477 m

Para sucção P = [−12,5; 1,2; 0,8]:
  z_efetivo = (−0,1604×(−12,5)) + (0,3827×1,2) + (0,9096×0,8)
            = 2,005 + 0,459 + 0,728 = 3,192 m

H_geo_bruto(+10°, +22,5°) = 3,477 − 3,192 = 0,285 m

NOTA: O golden value H_geo = 2,98 m e NPSHd = 4,40 m referem-se ao
resultado do pipeline integrado (com recálculo de perdas na inclinação),
não ao H_geo bruto de diferença de cotas. Validar via Teste 9.1.
```

---

## 5. Classes de Tubulação por Classificadora

### 5.1 Bureau Veritas (BV) — NR 467

| Classe | Pressão | Temperatura |
|---|---|---|
| I | P > 16 bar | T > 300°C |
| II | 7 bar < P ≤ 16 bar | 170°C < T ≤ 300°C |
| III | P ≤ 7 bar | T ≤ 170°C |

### 5.2 Lloyd's Register (LR)

| Classe | Pressão | Temperatura |
|---|---|---|
| I | P > 20 bar | T > 300°C |
| II | 7 bar < P ≤ 20 bar | 170°C < T ≤ 300°C |
| III | P ≤ 7 bar | T ≤ 170°C |

> **Divergência BV vs LR:** para P = 18 bar → Classe I pela BV, Classe II pela LR. O sistema reporta as duas classificações separadamente com nota de divergência.

### 5.3 ABS (American Bureau of Shipping)

| Classe | Pressão | Temperatura |
|---|---|---|
| I | P > 16 bar | T > 300°C |
| II | 7 bar < P ≤ 16 bar | 170°C < T ≤ 300°C |
| III | P ≤ 7 bar | T ≤ 170°C |

---

## 6. Velocidades Limite por Fluido e Serviço

| Fluido / Serviço | Sucção (m/s) | Recalque (m/s) | Ref. |
|---|---|---|---|
| Água (serviço geral) | 0,5–1,5 | 1,5–3,0 | Lloyd's Pt 5 Ch 5 |
| Água do mar | 0,5–1,2 | 1,0–2,5 | BV Pt C Ch 2 |
| Água de resfriamento | 0,5–1,5 | 1,5–2,5 | ABS Pt 4 Ch 3 |
| Óleo combustível (frio) | 0,3–0,8 | 0,5–1,5 | Lloyd's Pt 5 Ch 6 |
| Óleo combustível (quente) | 0,5–1,2 | 1,0–2,0 | Lloyd's Pt 5 Ch 6 |
| Óleo lubrificante | 0,3–0,8 | 0,5–1,5 | Lloyd's Pt 5 Ch 7 |
| Óleo hidráulico | — | 1,0–4,0 | ISO 4413 |
| Esgoto / resíduos | 0,5–1,0 | 1,0–2,0 | MARPOL / BV |
| Lastro | 1,0–2,0 | 2,0–4,0 | BV Pt C Ch 1 |
| Combate a incêndio | — | 3,0–5,0 | SOLAS / NFPA 20 |

---

## 7. Verificação de Redundância para Sistemas Essenciais

### 7.1 Quatro cenários obrigatórios de teste

| Cenário | Condição | Resultado esperado | Não-conformidades |
|---|---|---|---|
| A | Essencial, 1 bomba, alimentações não independentes | `REPROVADO` | 2 |
| B | Essencial, 2 bombas, alimentações independentes | `APROVADO` | 0 |
| C | Não-essencial, 1 bomba, sem standby | `APROVADO` | 0 |
| D | Essencial, 2 bombas, alimentações não independentes | `REPROVADO` | 1 |

### 7.2 Regras de verificação

```python
def verificar_redundancia(sistema_essencial, n_bombas, alimentacoes_independentes):
    nao_conformidades = []

    if sistema_essencial:
        if n_bombas < 2:
            nao_conformidades.append("bomba_standby_ausente")
        if not alimentacoes_independentes:
            nao_conformidades.append("alimentacoes_nao_independentes")

    return {
        "status": "APROVADO" if len(nao_conformidades) == 0 else "REPROVADO",
        "nao_conformidades": nao_conformidades
    }
```

---

## 8. Sistemas Navais Típicos

| Sistema | Fluido | BV | Lloyd's | ABS |
|---|---|---|---|---|
| Resfriamento — mar | Água do mar | Pt C, Ch 1 | Pt 5, Ch 12 | Pt 4, Ch 3 |
| Resfriamento — doce | Água doce | Pt C, Ch 1 | Pt 5, Ch 12 | Pt 4, Ch 3 |
| Lastro | Água do mar | Pt C, Ch 1 | Pt 5, Ch 8 | Pt 4, Ch 7 |
| Combustível | Óleo | Pt C, Ch 2 | Pt 5, Ch 6 | Pt 4, Ch 6 |
| Lubrificação | Óleo lubrificante | Pt C, Ch 2 | Pt 5, Ch 7 | Pt 4, Ch 3 |
| Hidráulico | Óleo hidráulico | Pt C, Ch 3 | Pt 5, Ch 11 | Pt 4, Ch 3 |
| Incêndio | Água do mar/doce | Pt C, Ch 4 | Pt 5, Ch 9 | Pt 4, Ch 4 |
| Esgoto | Efluentes | Pt C, Ch 5 | Pt 5, Ch 10 | Pt 4, Ch 9 |
| Água potável | Água doce | Pt C, Ch 5 | Pt 5, Ch 10 | Pt 4, Ch 9 |

---

## 9. Limitação Topológica — Malha Fechada

O sistema suporta exclusivamente topologia aberta:
- Trechos em série
- Ramificações simples (tê sem retorno)

**Não suporta** (rejeitar com `TOPOLOGIA_MALHA_NAO_SUPORTADA`):
- Anéis de incêndio naval
- Redes de lastro com manifold bidirecional
- Qualquer grafo com ciclo

```python
def detectar_malha_fechada(trechos: list) -> bool:
    """
    Heurística: se qualquer trecho define id_destino igual ao id
    de um trecho já processado, há malha fechada.

    Para detecção completa de ciclos em grafos complexos,
    usar DFS com marcação de back-edges.
    """
    ids_vistos = set()
    for trecho in trechos:
        if hasattr(trecho, 'id_destino') and trecho.id_destino in ids_vistos:
            return True
        ids_vistos.add(trecho.id)
    return False
```

A detecção deve ocorrer em `unit_casting.py`, **antes** de qualquer cálculo hidráulico.

---

## 10. Glossário Naval

| Termo | Definição |
|---|---|
| **Bombordo (BB)** | Lado esquerdo ao olhar para a proa (+Y) |
| **Estibordo (EB)** | Lado direito ao olhar para a proa (−Y) |
| **Proa / Vante** | Parte dianteira do navio (+X) |
| **Popa / Ré** | Parte traseira do navio (−X) |
| **Meia-nau** | Ponto médio longitudinal (origem X) |
| **Trim (pitch)** | Inclinação longitudinal (θ) |
| **Banda (heel/roll)** | Inclinação transversal (φ) |
| **Kingston** | Válvula de fundo do casco (sea chest valve) |
| **H_geo** | Diferença de cota entre descarga e sucção |
| **H_s** | Altura da lâmina d'água ao eixo da bomba |
| **MAWP** | Maximum Allowable Working Pressure |
| **NPSHd** | NPSH disponível — calculado pelo sistema |
| **NPSHr** | NPSH requerido — informado pelo fabricante |
| **Nss** | Velocidade específica de sucção |
| **Ns** | Velocidade específica da bomba |
| **HFO** | Heavy Fuel Oil (380 cSt a 50°C) |
| **MDO/DO** | Marine Diesel Oil |
| **GRP** | Glass Reinforced Plastic |
| **VFD** | Variable Frequency Drive (inversor de frequência) |
| **BV** | Bureau Veritas |
| **LR** | Lloyd's Register |
| **ABS** | American Bureau of Shipping |
| **SistemaSI** | Estrutura interna com todas as grandezas em SI |
| **alpha_cinetico** | Coeficiente de Coriolis na equação de Bernoulli |
| **alpha_viscos** | Coeficiente do modelo Linear de viscosidade |
| **condicao_critica** | Condição com menor NPSHd entre as 9 varridas |
| **golden value** | Valor numérico fixado para testes de regressão |
