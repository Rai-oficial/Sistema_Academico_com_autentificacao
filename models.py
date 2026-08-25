from sqlmodel import Field, SQLModel, Relationship
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Column, Numeric
from enum import Enum


class Aluno_Turma(SQLModel, table=True):
    id_aluno: int | None = Field(default=None, foreign_key="aluno.id", primary_key=True)
    id_turma: int | None = Field(default=None, foreign_key="turma.id", primary_key=True)


class Aluno(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    cpf: str = Field(unique=True)
    dataNascimento: date
    sexo: str
    telefone: str
    status: str
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    turmas: list["Turma"] = Relationship(back_populates="alunos", link_model=Aluno_Turma)
    registros_matriculas: list["RegistroMatricula"] = Relationship(back_populates="aluno")
    desempenhos: list["Desempenho"] = Relationship(back_populates="aluno")
    owner: "Usuario" = Relationship(back_populates="alunos")


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
    id_departamento: int | None = Field(default=None, foreign_key="departamento.id")
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    departamento: "Departamento" = Relationship(back_populates="professores")
    turmas: list["Turma"] = Relationship(back_populates="professor")
    owner: "Usuario" = Relationship(back_populates="professores")


class Departamento(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(unique=True)
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    professores: list["Professor"] = Relationship(back_populates="departamento")
    cursos: list["Curso"] = Relationship(back_populates="departamento")
    owner: "Usuario" = Relationship(back_populates="departamentos")


class Curso(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    cargaHoraria: int
    quantidadeSemestres: int
    id_departamento: int | None = Field(default=None, foreign_key="departamento.id")
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    departamento: "Departamento" = Relationship(back_populates="cursos")
    disciplinas: list["Disciplina"] = Relationship(back_populates="curso")
    owner: "Usuario" = Relationship(back_populates="cursos")


class Disciplina(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True)
    nome: str
    creditos: int
    id_curso: int | None = Field(default=None, foreign_key="curso.id")
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    curso: "Curso" = Relationship(back_populates="disciplinas")
    turmas: list["Turma"] = Relationship(back_populates="disciplina")
    owner: "Usuario" = Relationship(back_populates="disciplinas")


class Turma(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True)
    turno: str
    vagas: int
    id_disciplina: int | None = Field(default=None, foreign_key="disciplina.id")
    id_professor: int | None = Field(default=None, foreign_key="professor.id")
    id_periodoletivo: int | None = Field(default=None, foreign_key="periodoletivo.id")
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    disciplina: "Disciplina" = Relationship(back_populates="turmas")
    professor: "Professor" = Relationship(back_populates="turmas")
    periodo_letivo: "PeriodoLetivo" = Relationship(back_populates="turmas")
    alunos: list["Aluno"] = Relationship(back_populates="turmas", link_model=Aluno_Turma)
    desempenhos: list["Desempenho"] = Relationship(back_populates="turma")
    owner: "Usuario" = Relationship(back_populates="turmas")


class RegistroMatricula(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_aluno: int | None = Field(default=None, foreign_key="aluno.id")
    dataMatricula: date
    situacao: str
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    aluno: "Aluno" = Relationship(back_populates="registros_matriculas")
    owner: "Usuario" = Relationship(back_populates="matriculas")


class Desempenho(SQLModel, table=True):
    id_aluno: int | None = Field(default=None, foreign_key="aluno.id", primary_key=True)
    id_turma: int | None = Field(default=None, foreign_key="turma.id", primary_key=True)
    nota1: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    nota2: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    nota3: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    mediaFinal: Decimal = Field(sa_column=Column(Numeric(4, 2)))
    notaRecuperacao: Decimal | None = Field(default=None, sa_column=Column(Numeric(4, 2)))
    situacaoFinal: str
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    aluno: "Aluno" = Relationship(back_populates="desempenhos")
    turma: "Turma" = Relationship(back_populates="desempenhos")
    owner: "Usuario" = Relationship(back_populates="desempenhos")


class PeriodoLetivo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ano: int
    semestre: int
    dataInicio: date
    dataFim: date
    owner_id: int | None = Field(default=None, foreign_key="usuario.id")

    turmas: list["Turma"] = Relationship(back_populates="periodo_letivo")
    owner: "Usuario" = Relationship(back_populates="periodos_letivos")


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

    alunos: list["Aluno"] = Relationship(back_populates="owner")
    professores: list["Professor"] = Relationship(back_populates="owner")
    departamentos: list["Departamento"] = Relationship(back_populates="owner")
    cursos: list["Curso"] = Relationship(back_populates="owner")
    disciplinas: list["Disciplina"] = Relationship(back_populates="owner")
    turmas: list["Turma"] = Relationship(back_populates="owner")
    matriculas: list["RegistroMatricula"] = Relationship(back_populates="owner")
    desempenhos: list["Desempenho"] = Relationship(back_populates="owner")
    periodos_letivos: list["PeriodoLetivo"] = Relationship(back_populates="owner")
    logs: list["RegistroLog"] = Relationship(back_populates="usuario")


class RegistroLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int | None = Field(default=None, foreign_key="usuario.id")
    usuario_email: str | None = None
    acao: str
    tabela_afetada: str | None = None
    registro_id: int | None = None
    detalhes: str | None = None
    ip_origem: str | None = None
    status_code: int = 200
    data_hora: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    usuario: Usuario | None = Relationship(back_populates="logs")









