import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db, close_db
from flask_login import LoginManager, current_user, logout_user, UserMixin
import hashlib
import sqlite3  # Importe o módulo sqlite3

app = Flask(__name__)
CORS(app)
login_manager = LoginManager(app)

# Defina a classe User para representar um usuário
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Função para buscar um usuário no banco de dados com base no ID
def get_user_by_id(user_id):
    conn = sqlite3.connect('nutrilife.db')
    cursor = conn.cursor()

    # Execute a consulta SQL para buscar o usuário pelo ID
    cursor.execute("SELECT * FROM User WHERE userId = ?", (user_id,))
    user_data = cursor.fetchone()

    conn.close()

    if user_data:
        return User(user_data[0])  # Retorna um objeto User com base no ID
    else:
        return None  # Retorna None se o usuário não for encontrado

# Modifique a função load_user para usar a função get_user_by_id
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

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

    # Verificar se o email já está em uso
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({'message': 'Email already registered'}), 400

    # Se o email não estiver em uso, proceda com o registro do novo usuário
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO User (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
    db.commit()
    close_db()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.json
    email = data['email']
    password = data['password']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user:
        # Verifica se a senha está correta
        hashed_password = hash_password(password)
        if user[3] == hashed_password:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 401  # Unauthorized
    else:
        return jsonify({'success': False}), 404  # Not found

@app.route('/api/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# Rota para listar todos os usuários
@app.route('/api/users', methods=['GET'])
def get_users():
    db = get_db()
    cursor = db.cursor()
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

    close_db()
    return jsonify(users_list), 200


@app.route('/api/add_goal', methods=['POST'])
def add_goal():
    data = request.json
    user_id = data['userId']  
    meta_name = data['metaName']
    meta_quantity = data['metaQuantity']

    db = get_db()
    cursor = db.cursor()

    # Verifica se o usuário existe no banco de dados
    cursor.execute("SELECT * FROM User WHERE userId = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        # Se o usuário existir, insere os dados da meta na tabela Meta
        cursor.execute("INSERT INTO Meta (userId, metaNome, quantMeta, atualMeta) VALUES (?, ?, ?, ?)",
                       (user_id, meta_name, meta_quantity, 0))  # Inicializa atualMeta como 0
        db.commit()
        close_db()
        return jsonify({'userId': user_id, 'message': 'Goal added successfully'}), 201
    else:
        # Se o usuário não existir, retorna uma mensagem de erro
        return jsonify({'message': 'User does not exist'}), 404


@app.route('/api/post', methods=['POST'])
def post():
    data = request.json
    user_id = data['userId']
    title = data['title']
    description = data['description']
    encoded_pic = data['pic']  # Imagem codificada em base64

    # Decodifica a imagem base64
    decoded_pic = base64.b64decode(encoded_pic)

    db = get_db()
    cursor = db.cursor()

    # Verifica se o usuário existe no banco de dados
    cursor.execute("SELECT * FROM User WHERE userId = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        # Se o usuário existir, insere os dados da postagem na tabela Post
        cursor.execute("INSERT INTO Post (userId, title, description, pic) VALUES (?, ?, ?, ?)",
                       (user_id, title, description, decoded_pic))
        db.commit()
        close_db()
        return jsonify({'message': 'Post saved successfully'}), 201
    else:
        # Se o usuário não existir, retorna uma mensagem de erro
        return jsonify({'message': 'User does not exist'}), 404


if __name__ == '__main__':
    login_manager.init_app(app)  # Inicialize o Flask-Login
    app.run(debug=True)
