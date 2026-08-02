from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Departamento
from schemas import DepartamentoPublic, DepartamentoCreate, DepartamentoUpdate, ProfessorPublic, CursoPublic

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.post("/", response_model=DepartamentoPublic)
def criar_departamento(departamento: DepartamentoCreate, session: Session = Depends(get_session)):
    db_departamento = Departamento.model_validate(departamento)
    session.add(db_departamento)
    session.commit()
    session.refresh(db_departamento)
    return db_departamento


@router.get("/", response_model=list[DepartamentoPublic])
def listar_departamentos(session: Session = Depends(get_session)):
    return session.exec(select(Departamento)).all()


@router.get("/{departamento_id}", response_model=DepartamentoPublic)
def buscar_departamento_por_id(departamento_id: int, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento


@router.get("/{departamento_id}/professores", response_model=list[ProfessorPublic])
def professores_do_departamento(departamento_id: int, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento.professores


@router.get("/{departamento_id}/cursos", response_model=list[CursoPublic])
def cursos_do_departamento(departamento_id: int, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento.cursos


@router.put("/{departamento_id}", response_model=DepartamentoPublic)
def atualizar_departamento(departamento_id: int, dados: DepartamentoUpdate, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(departamento, campo, valor)
    session.add(departamento)
    session.commit()
    session.refresh(departamento)
    return departamento


@router.delete("/{departamento_id}")
def deletar_departamento(departamento_id: int, session: Session = Depends(get_session)):
    departamento = session.get(Departamento, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    session.delete(departamento)
    session.commit()
    return {"ok": True}
