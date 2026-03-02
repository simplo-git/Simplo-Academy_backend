from bson.objectid import ObjectId
from app.src.services.db_service import DBService
from app.src.services.file_upload_service import FileUploadService
from app.src.services.cascade_delete_service import cascade_delete_service
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class ActivityTemplateService:
    def __init__(self):
        mongo_uri = os.getenv("MONGO")
        self.db_service = DBService(mongo_uri)
        self.collection = self.db_service.get_db()["activity_templates"]
        self.file_upload_service = FileUploadService()

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
            # Busca o template antes de excluir para verificar arquivos anexados
            template = self.collection.find_one({"_id": ObjectId(template_id)})
            
            if not template:
                return {"status": "error", "message": "Template não encontrado"}

            # Tenta encontrar URL de arquivo anexo na estrutura do template
            # A estrutura pode variar, mas no caso de vídeo/upload costuma ser:
            # template['template']['dados']['url'] ou algo similar
            file_url = None
            try:
                # Caminho mais comum conforme implementado na rota 'create_video_template_with_upload'
                if "template" in template and "dados" in template["template"]:
                    file_url = template["template"]["dados"].get("url")
            except:
                pass

            if file_url and "/api/files/" in file_url:
                try:
                    # Extrair folder e filename da URL
                    # Ex: /api/files/video/nomearquivo.mp4
                    parts = file_url.split("/api/files/")
                    if len(parts) > 1:
                        path_parts = parts[1].split("/")
                        if len(path_parts) >= 2:
                            folder = path_parts[0]
                            filename = path_parts[1]
                            # Deletar arquivo físico
                            self.file_upload_service.delete_file(folder, filename)
                except Exception as e:
                    print(f"Erro ao tentar excluir arquivo físico: {e}")

            # Excluir do banco
            result = self.collection.delete_one({"_id": ObjectId(template_id)})
            if result.deleted_count > 0:
                # Cascade: remove referencias em outros documentos
                cascade_delete_service.on_template_deleted(template_id)
                return {"status": "success", "message": "Template excluído com sucesso"}
            return {"status": "error", "message": "Erro ao excluir template do banco"}
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
