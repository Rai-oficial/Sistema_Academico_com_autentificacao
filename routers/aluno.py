from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models import Aluno, RegistroMatricula, Desempenho
from schemas import (
    AlunoPublic, AlunoCreate, AlunoUpdate,
    TurmaPublic, RegistroMatriculaPublic, DesempenhoPublic,
)

router = APIRouter(prefix="/alunos", tags=["Alunos"])


@router.post("/", response_model=AlunoPublic)
def criar_aluno(aluno: AlunoCreate, session: Session = Depends(get_session)):
    db_aluno = Aluno.model_validate(aluno)
    session.add(db_aluno)
    session.commit()
    session.refresh(db_aluno)
    return db_aluno


@router.get("/", response_model=list[AlunoPublic])
def listar_alunos(session: Session = Depends(get_session)):
    return session.exec(select(Aluno)).all()


@router.get("/cpf/{cpf}", response_model=AlunoPublic)
def buscar_aluno_por_cpf(cpf: str, session: Session = Depends(get_session)):
    aluno = session.exec(select(Aluno).where(Aluno.cpf == cpf)).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


@router.get("/buscar/nome", response_model=list[AlunoPublic])
def buscar_alunos_por_nome(nome: str = Query(..., min_length=1), session: Session = Depends(get_session)):
    return session.exec(select(Aluno).where(Aluno.nome.contains(nome))).all()


@router.get("/status/{status}", response_model=list[AlunoPublic])
def listar_alunos_por_status(status: str, session: Session = Depends(get_session)):
    """Filtra por status do aluno, ex: Ativo, Trancado, Formado."""
    return session.exec(select(Aluno).where(Aluno.status == status)).all()


@router.get("/{aluno_id}", response_model=AlunoPublic)
def buscar_aluno_por_id(aluno_id: int, session: Session = Depends(get_session)):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


@router.get("/{aluno_id}/turmas", response_model=list[TurmaPublic])
def turmas_do_aluno(aluno_id: int, session: Session = Depends(get_session)):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno.turmas


@router.get("/{aluno_id}/matriculas", response_model=list[RegistroMatriculaPublic])
def historico_matriculas_do_aluno(aluno_id: int, session: Session = Depends(get_session)):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return session.exec(
        select(RegistroMatricula).where(RegistroMatricula.id_aluno == aluno_id)
    ).all()


@router.get("/{aluno_id}/desempenhos", response_model=list[DesempenhoPublic])
def boletim_do_aluno(aluno_id: int, session: Session = Depends(get_session)):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return session.exec(select(Desempenho).where(Desempenho.id_aluno == aluno_id)).all()


@router.put("/{aluno_id}", response_model=AlunoPublic)
def atualizar_aluno(aluno_id: int, dados: AlunoUpdate, session: Session = Depends(get_session)):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    aluno.sqlmodel_update(dados.model_dump(exclude_unset=True))

    session.add(aluno)
    session.commit()
    session.refresh(aluno)
    return aluno


@router.delete("/{aluno_id}")
def deletar_aluno(aluno_id: int, session: Session = Depends(get_session)):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    session.delete(aluno)
    session.commit()
    return {"ok": True}
