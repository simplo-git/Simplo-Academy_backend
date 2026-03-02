from bson.objectid import ObjectId
from app.src.services.db_service import DBService
from app.src.services.cascade_delete_service import cascade_delete_service
from app.src.models.certificate_model import CertificateModel
import os
from dotenv import load_dotenv

load_dotenv()

class CertificateService:
    def __init__(self):
        mongo_uri = os.getenv("MONGO")
        self.db_service = DBService(mongo_uri)
        self.collection = self.db_service.get_db()["certificates"]

    def create_certificate(self, data: dict):
        try:
            # Optionally validate with Pydantic model effectively
            # CertificateModel(**data) 
            
            result = self.collection.insert_one(data)
            return {"status": "success", "message": "Certificado criado com sucesso", "id": str(result.inserted_id)}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao criar certificado: {str(e)}"}

    def update_certificate(self, certificate_id: str, data: dict):
        try:
            result = self.collection.update_one({"_id": ObjectId(certificate_id)}, {"$set": data})
            if result.modified_count > 0:
                return {"status": "success", "message": "Certificado atualizado com sucesso"}
            return {"status": "error", "message": "Certificado não encontrado ou sem alterações"}
        except Exception as e:
             return {"status": "error", "message": f"Erro ao atualizar certificado: {str(e)}"}

    def delete_certificate(self, certificate_id: str):
        try:
            result = self.collection.delete_one({"_id": ObjectId(certificate_id)})
            if result.deleted_count > 0:
                # Cascade: remove referencias em outros documentos
                cascade_delete_service.on_certificate_deleted(certificate_id)
                return {"status": "success", "message": "Certificado excluído com sucesso"}
            return {"status": "error", "message": "Certificado não encontrado"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao excluir certificado: {str(e)}"}

    def list_certificates(self):
        certificates = []
        for cert in self.collection.find():
            cert["_id"] = str(cert["_id"])
            certificates.append(cert)
        return certificates

    def get_certificate_by_id(self, certificate_id: str):
        try:
            cert = self.collection.find_one({"_id": ObjectId(certificate_id)})
            if cert:
                cert["_id"] = str(cert["_id"])
                return cert
            return None
        except:
            return None
