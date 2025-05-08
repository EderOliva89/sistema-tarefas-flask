#!/usr/bin/env python3

import os
import psycopg2
import bcrypt


def conectar():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url, sslmode='require')
    # Fallback para dev local
    dsn = "dbname=tarefas_local user=postgres password=admin host=localhost port=5432"
    return psycopg2.connect(dsn)


def seed_users():
    # Usuário a ser seed: Eder
    users = [
        {'nome': 'Eder', 'username': 'eder', 'senha': 'Leticia021021'},
    ]
    conn = conectar()
    cur = conn.cursor()
    for u in users:
        # Gera hash da senha
        hashed = bcrypt.hashpw(u['senha'].encode(), bcrypt.gensalt()).decode()
        cur.execute(
            """
            INSERT INTO usuarios (nome, username, senha)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING;
            """,
            (u['nome'], u['username'], hashed)
        )
    conn.commit()
    conn.close()


if __name__ == '__main__':
    seed_users()
    print("Usuário Eder inserido com sucesso!")
