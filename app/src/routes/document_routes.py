from flask import Blueprint, request, jsonify
from app.src.services.file_upload_service import FileUploadService
from app.src.models.activity_template_model import DocumentUploadModel

document_bp = Blueprint('document_bp', __name__)
file_upload_service = FileUploadService()

@document_bp.route('/activity-templates/document-upload', methods=['POST'])
def document_upload():
    """
    Upload específico de documentos.
    Salva na pasta data/documents.
    """
    try:
        data = request.json
        # Validação
        upload_model = DocumentUploadModel(**data)
        
        host_url = request.host_url.rstrip('/')
        
        # Força tipo='upload' para salvar em documents com exceções estendidas
        response = file_upload_service.save_file_from_base64(
            upload_model.file, 
            upload_model.filename, 
            'upload', 
            host_url
        )
        
        if response["status"] == "success":
            return jsonify(response), 201
        return jsonify(response), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro no upload: {str(e)}"}), 500
