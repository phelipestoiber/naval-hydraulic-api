# INSTRUÇÕES DO AGENTE — Naval Hydraulic Calculator API

**Versão:** 3.0  
**Atualizar esta seção de estado ao iniciar cada sessão.**

---

## Estado Atual do Projeto

```
Versão implementada:  v1.0.0
Próxima versão:       v1.1.0
Fase atual:           Fase 4 Concluída / Funcionalidades Avançadas (v1.1.0)

Testes passando:      85 / 85
Testes pendentes:     11.1 → 11.4 (v1.1.0)
Cobertura global:     98%

Bloqueios conhecidos: nenhum
Última sessão:        2026-08-05 — v1.0.0 — API REST Pública, Persistência, Endpoints e Documentação Final
```

**Instrução de atualização:** ao encerrar cada sessão, reescrever o bloco acima com o estado real. Nunca iniciar uma sessão sem ler este bloco primeiro.

---

## LOG_SESSOES.md — Leitura e Escrita Obrigatórias

**`LOG_SESSOES.md`** é o histórico completo de implementação — memória de longo prazo entre sessões, complementar ao snapshot acima.

**OBRIGATÓRIO ao iniciar qualquer sessão:** ler `LOG_SESSOES.md` por inteiro, incluindo o Índice de Lições Rastreáveis no topo, **antes** de tocar em qualquer código. O Estado Atual diz onde parar; o log diz o que já foi tentado — inclusive o que falhou e por quê. Reimplementar uma abordagem já descartada em uma sessão anterior é o sintoma exato que este arquivo existe para evitar.

**OBRIGATÓRIO ao encerrar qualquer sessão** que tocou código (implementou, corrigiu, refatorou — não apenas leu documentação): adicionar uma entrada nova ao topo da seção "Entradas" de `LOG_SESSOES.md`, seguindo o template definido naquele arquivo. Uma sessão sem entrada de log é uma sessão cujo trabalho não pode ser auditado nem retomado com segurança pela próxima sessão.

**OBRIGATÓRIO ao encerrar qualquer sessão** que tocou código: sugerir os comandos git prontos para copiar e colar, no formato definido em `docs/03_ARQUITETURA.md` Seção 13.6. Distinguir entre sessão parcial (`wip`) e versão fechada (`feat` + tag). Se a versão fechou, incluir também os comandos de tag e push. O desenvolvedor executa os comandos manualmente — o agente nunca executa git diretamente.

Se a sessão revelou algo reutilizável — uma armadilha, uma decisão que valeu a pena documentar, um padrão que se repetiu — marcar com tag `LICAO-NNN` (próximo número sequencial) e adicionar ao Índice de Lições no topo do arquivo. Nem toda entrada gera uma lição; forçar uma tag onde não há nada reutilizável degrada o índice.

---

## Guardrails — Inegociáveis

Estas regras se aplicam a **todos os arquivos, em todas as versões, sem exceção**.

**PROIBIDO:** qualquer `import` de `fastapi`, `sqlalchemy`, `pydantic` ou `httpx` dentro de qualquer arquivo sob `app/core/`. O diretório `core/` recebe e retorna exclusivamente dataclasses Python puras (`SistemaSI`, `RastreabilidadeUnidades`, `ResultadoOutput`).

**PROIBIDO:** converter unidades de engenharia (m³/h, mm, bar, °C, cSt) em qualquer módulo que não seja `app/core/unit_casting.py`. Esta é a única fronteira dimensional do sistema. Todo valor que entra pelo payload em unidade de engenharia deve sair de `unit_casting.py` já em SI antes de chegar a qualquer função de `core/`.

**PROIBIDO:** usar `scipy.interpolate.CubicSpline` para interpolar curvas de bomba. Usar exclusivamente `scipy.interpolate.PchipInterpolator`. Razão: CubicSpline não garante monotonicidade e pode gerar overshoot físico impossível em curvas H×Q planas.

**PROIBIDO:** iniciar qualquer iterador numérico (bisseção, Newton-Raphson) sem executar primeiro o boundary check de existência de raiz. Verificar `g(Q_min)` e `g(Q_max)` antes do loop. Se não houver troca de sinal, lançar `ErroCalculo` com código específico antes de entrar no loop.

**PROIBIDO:** usar `assert` para validações de entrada. Usar exclusivamente `@field_validator` do Pydantic v2, que produz `ErrorResponse` estruturado com campo `codigo`.

**OBRIGATÓRIO:** TDD estrito. O arquivo de teste deve existir, ser executado e **falhar** antes de criar o módulo que o fará passar. Nunca criar o módulo antes do teste.

**OBRIGATÓRIO:** ao detectar topologia em malha fechada nos trechos do payload (qualquer `id_destino` apontando para um trecho já visitado), lançar `ErroCalculo` com `codigo="TOPOLOGIA_MALHA_NAO_SUPORTADA"` imediatamente em `unit_casting.py`, antes de qualquer cálculo hidráulico. Zero valores intermediários de cálculo devem ser retornados junto com este erro.

**OBRIGATÓRIO:** ao finalizar cada versão, verificar cobertura de testes:
- `app/core/` → ≥ 95%
- `app/api/` → ≥ 85%
- Global → ≥ 90%

Não avançar para a próxima versão sem todos os critérios satisfeitos.

---

## Premissas Gerais do Projeto

