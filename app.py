from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "minha_chave_secreta"

tarefas = []

# ---------------- ROTAS DE LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == "admin" and senha == "1234":
            session["logado"] = True
            return redirect("/")
        else:
            return "Usuário ou senha incorretos"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logado", None)
    return redirect("/login")

# ---------------- ROTAS PRINCIPAIS (protegidas) ----------------

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
        tarefas.append({
            "texto": texto,
            "feito": False,
            "favorito": False
        })
    return redirect("/")

@app.route("/remover/<int:index>")
def remover(index):
    if not session.get("logado"):
        return redirect("/login")
    if 0 <= index < len(tarefas):
        tarefas.pop(index)
    return redirect("/")

@app.route("/concluir/<int:index>")
def concluir(index):
    if not session.get("logado"):
        return redirect("/login")
    if 0 <= index < len(tarefas):
        tarefas[index]["feito"] = not tarefas[index]["feito"]
    return redirect("/")

@app.route("/favoritar/<int:index>")
def favoritar(index):
    if not session.get("logado"):
        return redirect("/login")
    if 0 <= index < len(tarefas):
        tarefas[index]["favorito"] = not tarefas[index]["favorito"]
    return redirect("/")

@app.route("/editar/<int:index>", methods=["GET", "POST"])
def editar(index):
    if not session.get("logado"):
        return redirect("/login")
    if request.method == "POST":
        novo_texto = request.form.get("tarefa")
        if novo_texto:
            tarefas[index]["texto"] = novo_texto
        return redirect("/")
    return render_template("editar.html", index=index, tarefa=tarefas[index])

if __name__ == "__main__":
    app.run(debug=True)
