from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_db_and_tables
from routers import aluno, professor, departamento, curso, disciplina, turma, periodo_letivo, registro_matricula, desempenho, relatorios, usuarios


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Sistema Acadêmico",version="1.0.0",lifespan=lifespan)

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

@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
    }