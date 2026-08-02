from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Usuario
from schemas import UsuarioCreate, UsuarioPublic
from auth import gerar_hash_senha

from fastapi.security import OAuth2PasswordRequestForm
from auth import autenticar_usuario, criar_access_token
from schemas import Token

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.post("/", response_model=UsuarioPublic)
def criar_usuario(
    usuario: UsuarioCreate,
    session: Session = Depends(get_session)
):

    existe = session.exec(
        select(Usuario).where(Usuario.email == usuario.email)
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado."
        )

    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha)
    )

    session.add(novo)
    session.commit()
    session.refresh(novo)

    return novo

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):

    usuario = autenticar_usuario(
        session,
        form_data.username,
        form_data.password
    )

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha inválidos."
        )

    token = criar_access_token(
        {"sub": usuario.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
