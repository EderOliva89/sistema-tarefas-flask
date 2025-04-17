from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import os, json, socket

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
app.permanent_session_lifetime = timedelta(days=7)

ARQUIVO = "dados.txt"
tarefas = []

# Carrega as tarefas do arquivo e garante os campos novos
def carregar():
    global tarefas
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            tarefas.extend(json.load(f))
    for t in tarefas:
        t.setdefault("data_criacao", "??/??/????")
        t.setdefault("data_conclusao", "")

# Salva as tarefas no arquivo
def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(tarefas, f)

carregar()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == "Lilly" and senha == "Leticia021021.":
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

        tarefas.append({
            "texto": texto,
            "feito": False,
            "favorito": False,
            "data_criacao": datetime.now().strftime("%d/%m/%Y"),
            "data_conclusao": data_conclusao_formatada
        })
        salvar()
    return redirect("/")

@app.route("/remover/<int:index>")
def remover(index):
    if not session.get("logado"):
        return redirect("/login")
    if 0 <= index < len(tarefas):
        tarefas.pop(index)
        salvar()
    return redirect("/")

@app.route("/concluir/<int:index>")
def concluir(index):
    if not session.get("logado"):
        return redirect("/login")
    if 0 <= index < len(tarefas):
        tarefas[index]["feito"] = not tarefas[index]["feito"]
        salvar()
    return redirect("/")

@app.route("/favoritar/<int:index>")
def favoritar(index):
    if not session.get("logado"):
        return redirect("/login")
    if 0 <= index < len(tarefas):
        tarefas[index]["favorito"] = not tarefas[index]["favorito"]
        salvar()
    return redirect("/")

@app.route("/editar/<int:index>", methods=["GET", "POST"])
def editar(index):
    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":
        novo_texto = request.form.get("tarefa")
        nova_data = request.form.get("data_conclusao")

        if novo_texto:
            tarefas[index]["texto"] = novo_texto

        if nova_data:
            try:
                data_formatada = datetime.strptime(nova_data, "%Y-%m-%d").strftime("%d/%m/%Y")
                tarefas[index]["data_conclusao"] = data_formatada
            except ValueError:
                tarefas[index]["data_conclusao"] = ""
        else:
            tarefas[index]["data_conclusao"] = ""

        salvar()
        return redirect("/")

    return render_template("editar.html", index=index, tarefa=tarefas[index])

# 🔁 Rodar localmente com host adaptável
if __name__ == "__main__":
    local = socket.gethostname().lower().startswith("thiago") or "localhost" in socket.gethostname().lower()
    app.run(debug=True, host="127.0.0.1" if local else "0.0.0.0", port=5000)
