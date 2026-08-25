from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from database import get_session
from models import Usuario
from schemas import UsuarioCreate, UsuarioPublic, UsuarioMeResponse, Token
from auth import gerar_hash_senha, autenticar_usuario, criar_access_token, get_usuario_atual
from log_service import registrar_log
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.post("/", response_model=UsuarioPublic)
def criar_usuario(
    usuario: UsuarioCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    existe = session.exec(
        select(Usuario).where(Usuario.email == usuario.email)
    ).first()

    if existe:
        registrar_log(
            session=session,
            acao="CRIAR_USUARIO_FALHA",
            usuario_email=usuario.email,
            tabela="usuario",
            detalhes=f"Tentativa de cadastro com email já existente: {usuario.email}",
            ip_origem=request.client.host if request.client else None,
            status_code=400,
        )
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado."
        )

    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha),
        papel=usuario.papel,
    )

    session.add(novo)
    session.commit()
    session.refresh(novo)

    registrar_log(
        session=session,
        acao="CRIAR_USUARIO",
        usuario=novo,
        tabela="usuario",
        registro_id=novo.id,
        detalhes=f"Usuário '{novo.nome}' ({novo.email}) cadastrado com papel '{novo.papel.value}'.",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )

    return novo


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    usuario = autenticar_usuario(
        session,
        form_data.username,
        form_data.password
    )

    if not usuario:
        registrar_log(
            session=session,
            acao="LOGIN_FALHA",
            usuario_email=form_data.username,
            tabela="usuario",
            detalhes=f"Falha de autenticação para o usuário: {form_data.username}",
            ip_origem=request.client.host if request.client else None,
            status_code=401,
        )
        raise HTTPException(
            status_code=401,
            detail="Email ou senha inválidos."
        )

    token = criar_access_token(
        {"sub": usuario.email}
    )

    registrar_log(
        session=session,
        acao="LOGIN_SUCESSO",
        usuario=usuario,
        tabela="usuario",
        registro_id=usuario.id,
        detalhes=f"Login realizado com sucesso por {usuario.email}.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UsuarioMeResponse)
def obter_usuario_logado(
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    """
    Retorna os dados do usuário atualmente autenticado.
    """
    return usuario_atual

