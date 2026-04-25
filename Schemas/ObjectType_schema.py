from pydantic import BaseModel, Field  # Importa BaseModel e Field per validazione
from pydantic import ConfigDict  # Configurazione Pydantic v2


class ObjectTypeCreate(BaseModel):

    name: str = Field(..., min_length=1, description="ObjectType namr")
    description: str = Field(default="", description="Description (optional)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "RawData",
                "description": "Dati grezzi in ingresso"
            }
        }
    )


class ObjectTypeResponse(BaseModel):  # Schema di risposta per ObjectType

    id: int  # ID del record
    name: str  # Nome del tipo
    description: str = ""  # Descrizione
    context_id: int # contesto
    context_name: str

    model_config = ConfigDict(  # Configurazione Pydantic
        from_attributes=True  # Permette conversione da oggetti ORM
    )