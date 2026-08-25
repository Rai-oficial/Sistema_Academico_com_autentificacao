from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from database import get_session
from models import Desempenho, Usuario
from schemas import DesempenhoPublic, DesempenhoCreate, DesempenhoUpdate
from auth import get_usuario_atual, verificar_permissao_owner
from log_service import registrar_log

router = APIRouter(prefix="/desempenhos", tags=["Desempenhos"])


@router.post("/", response_model=DesempenhoPublic)
def criar_desempenho(
    desempenho: DesempenhoCreate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    db_desempenho = Desempenho.model_validate(desempenho)
    db_desempenho.owner_id = usuario_atual.id

    session.add(db_desempenho)
    session.commit()
    session.refresh(db_desempenho)

    registrar_log(
        session=session,
        acao="CRIAR_DESEMPENHO",
        usuario=usuario_atual,
        tabela="desempenho",
        registro_id=db_desempenho.id_aluno,
        detalhes=f"Lançamento de notas para o aluno ID {db_desempenho.id_aluno} na turma ID {db_desempenho.id_turma} (Média: {db_desempenho.mediaFinal}).",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )
    return db_desempenho


@router.get("/", response_model=list[DesempenhoPublic])
def listar_desempenhos(session: Session = Depends(get_session)):
    return session.exec(select(Desempenho)).all()


@router.get("/aluno/{aluno_id}", response_model=list[DesempenhoPublic])
def notas_de_um_aluno(aluno_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Desempenho).where(Desempenho.id_aluno == aluno_id)).all()


@router.get("/turma/{turma_id}", response_model=list[DesempenhoPublic])
def notas_da_turma(turma_id: int, session: Session = Depends(get_session)):
    """Todos os alunos da turma com suas respectivas notas."""
    return session.exec(select(Desempenho).where(Desempenho.id_turma == turma_id)).all()


@router.get("/turma/{turma_id}/aprovados", response_model=list[DesempenhoPublic])
def aprovados_da_turma(turma_id: int, session: Session = Depends(get_session)):
    return session.exec(
        select(Desempenho).where(Desempenho.id_turma == turma_id, Desempenho.situacaoFinal == "Aprovado")
    ).all()


@router.get("/turma/{turma_id}/reprovados", response_model=list[DesempenhoPublic])
def reprovados_da_turma(turma_id: int, session: Session = Depends(get_session)):
    return session.exec(
        select(Desempenho).where(Desempenho.id_turma == turma_id, Desempenho.situacaoFinal == "Reprovado")
    ).all()


@router.get("/aluno/{aluno_id}/turma/{turma_id}", response_model=DesempenhoPublic)
def nota_do_aluno_na_turma(aluno_id: int, turma_id: int, session: Session = Depends(get_session)):
    """Consulta a nota de um aluno numa disciplina (via a turma em que cursou)."""
    desempenho = session.get(Desempenho, (aluno_id, turma_id))
    if not desempenho:
        raise HTTPException(status_code=404, detail="Desempenho não encontrado para esse aluno nessa turma")
    return desempenho


@router.put("/aluno/{aluno_id}/turma/{turma_id}", response_model=DesempenhoPublic)
def atualizar_desempenho(
    aluno_id: int,
    turma_id: int,
    dados: DesempenhoUpdate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    desempenho = session.get(Desempenho, (aluno_id, turma_id))
    if not desempenho:
        raise HTTPException(status_code=404, detail="Desempenho não encontrado")

    verificar_permissao_owner(desempenho, usuario_atual)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(desempenho, campo, valor)

    session.add(desempenho)
    session.commit()
    session.refresh(desempenho)

    registrar_log(
        session=session,
        acao="ATUALIZAR_DESEMPENHO",
        usuario=usuario_atual,
        tabela="desempenho",
        registro_id=aluno_id,
        detalhes=f"Notas atualizadas para o aluno ID {aluno_id} na turma ID {turma_id}.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return desempenho


@router.delete("/aluno/{aluno_id}/turma/{turma_id}")
def deletar_desempenho(
    aluno_id: int,
    turma_id: int,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    desempenho = session.get(Desempenho, (aluno_id, turma_id))
    if not desempenho:
        raise HTTPException(status_code=404, detail="Desempenho não encontrado")

    verificar_permissao_owner(desempenho, usuario_atual)

    session.delete(desempenho)
    session.commit()

    registrar_log(
        session=session,
        acao="EXCLUIR_DESEMPENHO",
        usuario=usuario_atual,
        tabela="desempenho",
        registro_id=aluno_id,
        detalhes=f"Registro de notas excluído para aluno ID {aluno_id} na turma ID {turma_id}.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return {"ok": True}
