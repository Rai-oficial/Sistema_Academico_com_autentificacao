from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Turma, Aluno, Aluno_Turma, Usuario
from schemas import (
    TurmaPublic,
    TurmaCreate,
    TurmaUpdate,
    AlunoPublic,
    ProfessorPublic,
    DisciplinaPublic,
    PeriodoLetivoPublic,
)

from auth import permitir_admin, permitir_todos

router = APIRouter(prefix="/turmas", tags=["Turmas"])


@router.post("/", response_model=TurmaPublic)
def criar_turma(
    turma: TurmaCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    db_turma = Turma.model_validate(turma)

    session.add(db_turma)
    session.commit()
    session.refresh(db_turma)

    return db_turma


@router.get("/", response_model=list[TurmaPublic])
def listar_turmas(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(select(Turma)).all()


@router.get("/codigo/{codigo}", response_model=TurmaPublic)
def buscar_turma_por_codigo(
    codigo: str,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    turma = session.exec(
        select(Turma).where(Turma.codigo == codigo)
    ).first()

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    return turma


@router.get("/{turma_id}", response_model=TurmaPublic)
def buscar_turma_por_id(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    return turma


@router.get("/{turma_id}/alunos", response_model=list[AlunoPublic])
def alunos_da_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    return turma.alunos


@router.get("/{turma_id}/professor", response_model=ProfessorPublic)
def professor_da_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    if not turma.professor:
        raise HTTPException(
            status_code=404,
            detail="Turma sem professor associado",
        )

    return turma.professor


@router.get("/{turma_id}/disciplina", response_model=DisciplinaPublic)
def disciplina_da_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    if not turma.disciplina:
        raise HTTPException(
            status_code=404,
            detail="Turma sem disciplina associada",
        )

    return turma.disciplina


@router.get("/{turma_id}/periodo-letivo", response_model=PeriodoLetivoPublic)
def periodo_letivo_da_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    if not turma.periodo_letivo:
        raise HTTPException(
            status_code=404,
            detail="Turma sem período letivo associado",
        )

    return turma.periodo_letivo


@router.post("/{turma_id}/matricular/{aluno_id}")
def matricular_aluno_na_turma(
    turma_id: int,
    aluno_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    """Vincula um aluno a uma turma (tabela associativa Aluno_Turma)."""

    turma = session.get(Turma, turma_id)
    aluno = session.get(Aluno, aluno_id)

    if not turma or not aluno:
        raise HTTPException(
            status_code=404,
            detail="Turma ou aluno não encontrado",
        )

    ja_matriculado = session.get(Aluno_Turma, (aluno_id, turma_id))

    if ja_matriculado:
        raise HTTPException(
            status_code=400,
            detail="Aluno já matriculado nessa turma",
        )

    vinculo = Aluno_Turma(
        id_aluno=aluno_id,
        id_turma=turma_id,
    )

    session.add(vinculo)
    session.commit()

    return {
        "ok": True,
        "mensagem": f"Aluno {aluno.nome} matriculado na turma {turma.codigo}",
    }


@router.put("/{turma_id}", response_model=TurmaPublic)
def atualizar_turma(
    turma_id: int,
    dados: TurmaUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    turma.sqlmodel_update(dados.model_dump(exclude_unset=True))

    session.add(turma)
    session.commit()
    session.refresh(turma)

    return turma


@router.delete("/{turma_id}")
def deletar_turma(
    turma_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    session.delete(turma)
    session.commit()

    return {"ok": True}