from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from database import get_session
from models import PeriodoLetivo, Usuario
from schemas import PeriodoLetivoPublic, PeriodoLetivoCreate, PeriodoLetivoUpdate, TurmaPublic
from auth import get_usuario_atual, verificar_permissao_owner
from log_service import registrar_log

router = APIRouter(prefix="/periodos-letivos", tags=["Períodos Letivos"])


@router.post("/", response_model=PeriodoLetivoPublic)
def criar_periodo_letivo(
    periodo: PeriodoLetivoCreate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    db_periodo = PeriodoLetivo.model_validate(periodo)
    db_periodo.owner_id = usuario_atual.id

    session.add(db_periodo)
    session.commit()
    session.refresh(db_periodo)

    registrar_log(
        session=session,
        acao="CRIAR_PERIODO_LETIVO",
        usuario=usuario_atual,
        tabela="periodoletivo",
        registro_id=db_periodo.id,
        detalhes=f"Período letivo {db_periodo.ano}/{db_periodo.semestre} criado.",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )
    return db_periodo


@router.get("/", response_model=list[PeriodoLetivoPublic])
def listar_periodos_letivos(session: Session = Depends(get_session)):
    return session.exec(select(PeriodoLetivo)).all()


@router.get("/buscar", response_model=PeriodoLetivoPublic)
def buscar_por_ano_semestre(ano: int, semestre: int, session: Session = Depends(get_session)):
    """Ex.: /periodos-letivos/buscar?ano=2026&semestre=2"""
    periodo = session.exec(
        select(PeriodoLetivo).where(PeriodoLetivo.ano == ano, PeriodoLetivo.semestre == semestre)
    ).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Período letivo não encontrado")
    return periodo


@router.get("/{periodo_id}", response_model=PeriodoLetivoPublic)
def buscar_periodo_letivo_por_id(periodo_id: int, session: Session = Depends(get_session)):
    periodo = session.get(PeriodoLetivo, periodo_id)
    if not periodo:
        raise HTTPException(status_code=404, detail="Período letivo não encontrado")
    return periodo


@router.get("/{periodo_id}/turmas", response_model=list[TurmaPublic])
def turmas_do_periodo(periodo_id: int, session: Session = Depends(get_session)):
    periodo = session.get(PeriodoLetivo, periodo_id)
    if not periodo:
        raise HTTPException(status_code=404, detail="Período letivo não encontrado")
    return periodo.turmas


@router.put("/{periodo_id}", response_model=PeriodoLetivoPublic)
def atualizar_periodo_letivo(
    periodo_id: int,
    dados: PeriodoLetivoUpdate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    periodo = session.get(PeriodoLetivo, periodo_id)
    if not periodo:
        raise HTTPException(status_code=404, detail="Período letivo não encontrado")

    verificar_permissao_owner(periodo, usuario_atual)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(periodo, campo, valor)

    session.add(periodo)
    session.commit()
    session.refresh(periodo)

    registrar_log(
        session=session,
        acao="ATUALIZAR_PERIODO_LETIVO",
        usuario=usuario_atual,
        tabela="periodoletivo",
        registro_id=periodo.id,
        detalhes=f"Período letivo {periodo.ano}/{periodo.semestre} atualizado.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return periodo


@router.delete("/{periodo_id}")
def deletar_periodo_letivo(
    periodo_id: int,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    periodo = session.get(PeriodoLetivo, periodo_id)
    if not periodo:
        raise HTTPException(status_code=404, detail="Período letivo não encontrado")

    verificar_permissao_owner(periodo, usuario_atual)

    descricao_periodo = f"{periodo.ano}/{periodo.semestre}"
    session.delete(periodo)
    session.commit()

    registrar_log(
        session=session,
        acao="EXCLUIR_PERIODO_LETIVO",
        usuario=usuario_atual,
        tabela="periodoletivo",
        registro_id=periodo_id,
        detalhes=f"Período letivo '{descricao_periodo}' excluído.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return {"ok": True}
