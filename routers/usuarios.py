from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Usuario, PapelUsuario
from schemas import UsuarioCreate, UsuarioPublic
from auth import gerar_hash_senha, get_usuario_atual, oauth2_scheme_optional

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
    session: Session = Depends(get_session),
    token: str | None = Depends(oauth2_scheme_optional),
):
    # Existe algum usuário cadastrado?
    primeiro_usuario = session.exec(select(Usuario)).first()

    # Se já existe usuário, somente um admin autenticado pode criar outro
    if primeiro_usuario is not None:

        if token is None:
            raise HTTPException(
                status_code=401,
                detail="Não autenticado."
            )

        usuario_logado = get_usuario_atual(
            token=token,
            session=session,
        )

        if usuario_logado.papel != PapelUsuario.admin:
            raise HTTPException(
                status_code=403,
                detail="Apenas administradores podem criar usuários."
            )

    # Impede email duplicado
    existe = session.exec(
        select(Usuario).where(
            Usuario.email == usuario.email
        )
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado."
        )

    # Segurança: o primeiro usuário obrigatoriamente será admin
    if primeiro_usuario is None:
        usuario.papel = PapelUsuario.admin

    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha),
        papel=usuario.papel,
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
