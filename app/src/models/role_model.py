from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RoleModel(BaseModel):
    nome: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "nome": "Manager"
            }
        }
