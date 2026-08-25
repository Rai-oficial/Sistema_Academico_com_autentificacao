import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_all():
    # Login as admin
    login_admin = client.post("/usuarios/login", data={"username": "admin@academico.com", "password": "senha123_admin"})
    token_admin = login_admin.json()["access_token"]
    h_admin = {"Authorization": f"Bearer {token_admin}"}

    # Login as Carlos (padrao)
    login_carlos = client.post("/usuarios/login", data={"username": "carlos@academico.com", "password": "senha123_carlos"})
    token_carlos = login_carlos.json()["access_token"]
    h_carlos = {"Authorization": f"Bearer {token_carlos}"}

    # Login as Mariana (padrao)
    login_mariana = client.post("/usuarios/login", data={"username": "mariana@academico.com", "password": "senha123_mariana"})
    token_mariana = login_mariana.json()["access_token"]
    h_mariana = {"Authorization": f"Bearer {token_mariana}"}

    print("--- Testando Departamento ---")
    d_resp = client.post("/departamentos/", json={"nome": "Departamento de Computacao"}, headers=h_carlos)
    assert d_resp.status_code == 200
    depto_id = d_resp.json()["id"]
    assert d_resp.json()["owner_id"] is not None

    # Mariana cannot update depto
    assert client.put(f"/departamentos/{depto_id}", json={"nome": "Computacao Modificada"}, headers=h_mariana).status_code == 403
    # Carlos can update
    assert client.put(f"/departamentos/{depto_id}", json={"nome": "Computacao e Tecnologia"}, headers=h_carlos).status_code == 200

    print("--- Testando Curso ---")
    c_resp = client.post("/cursos/", json={
        "nome": "Ciencia da Computacao", "cargaHoraria": 3000, "quantidadeSemestres": 8, "id_departamento": depto_id
    }, headers=h_carlos)
    assert c_resp.status_code == 200
    curso_id = c_resp.json()["id"]

    print("--- Testando Disciplina ---")
    disc_resp = client.post("/disciplinas/", json={
        "codigo": "DCC001", "nome": "Algoritmos e Estruturas de Dados", "creditos": 4, "id_curso": curso_id
    }, headers=h_carlos)
    assert disc_resp.status_code == 200
    disc_id = disc_resp.json()["id"]

    print("--- Testando Periodo Letivo ---")
    per_resp = client.post("/periodos-letivos/", json={
        "ano": 2026, "semestre": 2, "dataInicio": "2026-08-01", "dataFim": "2026-12-15"
    }, headers=h_carlos)
    assert per_resp.status_code == 200
    per_id = per_resp.json()["id"]

    print("--- Testando Professor ---")
    prof_resp = client.post("/professores/", json={
        "nome": "Prof. Alan Turing", "cpf": "11122233344", "dataNascimento": "1980-06-23",
        "sexo": "M", "telefone": "11988887777", "formacao": "Doutorado em Computacao",
        "anoContratacao": 2020, "status": "Ativo", "id_departamento": depto_id
    }, headers=h_carlos)
    assert prof_resp.status_code == 200
    prof_id = prof_resp.json()["id"]

    print("--- Testando Turma ---")
    turma_resp = client.post("/turmas/", json={
        "codigo": "TURMA-CC-2026-2", "turno": "Matutino", "vagas": 40,
        "id_disciplina": disc_id, "id_professor": prof_id, "id_periodoletivo": per_id
    }, headers=h_carlos)
    assert turma_resp.status_code == 200
    turma_id = turma_resp.json()["id"]

    print("--- Testando Aluno & Matricula & Desempenho ---")
    aluno_resp = client.post("/alunos/", json={
        "nome": "Ada Lovelace", "cpf": "55566677788", "dataNascimento": "2002-12-10",
        "sexo": "F", "telefone": "11977776666", "status": "Ativo"
    }, headers=h_carlos)
    assert aluno_resp.status_code == 200
    aluno_id = aluno_resp.json()["id"]

    # Matricular na turma
    matr_turma_resp = client.post(f"/turmas/{turma_id}/matricular/{aluno_id}", headers=h_carlos)
    assert matr_turma_resp.status_code == 200

    # Registro de Matricula
    reg_resp = client.post("/matriculas/", json={
        "id_aluno": aluno_id, "dataMatricula": "2026-08-01", "situacao": "Ativa"
    }, headers=h_carlos)
    assert reg_resp.status_code == 200
    reg_id = reg_resp.json()["id"]

    # Desempenho
    desemp_resp = client.post("/desempenhos/", json={
        "id_aluno": aluno_id, "id_turma": turma_id, "nota1": 9.5, "nota2": 8.5,
        "nota3": 9.0, "mediaFinal": 9.0, "notaRecuperacao": None, "situacaoFinal": "Aprovado"
    }, headers=h_carlos)
    assert desemp_resp.status_code == 200

    # Mariana cannot update desempenho
    assert client.put(f"/desempenhos/aluno/{aluno_id}/turma/{turma_id}", json={"nota1": 4.0}, headers=h_mariana).status_code == 403
    # Carlos can update
    assert client.put(f"/desempenhos/aluno/{aluno_id}/turma/{turma_id}", json={"nota1": 10.0}, headers=h_carlos).status_code == 200

    print("--- Testando Relatorios ---")
    rel_resp = client.get("/relatorios/alunos-por-curso")
    assert rel_resp.status_code == 200
    assert len(rel_resp.json()) > 0
    print("   -> Relatorio alunos-por-curso:", rel_resp.json())

    print("\n=== TODAS AS ROTAS E ENTIDADES ESTAO FUNCIONANDO PERFEITAMENTE! ===")

if __name__ == "__main__":
    test_all()
