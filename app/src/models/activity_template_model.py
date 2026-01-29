from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum

class ActivityType(str, Enum):
    MULTIPLA_ESCOLHA = "multipla_escolha"
    VIDEO = "video"
    TEXTO_LIVRE = "texto_livre"
    UPLOAD = "upload"
    DOCUMENTO = "documento"
    ARTIGO = "artigo"

class ActivityTemplateModel(BaseModel):
    nome: str = Field(..., description="Nome do template de atividade")
    tipo: ActivityType = Field(..., description="Tipo da atividade")
    template: Dict[str, Any] = Field(default={}, description="Template cadastrado - estrutura livre para o frontend")
    data_criacao: Optional[str] = Field(default=None, description="Data de criação")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "nome": "Quiz de Python Básico",
                "tipo": "multipla_escolha",
                "template": {
                    "perguntas": [
                        {
                            "texto": "O que é Python?",
                            "opcoes": ["Linguagem de programação", "Uma cobra", "Um framework"],
                            "resposta_correta": 0
                        }
                    ],
                    "config": {
                        "tempo_limite": 30,
                        "pontuacao_por_acerto": 10
                    }
                },
                "data_criacao": "2024-01-01"
            }
        }
