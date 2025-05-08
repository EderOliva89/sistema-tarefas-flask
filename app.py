from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import os
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key')
app.permanent_session_lifetime = timedelta(days=7)


def conectar():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # conecta ao Postgres remoto com SSL
        return psycopg2.connect(database_url, sslmode='require')
    # fallback local
    dsn = "dbname=tarefas_local user=postgres password=admin host=localhost port=5432"
    return psycopg2.connect(dsn)


def criar_tabelas_e_seed():
    conn = conectar()
    cur = conn.cursor()
    # cria tabelas
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
    # seed do usuário "eder"
    cur.execute("SELECT 1 FROM usuarios WHERE username = %s", ('eder',))
    if not cur.fetchone():
        senha_raw = 'Leticia021021'
        senha_hash = bcrypt.hashpw(senha_raw.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO usuarios (nome, username, senha) VALUES (%s, %s, %s)",
            ('Eder', 'eder', senha_hash)
        )
    conn.commit()
    conn.close()

# roda tudo antes do primeiro request
criar_tabelas_e_seed()


def buscar_tarefas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        'SELECT id, texto, feito, data_criacao, data_conclusao, favorito '
        'FROM tarefas ORDER BY id DESC'
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            'id':             r[0],
            'texto':          r[1],
            'feito':          r[2],
            'data_criacao':   r[3],
            'data_conclusao': r[4],
            'favorito':       r[5]
        }
        for r in rows
    ]


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha    = request.form['senha']
        conn = conectar()
        cur  = conn.cursor()
        cur.execute(
            'SELECT id, nome, senha FROM usuarios WHERE username = %s',
            (usuario,)
        )
        row = cur.fetchone()
        conn.close()
        if row and bcrypt.checkpw(senha.encode(), row[2].encode()):
            session['logado']      = True
            session['usuario_id']  = row[0]
            session['nome']        = row[1]
            return redirect('/')
        erro = 'Usuário ou senha inválidos'
    return render_template('login.html', erro=erro)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/')
def index():
    if not session.get('logado'):
        return redirect('/login')
    tarefas = buscar_tarefas()
    return render_template('index.html', tarefas=tarefas, nome=session.get('nome'))


@app.route('/adicionar', methods=['POST'])
def adicionar():
    if not session.get('logado'):
        return redirect('/login')
    texto  = request.form['tarefa']
    data_c = request.form.get('data_conclusao')
    data_fmt = ''
    if data_c:
        try:
            data_fmt = datetime.strptime(data_c, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            pass
    conn = conectar()
    cur  = conn.cursor()
    cur.execute(
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
    cur  = conn.cursor()
    cur.execute('UPDATE tarefas SET feito = NOT feito WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/favoritar/<int:id>')
def favoritar(id):
    conn = conectar()
    cur  = conn.cursor()
    cur.execute('UPDATE tarefas SET favorito = NOT favorito WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/remover/<int:id>')
def remover(id):
    conn = conectar()
    cur  = conn.cursor()
    cur.execute('DELETE FROM tarefas WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        texto  = request.form['tarefa']
        data_c = request.form.get('data_conclusao')
        data_fmt = ''
        if data_c:
            try:
                data_fmt = datetime.strptime(data_c, '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                pass
        conn = conectar()
        cur  = conn.cursor()
        cur.execute(
            'UPDATE tarefas SET texto = %s, data_conclusao = %s WHERE id = %s',
            (texto, data_fmt, id)
        )
        conn.commit()
        conn.close()
        return redirect('/')
    conn = conectar()
    cur  = conn.cursor()
    cur.execute(
        'SELECT id, texto, feito, data_criacao, data_conclusao, favorito '
        'FROM tarefas WHERE id = %s',
        (id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return 'Tarefa não encontrada', 404
    tarefa = {
        'id':            row[0],
        'texto':         row[1],
        'feito':         row[2],
        'data_criacao':  row[3],
        'data_conclusao':row[4],
        'favorito':      row[5]
    }
    return render_template('editar.html', tarefa=tarefa)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
