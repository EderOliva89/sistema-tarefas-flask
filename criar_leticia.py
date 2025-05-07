import psycopg2
import bcrypt


nome = "Leticia"
username = "leticia"
senha = "Lilly2025"


senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


conn = psycopg2.connect(
    dbname="tarefas_local",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432",
    options="-c client_encoding=UTF8"
)
cur = conn.cursor()


sql = (
    "INSERT INTO usuarios (nome, username, senha) "
    "VALUES (%s, %s, %s) "
    "ON CONFLICT (username) DO NOTHING"
)
cur.execute(sql, (nome, username, senha_hash))

conn.commit()
conn.close()

print("Usuario Leticia criado com sucesso!")
