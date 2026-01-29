from flask import Blueprint, request, jsonify
from app.src.services.certificate_service import CertificateService
from app.src.models.certificate_model import CertificateModel

certificate_bp = Blueprint('certificate_bp', __name__)
certificate_service = CertificateService()

@certificate_bp.route('/certificates', methods=['POST'])
def create_certificate():
    try:
        data = request.json
        # Validate data
        certificate = CertificateModel(**data)
        # Pass dict to service (or update service to accept model, but keeping it simple for now)
        response = certificate_service.create_certificate(certificate.model_dump())
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro de validação: {str(e)}"}), 400
        
    if response["status"] == "success":
        return jsonify(response), 201
    return jsonify(response), 400

@certificate_bp.route('/certificates/<id>', methods=['PUT'])
def update_certificate(id):
    data = request.json
    response = certificate_service.update_certificate(id, data)
    if response["status"] == "success":
        return jsonify(response), 200
    return jsonify(response), 404

@certificate_bp.route('/certificates/<id>', methods=['DELETE'])
def delete_certificate(id):
    response = certificate_service.delete_certificate(id)
    if response["status"] == "success":
        return jsonify(response), 200
    return jsonify(response), 404

@certificate_bp.route('/certificates', methods=['GET'])
def list_certificates():
    certificates = certificate_service.list_certificates()
    return jsonify(certificates), 200

@certificate_bp.route('/certificates/<id>', methods=['GET'])
def get_certificate(id):
    certificate = certificate_service.get_certificate_by_id(id)
    if certificate:
        return jsonify(certificate), 200
    return jsonify({"status": "error", "message": "Certificado não encontrado"}), 404
