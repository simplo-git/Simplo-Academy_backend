from bson.objectid import ObjectId
from app.src.services.db_service import DBService
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class ActivityTemplateService:
    def __init__(self):
        mongo_uri = os.getenv("MONGO")
        self.db_service = DBService(mongo_uri)
        self.collection = self.db_service.get_db()["activity_templates"]

    def create_template(self, data: dict):
        try:
            # Adiciona data de criação se não fornecida
            if not data.get("data_criacao"):
                data["data_criacao"] = datetime.now().isoformat()
            
            result = self.collection.insert_one(data)
            return {"status": "success", "message": "Template criado com sucesso", "id": str(result.inserted_id)}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao criar template: {str(e)}"}

    def update_template(self, template_id: str, data: dict):
        try:
            result = self.collection.update_one({"_id": ObjectId(template_id)}, {"$set": data})
            if result.modified_count > 0:
                return {"status": "success", "message": "Template atualizado com sucesso"}
            return {"status": "error", "message": "Template não encontrado ou sem alterações"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao atualizar template: {str(e)}"}

    def delete_template(self, template_id: str):
        try:
            result = self.collection.delete_one({"_id": ObjectId(template_id)})
            if result.deleted_count > 0:
                return {"status": "success", "message": "Template excluído com sucesso"}
            return {"status": "error", "message": "Template não encontrado"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao excluir template: {str(e)}"}

    def list_templates(self, tipo: str = None):
        try:
            query = {}
            if tipo:
                query["tipo"] = tipo
            
            templates = []
            for template in self.collection.find(query):
                template["_id"] = str(template["_id"])
                templates.append(template)
            return templates
        except Exception as e:
            return []

    def get_template_by_id(self, template_id: str):
        try:
            template = self.collection.find_one({"_id": ObjectId(template_id)})
            if template:
                template["_id"] = str(template["_id"])
                return template
            return None
        except:
            return None
