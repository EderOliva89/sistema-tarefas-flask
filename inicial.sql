DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS tarefas;

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    username TEXT UNIQUE,
    senha TEXT
);

CREATE TABLE tarefas (
    id SERIAL PRIMARY KEY,
    texto TEXT NOT NULL,
    feito BOOLEAN DEFAULT FALSE,
    favorito BOOLEAN DEFAULT FALSE,
    data_criacao TEXT,
    data_conclusao TEXT
);

-- hash da senha 'Leticia021021'
INSERT INTO usuarios (nome, username, senha) VALUES (
    'Eder', 'eder', '$2b$12$BlvS0ZGxl9ZwD0SB.vEGKe.QAh/g4c7uxbfHZQUxNabymHZsGsqJq'
);