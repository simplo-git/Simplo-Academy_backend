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

        # Verifica e processa o arquivo na estrutura 'dados'
        dados = data.get('dados', {})
        base64_file = dados.get('arquivo')
        filename = dados.get('nomeArquivo')
        
        if base64_file and filename:
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
                # Remover o base64
                if 'arquivo' in dados:
                    del dados['arquivo']
                
                # Se houver campo 'url' na raiz (compatibilidade), atualizar
                if 'url' in data:
                    data['url'] = upload_response['url']
                
                data['dados'] = dados
            else:
                return jsonify(upload_response), 400

        # Preparar dados para o ActivityTemplateModel
        # O model espera: nome, tipo, template (dict)
        model_data = {
            "nome": data.get("nome", "Novo Template Vídeo"),
            "tipo": data.get("tipo", "video"),
            "data_criacao": data.get("data_criacao", datetime.now().isoformat()),
        }

        # Organizar o conteúdo do template
        # Se já existe campo 'template', usa-o; caso contrário, data (limpo) vira o template
        if "template" in data:
            model_data["template"] = data["template"]
            # Garante que 'dados' atualizados estejam dentro do template se necessário
            if "dados" not in model_data["template"] and dados:
                 model_data["template"]["dados"] = dados
        else:
            # Remove campos de metadados para não duplicar dentro de 'template'
            clean_data = data.copy()
            clean_data.pop("nome", None)
            clean_data.pop("tipo", None)
            clean_data.pop("data_criacao", None)
            model_data["template"] = clean_data

        # Instanciar e Validar Model
        try:
            activity_template = ActivityTemplateModel(**model_data)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Erro de validação de modelo: {str(e)}"}), 400

        # Salvar no banco via service
        response = activity_template_service.create_template(activity_template.model_dump())
        
        if response["status"] == "success":
            return jsonify(response), 201
        return jsonify(response), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500


@activity_template_bp.route('/activity-templates/video-upload/<id>', methods=['PUT'])
def update_video_template_with_upload(id):
    """
    Atualizar template de atividade (vídeo/documento) com suporte a substituição de arquivo.
    
    Aceita requisição PUT contendo metadados e opcionalmente um novo arquivo Base64 em 'dados.arquivo'.
    Se um novo arquivo for enviado:
    1. Upload do novo arquivo.
    2. Exclusão do arquivo antigo (se existir e for local).
    3. Atualização da URL.
    4. Remoção do Base64 do payload antes de salvar.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Nenhum dado enviado"}), 400

        # 1. Buscar template existente
        existing_template = activity_template_service.get_template_by_id(id)
        if not existing_template:
             return jsonify({"status": "error", "message": "Template não encontrado"}), 404

        # 2. Verificar novo arquivo
        dados = data.get('dados', {})
        base64_file = dados.get('arquivo')
        filename = dados.get('nomeArquivo')
        
        # Recuperar URL antiga para possível exclusão
        old_url = None
        if "template" in existing_template and "dados" in existing_template["template"]:
             old_url = existing_template["template"]["dados"].get("url")
        elif "template" in existing_template and isinstance(existing_template["template"], dict):
             # Fallback se a estrutura for plana dentro de template
             old_url = existing_template["template"].get("url")

        if base64_file and filename:
            tipo_arquivo_mime = dados.get('tipoArquivo', '')
            tipo_save = 'video'
            if 'pdf' in tipo_arquivo_mime or 'document' in tipo_arquivo_mime:
                tipo_save = 'documento'
            
            host_url = request.host_url.rstrip('/')
            
            # Upload do novo arquivo
            upload_response = file_upload_service.save_file_from_base64(
                base64_file, 
                filename, 
                tipo_save, 
                host_url
            )
            
            if upload_response['status'] == 'success':
                new_url = upload_response['url']
                dados['url'] = new_url
                
                # Remover base64
                if 'arquivo' in dados: del dados['arquivo']
                if 'url' in data: data['url'] = new_url
                data['dados'] = dados

                # Tentar excluir arquivo antigo se diferente
                if old_url and old_url != new_url and "/api/files/" in old_url:
                    try:
                        parts = old_url.split("/api/files/")
                        if len(parts) > 1:
                            path_parts = parts[1].split("/")
                            if len(path_parts) >= 2:
                                file_upload_service.delete_file(path_parts[0], path_parts[1])
                    except Exception as ex:
                        print(f"Erro ao deletar arquivo antigo: {ex}")
            else:
                 return jsonify(upload_response), 400
        else:
            # Se não enviou arquivo novo, mantém a URL antiga nos dados se não vier no payload
            # (Geralmente o frontend manda o objeto completo, então a URL antiga já deve estar lá,
            # mas por garantia verificamos)
            if 'url' not in dados and old_url:
                dados['url'] = old_url
                data['dados'] = dados

        # 3. Preparar dados para atualização
        # A lógica de update do service espera um dict que será feito merge ($set)
        # Precisamos garantir que a estrutura respeite o model ou o que o banco espera.
        
        # Se structure for aninhada (padrão 'template'):
        if "template" in existing_template:
            # Atualizamos o campo 'template'
            update_data = {"template": data.get("template", {})}
            
            # Se o payload veio plano com 'dados', 'nome', etc (comum no frontend),
            # precisamos remontar o 'template'.
            # Se 'dados' foi modificado acima, precisamos injetá-lo.
            
            if "dados" in data:
                 if "template" not in update_data: update_data["template"] = {}
                 # Se update_data["template"] já veio do data["template"], check se dados tá lá
                 if "dados" not in update_data["template"]:
                      update_data["template"]["dados"] = data["dados"]
                 else:
                      # Se já tem, atualiza
                      update_data["template"]["dados"] = data["dados"]
            
            # Atualizar campos raiz também
            if "nome" in data: update_data["nome"] = data["nome"]
            if "tipo" in data: update_data["tipo"] = data["tipo"]
            
        else:
            # Se o base for diferente (legado?), salvamos data direto
            update_data = data

        # Chamar service
        response = activity_template_service.update_template(id, update_data)
        
        if response["status"] == "success":
            return jsonify(response), 200
        return jsonify(response), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

