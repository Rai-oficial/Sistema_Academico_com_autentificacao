from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Professor
from schemas import ProfessorPublic, ProfessorCreate, ProfessorUpdate, TurmaPublic

router = APIRouter(prefix="/professores", tags=["Professores"])


@router.post("/", response_model=ProfessorPublic)
def criar_professor(professor: ProfessorCreate, session: Session = Depends(get_session)):
    db_professor = Professor.model_validate(professor)
    session.add(db_professor)
    session.commit()
    session.refresh(db_professor)
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
def atualizar_professor(professor_id: int, dados: ProfessorUpdate, session: Session = Depends(get_session)):
    professor = session.get(Professor, professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(professor, campo, valor)
    session.add(professor)
    session.commit()
    session.refresh(professor)
    return professor


@router.delete("/{professor_id}")
def deletar_professor(professor_id: int, session: Session = Depends(get_session)):
    professor = session.get(Professor, professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")
    session.delete(professor)
    session.commit()
    return {"ok": True}
