from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.erro import ErroCalculo
from app.api.v1.router import api_router

app = FastAPI(
    title="Naval Hydraulic API",
    description="API REST pública para cálculo hidráulico de tubulações e bombas de embarcações navais",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ErroCalculo)
async def erro_calculo_handler(request: Request, exc: ErroCalculo):
    # Definir status 422 para erros de regra de negócio/parâmetros e 400 para erros operacionais
    status_code = 422 if exc.codigo in [
        "VAZAO_NEGATIVA", "CAMPO_OBRIGATORIO", "UNIDADE_INVALIDA",
        "TEMPERATURA_FORA_DO_RANGE", "CURVA_HQ_H_INVALIDO", "FLUIDO_INVALIDO",
        "TOPOLOGIA_MALHA_NAO_SUPORTADA"
    ] else 400

    payload = {
        "codigo": exc.codigo,
        "mensagem": exc.mensagem,
        "dados_diagnostico": exc.dados_diagnostico,
        "campo": exc.campo,
        "error": {
            "codigo": exc.codigo,
            "mensagem": exc.mensagem,
            "dados_diagnostico": exc.dados_diagnostico,
            "campo": exc.campo
        }
    }
    return JSONResponse(status_code=status_code, content=payload)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = {
        "codigo": "ERRO_VALIDACAO",
        "mensagem": "Falha de validação dos parâmetros de entrada.",
        "dados_diagnostico": exc.errors(),
        "error": {
            "codigo": "ERRO_VALIDACAO",
            "mensagem": "Falha de validação dos parâmetros de entrada.",
            "dados_diagnostico": exc.errors()
        }
    }
    return JSONResponse(status_code=422, content=payload)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    payload = {
        "codigo": "ERRO_INTERNO",
        "mensagem": "Ocorreu um erro interno não tratado no servidor.",
        "error": {
            "codigo": "ERRO_INTERNO",
            "mensagem": "Ocorreu um erro interno não tratado no servidor."
        }
    }
    return JSONResponse(status_code=500, content=payload)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
