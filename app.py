from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import psycopg2, os, socket

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
app.permanent_session_lifetime = timedelta(days=7)

# ⚡ Conexão PostgreSQL
def conectar():
    return psycopg2.connect(
        dbname="tarefas_db_0nh8",
        user="eder",
        password="ZNUN3pcl1LpodgbRz6hneUS0GanaY9Gl",
        host="dpg-d07n271r0fns738o07h0-a.virginia-postgres.render.com",
        port="5432"
    )

# 🔵 Cria a tabela (se não existir)
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id SERIAL PRIMARY KEY,
            texto TEXT NOT NULL,
            feito BOOLEAN DEFAULT FALSE,
            favorito BOOLEAN DEFAULT FALSE,
            data_criacao TEXT,
            data_conclusao TEXT
        )
    """)
    conn.commit()
    conn.close()

# 🔵 Buscar todas tarefas
def buscar_tarefas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas ORDER BY id DESC")
    linhas = cursor.fetchall()
    conn.close()
    tarefas = []
    for linha in linhas:
        tarefas.append({
            "id": linha[0],
            "texto": linha[1],
            "feito": linha[2],
            "favorito": linha[3],
            "data_criacao": linha[4],
            "data_conclusao": linha[5]
        })
    return tarefas

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == "admin" and senha == "1234":
            session.permanent = True
            session["logado"] = True
            return redirect("/")
        else:
            return "Usuário ou senha incorretos"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logado", None)
    return redirect("/login")

@app.route("/")
def index():
    if not session.get("logado"):
        return redirect("/login")
    tarefas = buscar_tarefas()
    return render_template("index.html", tarefas=tarefas, hoje=datetime.today().date())

@app.route("/adicionar", methods=["POST"])
def adicionar():
    if not session.get("logado"):
        return redirect("/login")

    texto = request.form.get("tarefa")
    data_conclusao = request.form.get("data_conclusao")
    if texto:
        if data_conclusao:
            try:
                data_conclusao_formatada = datetime.strptime(data_conclusao, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                data_conclusao_formatada = ""
        else:
            data_conclusao_formatada = ""

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tarefas (texto, feito, favorito, data_criacao, data_conclusao)
            VALUES (%s, FALSE, FALSE, %s, %s)
        """, (texto, datetime.now().strftime("%d/%m/%Y"), data_conclusao_formatada))
        conn.commit()
        conn.close()
    return redirect("/")

@app.route("/remover/<int:id>")
def remover(id):
    if not session.get("logado"):
        return redirect("/login")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/concluir/<int:id>")
def concluir(id):
    if not session.get("logado"):
        return redirect("/login")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET feito = NOT feito WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/favoritar/<int:id>")
def favoritar(id):
    if not session.get("logado"):
        return redirect("/login")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET favorito = NOT favorito WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if not session.get("logado"):
        return redirect("/login")
    if request.method == "POST":
        novo_texto = request.form.get("tarefa")
        nova_data = request.form.get("data_conclusao")
        if nova_data:
            try:
                data_formatada = datetime.strptime(nova_data, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                data_formatada = ""
        else:
            data_formatada = ""

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tarefas SET texto = %s, data_conclusao = %s WHERE id = %s
        """, (novo_texto, data_formatada, id))
        conn.commit()
        conn.close()
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas WHERE id = %s", (id,))
    linha = cursor.fetchone()
    conn.close()

    if not linha:
        return "Tarefa não encontrada", 404

    tarefa = {
        "id": linha[0],
        "texto": linha[1],
        "feito": linha[2],
        "favorito": linha[3],
        "data_criacao": linha[4],
        "data_conclusao": linha[5]
    }
    return render_template("editar.html", index=id, tarefa=tarefa)

# 🚀 Rodar localmente ou no Render
if __name__ == "__main__":
    criar_tabela()
    local = socket.gethostname().lower().startswith("thiago") or "localhost" in socket.gethostname().lower()
    app.run(debug=True, host="127.0.0.1" if local else "0.0.0.0", port=5000)
