from pydantic import BaseModel, Field
from typing import Optional, List

class RelatedCertificate(BaseModel):
    id: str
    nome: str

class CertificateModel(BaseModel):
    nome: str
    insignia: str 
    descricao: str
    data_criacao: str
    nivel: int = Field(..., ge=1, le=3, description="Nível do certificado de 1 a 3")
    relacionados: Optional[List[RelatedCertificate]] = Field(default=[], description="Lista de certificados relacionados")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "nome": "Certificado de Conclusão",
                "insignia": "https://example.com/image.png",
                "descricao": "Certificado para quem concluiu o curso básico",
                "data_criacao": "2024-01-01",
                "nivel": 1,
                "relacionados": [
                    {"id": "12345", "nome": "Certificado Avançado"}
                ]
            }
        }
