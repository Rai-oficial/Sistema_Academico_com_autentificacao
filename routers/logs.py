from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, desc

from database import get_session
from models import RegistroLog
from schemas import RegistroLogPublic
from auth import permitir_apenas_admin

router = APIRouter(prefix="/logs", tags=["Logs de Auditoria"])


@router.get("/", response_model=list[RegistroLogPublic])
def listar_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    acao: str | None = None,
    tabela: str | None = None,
    usuario_id: int | None = None,
    session: Session = Depends(get_session),
    _admin=Depends(permitir_apenas_admin),
):
    """
    Retorna o histórico de logs de auditoria do sistema. Acesso restrito a administradores.
    """
    query = select(RegistroLog).order_by(desc(RegistroLog.data_hora))
    if acao:
        query = query.where(RegistroLog.acao.contains(acao))
    if tabela:
        query = query.where(RegistroLog.tabela_afetada == tabela)
    if usuario_id:
        query = query.where(RegistroLog.usuario_id == usuario_id)

    return session.exec(query.offset(skip).limit(limit)).all()


@router.get("/{log_id}", response_model=RegistroLogPublic)
def buscar_log_por_id(
    log_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(permitir_apenas_admin),
):
    """
    Consulta um registro específico de log pelo ID. Acesso restrito a administradores.
    """
    log_entry = session.get(RegistroLog, log_id)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Registro de log não encontrado")
    return log_entry
