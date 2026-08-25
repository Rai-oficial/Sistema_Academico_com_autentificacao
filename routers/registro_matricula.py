from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from database import get_session
from models import RegistroMatricula, Usuario
from schemas import RegistroMatriculaPublic, RegistroMatriculaCreate, RegistroMatriculaUpdate
from auth import get_usuario_atual, verificar_permissao_owner
from log_service import registrar_log

router = APIRouter(prefix="/matriculas", tags=["Registros de Matrícula"])


@router.post("/", response_model=RegistroMatriculaPublic)
def criar_registro_matricula(
    registro: RegistroMatriculaCreate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    db_registro = RegistroMatricula.model_validate(registro)
    db_registro.owner_id = usuario_atual.id

    session.add(db_registro)
    session.commit()
    session.refresh(db_registro)

    registrar_log(
        session=session,
        acao="CRIAR_MATRICULA",
        usuario=usuario_atual,
        tabela="registromatricula",
        registro_id=db_registro.id,
        detalhes=f"Matrícula criada para o aluno ID {db_registro.id_aluno} (Situação: {db_registro.situacao}).",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )
    return db_registro


@router.get("/", response_model=list[RegistroMatriculaPublic])
def listar_registros_matricula(session: Session = Depends(get_session)):
    return session.exec(select(RegistroMatricula)).all()


@router.get("/aluno/{aluno_id}", response_model=list[RegistroMatriculaPublic])
def registros_de_um_aluno(aluno_id: int, session: Session = Depends(get_session)):
    return session.exec(select(RegistroMatricula).where(RegistroMatricula.id_aluno == aluno_id)).all()


@router.get("/aluno/{aluno_id}/ingresso")
def data_de_ingresso_do_aluno(aluno_id: int, session: Session = Depends(get_session)):
    """Retorna a matrícula mais antiga do aluno (data em que ingressou)."""
    primeiro = session.exec(
        select(RegistroMatricula)
        .where(RegistroMatricula.id_aluno == aluno_id)
        .order_by(RegistroMatricula.dataMatricula)
    ).first()
    if not primeiro:
        raise HTTPException(status_code=404, detail="Nenhuma matrícula encontrada para este aluno")
    return {"aluno_id": aluno_id, "data_ingresso": primeiro.dataMatricula}


@router.get("/situacao/{situacao}", response_model=list[RegistroMatriculaPublic])
def matriculas_por_situacao(situacao: str, session: Session = Depends(get_session)):
    """Ex.: Ativa, Trancada, Concluída."""
    return session.exec(select(RegistroMatricula).where(RegistroMatricula.situacao == situacao)).all()


@router.get("/{registro_id}", response_model=RegistroMatriculaPublic)
def buscar_registro_por_id(registro_id: int, session: Session = Depends(get_session)):
    registro = session.get(RegistroMatricula, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return registro


@router.put("/{registro_id}", response_model=RegistroMatriculaPublic)
def atualizar_registro_matricula(
    registro_id: int,
    dados: RegistroMatriculaUpdate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    registro = session.get(RegistroMatricula, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    verificar_permissao_owner(registro, usuario_atual)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(registro, campo, valor)

    session.add(registro)
    session.commit()
    session.refresh(registro)

    registrar_log(
        session=session,
        acao="ATUALIZAR_MATRICULA",
        usuario=usuario_atual,
        tabela="registromatricula",
        registro_id=registro.id,
        detalhes=f"Matrícula ID {registro.id} atualizada para situação '{registro.situacao}'.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return registro


@router.delete("/{registro_id}")
def deletar_registro_matricula(
    registro_id: int,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    registro = session.get(RegistroMatricula, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    verificar_permissao_owner(registro, usuario_atual)

    session.delete(registro)
    session.commit()

    registrar_log(
        session=session,
        acao="EXCLUIR_MATRICULA",
        usuario=usuario_atual,
        tabela="registromatricula",
        registro_id=registro_id,
        detalhes=f"Matrícula ID {registro_id} excluída.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return {"ok": True}
