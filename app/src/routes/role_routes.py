from flask import Blueprint, request, jsonify
from app.src.services.role_service import RoleService
from app.src.models.role_model import RoleModel
from pydantic import ValidationError

role_bp = Blueprint('roles', __name__)
role_service = RoleService()

@role_bp.route('/roles', methods=['POST'])
def create_role():
    """
    Cria um novo cargo.
    Recebe 'nome' e define data de criação.
    """
    try:
        data = request.json
        # Validate data - relying on Pydantic, though timestamps are optional in input
        role_model = RoleModel(**data)
        result = role_service.create_role(role_model.model_dump(exclude_none=True))
        status_code = 201 if result["status"] == "success" else 400
        return jsonify(result), status_code
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@role_bp.route('/roles', methods=['GET'])
def list_roles():
    """
    Lista todos os cargos.
    """
    roles = role_service.list_roles()
    return jsonify(roles), 200

@role_bp.route('/roles/<role_id>', methods=['PUT'])
def update_role(role_id):
    """
    Edita um cargo existente.
    Atualiza apenas os campos enviados e a data de edição.
    """
    data = request.json
    result = role_service.update_role(role_id, data)
    status_code = 200 if result["status"] == "success" else 400
    return jsonify(result), status_code

@role_bp.route('/roles/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    """
    Remove um cargo do sistema.
    """
    result = role_service.delete_role(role_id)
    status_code = 200 if result["status"] == "success" else 400
    return jsonify(result), status_code
