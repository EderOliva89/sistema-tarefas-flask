from flask import Flask, render_template, request, redirect, session
from datetime import timedelta
import os, json

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
app.permanent_session_lifetime = timedelta(days=7)

ARQUIVO = "dados.txt"
tarefas = []

def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(tarefas, f)

def carregar():
    global tarefas
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            tarefas.extend(json.load(f))

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
    return render_template("index.html", tarefas=tarefas)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    if not session.get("logado"):
        return redirect("/login")
    texto = request.form.get("tarefa")
    if texto:
        tarefas.append({"texto": texto, "feito": False, "favorito": False})
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
        if novo_texto:
            tarefas[index]["texto"] = novo_texto
            salvar()
        return redirect("/")
    return render_template("editar.html", index=index, tarefa=tarefas[index])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
