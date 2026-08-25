from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import Session, select

from database import get_session
from models import Aluno, RegistroMatricula, Desempenho, Usuario
from schemas import (
    AlunoPublic, AlunoCreate, AlunoUpdate,
    TurmaPublic, RegistroMatriculaPublic, DesempenhoPublic,
)
from auth import get_usuario_atual, verificar_permissao_owner
from log_service import registrar_log

router = APIRouter(prefix="/alunos", tags=["Alunos"])


@router.post("/", response_model=AlunoPublic)
def criar_aluno(
    aluno: AlunoCreate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    db_aluno = Aluno.model_validate(aluno)
    db_aluno.owner_id = usuario_atual.id

    session.add(db_aluno)
    session.commit()
    session.refresh(db_aluno)

    registrar_log(
        session=session,
        acao="CRIAR_ALUNO",
        usuario=usuario_atual,
        tabela="aluno",
        registro_id=db_aluno.id,
        detalhes=f"Aluno '{db_aluno.nome}' (CPF: {db_aluno.cpf}) cadastrado.",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )
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
def atualizar_aluno(
    aluno_id: int,
    dados: AlunoUpdate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    verificar_permissao_owner(aluno, usuario_atual)

    aluno.sqlmodel_update(dados.model_dump(exclude_unset=True))

    session.add(aluno)
    session.commit()
    session.refresh(aluno)

    registrar_log(
        session=session,
        acao="ATUALIZAR_ALUNO",
        usuario=usuario_atual,
        tabela="aluno",
        registro_id=aluno.id,
        detalhes=f"Dados do aluno '{aluno.nome}' atualizados.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return aluno


@router.delete("/{aluno_id}")
def deletar_aluno(
    aluno_id: int,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    verificar_permissao_owner(aluno, usuario_atual)

    nome_aluno = aluno.nome
    session.delete(aluno)
    session.commit()

    registrar_log(
        session=session,
        acao="EXCLUIR_ALUNO",
        usuario=usuario_atual,
        tabela="aluno",
        registro_id=aluno_id,
        detalhes=f"Aluno '{nome_aluno}' excluído.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return {"ok": True}
