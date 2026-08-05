from sqlmodel import Session, select

from database import engine
from models import Usuario, PapelUsuario
from auth import gerar_hash_senha


def criar_admin_inicial():
    with Session(engine) as session:

        admin = session.exec(
            select(Usuario).where(
                Usuario.email == "admin@sistema.com"
            )
        ).first()

        if admin:
            return

        admin = Usuario(
            nome="Administrador",
            email="admin@sistema.com",
            senha_hash=gerar_hash_senha("admin123"),
            ativo=True,
            papel=PapelUsuario.admin,
        )

        session.add(admin)
        session.commit()

        print("Administrador inicial criado com sucesso!")