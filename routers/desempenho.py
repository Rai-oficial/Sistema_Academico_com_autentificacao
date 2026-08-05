from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Desempenho, Usuario
from schemas import (
    DesempenhoPublic,
    DesempenhoCreate,
    DesempenhoUpdate,
)

from auth import permitir_admin, permitir_todos

router = APIRouter(prefix="/desempenhos", tags=["Desempenhos"])


@router.post("/", response_model=DesempenhoPublic)
def criar_desempenho(
    desempenho: DesempenhoCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    db_desempenho = Desempenho.model_validate(desempenho)

    session.add(db_desempenho)
    session.commit()
    session.refresh(db_desempenho)

    return db_desempenho


@router.get("/", response_model=list[DesempenhoPublic])
def listar_desempenhos(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(select(Desempenho)).all()


@router.get("/aluno/{aluno_id}", response_model=list[DesempenhoPublic])
def notas_de_um_aluno(
    aluno_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(
        select(Desempenho).where(Desempenho.id_aluno == aluno_id)
    ).all()


@router.get("/turma/{turma_id}", response_model=list[DesempenhoPublic])
def notas_da_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    """Todos os alunos da turma com suas respectivas notas."""
    return session.exec(
        select(Desempenho).where(Desempenho.id_turma == turma_id)
    ).all()


@router.get("/turma/{turma_id}/aprovados", response_model=list[DesempenhoPublic])
def aprovados_da_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(
        select(Desempenho).where(
            Desempenho.id_turma == turma_id,
            Desempenho.situacaoFinal == "Aprovado",
        )
    ).all()


@router.get("/turma/{turma_id}/reprovados", response_model=list[DesempenhoPublic])
def reprovados_da_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(
        select(Desempenho).where(
            Desempenho.id_turma == turma_id,
            Desempenho.situacaoFinal == "Reprovado",
        )
    ).all()


@router.get("/aluno/{aluno_id}/turma/{turma_id}", response_model=DesempenhoPublic)
def nota_do_aluno_na_turma(
    aluno_id: int,
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    """Consulta a nota de um aluno numa disciplina (via a turma em que cursou)."""

    desempenho = session.get(Desempenho, (aluno_id, turma_id))

    if not desempenho:
        raise HTTPException(
            status_code=404,
            detail="Desempenho não encontrado para esse aluno nessa turma",
        )

    return desempenho


@router.put("/aluno/{aluno_id}/turma/{turma_id}", response_model=DesempenhoPublic)
def atualizar_desempenho(
    aluno_id: int,
    turma_id: int,
    dados: DesempenhoUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    desempenho = session.get(Desempenho, (aluno_id, turma_id))

    if not desempenho:
        raise HTTPException(status_code=404, detail="Desempenho não encontrado")

    desempenho.sqlmodel_update(dados.model_dump(exclude_unset=True))

    session.add(desempenho)
    session.commit()
    session.refresh(desempenho)

    return desempenho


@router.delete("/aluno/{aluno_id}/turma/{turma_id}")
def deletar_desempenho(
    aluno_id: int,
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    desempenho = session.get(Desempenho, (aluno_id, turma_id))

    if not desempenho:
        raise HTTPException(status_code=404, detail="Desempenho não encontrado")

    session.delete(desempenho)
    session.commit()

    return {"ok": True}