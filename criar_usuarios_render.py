import psycopg2
import bcrypt

# Conexão com o banco no Render
conn = psycopg2.connect(
    dbname="tarefas_db_0nh8",
    user="eder",
    password="ZNUN3pcl1LpodgbRz6hneUS0GanaY9Gl",
    host="dpg-d07n271r0fns738o07h0-a.virginia-postgres.render.com",
    port="5432"
)

cursor = conn.cursor()

# Usuários a serem criados
usuarios = [
    {"nome": "Eder", "username": "eder", "senha": "eder123"},
    {"nome": "Letícia Sanches", "username": "leticia", "senha": "leticia123"}
]

for u in usuarios:
    senha_hash = bcrypt.hashpw(u["senha"].encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, username, senha, ativo) VALUES (%s, %s, %s, %s)",
            (u["nome"], u["username"], senha_hash, True)  # Altere para False se quiser revisar
        )
        print(f"✅ Usuário {u['username']} criado com sucesso.")
    except psycopg2.errors.UniqueViolation:
        print(f"⚠️ Usuário {u['username']} já existe.")
        conn.rollback()

conn.commit()
conn.close()
