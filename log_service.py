import logging
from datetime import datetime, timezone
from sqlmodel import Session
from models import RegistroLog, Usuario

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("sistema_academico.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

app_logger = logging.getLogger("sistema_academico")


def registrar_log(
    session: Session,
    acao: str,
    usuario: Usuario | None = None,
    usuario_id: int | None = None,
    usuario_email: str | None = None,
    tabela: str | None = None,
    registro_id: int | None = None,
    detalhes: str | None = None,
    ip_origem: str | None = None,
    status_code: int = 200
) -> RegistroLog:
    final_user_id = usuario.id if usuario else usuario_id
    final_user_email = usuario.email if usuario else usuario_email

    log_entry = RegistroLog(
        usuario_id=final_user_id,
        usuario_email=final_user_email,
        acao=acao,
        tabela_afetada=tabela,
        registro_id=registro_id,
        detalhes=detalhes,
        ip_origem=ip_origem,
        status_code=status_code,
        data_hora=datetime.now(timezone.utc)
    )
    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)

    app_logger.info(
        f"[{acao}] {detalhes or ''} | Usuario: {final_user_email or 'Anonimo'} | Recurso: {tabela or '-'} #{registro_id or '-'} | Status: {status_code}"
    )
    return log_entry
