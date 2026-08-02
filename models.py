from sqlmodel import Field, SQLModel, Relationship
from datetime import date
from decimal import Decimal
from sqlalchemy import Column, Numeric
from enum import Enum


class Aluno_Turma(SQLModel, table=True):
    id_aluno: int | None = Field(default=None, foreign_key="aluno.id", primary_key=True)
    id_turma: int | None = Field(default=None, foreign_key="turma.id", primary_key=True)


class Aluno (SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    cpf: str = Field(unique=True)
    dataNascimento: date
    sexo: str
    telefone: str
    status: str
    turmas: list["Turma"] = Relationship(back_populates="alunos", link_model = Aluno_Turma)
    registros_matriculas: list["RegistroMatricula"] = Relationship(back_populates="aluno")
    desempenhos: list["Desempenho"] = Relationship(back_populates="aluno")


class Professor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    cpf: str = Field(unique=True)
    dataNascimento: date
    sexo: str
    telefone: str
    formacao: str
    anoContratacao: int
    status: str
    id_departamento: int | None= Field(default=None, foreign_key="departamento.id")
    departamento: "Departamento" = Relationship(back_populates="professores")
    turmas: list["Turma"] = Relationship(back_populates="professor")

class Departamento(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(unique=True)
    professores: list["Professor"] = Relationship(back_populates="departamento")
    cursos: list["Curso"] = Relationship(back_populates="departamento")

class Curso(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    cargaHoraria: int
    quantidadeSemestres: int
    id_departamento: int | None = Field(default=None, foreign_key="departamento.id")
    departamento: "Departamento" = Relationship(back_populates="cursos")
    disciplinas: list["Disciplina"] = Relationship(back_populates="curso")

class Disciplina(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True)
    nome: str
    creditos: int
    id_curso: int | None = Field(default=None, foreign_key="curso.id")
    curso: "Curso" = Relationship(back_populates="disciplinas")
    turmas: list["Turma"] = Relationship(back_populates="disciplina")

class Turma(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True)
    turno: str
    vagas: int
    id_disciplina: int | None = Field(default=None, foreign_key="disciplina.id")
    id_professor: int | None = Field(default=None, foreign_key="professor.id")
    id_periodoletivo: int | None = Field(default=None, foreign_key="periodoletivo.id")
    disciplina: "Disciplina" = Relationship(back_populates="turmas")
    professor: "Professor" = Relationship(back_populates="turmas")
    periodo_letivo: "PeriodoLetivo" = Relationship(back_populates="turmas")
    alunos: list["Aluno"] = Relationship(back_populates="turmas", link_model= Aluno_Turma)
    desempenhos: list["Desempenho"] = Relationship(back_populates="turma")


class RegistroMatricula(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_aluno: int | None = Field(default=None, foreign_key="aluno.id")
    dataMatricula: date
    situacao: str
    aluno: "Aluno" = Relationship(back_populates="registros_matriculas")

class Desempenho(SQLModel, table=True):
    id_aluno: int | None = Field(default=None, foreign_key="aluno.id", primary_key=True)
    id_turma: int | None = Field(default=None, foreign_key="turma.id", primary_key=True )
    nota1: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    nota2: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    nota3: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    mediaFinal: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    notaRecuperacao: Decimal | None = Field(default = None, sa_column=Column(Numeric(4, 2)))
    situacaoFinal: str
    aluno: "Aluno" = Relationship(back_populates="desempenhos")
    turma: "Turma" = Relationship(back_populates="desempenhos")

class PeriodoLetivo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ano: int
    semestre: int
    dataInicio: date
    dataFim: date
    turmas: list["Turma"] = Relationship(back_populates="periodo_letivo")

class PapelUsuario(str, Enum):
    admin = "admin"
    padrao = "padrao"


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    nome: str
    email: str = Field(index=True, unique=True)

    senha_hash: str

    ativo: bool = True

    papel: PapelUsuario = Field(default=PapelUsuario.padrao)









