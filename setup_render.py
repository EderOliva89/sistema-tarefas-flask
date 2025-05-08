import psycopg2
import bcrypt

HOST     = "postgresql://tarefas_db_wucp_user:Fjv5sh9BKlsZIaMLtRrxTI7uglvWj8LY@dpg-d0dqlh49c44c738dqgqg-a.oregon-postgres.render.com/tarefas_db_wucp"
PORT     = "5432"
DBNAME   = "tarefas_db_wucp"
USER     = "tarefas_db_wucp_user"
PASSWORD = "Fjv5sh9BKlsZIaMLtRrxTI7uglvWj8LY"

def conectar():
    dsn = (
        f"host={HOST} port={PORT} dbname={DBNAME} "
        f"user={USER} password={PASSWORD} sslmode=require"
    )
    return psycopg2.connect(dsn)

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            username TEXT UNIQUE,
            senha TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id SERIAL PRIMARY KEY,
            texto TEXT NOT NULL,
            feito BOOLEAN DEFAULT FALSE,
            favorito BOOLEAN DEFAULT FALSE,
            data_criacao TEXT,
            data_conclusao TEXT
        );
    """)
    senha_hash = '$2b$12$SdxHOrbb6S0An0nFYX.CzOm7euV1iPT9HRewB41eAf4.vZizYEmQ6'
    cur.execute("""
        INSERT INTO usuarios (nome, username, senha)
        VALUES (%s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
    """, ("Eder", "eder", senha_hash))
    conn.commit()
    conn.close()
    print("Tabelas e usuário inicial criados com sucesso!")

if __name__ == "__main__":
    criar_tabelas()
