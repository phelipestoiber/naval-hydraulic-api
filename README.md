# ⚓ Naval Hydraulic Calculator API

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-85%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

Motor de cálculo hidráulico e dimensionamento eletromecânico de plantas de bombeamento navais, com varredura espacial 3D de inclinação estática/dinâmica (prumo, Trim, banda, avaria), verificação de normas de sociedades classificadoras (BV, LR, ABS, DNV) e API REST pública baseada em FastAPI.

---

## 🗺️ Guias de Documentação Especializados

Para atender com máxima clareza tanto engenheiros de bordo quanto desenvolvedores de software, a documentação está dividida em dois manuais técnicos completos:

```
│
├── 👷 Guia de Engenharia Naval e Hidráulica  ──> docs/GUIA_ENGENHARIA_NAVAL.md
└── 💻 Guia de Desenvolvedores e API REST     ──> docs/GUIA_DESENVOLVEDORES_API.md
```

- **[Guia de Engenharia Naval](docs/GUIA_ENGENHARIA_NAVAL.md)**: Explicações físicas e normativas sem termos de programação, casos de estudo reais de bordo (Resfriamento ME, Óleo HFO, Esgoto de Porão em Avaria, Incêndio SOLAS), equações de Churchill, Darcy-Weisbach, PCHIP, NPSH, 9 condições 3D e matrizes de decisão.
- **[Guia de Desenvolvedores API](docs/GUIA_DESENVOLVEDORES_API.md)**: Especificação da API REST, schemas JSON de entrada/saída, tabela de códigos de erro (`ErrorResponse`), arquitetura em camadas, exemplos em Python, JavaScript/TypeScript, cURL e Docker.

---

## 🛠️ Guia Passo a Passo Detalhado de Instalação
> **Nota para Engenheiros e Iniciantes**: Não é preciso ser um programador experiente para rodar esta ferramenta no seu computador. Siga o passo a passo simples abaixo!

---

### Passo 1: Verificar e Instalar o Python

Esta ferramenta necessita do **Python versão 3.11 ou superior** instalado no seu computador.

1. Abra o **PowerShell** ou **Prompt de Comando** (no Windows, pressione as teclas `Windows + R`, digite `powershell` e aperte `Enter`).
2. Digite o comando abaixo e aperte `Enter`:
   ```powershell
   python --version
   ```
