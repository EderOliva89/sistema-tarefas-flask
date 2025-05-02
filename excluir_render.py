import psycopg2

# Conexão com banco do Render
conn = psycopg2.connect(
    dbname="tarefas_db_0nh8",
    user="eder",
    password="ZNUN3pcl1LpodgbRz6hneUS0GanaY9Gl",
    host="dpg-d07n271r0fns738o07h0-a.virginia-postgres.render.com",
    port="5432"
)

cursor = conn.cursor()

# Exibe os usuários cadastrados
cursor.execute("SELECT id, nome, username FROM usuarios ORDER BY id")
usuarios = cursor.fetchall()

print("\n👥 Usuários cadastrados:")
for u in usuarios:
    print(f"{u[0]} - {u[1]} ({u[2]})")

id_excluir = input("\nDigite o ID do usuário que deseja excluir (ou Enter para sair): ")

if id_excluir.strip():
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_excluir,))
    conn.commit()
    print("🗑️ Usuário excluído com sucesso!")

conn.close()
