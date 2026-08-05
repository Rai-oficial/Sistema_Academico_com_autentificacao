from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import PeriodoLetivo, Usuario
from schemas import (
    PeriodoLetivoPublic,
    PeriodoLetivoCreate,
    PeriodoLetivoUpdate,
    TurmaPublic,
)

from auth import permitir_admin, permitir_todos

router = APIRouter(prefix="/periodos-letivos", tags=["Períodos Letivos"])


@router.post("/", response_model=PeriodoLetivoPublic)
def criar_periodo_letivo(
    periodo: PeriodoLetivoCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    db_periodo = PeriodoLetivo.model_validate(periodo)

    session.add(db_periodo)
    session.commit()
    session.refresh(db_periodo)

    return db_periodo


@router.get("/", response_model=list[PeriodoLetivoPublic])
def listar_periodos_letivos(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    return session.exec(select(PeriodoLetivo)).all()


@router.get("/buscar", response_model=PeriodoLetivoPublic)
def buscar_por_ano_semestre(
    ano: int,
    semestre: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    """Ex.: /periodos-letivos/buscar?ano=2026&semestre=2"""

    periodo = session.exec(
        select(PeriodoLetivo).where(
            PeriodoLetivo.ano == ano,
            PeriodoLetivo.semestre == semestre,
        )
    ).first()

    if not periodo:
        raise HTTPException(
            status_code=404,
            detail="Período letivo não encontrado",
        )

    return periodo


@router.get("/{periodo_id}", response_model=PeriodoLetivoPublic)
def buscar_periodo_letivo_por_id(
    periodo_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    periodo = session.get(PeriodoLetivo, periodo_id)

    if not periodo:
        raise HTTPException(
            status_code=404,
            detail="Período letivo não encontrado",
        )

    return periodo


@router.get("/{periodo_id}/turmas", response_model=list[TurmaPublic])
def turmas_do_periodo(
    periodo_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_todos),
):
    periodo = session.get(PeriodoLetivo, periodo_id)

    if not periodo:
        raise HTTPException(
            status_code=404,
            detail="Período letivo não encontrado",
        )

    return periodo.turmas


@router.put("/{periodo_id}", response_model=PeriodoLetivoPublic)
def atualizar_periodo_letivo(
    periodo_id: int,
    dados: PeriodoLetivoUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    periodo = session.get(PeriodoLetivo, periodo_id)

    if not periodo:
        raise HTTPException(
            status_code=404,
            detail="Período letivo não encontrado",
        )

    periodo.sqlmodel_update(dados.model_dump(exclude_unset=True))

    session.add(periodo)
    session.commit()
    session.refresh(periodo)

    return periodo


@router.delete("/{periodo_id}")
def deletar_periodo_letivo(
    periodo_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(permitir_admin),
):
    periodo = session.get(PeriodoLetivo, periodo_id)

    if not periodo:
        raise HTTPException(
            status_code=404,
            detail="Período letivo não encontrado",
        )

    session.delete(periodo)
    session.commit()

    return {"ok": True}