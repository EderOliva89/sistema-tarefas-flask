from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime, timedelta
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
app.permanent_session_lifetime = timedelta(days=7)

# Banco local ou remoto (Render)
def conectar():
    return psycopg2.connect(
        dbname="tarefas_local",  # Altere se estiver no Render
        user="postgres",
        password="admin",        # Altere a senha conforme seu banco
        host="localhost",
        port="5432"
    )

# Filtro para campo data no editar
@app.template_filter('reverse_date')
def reverse_date(date_str):
    try:
        d, m, y = date_str.split('/')
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    except:
        return ""

# Buscar tarefas (compartilhadas)
def buscar_tarefas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas ORDER BY id DESC")
    tarefas = cursor.fetchall()
    conn.close()
    return tarefas

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        username = request.form.get("usuario")
        senha = request.form.get("senha")
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nome, username, senha, ativo) VALUES (%s, %s, %s, %s)", (nome, username, senha_hash, False))
            conn.commit()
            flash("Cadastro realizado! Aguarde autorização para acesso.")
            return redirect("/login")
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Nome de usuário já existe.")
        finally:
            conn.close()
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("usuario")
        senha = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, senha, ativo FROM usuarios WHERE username = %s", (username,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            if not usuario[3]:
                flash("Seu acesso ainda não foi autorizado.")
                return redirect("/login")
            if bcrypt.checkpw(senha.encode(), usuario[2].encode()):
                session["logado"] = True
                session["usuario_id"] = usuario[0]
                session["nome"] = usuario[1]
                return redirect("/")
        flash("Usuário ou senha inválidos.")
    return render_template("login.html")

@app.route("/")
def index():
    if not session.get("logado"):
        return redirect("/login")
    tarefas = buscar_tarefas()
    return render_template("index.html", tarefas=tarefas, hoje=datetime.today().date(), usuario=session["nome"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/adicionar", methods=["POST"])
def adicionar():
    if not session.get("logado"):
        return redirect("/login")
    texto = request.form.get("tarefa")
    data_conclusao = request.form.get("data_conclusao")
    if texto:
        data_formatada = ""
        if data_conclusao:
            try:
                data_formatada = datetime.strptime(data_conclusao, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                pass
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tarefas (texto, feito, favorito, data_criacao, data_conclusao) VALUES (%s, FALSE, FALSE, %s, %s)",
            (texto, datetime.now().strftime("%d/%m/%Y"), data_formatada))
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
        data_formatada = ""
        if nova_data:
            try:
                data_formatada = datetime.strptime(nova_data, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                pass
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE tarefas SET texto = %s, data_conclusao = %s WHERE id = %s",
                       (novo_texto, data_formatada, id))
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
    return render_template("editar.html", tarefa=tarefa)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)