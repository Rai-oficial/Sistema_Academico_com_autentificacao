from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from database import get_session
from models import Professor, Usuario
from schemas import ProfessorPublic, ProfessorCreate, ProfessorUpdate, TurmaPublic
from auth import get_usuario_atual, verificar_permissao_owner
from log_service import registrar_log

router = APIRouter(prefix="/professores", tags=["Professores"])


@router.post("/", response_model=ProfessorPublic)
def criar_professor(
    professor: ProfessorCreate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    db_professor = Professor.model_validate(professor)
    db_professor.owner_id = usuario_atual.id

    session.add(db_professor)
    session.commit()
    session.refresh(db_professor)

    registrar_log(
        session=session,
        acao="CRIAR_PROFESSOR",
        usuario=usuario_atual,
        tabela="professor",
        registro_id=db_professor.id,
        detalhes=f"Professor '{db_professor.nome}' (CPF: {db_professor.cpf}) cadastrado.",
        ip_origem=request.client.host if request.client else None,
        status_code=201,
    )
    return db_professor


@router.get("/", response_model=list[ProfessorPublic])
def listar_professores(session: Session = Depends(get_session)):
    return session.exec(select(Professor)).all()


@router.get("/cpf/{cpf}", response_model=ProfessorPublic)
def buscar_professor_por_cpf(cpf: str, session: Session = Depends(get_session)):
    professor = session.exec(select(Professor).where(Professor.cpf == cpf)).first()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    return professor


@router.get("/departamento/{departamento_id}", response_model=list[ProfessorPublic])
def professores_por_departamento(departamento_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Professor).where(Professor.id_departamento == departamento_id)).all()


@router.get("/{professor_id}", response_model=ProfessorPublic)
def buscar_professor_por_id(professor_id: int, session: Session = Depends(get_session)):
    professor = session.get(Professor, professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    return professor


@router.get("/{professor_id}/turmas", response_model=list[TurmaPublic])
def turmas_do_professor(professor_id: int, session: Session = Depends(get_session)):
    professor = session.get(Professor, professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    return professor.turmas


@router.put("/{professor_id}", response_model=ProfessorPublic)
def atualizar_professor(
    professor_id: int,
    dados: ProfessorUpdate,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    professor = session.get(Professor, professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    verificar_permissao_owner(professor, usuario_atual)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(professor, campo, valor)

    session.add(professor)
    session.commit()
    session.refresh(professor)

    registrar_log(
        session=session,
        acao="ATUALIZAR_PROFESSOR",
        usuario=usuario_atual,
        tabela="professor",
        registro_id=professor.id,
        detalhes=f"Professor '{professor.nome}' atualizado.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return professor


@router.delete("/{professor_id}")
def deletar_professor(
    professor_id: int,
    request: Request,
    session: Session = Depends(get_session),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    professor = session.get(Professor, professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    verificar_permissao_owner(professor, usuario_atual)

    nome_professor = professor.nome
    session.delete(professor)
    session.commit()

    registrar_log(
        session=session,
        acao="EXCLUIR_PROFESSOR",
        usuario=usuario_atual,
        tabela="professor",
        registro_id=professor_id,
        detalhes=f"Professor '{nome_professor}' excluído.",
        ip_origem=request.client.host if request.client else None,
        status_code=200,
    )
    return {"ok": True}
