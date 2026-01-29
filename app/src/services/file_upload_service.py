import os
import uuid
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

class FileUploadService:
    """Serviço para upload e gerenciamento de arquivos locais"""
    
    # Extensões permitidas por tipo
    ALLOWED_EXTENSIONS = {
        'documento': {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx'},
        'video': {'mp4', 'avi', 'mov', 'mkv', 'webm'},
        'upload': {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'zip', 'rar'}
    }
    
    # Mapeamento de tipo para pasta
    TYPE_TO_FOLDER = {
        'documento': 'documents',
        'video': 'video',
        'upload': 'documents'  # uploads gerais vão para documents
    }
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Caminho relativo à raiz do projeto
            self.base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data')
        else:
            self.base_path = base_path
        
        # Garantir que as pastas existam
        self._ensure_folders_exist()
    
    def _ensure_folders_exist(self):
        """Cria as pastas necessárias se não existirem"""
        folders = ['documents', 'video', 'image']
        for folder in folders:
            folder_path = os.path.join(self.base_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
    
    def _get_extension(self, filename: str) -> str:
        """Retorna a extensão do arquivo"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    def _is_allowed_file(self, filename: str, tipo: str) -> bool:
        """Verifica se a extensão é permitida para o tipo"""
        ext = self._get_extension(filename)
        allowed = self.ALLOWED_EXTENSIONS.get(tipo, set())
        return ext in allowed
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Gera um nome único para o arquivo"""
        ext = self._get_extension(original_filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        safe_name = secure_filename(original_filename.rsplit('.', 1)[0])[:50]
        return f"{safe_name}_{timestamp}_{unique_id}.{ext}"
    
    def save_file_from_base64(self, base64_data: str, filename: str, tipo: str, host_url: str = None):
        """
        Salva arquivo a partir de base64 e retorna a URL interna
        
        Args:
            base64_data: String base64 do arquivo (pode incluir data URI prefix)
            filename: Nome original do arquivo com extensão
            tipo: Tipo de atividade (documento, video, upload)
            host_url: URL base do servidor (ex: http://127.0.0.1:5000)
        
        Returns:
            dict com status, url e informações do arquivo
        """
        try:
            if not base64_data:
                return {"status": "error", "message": "Nenhum arquivo enviado"}
            
            if not filename:
                return {"status": "error", "message": "Nome do arquivo é obrigatório"}
            
            if tipo not in self.TYPE_TO_FOLDER:
                return {"status": "error", "message": f"Tipo '{tipo}' não suportado para upload"}
            
            if not self._is_allowed_file(filename, tipo):
                allowed = ', '.join(self.ALLOWED_EXTENSIONS.get(tipo, []))
                return {"status": "error", "message": f"Extensão não permitida. Extensões permitidas: {allowed}"}
            
            # Remover prefixo data URI se existir (ex: "data:application/pdf;base64,")
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decodificar base64
            try:
                file_bytes = base64.b64decode(base64_data)
            except Exception as e:
                return {"status": "error", "message": f"Erro ao decodificar base64: {str(e)}"}
            
            # Gerar nome único e determinar pasta
            unique_filename = self._generate_unique_filename(filename)
            folder = self.TYPE_TO_FOLDER[tipo]
            folder_path = os.path.join(self.base_path, folder)
            file_path = os.path.join(folder_path, unique_filename)
            
            # Salvar arquivo
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            # Gerar URL interna
            internal_url = f"/api/files/{folder}/{unique_filename}"
            if host_url:
                full_url = f"{host_url}{internal_url}"
            else:
                full_url = internal_url
            
            return {
                "status": "success",
                "message": "Arquivo salvo com sucesso",
                "url": full_url,
                "internal_path": internal_url,
                "filename": unique_filename,
                "original_filename": filename,
                "folder": folder,
                "tipo": tipo
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Erro ao salvar arquivo: {str(e)}"}
    
    def save_file(self, file, tipo: str, host_url: str = None):
        """
        Salva o arquivo localmente e retorna a URL interna (para multipart/form-data)
        
        Args:
            file: Arquivo do request (FileStorage)
            tipo: Tipo de atividade (documento, video, upload)
            host_url: URL base do servidor (ex: http://127.0.0.1:5000)
        
        Returns:
            dict com status, url e informações do arquivo
        """
        try:
            if not file or file.filename == '':
                return {"status": "error", "message": "Nenhum arquivo enviado"}
            
            if tipo not in self.TYPE_TO_FOLDER:
                return {"status": "error", "message": f"Tipo '{tipo}' não suportado para upload"}
            
            if not self._is_allowed_file(file.filename, tipo):
                allowed = ', '.join(self.ALLOWED_EXTENSIONS.get(tipo, []))
                return {"status": "error", "message": f"Extensão não permitida. Extensões permitidas: {allowed}"}
            
            # Gerar nome único e determinar pasta
            unique_filename = self._generate_unique_filename(file.filename)
            folder = self.TYPE_TO_FOLDER[tipo]
            folder_path = os.path.join(self.base_path, folder)
            file_path = os.path.join(folder_path, unique_filename)
            
            # Salvar arquivo
            file.save(file_path)
            
            # Gerar URL interna
            internal_url = f"/api/files/{folder}/{unique_filename}"
            if host_url:
                full_url = f"{host_url}{internal_url}"
            else:
                full_url = internal_url
            
            return {
                "status": "success",
                "message": "Arquivo salvo com sucesso",
                "url": full_url,
                "internal_path": internal_url,
                "filename": unique_filename,
                "original_filename": file.filename,
                "folder": folder,
                "tipo": tipo
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Erro ao salvar arquivo: {str(e)}"}
    
    def delete_file(self, folder: str, filename: str):
        """Remove um arquivo do sistema"""
        try:
            file_path = os.path.join(self.base_path, folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return {"status": "success", "message": "Arquivo removido com sucesso"}
            return {"status": "error", "message": "Arquivo não encontrado"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao remover arquivo: {str(e)}"}
    
    def get_file_path(self, folder: str, filename: str) -> str:
        """Retorna o caminho completo do arquivo"""
        return os.path.join(self.base_path, folder, filename)

