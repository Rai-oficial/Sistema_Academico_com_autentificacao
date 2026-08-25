import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from database import create_db_and_tables
from routers import (
    aluno, professor, departamento, curso, disciplina,
    turma, periodo_letivo, registro_matricula, desempenho,
    relatorios, usuarios, logs
)
from log_service import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    app_logger.info("Sistema Acadêmico iniciado com sucesso.")
    yield
    app_logger.info("Sistema Acadêmico finalizado.")


app = FastAPI(title="Sistema Acadêmico", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    client_ip = request.client.host if request.client else "N/A"

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        app_logger.info(
            f"HTTP {request.method} {request.url.path} - Status {response.status_code} ({process_time:.2f}ms) - IP: {client_ip}"
        )
        return response
    except Exception as exc:
        process_time = (time.time() - start_time) * 1000
        app_logger.error(
            f"HTTP {request.method} {request.url.path} - ERRO 500 ({process_time:.2f}ms) - IP: {client_ip} - Exceção: {str(exc)}"
        )
        raise exc


app.include_router(aluno.router)
app.include_router(professor.router)
app.include_router(departamento.router)
app.include_router(curso.router)
app.include_router(disciplina.router)
app.include_router(turma.router)
app.include_router(periodo_letivo.router)
app.include_router(registro_matricula.router)
app.include_router(desempenho.router)
app.include_router(relatorios.router)
app.include_router(usuarios.router)
app.include_router(logs.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
    }