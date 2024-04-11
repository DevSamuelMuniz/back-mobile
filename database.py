import sqlite3
from flask import g

DATABASE = 'nutrilife.db'

# Função para obter conexão com o banco de dados
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Fechar conexão com o banco de dados quando o contexto do aplicativo é encerrado
def close_db():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
