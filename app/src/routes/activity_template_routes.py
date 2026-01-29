from flask import Blueprint, request, jsonify, send_from_directory
from app.src.services.activity_template_service import ActivityTemplateService
from app.src.services.file_upload_service import FileUploadService
from app.src.models.activity_template_model import ActivityTemplateModel
import os
from datetime import datetime

activity_template_bp = Blueprint('activity_template_bp', __name__)
activity_template_service = ActivityTemplateService()
file_upload_service = FileUploadService()

@activity_template_bp.route('/activity-templates', methods=['POST'])
def create_template():
    """Criar um novo template de atividade"""
    try:
        data = request.json
        # Validar dados com Pydantic
        template = ActivityTemplateModel(**data)
        response = activity_template_service.create_template(template.model_dump())
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro de validação: {str(e)}"}), 400
    
    if response["status"] == "success":
        return jsonify(response), 201
    return jsonify(response), 400

@activity_template_bp.route('/activity-templates/<id>', methods=['PUT'])
def update_template(id):
    """Atualizar um template de atividade"""
    data = request.json
    response = activity_template_service.update_template(id, data)
    if response["status"] == "success":
        return jsonify(response), 200
    return jsonify(response), 404

@activity_template_bp.route('/activity-templates/<id>', methods=['DELETE'])
def delete_template(id):
    """Excluir um template de atividade"""
    response = activity_template_service.delete_template(id)
    if response["status"] == "success":
        return jsonify(response), 200
    return jsonify(response), 404

@activity_template_bp.route('/activity-templates', methods=['GET'])
def list_templates():
    """
    Listar todos os templates de atividade
    Query params:
        - tipo: filtrar por tipo (multipla_escolha, video, texto_livre, upload, documento, artigo)
    """
    tipo = request.args.get('tipo')
    templates = activity_template_service.list_templates(tipo)
    return jsonify(templates), 200

@activity_template_bp.route('/activity-templates/<id>', methods=['GET'])
def get_template(id):
    """Buscar um template de atividade pelo ID"""
    template = activity_template_service.get_template_by_id(id)
    if template:
        return jsonify(template), 200
    return jsonify({"status": "error", "message": "Template não encontrado"}), 404

@activity_template_bp.route('/activity-templates/types', methods=['GET'])
def get_types():
    """Listar todos os tipos de atividade disponíveis"""
    types = [
        {"value": "multipla_escolha", "label": "Múltipla Escolha"},
        {"value": "video", "label": "Vídeo"},
        {"value": "texto_livre", "label": "Atividade Texto Livre"},
        {"value": "upload", "label": "Upload"},
        {"value": "documento", "label": "Documento"},
        {"value": "artigo", "label": "Artigo"}
    ]
    return jsonify(types), 200

