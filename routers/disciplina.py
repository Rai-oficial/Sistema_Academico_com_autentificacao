from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Disciplina
from schemas import DisciplinaPublic, DisciplinaCreate, DisciplinaUpdate, TurmaPublic, CursoPublic

router = APIRouter(prefix="/disciplinas", tags=["Disciplinas"])


@router.post("/", response_model=DisciplinaPublic)
def criar_disciplina(disciplina: DisciplinaCreate, session: Session = Depends(get_session)):
    db_disciplina = Disciplina.model_validate(disciplina)
    session.add(db_disciplina)
    session.commit()
    session.refresh(db_disciplina)
    return db_disciplina


@router.get("/", response_model=list[DisciplinaPublic])
def listar_disciplinas(session: Session = Depends(get_session)):
    return session.exec(select(Disciplina)).all()


@router.get("/codigo/{codigo}", response_model=DisciplinaPublic)
def buscar_disciplina_por_codigo(codigo: str, session: Session = Depends(get_session)):
    disciplina = session.exec(select(Disciplina).where(Disciplina.codigo == codigo)).first()
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return disciplina


@router.get("/buscar/nome", response_model=list[DisciplinaPublic])
def buscar_disciplina_por_nome(nome: str, session: Session = Depends(get_session)):
    return session.exec(select(Disciplina).where(Disciplina.nome.contains(nome))).all()


@router.get("/{disciplina_id}", response_model=DisciplinaPublic)
def buscar_disciplina_por_id(disciplina_id: int, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return disciplina


@router.get("/{disciplina_id}/turmas", response_model=list[TurmaPublic])
def turmas_da_disciplina(disciplina_id: int, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return disciplina.turmas


@router.get("/{disciplina_id}/curso", response_model=CursoPublic)
def curso_da_disciplina(disciplina_id: int, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    if not disciplina.curso:
        raise HTTPException(status_code=404, detail="Disciplina sem curso associado")
    return disciplina.curso


@router.put("/{disciplina_id}", response_model=DisciplinaPublic)
def atualizar_disciplina(disciplina_id: int, dados: DisciplinaUpdate, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(disciplina, campo, valor)
    session.add(disciplina)
    session.commit()
    session.refresh(disciplina)
    return disciplina


@router.delete("/{disciplina_id}")
def deletar_disciplina(disciplina_id: int, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    session.delete(disciplina)
    session.commit()
    return {"ok": True}
