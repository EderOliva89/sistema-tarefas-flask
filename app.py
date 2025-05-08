import os
from dotenv import load_dotenv
import logging
from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import psycopg2
import bcrypt

# Carrega variáveis de ambiente do .env (dev) ou do sistema
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(days=7)


def conectar():
    database_url = os.environ.get('DATABASE_URL')
    logger.info(f"Tentando conectar ao banco. DATABASE_URL={database_url}")
    try:
        conn = psycopg2.connect(database_url, sslmode='require')
        logger.info("Conexão ao DB estabelecida com sucesso.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        raise


def criar_tabelas_e_seed():
    conn = conectar()
    cur = conn.cursor()
    # Cria tabelas, se não existirem
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            username TEXT UNIQUE,
            senha TEXT
        );
    """ )
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id SERIAL PRIMARY KEY,
            texto TEXT NOT NULL,
            feito BOOLEAN DEFAULT FALSE,
            favorito BOOLEAN DEFAULT FALSE,
            data_criacao TEXT,
            data_conclusao TEXT
        );
    """ )
    # Seed do usuário 'eder'
    cur.execute("SELECT 1 FROM usuarios WHERE username = %s", ('eder',))
    if not cur.fetchone():
        # Usa hash pré-gerado ou variável de ambiente EDER_HASH
        senha_hash = os.getenv('EDER_HASH')
        if not senha_hash:
            logger.error("Hash do usuário 'eder' não encontrado em EDER_HASH")
        else:
            cur.execute(
                "INSERT INTO usuarios (nome, username, senha) VALUES (%s, %s, %s)",
                ('Eder', 'eder', senha_hash)
            )
            logger.info("Usuário 'eder' seedado no banco.")
    conn.commit()
    conn.close()
    logger.info("Tabelas criadas e seed completo.")

# Executa migrações e seed antes de atender requisições
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
            'id':           r[0],
            'texto':        r[1],
            'feito':        r[2],
            'data_criacao': r[3],
            'data_conclusao': r[4],
            'favorito':     r[5]
        }
        for r in rows
    ]

@app.route('/login', methods=['GET','POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha    = request.form['senha']
        logger.info(f"Tentativa de login - usuário: {usuario}")
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT id, nome, senha FROM usuarios WHERE username = %s',
                (usuario,)
            )
            row = cur.fetchone()
            conn.close()
            logger.info(f"Resultado do SELECT login para '{usuario}': {row}")
            if row and bcrypt.checkpw(senha.encode(), row[2].encode()):
                session['logado']     = True
                session['usuario_id'] = row[0]
                session['nome']       = row[1]
                logger.info(f"Login bem-sucedido para usuário '{usuario}'")
                return redirect('/')
            erro = 'Usuário ou senha inválidos'
            logger.warning(f"Falha no login para usuário '{usuario}'")
        except Exception as e:
            erro = 'Erro interno. Veja logs para mais detalhes.'
            logger.error(f"Exceção durante login de '{usuario}': {e}")
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    logger.info(f"Logout do usuário: {session.get('nome')}")
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
        except Exception as e:
            logger.warning(f"Formato de data inválido para tarefa: {data_c}")
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

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):
    if request.method == 'POST':
        texto  = request.form['tarefa']
        data_c = request.form.get('data_conclusao')
        data_fmt = ''
        if data_c:
            try:
                data_fmt = datetime.strptime(data_c, '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception as e:
                logger.warning(f"Formato de data inválido para tarefa: {data_c}")
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
        'id':           row[0],
        'texto':        row[1],
        'feito':        row[2],
        'data_criacao': row[3],
        'data_conclusao':row[4],
        'favorito':     row[5]
    }
    return render_template('editar.html', tarefa=tarefa)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Iniciando app na porta {port}")
    app.run(host='0.0.0.0', port=port)
