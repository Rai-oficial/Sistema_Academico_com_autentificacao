from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import RegistroMatricula
from schemas import RegistroMatriculaPublic, RegistroMatriculaCreate, RegistroMatriculaUpdate

router = APIRouter(prefix="/matriculas", tags=["Registros de Matrícula"])


@router.post("/", response_model=RegistroMatriculaPublic)
def criar_registro_matricula(registro: RegistroMatriculaCreate, session: Session = Depends(get_session)):
    db_registro = RegistroMatricula.model_validate(registro)
    session.add(db_registro)
    session.commit()
    session.refresh(db_registro)
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
def atualizar_registro_matricula(registro_id: int, dados: RegistroMatriculaUpdate, session: Session = Depends(get_session)):
    registro = session.get(RegistroMatricula, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(registro, campo, valor)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


@router.delete("/{registro_id}")
def deletar_registro_matricula(registro_id: int, session: Session = Depends(get_session)):
    registro = session.get(RegistroMatricula, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    session.delete(registro)
    session.commit()
    return {"ok": True}
