from bson.objectid import ObjectId
from app.src.services.db_service import DBService
import os
from dotenv import load_dotenv

load_dotenv()


class CascadeDeleteService:
    """
    Serviço centralizado para gerenciar exclusões em cascata.
    Mantém a integridade referencial removendo IDs deletados de todas as coleções relacionadas.
    """

    def __init__(self):
        mongo_uri = os.getenv("MONGO")
        self.db_service = DBService(mongo_uri)
        db = self.db_service.get_db()
        self.conteudos_collection = db["conteudos"]
        self.users_collection = db["users"]
        self.certificates_collection = db["certificates"]
        self.templates_collection = db["activity_templates"]
        self.setores_collection = db["setores"]

    def on_template_deleted(self, template_id: str):
        """
        Remove todas as referências ao template deletado.
        - Remove do array conteudos[] em conteúdos
        - Remove respostas de usuários que referenciam este template
        """
        try:
            print(f"[CASCADE] Removing template {template_id} references...")

            # 1. Remove template ID do array 'conteudos' em todos os documentos de conteúdo
            result1 = self.conteudos_collection.update_many(
                {"conteudos": template_id},
                {"$pull": {"conteudos": template_id}}
            )
            print(f"[CASCADE] Removed from conteudos.conteudos[]: {result1.modified_count} docs")

            # 2. Remove respostas de usuários que referenciam este template
            # Estrutura: usuarios.{user_id}.conteudo[] onde cada item tem template_id
            # Precisamos iterar sobre todos os conteúdos e remover as respostas
            conteudos = self.conteudos_collection.find({"usuarios": {"$exists": True}})
            updated_count = 0
            
            for conteudo in conteudos:
                usuarios = conteudo.get("usuarios", {})
                updates_needed = {}
                
                for user_id, user_data in usuarios.items():
                    user_responses = user_data.get("conteudo", [])
                    if isinstance(user_responses, list):
                        # Filtra respostas que NÃO são do template deletado
                        filtered_responses = [
                            r for r in user_responses 
                            if r.get("template_id") != template_id
                        ]
                        if len(filtered_responses) != len(user_responses):
                            updates_needed[f"usuarios.{user_id}.conteudo"] = filtered_responses
                
                if updates_needed:
                    self.conteudos_collection.update_one(
                        {"_id": conteudo["_id"]},
                        {"$set": updates_needed}
                    )
                    updated_count += 1
            
            print(f"[CASCADE] Removed from user responses: {updated_count} docs")
            return {"status": "success", "message": f"Template references removed from {result1.modified_count + updated_count} documents"}

        except Exception as e:
            print(f"[CASCADE ERROR] on_template_deleted: {str(e)}")
            return {"status": "error", "message": str(e)}

    def on_certificate_deleted(self, certificate_id: str):
        """
        Remove todas as referências ao certificado deletado.
        - Set null em conteudos.certificado_id
        - Remove de users.certificados[]
        - Remove de certificates.relacionados[]
        """
        try:
            print(f"[CASCADE] Removing certificate {certificate_id} references...")

            # 1. Remove referência em conteúdos (set null)
            result1 = self.conteudos_collection.update_many(
                {"certificado_id": certificate_id},
                {"$set": {"certificado_id": None}}
            )
            print(f"[CASCADE] Set null in conteudos.certificado_id: {result1.modified_count} docs")

            # 2. Remove de certificados do usuário (array de objetos com id)
            result2 = self.users_collection.update_many(
                {"certificados.id": certificate_id},
                {"$pull": {"certificados": {"id": certificate_id}}}
            )
            print(f"[CASCADE] Removed from users.certificados[]: {result2.modified_count} docs")

            # 3. Remove de certificados relacionados (em outros certificados)
            result3 = self.certificates_collection.update_many(
                {"relacionados.id": certificate_id},
                {"$pull": {"relacionados": {"id": certificate_id}}}
            )
            print(f"[CASCADE] Removed from certificates.relacionados[]: {result3.modified_count} docs")

            total = result1.modified_count + result2.modified_count + result3.modified_count
            return {"status": "success", "message": f"Certificate references removed from {total} documents"}

        except Exception as e:
            print(f"[CASCADE ERROR] on_certificate_deleted: {str(e)}")
            return {"status": "error", "message": str(e)}

    def on_user_deleted(self, user_id: str):
        """
        Remove todas as referências ao usuário deletado.
        - Remove de conteudos.usuarios{user_id}
        """
        try:
            print(f"[CASCADE] Removing user {user_id} references...")

            # Remove progresso do usuário em todos os conteúdos
            # A chave é dinâmica (usuarios.{user_id}), então usamos $unset
            result = self.conteudos_collection.update_many(
                {f"usuarios.{user_id}": {"$exists": True}},
                {"$unset": {f"usuarios.{user_id}": ""}}
            )
            print(f"[CASCADE] Removed from conteudos.usuarios: {result.modified_count} docs")

            return {"status": "success", "message": f"User references removed from {result.modified_count} documents"}

        except Exception as e:
            print(f"[CASCADE ERROR] on_user_deleted: {str(e)}")
            return {"status": "error", "message": str(e)}

    def on_conteudo_deleted(self, conteudo_id: str):
        """
        Remove todas as referências ao conteúdo deletado.
        - Remove de users.conteudos[] (pode ser objeto ou string)
        """
        try:
            print(f"[CASCADE] Removing conteudo {conteudo_id} references...")

            # Remove conteúdo da lista de conteúdos do usuário (como objeto com id)
            result1 = self.users_collection.update_many(
                {"conteudos.id": conteudo_id},
                {"$pull": {"conteudos": {"id": conteudo_id}}}
            )
            print(f"[CASCADE] Removed from users.conteudos[] (object): {result1.modified_count} docs")

            # Também tenta remover se for string simples
            result2 = self.users_collection.update_many(
                {"conteudos": conteudo_id},
                {"$pull": {"conteudos": conteudo_id}}
            )
            print(f"[CASCADE] Removed from users.conteudos[] (string): {result2.modified_count} docs")

            total = result1.modified_count + result2.modified_count
            return {"status": "success", "message": f"Conteudo references removed from {total} documents"}

        except Exception as e:
            print(f"[CASCADE ERROR] on_conteudo_deleted: {str(e)}")
            return {"status": "error", "message": str(e)}

    def on_setor_deleted(self, setor_id: str):
        """
        Remove todas as referências ao setor deletado.
        - Remove de conteudos.setor[] (array de objetos {id, nome})
        - Limpa users.setor se corresponder
        """
        try:
            print(f"[CASCADE] Removing setor {setor_id} references...")

            # Remove setor de conteúdos
            result1 = self.conteudos_collection.update_many(
                {"setor.id": setor_id},
                {"$pull": {"setor": {"id": setor_id}}}
            )
            print(f"[CASCADE] Removed from conteudos.setor[]: {result1.modified_count} docs")

            # Buscar nome do setor para limpar de usuários (que usam nome, não ID)
            setor = self.setores_collection.find_one({"_id": ObjectId(setor_id)})
            if setor:
                setor_nome = setor.get("nome", "")
                if setor_nome:
                    result2 = self.users_collection.update_many(
                        {"setor": setor_nome},
                        {"$set": {"setor": ""}}
                    )
                    print(f"[CASCADE] Cleared users.setor: {result2.modified_count} docs")

            return {"status": "success", "message": f"Setor references removed"}

        except Exception as e:
            print(f"[CASCADE ERROR] on_setor_deleted: {str(e)}")
            return {"status": "error", "message": str(e)}


# Instância singleton para uso global
cascade_delete_service = CascadeDeleteService()
