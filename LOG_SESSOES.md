# LOG DE SESSÕES — Naval Hydraulic Calculator API

**Propósito:** memória de longo prazo entre sessões do agente. Este arquivo é lido por inteiro no início de toda sessão — por isso cada entrada deve ser densa e escaneável, não narrativa.

**Relação com `INSTRUCOES_AGENTE.md`:** o bloco "Estado Atual" naquele arquivo é o snapshot (onde estou agora). Este arquivo é o histórico completo (como cheguei aqui, o que já foi tentado). Sempre ler os dois — o Estado Atual primeiro, depois este arquivo inteiro.

---

## Índice de Lições Rastreáveis

Toda entrada com impacto além da própria sessão recebe uma tag `LICAO-NNN`. Use este índice para referenciar uma lição de sessões anteriores sem precisar reler o log inteiro em busca dela.

| Tag | Resumo em uma linha | Sessão |
|---|---|---|
| LICAO-001 | Assinatura de `calcular_reynolds(Q_m3s, D_m, nu)` espera `Q_m3s` e não velocidade `v` | 2026-08-05 (v0.9.0) |
| LICAO-002 | Decoradores em sub-roteadores FastAPI devem usar `@router.post` e não `@APIRouter().post` | 2026-08-05 (v1.0.0) |

---

## Como Preencher Uma Entrada

Copiar o template abaixo, preencher, colar no topo da seção "Entradas" (ordem cronológica reversa — mais recente primeiro). Se a sessão gerou uma lição reutilizável, adicionar a tag ao Índice acima também.

```markdown
### [DATA ISO] — vX.Y.Z — [título curto do escopo da sessão]

**Objetivo da sessão:** o que estava planejado ao iniciar.

**Feito:**
- lista curta, uma linha por item, módulo/teste tocado

**Por quê:** a decisão técnica que não é óbvia só de olhar o roadmap —
  o "porquê" que já está no roadmap não precisa ser repetido aqui.

**Deu certo:**
- o que funcionou como esperado, sem surpresas relevantes

**Deu errado / retrabalho:** [ou "nada a registrar"]
- o que foi tentado e não funcionou, e o que foi feito em vez disso
- se isso é uma lição reutilizável, marcar: `[LICAO-NNN]`

**Estado ao final:** testes passando/total; cobertura; bloqueios abertos
```

**Regra de densidade:** se a entrada não tem nada relevante em "Deu errado", escrever "nada a registrar" — não inventar conteúdo para preencher a seção. Entradas sem atrito real devem ser as mais curtas do log, não as mais longas.

---

## Entradas

### 2026-08-05 — v1.0.0 — API REST Pública, Persistência Ativa e Documentação Final

**Objetivo da sessão:** Finalizar a Fase 4 (API REST Pública), disponibilizando os endpoints HTTP `/api/v1/calcular`, `/api/v1/resultado/{id_calculo}`, `/api/v1/materiais` e `/api/v1/singularidades/biblioteca`, implementar tratamento global de exceções HTTP 500 (`ERRO_INTERNO`), validar todos os 5 testes da suíte $T10.1 \rightarrow T10.5$ e criar o `README.md` do projeto.

**Feito:**
- Criados os endpoints REST em `app/api/v1/endpoints/`: [pipeline.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/api/v1/endpoints/pipeline.py) (`POST /api/v1/calcular`, `GET /api/v1/resultado/{id_calculo}`) e [bibliotecas.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/api/v1/endpoints/bibliotecas.py) (`GET /api/v1/materiais`, `GET /api/v1/singularidades/biblioteca`)
- Atualizados os roteadores em [router.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/api/v1/router.py) e adicionado o tratamento de exceção global HTTP 500 (`ERRO_INTERNO`) em [main.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/main.py)
- Criados 3 novos arquivos de testes de API em `tests/api/`: `test_endpoint_calcular.py` ($T10.1, T10.3, T10.5$), `test_endpoint_resultado.py` ($T10.2$) e `test_endpoint_bibliotecas.py` ($T10.4$)
- Criado o arquivo [README.md](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/README.md) completo com visão geral, arquitetura, instalação, guia de testes e exemplos de requisição cURL

