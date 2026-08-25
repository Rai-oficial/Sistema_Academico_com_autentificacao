from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from database import get_session
from models import Departamento, Usuario
from schemas import DepartamentoPublic, DepartamentoCreate, DepartamentoUpdate, ProfessorPublic, CursoPublic
from auth import get_usuario_atual, verificar_permissao_owner
from log_service import registrar_log

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.post("/", response_model=DepartamentoPublic)
def criar_departamento(
    departamento: DepartamentoCreate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    db_departamento = Departamento.model_validate(departamento)
    db_departamento.owner_id = usuario_atual.id

    session.add(db_departamento)
    session.commit()
    session.refresh(db_departamento)

    registrar_log(
        session=session,
        acao="CRIAR_DEPARTAMENTO",
        usuario=usuario_atual,
        tabela="departamento",
        registro_id=db_departamento.id,
        detalhes=f"Departamento '{db_departamento.nome}' criado.",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )
    return db_departamento


@router.get("/", response_model=list[DepartamentoPublic])
def listar_departamentos(session: Session = Depends(get_session)):
    return session.exec(select(Departamento)).all()


@router.get("/{departamento_id}", response_model=DepartamentoPublic)
def buscar_departamento_por_id(departamento_id: int, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento


@router.get("/{departamento_id}/professores", response_model=list[ProfessorPublic])
def professores_do_departamento(departamento_id: int, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento.professores


@router.get("/{departamento_id}/cursos", response_model=list[CursoPublic])
def cursos_do_departamento(departamento_id: int, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento.cursos


@router.put("/{departamento_id}", response_model=DepartamentoPublic)
def atualizar_departamento(
    departamento_id: int,
    dados: DepartamentoUpdate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    verificar_permissao_owner(departamento, usuario_atual)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(departamento, campo, valor)

    session.add(departamento)
    session.commit()
    session.refresh(departamento)

    registrar_log(
        session=session,
        acao="ATUALIZAR_DEPARTAMENTO",
        usuario=usuario_atual,
        tabela="departamento",
        registro_id=departamento.id,
        detalhes=f"Departamento '{departamento.nome}' atualizado.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return departamento


@router.delete("/{departamento_id}")
def deletar_departamento(
    departamento_id: int,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    verificar_permissao_owner(departamento, usuario_atual)

    nome_depto = departamento.nome
    session.delete(departamento)
    session.commit()

    registrar_log(
        session=session,
        acao="EXCLUIR_DEPARTAMENTO",
        usuario=usuario_atual,
        tabela="departamento",
        registro_id=departamento_id,
        detalhes=f"Departamento '{nome_depto}' excluído.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return {"ok": True}
