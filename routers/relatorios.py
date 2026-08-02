from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from database import get_session
from models import Aluno, Professor, Curso, Disciplina, Turma, Aluno_Turma, Desempenho, RegistroMatricula
from schemas import AlunoPublic, TurmaPublic, DesempenhoPublic, RegistroMatriculaPublic

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/alunos-por-curso")
def quantidade_alunos_por_curso(session: Session = Depends(get_session)):
    resultado = session.exec(
        select(Curso.nome, func.count(func.distinct(Aluno.id)))
        .join(Disciplina, Disciplina.id_curso == Curso.id)
        .join(Turma, Turma.id_disciplina == Disciplina.id)
        .join(Aluno_Turma, Aluno_Turma.id_turma == Turma.id)
        .join(Aluno, Aluno.id == Aluno_Turma.id_aluno)
        .group_by(Curso.nome)
    ).all()
    return [{"curso": nome, "quantidade_alunos": qtd} for nome, qtd in resultado]


@router.get("/alunos-por-turma")
def quantidade_alunos_por_turma(session: Session = Depends(get_session)):
    resultado = session.exec(
        select(Turma.codigo, func.count(Aluno_Turma.id_aluno))
        .join(Aluno_Turma, Aluno_Turma.id_turma == Turma.id)
        .group_by(Turma.codigo)
    ).all()
    return [{"turma": codigo, "quantidade_alunos": qtd} for codigo, qtd in resultado]


@router.get("/turmas-por-professor")
def quantidade_turmas_por_professor(session: Session = Depends(get_session)):
    resultado = session.exec(
        select(Professor.nome, func.count(Turma.id))
        .join(Turma, Turma.id_professor == Professor.id)
        .group_by(Professor.nome)
    ).all()
    return [{"professor": nome, "quantidade_turmas": qtd} for nome, qtd in resultado]


@router.get("/disciplinas-por-curso")
def quantidade_disciplinas_por_curso(session: Session = Depends(get_session)):
    resultado = session.exec(
        select(Curso.nome, func.count(Disciplina.id))
        .join(Disciplina, Disciplina.id_curso == Curso.id)
        .group_by(Curso.nome)
    ).all()
    return [{"curso": nome, "quantidade_disciplinas": qtd} for nome, qtd in resultado]


@router.get("/media-turma/{turma_id}")
def media_da_turma(turma_id: int, session: Session = Depends(get_session)):
    turma = session.get(Turma, turma_id)
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    media = session.exec(
        select(func.avg(Desempenho.mediaFinal)).where(Desempenho.id_turma == turma_id)
    ).first()
    return {"turma": turma.codigo, "media_geral": float(media) if media is not None else None}


@router.get("/aprovados-reprovados/{turma_id}")
def aprovados_reprovados_por_turma(turma_id: int, session: Session = Depends(get_session)):
    turma = session.get(Turma, turma_id)
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    resultado = session.exec(
        select(Desempenho.situacaoFinal, func.count(Desempenho.id_aluno))
        .where(Desempenho.id_turma == turma_id)
        .group_by(Desempenho.situacaoFinal)
    ).all()
    return [{"situacao": situacao, "quantidade": qtd} for situacao, qtd in resultado]


@router.get("/professor-mais-turmas")
def professor_com_mais_turmas(session: Session = Depends(get_session)):
    resultado = session.exec(
        select(Professor.nome, func.count(Turma.id).label("qtd"))
        .join(Turma, Turma.id_professor == Professor.id)
        .group_by(Professor.nome)
        .order_by(func.count(Turma.id).desc())
    ).first()
    if not resultado:
        raise HTTPException(status_code=404, detail="Nenhuma turma encontrada")
    nome, qtd = resultado
    return {"professor": nome, "quantidade_turmas": qtd}


@router.get("/curso-mais-alunos")
def curso_com_mais_alunos(session: Session = Depends(get_session)):
    resultado = session.exec(
        select(Curso.nome, func.count(func.distinct(Aluno.id)).label("qtd"))
        .join(Disciplina, Disciplina.id_curso == Curso.id)
        .join(Turma, Turma.id_disciplina == Disciplina.id)
        .join(Aluno_Turma, Aluno_Turma.id_turma == Turma.id)
        .join(Aluno, Aluno.id == Aluno_Turma.id_aluno)
        .group_by(Curso.nome)
        .order_by(func.count(func.distinct(Aluno.id)).desc())
    ).first()
    if not resultado:
        raise HTTPException(status_code=404, detail="Nenhum aluno matriculado encontrado")
    nome, qtd = resultado
    return {"curso": nome, "quantidade_alunos": qtd}


@router.get("/historico-academico/{aluno_id}")
def historico_academico_do_aluno(aluno_id: int, session: Session = Depends(get_session)):
    """Combina matrículas + turmas + notas de um aluno num único retorno."""
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    matriculas = session.exec(
        select(RegistroMatricula).where(RegistroMatricula.id_aluno == aluno_id)
    ).all()
    turmas = aluno.turmas
    desempenhos = session.exec(
        select(Desempenho).where(Desempenho.id_aluno == aluno_id)
    ).all()

    return {
        "aluno": AlunoPublic.model_validate(aluno),
        "matriculas": [RegistroMatriculaPublic.model_validate(m) for m in matriculas],
        "turmas": [TurmaPublic.model_validate(t) for t in turmas],
        "desempenhos": [DesempenhoPublic.model_validate(d) for d in desempenhos],
    }