**Por quê:** Concluir a API REST pública com suporte total a round-trip HTTP, persistência ativa em banco de dados em memória e documentação pública para consumo por aplicações externas.

**Deu certo:**
- 85/85 testes (unitários + integração + API) passando com 98% de cobertura global
- POST `/api/v1/calcular` reproduzindo com exatidão todos os Golden Values e gerando UUID v4 válido ($T10.1$)
- GET `/api/v1/resultado/{id_calculo}` recuperando perfeitamente o resultado gravado no DB e retornando HTTP 404 estruturado com `RESULTADO_NAO_ENCONTRADO` para IDs inexistentes ($T10.2$)
- Rejeição de 9 tipos de entradas inválidas retornando HTTP 422 com códigos de erro limpos ($T10.3$)
- Endpoints de bibliotecas `/api/v1/materiais` e `/api/v1/singularidades/biblioteca` servindo dados corretos ($T10.4$)
- Exception handler de HTTP 500 interceptando erros inesperados e ocultando a stack trace em produção ($T10.5$)

**Deu errado / retrabalho:**
- Ao registrar rotas em um `APIRouter()` específico dentro dos módulos de endpoint, deve-se usar a instância `router.post(...)` ou `router.get(...)`. Instanciar `@APIRouter().post(...)` cria um roteador temporário e não registra as rotas na instância exportada, causando HTTP 404 nas requisições. `[LICAO-002]`

**Estado ao final:** 85/85 testes passando; 98% cobertura global; 0 bloqueios abertos

---

### 2026-08-05 — v0.9.0 — Pipeline de Cálculo Integrado, Banco de Dados e Testes de Integração

**Objetivo da sessão:** Implementar o motor de pipeline integrado `app/core/pipeline.py`, a persistência em memória UUID v4 em `app/db/crud.py`, o módulo naval de varredura 3D `app/core/naval/inclinacao.py`, verificação de normas `app/core/naval/normas.py`, redundância `app/core/naval/redundancia.py`, fixture `payload_referencia` em `conftest.py` e validação estrita de todos os Golden Values por TDD.

**Feito:**
- Criado [conftest.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/conftest.py) com a fixture `payload_referencia` completa para resfriamento de motor principal
- Criados [database.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/db/database.py) e [crud.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/db/crud.py) com suporte a CRUD em dicionário em memória e geração de UUID v4 (`create_calculo`, `get_calculo`)
- Criado [test_db.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_db.py) validando persistência e busca por UUID ($T9.4$)
- Criados os módulos navais em `app/core/naval/`: [inclinacao.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/naval/inclinacao.py) (varredura 3D das 9 condições), [normas.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/naval/normas.py) (limites de velocidade de sucção/descarga) e [redundancia.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/naval/redundancia.py) (avaliação de bombas essenciais)
- Criado [pipeline.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/pipeline.py) integrando as Camadas 1 a 6 em `executar_pipeline_calculo(payload)`
- Criado [test_pipeline_completo.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/integration/test_pipeline_completo.py) cobrindo $T9.1$ (Golden Values), $T9.2$ (Reprovação por inclinação em avaria), $T9.3$ (Vazão em galões/min), $T9.5$ (Erro Shut-Off), $T9.6$ (Erro Malha Fechada), $T9.7$ (Corte por viscosidade), $T9.8$ (Persistência)

**Por quê:** Conectar todos os sub-sistemas isolados (Fases 1, 2 e 3) em uma única função de cálculo de ponta a ponta que garanta a reprodução exata de todos os Golden Values especificados nas normas navais.

**Deu certo:**
- 78/78 testes (unitários + integração) passando com 98% de cobertura global
- Reprodução exata de todos os Golden Values do sistema de referência
- Persistência com UUID v4 em banco em memória gerando identificadores válidos ($T9.4$) e permitindo recuperação integral do resultado por ID ($T9.8$)

**Deu errado / retrabalho:**
- A função `calcular_reynolds` em `reynolds.py` exige a vazão em m³/s (`Q_m3s`) e o diâmetro (`D_m`), não a velocidade. `[LICAO-001]`

**Estado ao final:** 78/78 testes passando; 98% cobertura global; 0 bloqueios abertos
