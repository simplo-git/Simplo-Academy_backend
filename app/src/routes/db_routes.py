from flask import Blueprint, jsonify
from app.src.services.db_service import DBService
import os
from dotenv import load_dotenv

load_dotenv()

db_bp = Blueprint('db', __name__)

@db_bp.route('/verify-db', methods=['GET'])
def verify_db():
    """
    Verifica se o banco de dados 'simploacademy_database' existe.
    Retorna o status da conexão e a existência do banco.
    """
    mongo_uri = os.getenv("MONGO")
    service = DBService(mongo_uri)
    result = service.check_db_status()
    return jsonify(result)
