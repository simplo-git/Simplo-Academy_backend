from bson.objectid import ObjectId
from app.src.services.db_service import DBService
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class ConteudoService:
    def __init__(self):
        mongo_uri = os.getenv("MONGO")
        self.db_service = DBService(mongo_uri)
        self.collection = self.db_service.get_db()["conteudos"]
        self.users_collection = self.db_service.get_db()["users"]
        self.sectors_collection = self.db_service.get_db()["setores"]
        self.templates_collection = self.db_service.get_db()["activity_templates"]

    def _issue_certificate(self, conteudo, user_id, nota):
        """Helper para emitir certificado se aplicável"""
        certificado_id = conteudo.get("certificado_id")
        if certificado_id:
             try:
                 # Verificar se já possui certificado com este ID
                 user_doc = self.users_collection.find_one(
                     {"_id": ObjectId(user_id), "certificados.id": certificado_id}
                 )
                 
                 if not user_doc:
                     certificate_data = {
                         "id": certificado_id,
                         "data_conclusao": datetime.now().isoformat(),
                         "conteudo_id": str(conteudo["_id"]),
                         "nome_conteudo": conteudo.get("nome"),
                         "nota_final": nota
                     }
                     
                     self.users_collection.update_one(
                         {"_id": ObjectId(user_id)},
                         {"$push": {"certificados": certificate_data}}
                     )
                     return True
             except Exception as e_cert:
                 print(f"Erro ao emitir certificado automaticamente: {e_cert}")
        return False

    def _promote_user_to_level_2(self, user_id):
        """Promove usuário para nível 2 se estiver no nível 1"""
        try:
            print(f"[PROMOTION] Checking promotion for user {user_id}")
            user = self.users_collection.find_one({"_id": ObjectId(user_id)}, {"nivel": 1})
            if user:
                current_level = str(user.get("nivel", "")).strip()
                print(f"[PROMOTION] User {user_id} level: '{current_level}'")
                
                # Check normalized level
                normalized_level = current_level.lower().replace("í", "i").replace("0", "")
                
                # Accept: "1", "nivel 1", "nivel 01", "", "none"
                is_level_1 = (
                    current_level in ["1", "None", ""] or
                    "nivel 1" in normalized_level
                )
                
                if is_level_1:
                     print(f"[PROMOTION] Promoting user {user_id} to Nível 02")
                     self.users_collection.update_one(
                         {"_id": ObjectId(user_id)},
                         {"$set": {"nivel": "Nível 02"}}
                     )
                     return True
                else:
                    print(f"[PROMOTION] User {user_id} is not Level 1 (Raw: '{current_level}'), skipping.")
        except Exception as e:
            print(f"Erro ao promover usuario: {e}")
        return False

    def _populate_sectors_from_users(self, data: dict):
        """Preenche o campo setor com base em 'setores' (IDs explicito) ou usuários (fallback)"""
        
        # 1. Verificar se veio 'setores' (plural, lista de IDs) do frontend
        explicit_sector_ids = data.get("setores")
        target_sector_ids = set()

        if explicit_sector_ids and isinstance(explicit_sector_ids, list):
            target_sector_ids.update(explicit_sector_ids)
        
        # 2. Verificar se veio 'setor' (singular, lista de objetos) caso 'setores' esteja ausente
        if explicit_sector_ids is None:
            raw_setor = data.get("setor")
            if raw_setor and isinstance(raw_setor, list):
                for s_item in raw_setor:
                    if isinstance(s_item, dict) and s_item.get("id"):
                        target_sector_ids.add(s_item.get("id"))
                    elif isinstance(s_item, str):
                        target_sector_ids.add(s_item)

        # 3. Se não veio setores validos, tenta pegar dos usuários (fallback)
        if explicit_sector_ids is None and not target_sector_ids:
            usuarios = data.get("usuarios", {})
            if usuarios:
                if isinstance(usuarios, dict):
                    user_ids = list(usuarios.keys())
                    if user_ids:
                        try:
                            obj_ids = [ObjectId(uid) for uid in user_ids]
                            users = self.users_collection.find({"_id": {"$in": obj_ids}}, {"setor": 1})
                            for user in users:
                                s = user.get("setor")
                                if s:
                                    target_sector_ids.add(s)
                        except Exception as e:
                            print(f"Erro ao buscar setores de usuarios: {e}")

        # 3. Resolver Nomes (buscando na collection de setores)
        sector_list = []
        if target_sector_ids:
            for sec_id in target_sector_ids:
                found_sector = None
                # Tentativa 1: Buscar por ObjectId
                try:
                    found_sector = self.sectors_collection.find_one({"_id": ObjectId(sec_id)})
                except:
                    pass
                
                # Tentativa 2: Buscar por String (caso o banco use Strings nos IDs)
                if not found_sector:
                    found_sector = self.sectors_collection.find_one({"_id": str(sec_id)})
                
                if found_sector:
                    sector_list.append({
                        "id": str(found_sector["_id"])
                    })
                else:
                    sector_list.append({
                        "id": str(sec_id)
                    })
        
        # 4. Atualizar campo 'setor' (singular) no data
        if explicit_sector_ids is not None:
             data["setor"] = sector_list
        elif sector_list: 
             data["setor"] = sector_list
             
        # Limpar campo 'setores' auxiliar
        if "setores" in data:
            del data["setores"]

        return data

    def create_conteudo(self, data: dict):
        try:
            # Adiciona data de criação se não fornecida
            if not data.get("data_criacao"):
                data["data_criacao"] = datetime.now().isoformat()
            
            # Garantir que usuarios seja um dict se vazio
            if "usuarios" not in data:
                data["usuarios"] = {}

            # Popula setores se vazio
            data = self._populate_sectors_from_users(data)

            result = self.collection.insert_one(data)
            return {"status": "success", "message": "Conteúdo criado com sucesso", "id": str(result.inserted_id)}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao criar conteúdo: {str(e)}"}

    def update_conteudo(self, conteudo_id: str, data: dict):
        try:
            # Remove _id do payload se existir para evitar erro de imutabilidade
            if "_id" in data:
                del data["_id"]

            # Popula setores se vazio (e se houve envio de usuarios ou setores vazios)
            # Se for atualização parcial e não enviou setor nem usuarios, nao faz nada.
            if "setor" in data or "usuarios" in data:
                 data = self._populate_sectors_from_users(data)

            result = self.collection.update_one({"_id": ObjectId(conteudo_id)}, {"$set": data})
            if result.modified_count > 0:
                return {"status": "success", "message": "Conteúdo atualizado com sucesso"}
            return {"status": "error", "message": "Conteúdo não encontrado ou sem alterações"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao atualizar conteúdo: {str(e)}"}

    def delete_conteudo(self, conteudo_id: str):
        try:
            result = self.collection.delete_one({"_id": ObjectId(conteudo_id)})
            if result.deleted_count > 0:
                return {"status": "success", "message": "Conteúdo excluído com sucesso"}
            return {"status": "error", "message": "Erro ao excluir conteúdo do banco"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao excluir conteúdo: {str(e)}"}

    def list_conteudos(self):
        try:
            conteudos = []
            for conteudo in self.collection.find():
                conteudo["_id"] = str(conteudo["_id"])
                conteudos.append(conteudo)
            return conteudos
        except Exception as e:
            return []

    def get_conteudo_by_id(self, conteudo_id: str):
        try:
            conteudo = self.collection.find_one({"_id": ObjectId(conteudo_id)})
            if conteudo:
                conteudo["_id"] = str(conteudo["_id"])
                return conteudo
            return None
        except:
            return None

    def add_user_response(self, conteudo_id: str, user_id: str, response_data: dict):
        try:
            # Verifica se o conteúdo existe
            conteudo = self.collection.find_one({"_id": ObjectId(conteudo_id)})
            if not conteudo:
                return {"status": "error", "message": "Conteúdo não encontrado"}
            
            # Verifica se o usuário existe na lista de usuários do conteúdo
            usuarios = conteudo.get("usuarios", {})
            if user_id not in usuarios:
                usuarios[user_id] = {
                    "realizado": False,
                    "nota": None,
                    "data_conclusao": None,
                    "status": None,
                    "conteudo": []
                }
            
            # Verificar correção imediata se for multipla_escolha
            is_correct = None
            template_id = response_data.get("template_id")
            tipo = response_data.get("tipo")
            user_ans = response_data.get("resposta")
            
            if template_id and tipo == "multipla_escolha":
                try:
                    template_doc = self.templates_collection.find_one({"_id": ObjectId(template_id)})
                    if template_doc:
                        internal_template = template_doc.get("template", {})
                        opcoes = internal_template.get("opcoes", [])
                        
                        # Achar correta
                        correct_index = -1
                        correct_text = None
                        for idx, opt in enumerate(opcoes):
                            if opt.get("correta") is True:
                                correct_index = idx
                                correct_text = opt.get("texto")
                                break
                        
                        if correct_index != -1 and user_ans is not None:
                            # Comparação flexível
                            if isinstance(user_ans, int) and user_ans == correct_index:
                                is_correct = True
                            elif isinstance(user_ans, str) and str(user_ans).strip() == str(correct_text).strip():
                                is_correct = True
                            elif str(user_ans).isdigit() and int(user_ans) == correct_index:
                                is_correct = True
                            else:
                                is_correct = False
                        else:
                             # Se não achou correta no template, não tem como avaliar, ou user_ans nulo
                             is_correct = False
                except Exception as e:
                    print(f"Erro ao verificar correcao imediata: {e}")
            
            # Verificar tipos auto-corrigíveis (informativos)
            if tipo in ["artigo", "video", "documento"]:
                is_correct = True

            # Preparar objeto de resposta
            new_response = {
                "template_id": template_id,
                "tipo": tipo,
                "resposta": user_ans,
                "data_resposta": response_data.get("data_resposta", datetime.now().isoformat()),
                "correta": is_correct,
                "nota": response_data.get("nota")
            }

            # Caminho de atualização
            update_path = f"usuarios.{user_id}.conteudo"
            
            # Garantir existência do usuario
            if user_id not in conteudo.get("usuarios", {}):
                 self.collection.update_one(
                     {"_id": ObjectId(conteudo_id)},
                     {"$set": {f"usuarios.{user_id}": usuarios[user_id]}}
                 )
            
            # Persistir resposta
            result = self.collection.update_one(
                {"_id": ObjectId(conteudo_id)},
                {"$push": {update_path: new_response}}
            )

            if result.modified_count > 0:
                return {
                    "status": "success", 
                    "message": "Resposta salva com sucesso", 
                    "correta": is_correct  # Retorna feedback imediato
                }
            return {"status": "error", "message": "Não foi possível salvar a resposta"}

        except Exception as e:
            return {"status": "error", "message": f"Erro ao salvar resposta: {str(e)}"}

    def conclude_content(self, conteudo_id: str, user_id: str):
        try:
            # 1. Busca Conteudo
            conteudo = self.collection.find_one({"_id": ObjectId(conteudo_id)})
            if not conteudo:
                return {"status": "error", "message": "Conteúdo não encontrado"}
            
            # 2. Verifica se usuário existe
            usuarios = conteudo.get("usuarios", {})
            if user_id not in usuarios:
                # Se não existe, inicializa
                usuarios[user_id] = {
                    "realizado": False,
                    "nota": None,
                    "data_conclusao": None,
                    "status": None,
                    "conteudo": []
                }

            # 3. Preparar dados base de atualização
            # Nota: para atualizar dinamicamente dicionário nested com chave ID variavel,
            # usamos string notation no $set
            user_data = usuarios[user_id]
            user_data["realizado"] = True
            user_data["data_conclusao"] = datetime.now().isoformat()
            
            current_nota = user_data.get("nota")

            # 4. Verificar Tipo de Correção
            correcao = conteudo.get("correcao")
            
            if correcao == "manual":
                user_data["status"] = "aguardando correção"
            
            elif correcao == "automatica":
                # LÓGICA DE CORREÇÃO AUTOMÁTICA
                current_nota = 0.0
                total_questions = 0
                hits = 0

                # IDs dos templates vinculados ao conteúdo
                template_ids = conteudo.get("conteudos", [])
                
                # Respostas enviadas pelo usuário
                user_responses = user_data.get("conteudo", [])
                # Transforma em dict para busca rápida: {template_id: resposta_obj}
                responses_map = {r.get("template_id"): r for r in user_responses if r.get("template_id")}

                for t_id in template_ids:
                    # Busca o template original
                    try:
                         # Tenta buscar por string direto, e depois por ObjectId se falhar/vice-versa
                         # O service usa ObjectId geralmente
                        template_doc = self.templates_collection.find_one({"_id": ObjectId(t_id)})
                        if not template_doc:
                             continue

                        tipo_atividade = template_doc.get("tipo")
                        
                        # Apenas multipla_escolha é corrigível automaticamente com gabarito simples
                        if tipo_atividade == "multipla_escolha":
                            total_questions += 1
                            
                            # Acessa estrutura interna do template
                            # Estrutura esperada: template['template'] -> { 'opcoes': [...], ... } ou direto
                            # O user mostrou: template: { pergunta: "...", opcoes: [...] }
                            # opcoes: [{texto: "...", correta: bool}]
                            
                            internal_template = template_doc.get("template", {})
                            opcoes = internal_template.get("opcoes", [])
                            
                            # Achar opção correta
                            # Pode ser index ou texto. Vamos achar o indice da correta.
                            correct_index = -1
                            correct_text = None
                            
                            for idx, opt in enumerate(opcoes):
                                if opt.get("correta") is True:
                                    correct_index = idx
                                    correct_text = opt.get("texto")
                                    break
                            
                            if correct_index != -1:
                                # Verifica resposta do user
                                user_resp_obj = responses_map.get(str(template_doc["_id"]))
                                if user_resp_obj:
                                    user_ans = user_resp_obj.get("resposta")
                                    
                                    # Comparação:
                                    # User pode ter mandado index (int) ou texto (str) ou até dict.
                                    # Vamos tentar ser flexíveis.
                                    
                                    is_correct = False
                                    try:
                                        # Se for int e bater com index
                                        if isinstance(user_ans, int) and user_ans == correct_index:
                                            is_correct = True
                                        # Se for str e bater com texto (strip and lower?)
                                        elif isinstance(user_ans, str) and str(user_ans).strip() == str(correct_text).strip():
                                            is_correct = True
                                        # Se for string numérica
                                        elif str(user_ans).isdigit() and int(user_ans) == correct_index:
                                            is_correct = True
                                    except:
                                        pass
                                    
                                    if is_correct:
                                        hits += 1

                    except Exception as ex_temp:
                        print(f"Erro ao processar template {t_id}: {ex_temp}")

                # Calcula nota final
                if total_questions > 0:
                    current_nota = (hits / total_questions) * 10.0
                else:
                    current_nota = 10.0 
                
                # Arredonda nota
                user_data["nota"] = round(current_nota, 1)
                
                # Regra de aprovação: Nota < 6.0 (60%) -> Reprovado
                if user_data["nota"] < 6.0:
                    user_data["status"] = "reprovado"
                else:
                    user_data["status"] = "aprovado"

            # 5. Executar Update
            # Atualizamos o objeto do usuario inteiro para garantir consistência
            result = self.collection.update_one(
                {"_id": ObjectId(conteudo_id)},
                {"$set": {f"usuarios.{user_id}": user_data}}
            )

            # 6. Emissão Automática de Certificado
            if user_data.get("status") == "aprovado":
                self._issue_certificate(conteudo, user_id, user_data.get("nota"))
                
                # Regra de Mudança de Nível Automática (1 -> 2)
                # Somente para conteúdo de Nivel 1 com correção automatica
                if correcao == "automatica" and str(conteudo.get("nivel")) == "1":
                     self._promote_user_to_level_2(user_id)

            if result.modified_count > 0 or result.matched_count > 0:
                resp = {
                    "status": "success", 
                    "message": "Conteúdo concluído com sucesso", 
                    "nota": user_data.get("nota"),
                    "final_status": user_data.get("status")
                }
                return resp
                
            return {"status": "error", "message": "Não foi possível atualizar o status"}

        except Exception as e:
             return {"status": "error", "message": f"Erro ao concluir conteúdo: {str(e)}"}

    def apply_grade(self, conteudo_id: str, user_id: str, nota: float, status: str):
        """
        Aplica nota e status manualmente para um usuário (Correção Manual)
        """
        try:
            # 1. Busca Conteudo
            conteudo = self.collection.find_one({"_id": ObjectId(conteudo_id)})
            if not conteudo:
                return {"status": "error", "message": "Conteúdo não encontrado"}
            
            # 2. Verifica user
            usuarios = conteudo.get("usuarios", {})
            if user_id not in usuarios:
                return {"status": "error", "message": "Usuário não vinculado a este conteúdo"}

            # 3. Atualiza dados
            update_path = f"usuarios.{user_id}"
            
            # Mantém dados existentes, atualiza nota, status e data de conclusão (se aprovado)
            # Se reprovado, mantem ou reseta? O user pediu 'fazer novamente', mas isso é reset.
            # Aqui vamos setar o status e nota.
            
            updates = {
                f"{update_path}.nota": nota,
                f"{update_path}.status": status
            }
            
            if status == "aprovado":
                 updates[f"{update_path}.data_conclusao"] = datetime.now().isoformat()
                 updates[f"{update_path}.realizado"] = True
                 
                 # Regra de Mudança de Nível Automática (1 -> 2)
                 if str(conteudo.get("nivel")) == "1":
                     self._promote_user_to_level_2(user_id)

            result = self.collection.update_one(
                {"_id": ObjectId(conteudo_id)},
                {"$set": updates}
            )

            # 4. Emissão de Certificado se Aprovado
            if status == "aprovado":
                self._issue_certificate(conteudo, user_id, nota)

            return {"status": "success", "message": "Nota aplicada com sucesso"}

        except Exception as e:
            return {"status": "error", "message": f"Erro ao aplicar nota: {str(e)}"}
