from flask import Blueprint, request, jsonify
from app.src.services.user_service import UserService
from app.src.models.user_model import UserModel
from pydantic import ValidationError

user_bp = Blueprint('users', __name__)
user_service = UserService()

@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Cria um novo usuário no sistema.
    Recebe os dados do usuário no corpo da requisição, valida e salva no banco de dados.
    """
    try:
        data = request.json
        # Validate data
        user_model = UserModel(**data)
        result = user_service.create_user(user_model.model_dump())
        status_code = 201 if result["status"] == "success" else 400
        return jsonify(result), status_code
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/users', methods=['GET'])
def list_users():
    """
    Lista todos os usuários cadastrados.
    Retorna uma lista de usuários, ocultando informações sensíveis como a senha.
    """
    users = user_service.list_users()
    return jsonify(users), 200

@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Busca um usuário específico pelo ID.
    Retorna os detalhes do usuário se encontrado, ou erro 404.
    """
    user = user_service.get_user(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"status": "error", "message": "Usuário não encontrado"}), 404

@user_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Atualiza os dados de um usuário existente.
    Recebe o ID do usuário e os dados a serem atualizados no corpo da requisição.
    """
    data = request.json
    result = user_service.update_user(user_id, data)
    status_code = 200 if result["status"] == "success" else 400
    return jsonify(result), status_code

@user_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Remove um usuário do sistema pelo ID.
    """
    result = user_service.delete_user(user_id)
    status_code = 200 if result["status"] == "success" else 400
    return jsonify(result), status_code

@user_bp.route('/users/login', methods=['POST'])
def login():
    """
    Realiza o login do usuário.
    Verifica email e senha e retorna o status de sucesso.
    """
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"status": "error", "message": "E-mail e senha são obrigatórios"}), 400
    
    result = user_service.login(email, password)
    status_code = 200 if result["status"] == "success" else 401
    return jsonify(result), status_code
