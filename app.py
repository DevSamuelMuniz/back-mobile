import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import hashlib
import sqlite3

app = Flask(__name__)
CORS(app)

# Ler variáveis de ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')
CHAVE = os.environ.get('CHAVE')

# Função para calcular o hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Rota para registrar um novo usuário
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    name = data['name']
    email = data['email']
    password = data['password']

    hashed_password = hash_password(password)

    # Conectar ao banco de dados
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO User (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.json
    email = data['email']
    password = data['password']

    # Conectar ao banco de dados
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Verifica se a senha está correta
        hashed_password = hash_password(password)
        if user[3] == hashed_password:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 401  # Unauthorized
    else:
        return jsonify({'success': False}), 404  # Not found

# Rota para listar todos os usuários
@app.route('/api/users', methods=['GET'])
def get_users():
    # Conectar ao banco de dados
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()

    users_list = []
    for user in users:
        user_dict = {
            'userId': user[0],
            'name': user[1],
            'email': user[2]
        }
        users_list.append(user_dict)

    conn.close()
    return jsonify(users_list), 200

if __name__ == '__main__':
    app.run(debug=True)
