from flask import Blueprint, request, jsonify
from app.src.services.conteudo_service import ConteudoService
from app.src.models.conteudo_model import ConteudoModel
from datetime import datetime

conteudo_bp = Blueprint('conteudo_bp', __name__)
conteudo_service = ConteudoService()

@conteudo_bp.route('/conteudos', methods=['POST'])
def create_conteudo():
    """Criar um novo conteúdo"""
    try:
        data = request.json
        # Validação com Pydantic
        # Se 'usuarios' vier como lista, precisamos converter ou validar se o model aceita.
        # O model espera Dict[str, UserProgress].
        
        conteudo = ConteudoModel(**data)
        response = conteudo_service.create_conteudo(conteudo.model_dump())
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro de validação: {str(e)}"}), 400
    
    if response["status"] == "success":
        return jsonify(response), 201
    return jsonify(response), 400

@conteudo_bp.route('/conteudos/<id>', methods=['PUT'])
def update_conteudo(id):
    """Atualizar um conteúdo"""
    try:
        data = request.json
        # Para atualização, validar parcialmente se desejar, ou validar schema completo.
        # Aqui vamos permitir atualização parcial, mas se quiser garantir schema,
        # poderíamos instanciar o model. Porém PUT costuma ser substituição total ou parcial grande.
        # Se formos rigorosos:
        # conteudo = ConteudoModel(**data) 
        # Mas Pydantic exige todos os campos obrigatórios. 
        # Vamos passar os dados diretos para o service, confiando que o frontend manda o formato certo
        # ou fazendo uma validação manual se necessario.
        
        response = conteudo_service.update_conteudo(id, data)
        if response["status"] == "success":
            return jsonify(response), 200
        return jsonify(response), 404
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao atualizar: {str(e)}"}), 400

@conteudo_bp.route('/conteudos/<id>', methods=['DELETE'])
def delete_conteudo(id):
    """Excluir um conteúdo"""
    response = conteudo_service.delete_conteudo(id)
    if response["status"] == "success":
        return jsonify(response), 200
    return jsonify(response), 404

@conteudo_bp.route('/conteudos', methods=['GET'])
def list_conteudos():
    """Listar todos os conteúdos"""
    conteudos = conteudo_service.list_conteudos()
    return jsonify(conteudos), 200

@conteudo_bp.route('/conteudos/<id>', methods=['GET'])
def get_conteudo(id):
    """Buscar um conteúdo pelo ID"""
    conteudo = conteudo_service.get_conteudo_by_id(id)
    if conteudo:
        return jsonify(conteudo), 200
    return jsonify({"status": "error", "message": "Conteúdo não encontrado"}), 404

@conteudo_bp.route('/conteudos/<id>/resposta', methods=['POST'])
def add_resposta(id):
    """
    Adicionar resposta de usuário a um conteúdo
    Payload:
        - user_id: ID do usuário
        - template_id: ID do template da atividade
        - tipo: tipo da atividade
        - resposta: conteúdo da resposta
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"status": "error", "message": "user_id é obrigatório"}), 400

        response = conteudo_service.add_user_response(id, user_id, data)
        
        if response["status"] == "success":
            return jsonify(response), 200
        return jsonify(response), 400
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

@conteudo_bp.route('/conteudos/<id>/conclusao', methods=['POST'])
def conclude_conteudo(id):
    """
    Concluir um conteúdo para o usuário
    Payload:
        - user_id: ID do usuário
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"status": "error", "message": "user_id é obrigatório"}), 400

        response = conteudo_service.conclude_content(id, user_id)
        
        if response["status"] == "success":
            return jsonify(response), 200
        return jsonify(response), 400
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

@conteudo_bp.route('/conteudos/<id>/grade', methods=['POST'])
def grade_content(id):
    """
    Aplicar nota e status manualmente (Correção Manual)
    Payload:
        - user_id: ID do usuário
        - nota: Nota atribuída
        - status: 'aprovado', 'reprovado' (ou 'falhou')
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        nota = data.get("nota")
        status = data.get("status")

        if not user_id:
            return jsonify({"status": "error", "message": "user_id é obrigatório"}), 400
        
        if nota is None or status is None:
             return jsonify({"status": "error", "message": "nota e status são obrigatórios"}), 400

        response = conteudo_service.apply_grade(id, user_id, nota, status)
        
        if response["status"] == "success":
            return jsonify(response), 200
        return jsonify(response), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500