3. **Se aparecer `Python 3.11.x` ou `Python 3.12.x` / `3.13.x`**: O Python já está pronto! Avance para o Passo 2.
4. **Se der erro ou a versão for antiga (ex: Python 2.7 ou 3.8)**:
   - Baixe a versão mais recente em: [python.org/downloads](https://www.python.org/downloads/)
   - ⚠️ **MUITO IMPORTANTE NA INSTALAÇÃO DO WINDOWS**: Na primeira tela do instalador do Python, **marque obrigatoriamente a caixa de seleção**:
     > `☑ Add python.exe to PATH` (Adicionar Python ao PATH)
   - Clique em *"Install Now"* e aguarde a conclusão.

---

### Passo 2: Baixar a Aplicação

Você pode obter os arquivos da aplicação de duas formas:

- **Opção A (Via Git)**:
  No PowerShell, execute:
  ```powershell
  git clone https://github.com/phelipestoiber/naval-hydraulic-api.git
  cd naval-hydraulic-api
  ```

- **Opção B (Arquivo ZIP)**:
  Baixe o arquivo `.zip` da aplicação, extraia para uma pasta no seu computador (ex: `C:\Projetos\naval-hydraulic-api`) e abra o PowerShell dentro dessa pasta.

---

### Passo 3: Criar um Ambiente Virtual (`.venv`)

O ambiente virtual é uma "caixa isolada" no computador para garantir que as bibliotecas da API não entrem em conflito com outros programas instalados.

No PowerShell (dentro da pasta do projeto), digite:

#### No Windows:
```powershell
# 1. Criar o ambiente virtual
python -m venv .venv

# 2. Ativar o ambiente virtual
.\.venv\Scripts\activate
```
*(Quando ativado com sucesso, o texto `(.venv)` aparecerá no início da linha do seu PowerShell).*

#### No Linux ou macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Passo 4: Instalar as Dependências

Com o ambiente `(.venv)` ativado, instale todas as bibliotecas de cálculo executando:

```powershell
pip install -r pyproject.toml
```
*(Aguarde alguns segundos até que a mensagem de instalação concluída apareça).*

---

### Passo 5: Executar o Servidor da API

Para iniciar o motor de cálculo da aplicação, execute o comando:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Se tudo deu certo, você verá uma mensagem similar a esta no terminal:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Pronto! A API está **rodando perfeitamente** no seu computador! 🎉

---

## 🌐 Como Usar a Interface Gráfica Interativa (Sem Programar)

Você não precisa escrever código para testar seus cálculos. A API possui uma **Interface Gráfica Interativa (Swagger UI)** no próprio navegador!

1. Abra o seu navegador de internet (Chrome, Edge, Firefox).
2. Acesse o endereço: **[http://localhost:8000/docs](http://localhost:8000/docs)**
3. Clique no botão verde do endpoint **`POST /api/v1/calcular`**.
4. Clique no botão **"Try it out"** no canto superior direito do bloco.
5. Cole os dados do seu projeto no quadro de texto e clique no botão azul **"Execute"**.
6. O resultado completo (incluindo o status `OK`, velocidades, NPSH em avaria e motor ABNT em CV) aparecerá na tela imediatamente abaixo!

---

## ❓ Solução de Problemas Frequentes durante a Instalação (Troubleshooting)

### 🔴 Problema 1: `"python não é reconhecido como um comando interno ou externo"`
- **Causa**: O Python foi instalado no Windows sem marcar a caixa *"Add Python to PATH"*.
- **Solução**: Abra o instalador do Python novamente, escolha a opção *Modify* (Modificar) e marque a opção **Add Python to Environment Variables / PATH**.

### 🔴 Problema 2: `"A execução de scripts foi desativada neste sistema"` (Ao ativar `.venv\Scripts\activate`)
- **Causa**: Política de segurança padrão do PowerShell no Windows.
- **Solução**: No PowerShell, execute o comando abaixo e tente ativar novamente:
  ```powershell
  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### 🔴 Problema 3: `"Port 8000 is already in use"` (Porta em uso)
- **Causa**: Outro programa já está utilizando a porta 8000.
- **Solução**: Inicie a aplicação em outra porta (ex: 8080):
  ```powershell
  uvicorn app.main:app --reload --port 8080
  ```
  E acesse em: `http://localhost:8080/docs`

---

## 💡 Exemplo Rápido de Requisição via cURL

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/calcular' \
  -H 'Content-Type: application/json' \
  -d '{
  "projeto": {
    "nome": "Sistema de Resfriamento — ME Principal",
    "navio": "MV Example",
    "classificadora": "BV"
  },
  "fluido": {
    "tipo": "agua_salgada",
    "temperatura_C": 32,
    "densidade_kg_m3": 1025,
    "viscosidade_dinamica_Pa_s": 0.001
  },
  "sistema": {
    "unidade_vazao": "m3h",
    "vazao": 118.5,
    "pontos_sistema": {
      "succao": {"z_m": 0.8},
      "bomba": {"z_m": 1.5},
      "descarga": {"z_m": 4.2}
    }
  },
  "bomba": {
    "rotacao_rpm": 1450,
    "curva_hq": [
      {"Q_m3h": 0, "H_m": 42},
      {"Q_m3h": 50, "H_m": 40},
      {"Q_m3h": 118.5, "H_m": 36},
      {"Q_m3h": 150, "H_m": 28},
      {"Q_m3h": 180, "H_m": 18}
    ]
  }
}'
```

### Resposta Resumida:

```json
{
  "id_calculo": "e83b48f9-467a-4c28-98e3-85f6e80b2a8d",
  "status": "OK",
  "resultados_prumo": {
    "velocidade_succao_m_s": 1.87,
    "velocidade_descarga_m_s": 2.69,
    "reynolds_succao": 287000.0,
    "h_geo_m": 3.4,
    "altura_manometrica_m": 8.45,
    "npsh_disponivel_m": 4.85,
    "velocidade_especifica_ns": 63.7,
    "tipo_bomba": "centrifuga_mista",
    "motor_selecionado_cv": 7.5
  }
}
```

---

## 📁 Estrutura da Base de Código

```
naval-hydraulic-api/
├── app/
│   ├── api/v1/endpoints/   # Endpoints HTTP da API REST (FastAPI)
│   ├── core/               # Núcleo hidráulico e naval (Python puro em Dataclasses)
│   ├── data/               # Bibliotecas de materiais, acessórios e normas
│   ├── db/                 # Repositório de persistência em memória (UUID v4)
│   ├── schemas/            # DTOs de validação Pydantic v2
│   └── main.py             # Aplicação principal FastAPI e tratamento de erros
├── docs/
│   ├── GUIA_ENGENHARIA_NAVAL.md    # Manual de física hidráulica, 9 condições 3D e normas
│   └── GUIA_DESENVOLVEDORES_API.md # Manual técnico da API REST, Schemas e Erros
├── tests/                  # 85 testes automatizados (unitários, integração e API)
└── README.md
```

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para mais detalhes.
