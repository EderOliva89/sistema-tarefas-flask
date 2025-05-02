import psycopg2

# Conexão com banco no RENDER
conn = psycopg2.connect(
    dbname="tarefas_db_0nh8",
    user="eder",
    password="ZNUN3pcl1LpodgbRz6hneUS0GanaY9Gl",
    host="dpg-d07n271r0fns738o07h0-a.virginia-postgres.render.com",
    port="5432"
)

cursor = conn.cursor()
cursor.execute("SELECT id, nome, username, ativo FROM usuarios ORDER BY id")
usuarios = cursor.fetchall()

print("\n🌐 Usuários cadastrados no Render:")
for u in usuarios:
    status = "✅ Ativo" if u[3] else "❌ Inativo"
    print(f"{u[0]} - {u[1]} ({u[2]}) -> {status}")

id_autorizar = input("\nDigite o ID do usuário que deseja autorizar (ou Enter para sair): ")

if id_autorizar.strip():
    cursor.execute("UPDATE usuarios SET ativo = TRUE WHERE id = %s", (id_autorizar,))
    conn.commit()
    print("✅ Usuário autorizado com sucesso!")

conn.close()