@activity_template_bp.route('/activity-templates/upload', methods=['POST'])
def upload_file():
    """
    Upload de arquivo para templates de atividade (via base64)
    
    JSON body:
        - file: string base64 do arquivo (pode incluir data URI prefix)
        - filename: nome original do arquivo com extensão (ex: "documento.pdf")
        - tipo: tipo de atividade (documento, video, upload)
    
    Retorna:
        - url: URL interna para acessar o arquivo
        - filename: nome do arquivo salvo
        - original_filename: nome original do arquivo
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"status": "error", "message": "Nenhum dado enviado"}), 400
        
        base64_data = data.get('file')
        filename = data.get('filename')
        tipo = data.get('tipo', 'upload')
        
        if not base64_data:
            return jsonify({"status": "error", "message": "Campo 'file' (base64) é obrigatório"}), 400
        
        if not filename:
            return jsonify({"status": "error", "message": "Campo 'filename' é obrigatório"}), 400
        
        # Obter URL base do servidor
        host_url = request.host_url.rstrip('/')
        
        response = file_upload_service.save_file_from_base64(base64_data, filename, tipo, host_url)
        
        if response["status"] == "success":
            return jsonify(response), 201
        return jsonify(response), 400
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro no upload: {str(e)}"}), 500

@activity_template_bp.route('/files/<folder>/<filename>', methods=['GET'])
def serve_file(folder, filename):
    """
    Servir arquivos salvos localmente
    
    Args:
        folder: pasta do arquivo (documents, video, image)
        filename: nome do arquivo
    """
    try:
        file_path = file_upload_service.get_file_path(folder, filename)
        directory = os.path.dirname(file_path)
        
        if os.path.exists(file_path):
            return send_from_directory(directory, filename)
        return jsonify({"status": "error", "message": "Arquivo não encontrado"}), 404
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao buscar arquivo: {str(e)}"}), 500

@activity_template_bp.route('/files/<folder>/<filename>', methods=['DELETE'])
def delete_file(folder, filename):
    """Remover arquivo do sistema"""
    response = file_upload_service.delete_file(folder, filename)
    if response["status"] == "success":
        return jsonify(response), 200
    return jsonify(response), 404


@activity_template_bp.route('/activity-templates/video-upload', methods=['POST'])
def create_video_template_with_upload():
    """
    Criar template de atividade (focado em vídeo) com upload de arquivo Base64.
    
    Recebe uma estrutura JSON contendo metadados e o arquivo em Base64 dentro de 'dados'.
    O arquivo é salvo no servidor e a URL é salva no campo 'url' dentro de 'dados'.
    O campo original 'arquivo' (base64) é removido para não sobrecarregar o banco.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Nenhum dado enviado"}), 400

        # Verifica se existe a estrutura 'dados' e 'arquivo'
        dados = data.get('dados', {})
        base64_file = dados.get('arquivo')
        filename = dados.get('nomeArquivo')
        
        # O user mencionou 'tipo' no root e também 'tipoArquivo' em dados.
        # Vamos usar 'video' como padrão se não especificado, já que a rota é para isso.
        
        if base64_file and filename:
            # Determinar tipo para pasta (usando 'video' conforme solicitado para essa rota)
            # ou tentar inferir do tipoArquivo se disponível
            tipo_arquivo_mime = dados.get('tipoArquivo', '')
            tipo_save = 'video'
            if 'pdf' in tipo_arquivo_mime or 'document' in tipo_arquivo_mime:
                tipo_save = 'documento'
            
            # Obter URL base
            host_url = request.host_url.rstrip('/')
            
            # Salvar arquivo
            upload_response = file_upload_service.save_file_from_base64(
                base64_file, 
                filename, 
                tipo_save, 
                host_url
            )
            
            if upload_response['status'] == 'success':
                # Atualizar dados com a URL do arquivo
                dados['url'] = upload_response['url']
                # Remover o base64 para não salvar no banco
                if 'arquivo' in dados:
                    del dados['arquivo']
                
                # Se houver campo 'url' na raiz também, atualizar (redundância conforme exemplo do user?)
                if 'url' in data:
                    data['url'] = upload_response['url']
                
                # Atualizar o objeto dados no payload original
                data['dados'] = dados
            else:
                return jsonify(upload_response), 400

        # Validar e Salvar no Banco (usando o service existente)
        # O service espera um formato compatível com ActivityTemplateModel
        # O exemplo do user tem campos como '_id', 'nome', 'tipo', 'template', etc.
        # O model espera 'nome', 'tipo', 'template'.
        
        # Adaptar estrutura do usuário para o modelo, se necessário.
        # O modelo ActivityTemplateModel tem: nome, tipo, template, data_criacao
        # O JSON do usuário tem: nome, tipo, dados, descricao, etc.
        # Provavelmente 'dados' faz parte do 'template' ou é campos soltos.
        # Vou assumir que 'dados' deve ser preservado.
        # Se o service validar estritamente o model, pode falhar se passarmos campos extras.
        # O model ActivityTemplateModel usa Pydantic. 'template' é Dict[str, Any].
        # Vamos mover campos extras para dentro de 'template' se não baterem com o model raiz,
        # OU vamos salvar direto se o service permitir dict.
        
        # Observando o create_template original:
        # template = ActivityTemplateModel(**data)
        # response = activity_template_service.create_template(template.model_dump())
        
        # Vou tentar ajustar a entrada para bater com o Model.
        # O user passou 'nome', 'tipo'. 'dados' pode ir para dentro de 'template'?
        # Ou será que o user quer salvar exatamente essa estrutura?
        # Se eu usar o create_template existente, ele valida com ActivityTemplateModel.
        # ActivityTemplateModel: nome, tipo, template (dict), data_criacao.
        
        # Vamos construir o objeto para o Model
        model_data = {
            "nome": data.get("nome", "Novo Template"),
            "tipo": data.get("tipo", "video"),
            "data_criacao": data.get("data_criacao", datetime.now().isoformat()),
            "template": data  # Enfiamos tudo dentro de template para flexibilidade?
        }
        
        # Mas o user forneceu uma estrutura plana similar ao documento.
        # Talvez 'dados' seja o 'template'.
        # Vou colocar o payload processado (sem o base64) dentro do campo 'template' do Model,
        # mantendo 'nome' e 'tipo' no nível raiz do Model.
        
        if "template" not in data:
             # Se não veio campo 'template', assumimos que o resto dos dados COMPÕE o template
             # Mas cuidado com recursão se eu botar 'data' em 'template'.
             clean_data = data.copy()
             if "nome" in clean_data: del clean_data["nome"]
             if "tipo" in clean_data: del clean_data["tipo"]
             model_data["template"] = clean_data
        else:
             model_data["template"] = data["template"]

        # Se o user enviou 'dados' e eu processei ele, preciso garantir que ele vá para o lugar certo.
        # No bloco acima, 'data' jã tem 'dados' modificado.
        # Entao clean_data["dados"] terá a URL.
        
        # Instanciar Model
        try:
            activity_template = ActivityTemplateModel(**model_data)
        except Exception as e:
             # Fallback: se falhar validação, tenta salvar como genérico se o service permitir,
             # mas o service chama o repo. O repo usa mongo?
             # Vou tentar usar o service normal.
             return jsonify({"status": "error", "message": f"Erro de validação Pydantic: {str(e)}"}), 400

        response = activity_template_service.create_template(activity_template.model_dump())
        
        if response["status"] == "success":
            return jsonify(response), 201
        return jsonify(response), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

