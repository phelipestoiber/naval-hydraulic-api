from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.erro import ErroCalculo
from app.api.v1.router import api_router

app = FastAPI(
    title="Naval Hydraulic API",
    description="API para cálculo hidráulico de tubulações e bombas de embarcações navais",
    version="0.8.0"
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
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "codigo": exc.codigo,
                "mensagem": exc.mensagem,
                "dados_diagnostico": exc.dados_diagnostico,
                "campo": exc.campo
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "codigo": "ERRO_VALIDACAO",
                "mensagem": "Falha de validação dos parâmetros de entrada.",
                "dados_diagnostico": exc.errors()
            }
        }
    )

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.8.0"}
