import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def run_tests():
    print("=== INICIANDO TESTES DO SISTEMA DE OWNER E LOGS ===")

    # 1. Registrar Usuário Padrão 1
    resp_user1 = client.post("/usuarios/", json={
        "nome": "Carlos Silva",
        "email": "carlos@academico.com",
        "senha": "senha123_carlos",
        "papel": "padrao"
    })
    print(f"1. Criar Usuario 1 (Padrao): {resp_user1.status_code}")
    assert resp_user1.status_code in (200, 400), f"Erro ao criar usuario 1: {resp_user1.text}"

    # 2. Registrar Usuário Padrão 2
    resp_user2 = client.post("/usuarios/", json={
        "nome": "Mariana Souza",
        "email": "mariana@academico.com",
        "senha": "senha123_mariana",
        "papel": "padrao"
    })
    print(f"2. Criar Usuario 2 (Padrao): {resp_user2.status_code}")
    assert resp_user2.status_code in (200, 400), f"Erro ao criar usuario 2: {resp_user2.text}"

    # 3. Registrar Usuário Admin
    resp_admin = client.post("/usuarios/", json={
        "nome": "Diretora Ana",
        "email": "admin@academico.com",
        "senha": "senha123_admin",
        "papel": "admin"
    })
    print(f"3. Criar Usuario Admin: {resp_admin.status_code}")
    assert resp_admin.status_code in (200, 400), f"Erro ao criar admin: {resp_admin.text}"

    # 4. Fazer Login com Usuário 1
    login_user1 = client.post("/usuarios/login", data={
        "username": "carlos@academico.com",
        "password": "senha123_carlos"
    })
    assert login_user1.status_code == 200, f"Falha no login user1: {login_user1.text}"
    token_user1 = login_user1.json()["access_token"]
    headers_user1 = {"Authorization": f"Bearer {token_user1}"}
    print("4. Login Usuario 1: Sucesso")

    # 5. Fazer Login com Usuário 2
    login_user2 = client.post("/usuarios/login", data={
        "username": "mariana@academico.com",
        "password": "senha123_mariana"
    })
    assert login_user2.status_code == 200, f"Falha no login user2: {login_user2.text}"
    token_user2 = login_user2.json()["access_token"]
    headers_user2 = {"Authorization": f"Bearer {token_user2}"}
    print("5. Login Usuario 2: Sucesso")

    # 6. Fazer Login com Admin
    login_admin = client.post("/usuarios/login", data={
        "username": "admin@academico.com",
        "password": "senha123_admin"
    })
    assert login_admin.status_code == 200, f"Falha no login admin: {login_admin.text}"
    token_admin = login_admin.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    print("6. Login Admin: Sucesso")

    # 7. Testar GET /usuarios/me
    me_resp = client.get("/usuarios/me", headers=headers_user1)
    assert me_resp.status_code == 200
    user1_id = me_resp.json()["id"]
    print(f"7. /usuarios/me de Carlos: ID={user1_id}, Email={me_resp.json()['email']}")

    # 8. Usuário 1 cria um Aluno
    cpf_teste = f"99988877{user1_id:03d}"
    aluno_resp = client.post("/alunos/", json={
        "nome": "Aluno do Carlos",
        "cpf": cpf_teste,
        "dataNascimento": "2000-01-15",
        "sexo": "M",
        "telefone": "11999998888",
        "status": "Ativo"
    }, headers=headers_user1)
    print(f"8. Criar Aluno (pelo Usuario 1): {aluno_resp.status_code}")
    assert aluno_resp.status_code == 200, f"Erro ao criar aluno: {aluno_resp.text}"
    aluno_data = aluno_resp.json()
    aluno_id = aluno_data["id"]
    assert aluno_data["owner_id"] == user1_id, f"owner_id incorreto: esperado {user1_id}, obteve {aluno_data.get('owner_id')}"
    print(f"   -> Aluno criado com ID={aluno_id} e owner_id={aluno_data['owner_id']}")

    # 9. Usuário 2 tenta ATUALIZAR o Aluno de Usuário 1 (deve receber 403 Forbidden)
    upd_forbidden = client.put(f"/alunos/{aluno_id}", json={
        "nome": "Nome Alterado por Intruso"
    }, headers=headers_user2)
    print(f"9. Tentativa de Atualizacao por Outro Usuario (User 2): Status {upd_forbidden.status_code}")
    assert upd_forbidden.status_code == 403, f"Esperado 403, obteve: {upd_forbidden.status_code}"
    print("   -> [OK] Bloqueado com 403 Forbidden!")

    # 10. Usuário 2 tenta DELETAR o Aluno de Usuário 1 (deve receber 403 Forbidden)
    del_forbidden = client.delete(f"/alunos/{aluno_id}", headers=headers_user2)
    print(f"10. Tentativa de Delecao por Outro Usuario (User 2): Status {del_forbidden.status_code}")
    assert del_forbidden.status_code == 403, f"Esperado 403, obteve: {del_forbidden.status_code}"
    print("   -> [OK] Bloqueado com 403 Forbidden!")

    # 11. Usuário 1 atualiza seu próprio Aluno (deve receber 200 OK)
    upd_allowed = client.put(f"/alunos/{aluno_id}", json={
        "nome": "Aluno do Carlos (Atualizado pelo Dono)"
    }, headers=headers_user1)
    print(f"11. Atualizacao pelo Proprio Dono (User 1): Status {upd_allowed.status_code}")
    assert upd_allowed.status_code == 200
    assert upd_allowed.json()["nome"] == "Aluno do Carlos (Atualizado pelo Dono)"
    print("   -> [OK] Atualizado com sucesso!")

    # 12. Admin atualiza o Aluno de Usuário 1 (Admin tem permissão total)
    upd_admin = client.put(f"/alunos/{aluno_id}", json={
        "nome": "Aluno do Carlos (Supervisionado pelo Admin)"
    }, headers=headers_admin)
    print(f"12. Atualizacao pelo Admin: Status {upd_admin.status_code}")
    assert upd_admin.status_code == 200
    assert upd_admin.json()["nome"] == "Aluno do Carlos (Supervisionado pelo Admin)"
    print("   -> [OK] Admin atualizou com sucesso!")

    # 13. Usuário Comum tenta acessar /logs (deve receber 403 Forbidden)
    logs_forbidden = client.get("/logs/", headers=headers_user1)
    print(f"13. Usuario Comum acessando /logs: Status {logs_forbidden.status_code}")
    assert logs_forbidden.status_code == 403
    print("   -> [OK] Bloqueado com 403 Forbidden!")

    # 14. Admin acessa /logs (deve receber 200 OK e lista de logs)
    logs_admin = client.get("/logs/", headers=headers_admin)
    print(f"14. Admin acessando /logs: Status {logs_admin.status_code}")
    assert logs_admin.status_code == 200
    lista_logs = logs_admin.json()
    print(f"   -> Total de logs registrados no banco: {len(lista_logs)}")
    assert len(lista_logs) > 0

    # Imprimir últimos 5 logs para demonstração
    print("   -> Ultimos 5 logs de auditoria:")
    for log in lista_logs[:5]:
        print(f"      * [{log['acao']}] User: {log['usuario_email']} | Recurso: {log['tabela_afetada']} #{log['registro_id']} | Detalhes: {log['detalhes']}")

    # 15. Admin deleta o Aluno de teste
    del_admin = client.delete(f"/alunos/{aluno_id}", headers=headers_admin)
    assert del_admin.status_code == 200
    print(f"15. Admin exclui o Aluno: Status {del_admin.status_code}")

    # 16. Verificar se arquivo sistema_academico.log existe
    assert os.path.exists("sistema_academico.log"), "Arquivo de log 'sistema_academico.log' nao foi gerado!"
    print("16. Arquivo de log 'sistema_academico.log' validado com sucesso!")

    print("\n=== TODOS OS TESTES PASSARAM COM SUCESSO (100% OK) ===")

if __name__ == "__main__":
    run_tests()
