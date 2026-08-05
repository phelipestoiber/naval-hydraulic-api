from fastapi import APIRouter
from app.api.v1.endpoints import fluidos, perda_carga, bombas, cavitacao, motores

api_router = APIRouter(prefix="/v1")
api_router.include_router(fluidos.router)
api_router.include_router(perda_carga.router)
api_router.include_router(bombas.router)
api_router.include_router(cavitacao.router)
api_router.include_router(motores.router)
