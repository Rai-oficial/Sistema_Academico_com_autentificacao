from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from database import get_session
from models import Curso, Usuario
from schemas import CursoPublic, CursoCreate, CursoUpdate, DisciplinaPublic, DepartamentoPublic
from auth import get_usuario_atual, verificar_permissao_owner
from log_service import registrar_log

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.post("/", response_model=CursoPublic)
def criar_curso(
    curso: CursoCreate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    db_curso = Curso.model_validate(curso)
    db_curso.owner_id = usuario_atual.id

    session.add(db_curso)
    session.commit()
    session.refresh(db_curso)

    registrar_log(
        session=session,
        acao="CRIAR_CURSO",
        usuario=usuario_atual,
        tabela="curso",
        registro_id=db_curso.id,
        detalhes=f"Curso '{db_curso.nome}' criado.",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )
    return db_curso


@router.get("/", response_model=list[CursoPublic])
def listar_cursos(session: Session = Depends(get_session)):
    return session.exec(select(Curso)).all()


@router.get("/buscar/nome", response_model=list[CursoPublic])
def buscar_curso_por_nome(nome: str, session: Session = Depends(get_session)):
    return session.exec(select(Curso).where(Curso.nome.contains(nome))).all()


@router.get("/{curso_id}", response_model=CursoPublic)
def buscar_curso_por_id(curso_id: int, session: Session = Depends(get_session)):
    curso = session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return curso


@router.get("/{curso_id}/disciplinas", response_model=list[DisciplinaPublic])
def disciplinas_do_curso(curso_id: int, session: Session = Depends(get_session)):
    curso = session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return curso.disciplinas


@router.get("/{curso_id}/departamento", response_model=DepartamentoPublic)
def departamento_do_curso(curso_id: int, session: Session = Depends(get_session)):
    curso = session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    if not curso.departamento:
        raise HTTPException(status_code=404, detail="Curso sem departamento associado")
    return curso.departamento


@router.put("/{curso_id}", response_model=CursoPublic)
def atualizar_curso(
    curso_id: int,
    dados: CursoUpdate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    curso = session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    verificar_permissao_owner(curso, usuario_atual)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(curso, campo, valor)

    session.add(curso)
    session.commit()
    session.refresh(curso)

    registrar_log(
        session=session,
        acao="ATUALIZAR_CURSO",
        usuario=usuario_atual,
        tabela="curso",
        registro_id=curso.id,
        detalhes=f"Curso '{curso.nome}' atualizado.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return curso


@router.delete("/{curso_id}")
def deletar_curso(
    curso_id: int,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    curso = session.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    verificar_permissao_owner(curso, usuario_atual)

    nome_curso = curso.nome
    session.delete(curso)
    session.commit()

    registrar_log(
        session=session,
        acao="EXCLUIR_CURSO",
        usuario=usuario_atual,
        tabela="curso",
        registro_id=curso_id,
        detalhes=f"Curso '{nome_curso}' excluído.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return {"ok": True}
