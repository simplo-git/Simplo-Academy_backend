from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any

class UserModel(BaseModel):
    foto: Optional[str] = ""
    nome: str
    setor: Optional[str] = ""
    cargo: Optional[str] = ""
    dt_adminisao: Optional[str] = ""
    phone: Optional[str] = ""
    nivel: Optional[str] = ""
    tipo: Optional[str] = ""
    status: Optional[str] = ""
    email: EmailStr
    password: str
    certificados: List[Any] = []
    conteudos: List[Any] = []

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "nome": "admin",
                "email": "admin@admin.com",
                "password": "1234",
                "setor": "IT",
                "cargo": "Developer"
            }
        }
