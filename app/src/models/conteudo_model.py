from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class CorrectionType(str, Enum):
    AUTOMATICA = "automatica"
    MANUAL = "manual"


class UserResponse(BaseModel):
    template_id: str
    tipo: str
    resposta: Any
    data_resposta: str
    correta: Optional[bool] = None
    nota: Optional[float] = None

class UserProgress(BaseModel):
    realizado: bool = False
    nota: Optional[float] = None
    data_conclusao: Optional[str] = None
    status: Optional[str] = None
    conteudo: List[UserResponse] = []

class Setor(BaseModel):
    id: str

class ConteudoModel(BaseModel):
    nome: str = Field(..., description="Nome do conteúdo")
    descricao: str = Field(..., description="Descrição do conteúdo")
    conteudos: List[str] = Field(default=[], description="Lista de IDs dos templates de atividade")
    nivel: int = Field(..., description="Nível do conteúdo")
    usuarios: Dict[str, UserProgress] = Field(default={}, description="Progresso dos usuários, chaveado por ID do usuário")
    setor: List[Setor] = Field(default=[], description="Lista de setores relacionados")
    data_criacao: Optional[str] = Field(default=None, description="Data de criação")
    correcao: CorrectionType = Field(CorrectionType.MANUAL, description="Tipo de correção")
    certificado_id: Optional[str] = Field(None, description="ID do certificado associado")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "nome": "Curso Introdutório",
                "descricao": "Curso básico para iniciantes",
                "conteudos": ["65b9f...", "65c1a..."],
                "nivel": 1,
                "usuarios": {
                    "65d2e...": {"realizado": True, "nota": 9.5, "data_conclusao": "2024-02-01"}
                },
                "setor": [{"id": "1", "nome": "Tecnologia"}, {"id": "2", "nome": "RH"}],
                "data_criacao": "2024-01-30T10:00:00",
                "correcao": "automatica",
                "certificado_id": "65e3f..."
            }
        }