- **Fluido:** qualquer Newtoniano (τ = μ·dv/dy). Não-Newtonianos → `FLUIDO_NAO_NEWTONIANO`
- **Regime:** laminar, transição e turbulento
- **Escoamento:** incompressível, permanente, unidimensional (ver limitação de malha fechada)
- **Pressão:** baixa a média (classes I/II/III por classificadora)
- **Deploy:** local/intranet de estaleiro, com suporte a Docker
- **Interface:** API REST exclusivamente — sem frontend nesta versão

## Regra de Status do Resultado — Atenção Especial

**Não confundir NPSH, BEP e redundância na mesma regra.** São três verificações independentes que compõem o `status` final pelo **pior valor entre elas**:

```
Regra primária (NPSH por inclinação):
  "OK"        → NPSHd ≥ critério nas 9 condições
  "AVISO"     → NPSHd ok nas 5 de operação/prumo; falha em ≥1 das 4 de avaria
  "REPROVADO" → NPSHd falha em qualquer condição de operação/prumo

Regras complementares (agravam, nunca abrandam):
  status_bep = "ALERTA"                      → eleva para no mínimo "AVISO"
  verificacao_redundancia.status="REPROVADO" → eleva para "REPROVADO"

status_final = pior(status_npsh, status_bep_convertido, status_redundancia)
```

## Golden Values — Regressão Obrigatória

Estes valores devem ser reproduzidos pelo pipeline com as tolerâncias indicadas. Qualquer alteração que mude um golden value é um BREAKING CHANGE e deve ser documentada.

| Grandeza | Condição | Valor esperado | Tolerância |
|---|---|---|---|
| Reynolds sucção | Prumo | 287.000 | ±2% |
| Velocidade sucção | Prumo | 1,87 m/s | ±2% |
| Velocidade descarga | Prumo | 2,69 m/s | ±2% |
| H_geo | Prumo (0°, 0°) | 3,40 m | ±2% |
| H_s (bomba) | Prumo (0°, 0°) | 0,70 m | ±2% |
| Altura manométrica | Prumo | 8,45 m | ±5% |
| NPSHd | Prumo (0°, 0°) | 4,82 m | ±5% |
| NPSHd | Avaria BB (+10°, +22,5°) | 4,40 m | ±5% |
| H_geo integrado | Avaria BB (+10°, +22,5°) | 2,98 m | ±5% |
| Velocidade específica Ns | Ponto de operação | ≈ 63,7 | ±5% |
| Tipo de bomba | Ponto de operação | centrifuga_mista | exato |
| Motor selecionado | Caso de referência | 7,5 CV | exato |

---

## Mapa dos Documentos de Referência

Consultar o documento correspondente ao módulo sendo implementado:

| Implementando | Consultar |
|---|---|
| Reynolds, viscosidade, Darcy-Weisbach, Churchill, Haaland, Hazen-Williams, NPSH, Ns, leis de afinidade | `docs/01_REFERENCIAL_MATEMATICO.md` |
| Geometria 3D, matrizes de rotação, varredura de 9 condições, normas BV/LR/ABS, redundância | `docs/02_REFERENCIAL_NAVAL.md` |
| Estrutura de pastas, schemas Pydantic, endpoints, banco de dados, códigos de erro | `docs/03_ARQUITETURA.md` |
| Fases de implementação, critérios de avanço, testes completos de cada versão | `docs/04_ROADMAP.md` |
| **Qualquer sessão — antes de começar e ao terminar** | `LOG_SESSOES.md` (leitura e escrita obrigatórias) |

---

## Limitações de Escopo — Rejeitar com Código

O sistema **não suporta** os itens abaixo. Ao detectar qualquer um, rejeitar com HTTP 422 e código indicado — nunca processar silenciosamente:

| Limitação | Código de rejeição |
|---|---|
| Topologia em malha fechada (loops, anéis) | `TOPOLOGIA_MALHA_NAO_SUPORTADA` |
| Fluidos não-Newtonianos | `FLUIDO_NAO_NEWTONIANO` |
| Escoamento compressível / multifásico / transiente | `FLUIDO_INVALIDO` |
| Verificação estrutural ASME B31 | fora do escopo — não implementar |

---

## Sequência de Versões (resumo)

```
FASE 1 — Núcleo Hidráulico
  v0.1.0  Fundação: math_utils (PCHIP), unit_casting, reynolds, viscosidade,
           csv_utils, detecção de malha (F1), schemas JSON estáticos
  v0.2.0  Fator de atrito: Churchill, Colebrook, Swamee-Jain, Haaland, Darcy
  v0.3.0  Perdas localizadas: HW, singularidades, Bernoulli, sistema

FASE 2 — Bombas
  v0.4.0  Interpolação PCHIP (F2), ponto_operacao com boundary check (F3),
           velocidade_especifica, bep
  v0.5.0  NPSH: NPSHd, NPSHr aprox., 3 métodos de margem, Nss
  v0.6.0  Potência ABNT, afinidade (Métodos A/B/C), pré-dimensionamento

FASE 3 — Naval
  v0.7.0  Geometria 3D, matrizes R(θ,φ), varredura 9 condições,
           status OK/AVISO/REPROVADO, condicoes_reprovadas
  v0.8.0  Normas BV/LR/ABS, MAWP, velocidades, redundância (4 cenários)

FASE 4 — API REST
  v0.9.0  Pipeline completo, banco de dados, ErrorResponse, conftest,
           testes de integração
  v1.0.0  Todos os endpoints, persistência ativa, middleware de erro, README
  v1.1.0  Upload CSV, POST /comparar, modelos de viscosidade no payload
```
