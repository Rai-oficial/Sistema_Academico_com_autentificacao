import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from database import get_session
from models import Usuario, PapelUsuario


import bcrypt

# Em produção, defina a variável de ambiente SECRET_KEY (ex: com `openssl rand -hex 32`)
# Nunca deixe uma chave fixa como esta indo para produção.
SECRET_KEY = os.getenv("SECRET_KEY", "chave-de-desenvolvimento-troque-isso-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


def gerar_hash_senha(senha: str) -> str:
    pwd_bytes = senha.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    try:
        pwd_bytes = senha_plana.encode("utf-8")[:72]
        hash_bytes = senha_hash.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False



def criar_access_token(dados: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = dados.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def autenticar_usuario(session: Session, email: str, senha: str) -> Usuario | None:
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not usuario:
        return None
    if not verificar_senha(senha, usuario.senha_hash):
        return None
    if not usuario.ativo:
        return None
    return usuario



credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar as credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_usuario_atual(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if usuario is None or not usuario.ativo:
        raise credentials_exception
    return usuario


def exigir_papel(*papeis_permitidos: PapelUsuario):
    """
    Dependência que restringe o acesso a determinados papéis.
    Uso: Depends(exigir_papel(PapelUsuario.admin, PapelUsuario.padrao))
    """
    def verificador(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.papel not in papeis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para realizar esta ação",
            )
        return usuario
    return verificador


# Atalhos prontos para usar nos routers
permitir_escrita = exigir_papel(PapelUsuario.admin, PapelUsuario.padrao)
permitir_apenas_admin = exigir_papel(PapelUsuario.admin)


def verificar_permissao_owner(recurso, usuario_atual: Usuario) -> None:
    """
    Garante que apenas o dono do registro ou um administrador possa alterar/excluir o recurso.
    """
    if usuario_atual.papel == PapelUsuario.admin:
        return
    owner_id = getattr(recurso, "owner_id", None)
    if owner_id is not None and owner_id == usuario_atual.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para acessar ou modificar este recurso.",
    )