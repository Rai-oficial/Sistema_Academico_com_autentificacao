from datetime import date, datetime
from decimal import Decimal
from sqlmodel import SQLModel
from enum import Enum


class AlunoBase(SQLModel):
    nome: str
    cpf: str
    dataNascimento: date
    sexo: str
    telefone: str
    status: str

class AlunoCreate(AlunoBase):
    pass

class AlunoPublic(AlunoBase):
    id: int
    owner_id: int | None = None

class AlunoUpdate(SQLModel):
    nome: str | None = None
    cpf: str | None = None
    dataNascimento: date | None = None
    sexo: str | None = None
    telefone: str | None = None
    status: str | None = None



class ProfessorBase(SQLModel):
    nome: str
    cpf: str
    dataNascimento: date
    sexo: str
    telefone: str
    formacao: str
    anoContratacao: int
    status: str
    id_departamento: int | None = None

class ProfessorCreate(ProfessorBase):
    pass

class ProfessorPublic(ProfessorBase):
    id: int
    owner_id: int | None = None

class ProfessorUpdate(SQLModel):
    nome: str | None = None
    cpf: str | None = None
    dataNascimento: date | None = None
    sexo: str | None = None
    telefone: str | None = None
    formacao: str | None = None
    anoContratacao: int | None = None
    status: str | None = None
    id_departamento: int | None = None



class DepartamentoBase(SQLModel):
    nome: str

class DepartamentoCreate(DepartamentoBase):
    pass

class DepartamentoPublic(DepartamentoBase):
    id: int
    owner_id: int | None = None

class DepartamentoUpdate(SQLModel):
    nome: str | None = None



class CursoBase(SQLModel):
    nome: str
    cargaHoraria: int
    quantidadeSemestres: int
    id_departamento: int | None = None

class CursoCreate(CursoBase):
    pass

class CursoPublic(CursoBase):
    id: int
    owner_id: int | None = None

class CursoUpdate(SQLModel):
    nome: str | None = None
    cargaHoraria: int | None = None
    quantidadeSemestres: int | None = None
    id_departamento: int | None = None



class DisciplinaBase(SQLModel):
    codigo: str
    nome: str
    creditos: int
    id_curso: int | None = None


class DisciplinaCreate(DisciplinaBase):
    pass


class DisciplinaPublic(DisciplinaBase):
    id: int
    owner_id: int | None = None


class DisciplinaUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None
    creditos: int | None = None
    id_curso: int | None = None



class TurmaBase(SQLModel):
    codigo: str
    turno: str
    vagas: int
    id_disciplina: int | None = None
    id_professor: int | None = None
    id_periodoletivo: int | None = None


class TurmaCreate(TurmaBase):
    pass


class TurmaPublic(TurmaBase):
    id: int
    owner_id: int | None = None


class TurmaUpdate(SQLModel):
    codigo: str | None = None
    turno: str | None = None
    vagas: int | None = None
    id_disciplina: int | None = None
    id_professor: int | None = None
    id_periodoletivo: int | None = None



class PeriodoLetivoBase(SQLModel):
    ano: int
    semestre: int
    dataInicio: date
    dataFim: date


class PeriodoLetivoCreate(PeriodoLetivoBase):
    pass


class PeriodoLetivoPublic(PeriodoLetivoBase):
    id: int
    owner_id: int | None = None


class PeriodoLetivoUpdate(SQLModel):
    ano: int | None = None
    semestre: int | None = None
    dataInicio: date | None = None
    dataFim: date | None = None



class RegistroMatriculaBase(SQLModel):
    id_aluno: int
    dataMatricula: date
    situacao: str


class RegistroMatriculaCreate(RegistroMatriculaBase):
    pass


class RegistroMatriculaPublic(RegistroMatriculaBase):
    id: int
    owner_id: int | None = None


class RegistroMatriculaUpdate(SQLModel):
    situacao: str | None = None



class DesempenhoBase(SQLModel):
    id_aluno: int
    id_turma: int
    nota1: Decimal
    nota2: Decimal
    nota3: Decimal
    mediaFinal: Decimal
    notaRecuperacao: Decimal | None = None
    situacaoFinal: str


class DesempenhoCreate(DesempenhoBase):
    pass


class DesempenhoPublic(DesempenhoBase):
    owner_id: int | None = None


class DesempenhoUpdate(SQLModel):
    nota1: Decimal | None = None
    nota2: Decimal | None = None
    nota3: Decimal | None = None
    mediaFinal: Decimal | None = None
    notaRecuperacao: Decimal | None = None
    situacaoFinal: str | None = None



class PapelUsuario(str, Enum):
    admin = "admin"
    padrao = "padrao"


class UsuarioBase(SQLModel):
    nome: str
    email: str


class UsuarioCreate(UsuarioBase):
    senha: str
    papel: PapelUsuario = PapelUsuario.padrao


class UsuarioPublic(UsuarioBase):
    id: int
    ativo: bool
    papel: PapelUsuario


class UsuarioLogin(SQLModel):
    email: str
    senha: str


class Token(SQLModel):
    access_token: str
    token_type: str


class UsuarioMeResponse(UsuarioPublic):
    pass


class RegistroLogPublic(SQLModel):
    id: int
    usuario_id: int | None = None
    usuario_email: str | None = None
    acao: str
    tabela_afetada: str | None = None
    registro_id: int | None = None
    detalhes: str | None = None
    ip_origem: str | None = None
    status_code: int
    data_hora: datetime
    