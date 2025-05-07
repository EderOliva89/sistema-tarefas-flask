from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.permanent_session_lifetime = timedelta(days=7)

def conectar():
    return psycopg2.connect(
        dbname='tarefas_local',
        user='postgres',
        password='admin',
        host='localhost',
        port='5432',
        options='-c client_encoding=UTF8'
    )

def buscar_tarefas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, texto, feito, data_criacao, data_conclusao, favorito '
        'FROM tarefas ORDER BY id DESC'
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': r[0],
            'texto': r[1],
            'feito': r[2],
            'data_criacao': r[3],
            'data_conclusao': r[4],
            'favorito': r[5]
        }
        for r in rows
    ]

@app.route('/')
def index():
    if not session.get('logado'):
        return redirect('/login')
    tarefas = buscar_tarefas()
    return render_template('index.html', tarefas=tarefas, nome=session.get('nome'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, nome, senha FROM usuarios WHERE username = %s',
            (usuario,)
        )
        result = cursor.fetchone()
        conn.close()

        if result and bcrypt.checkpw(senha.encode(), result[2].encode()):
            session['logado'] = True
            session['usuario_id'] = result[0]
            session['nome'] = result[1]
            return redirect('/')
        return 'Usuário ou senha inválidos'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/adicionar', methods=['POST'])
def adicionar():
    if not session.get('logado'):
        return redirect('/login')
    texto = request.form['tarefa']
    data_conc = request.form.get('data_conclusao')
    data_fmt = ''
    if data_conc:
        try:
            data_fmt = datetime.strptime(data_conc, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            pass

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tarefas (texto, feito, data_criacao, data_conclusao, favorito) '
        'VALUES (%s, FALSE, %s, %s, FALSE)',
        (texto, datetime.now().strftime('%d/%m/%Y'), data_fmt)
    )
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/concluir/<int:id>')
def concluir(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE tarefas SET feito = NOT feito WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/favoritar/<int:id>')
def favoritar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE tarefas SET favorito = NOT favorito WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/remover/<int:id>')
def remover(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tarefas WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        texto = request.form['tarefa']
        data_conc = request.form.get('data_conclusao')
        data_fmt = ''
        if data_conc:
            try:
                data_fmt = datetime.strptime(data_conc, '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                pass

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE tarefas SET texto = %s, data_conclusao = %s WHERE id = %s',
            (texto, data_fmt, id)
        )
        conn.commit()
        conn.close()
        return redirect('/')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, texto, feito, data_criacao, data_conclusao, favorito FROM tarefas WHERE id = %s',
        (id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return 'Tarefa não encontrada', 404

    tarefa = {
        'id': row[0],
        'texto': row[1],
        'feito': row[2],
        'data_criacao': row[3],
        'data_conclusao': row[4],
        'favorito': row[5]
    }
    return render_template('editar.html', tarefa=tarefa)

if __name__ == "__main__":
    import os
    criar_tabelas()  # se ainda precisar criar as tabelas
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
