from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Curso, Usuario
from schemas import (
    CursoPublic,
    CursoCreate,
    CursoUpdate,
    DisciplinaPublic,
    DepartamentoPublic,
)

from auth import permitir_admin, permitir_todos

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.post("/", response_model=CursoPublic)
def criar_curso(
    curso: CursoCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    db_curso = Curso.model_validate(curso)

    session.add(db_curso)
    session.commit()
    session.refresh(db_curso)

    return db_curso


@router.get("/", response_model=list[CursoPublic])
def listar_cursos(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(select(Curso)).all()


@router.get("/buscar/nome", response_model=list[CursoPublic])
def buscar_curso_por_nome(
    nome: str,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(
        select(Curso).where(Curso.nome.contains(nome))
    ).all()


@router.get("/{curso_id}", response_model=CursoPublic)
def buscar_curso_por_id(
    curso_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    curso = session.get(Curso, curso_id)

    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    return curso


@router.get("/{curso_id}/disciplinas", response_model=list[DisciplinaPublic])
def disciplinas_do_curso(
    curso_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    curso = session.get(Curso, curso_id)

    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    return curso.disciplinas


@router.get("/{curso_id}/departamento", response_model=DepartamentoPublic)
def departamento_do_curso(
    curso_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    curso = session.get(Curso, curso_id)

    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    if not curso.departamento:
        raise HTTPException(
            status_code=404,
            detail="Curso sem departamento associado",
        )

    return curso.departamento


@router.put("/{curso_id}", response_model=CursoPublic)
def atualizar_curso(
    curso_id: int,
    dados: CursoUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    curso = session.get(Curso, curso_id)

    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    curso.sqlmodel_update(dados.model_dump(exclude_unset=True))

    session.add(curso)
    session.commit()
    session.refresh(curso)

    return curso


@router.delete("/{curso_id}")
def deletar_curso(
    curso_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    curso = session.get(Curso, curso_id)

    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    session.delete(curso)
    session.commit()

    return {"ok": True}