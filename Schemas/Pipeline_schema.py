from pydantic import BaseModel, Field  # Importa BaseModel e Field per validazione
from pydantic import ConfigDict  # Configurazione Pydantic v2
from typing import Literal  # Per vincolare valori possibili


class PipelineBuildRequest(BaseModel):  # Schema per richiesta costruzione pipeline

    start_type: str = Field(..., min_length=1, description="Start type")  # Nome tipo iniziale non vuoto
    end_type: str = Field(..., min_length=1, description="End type")  # Nome tipo finale non vuoto

    model_config = ConfigDict(  # Configurazione schema
        json_schema_extra={  # Esempio Swagger
            "example": {
                "start_type": "RawData",
                "end_type": "CleanData"
            }
        }
    )


class PipelineStepResponse(BaseModel):  # Schema per rappresentare uno step della pipeline

    input_type: str  # Nome tipo input
    algorithm: str  # Nome algoritmo
    output_type: str  # Nome tipo output


class PipelineResponse(BaseModel):  # Schema per risposta pipeline

    id: int  # ID pipeline
    name: str | None = None
    start_type: str  # Tipo iniziale
    end_type: str  # Tipo finale
    total_cost: float  # Costo totale
    steps: list[PipelineStepResponse]  # Lista strutturata degli step
    context_id: int
    context_name: str

    model_config = ConfigDict(  # Configurazione
        from_attributes=True  # Conversione da ORM
    )


class SelectStepRequest(BaseModel):  # Schema per selezione manuale step

    algorithm_name: str = Field(..., min_length=1, description="Selected algorithm name")  # Nome algoritmo non vuoto

    model_config = ConfigDict(  # Configurazione
        json_schema_extra={  # Esempio Swagger
            "example": {
                "algorithm_name": "NormalizeData"
            }
        }
    )

class SavePipelineRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Pipeline name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "My Pipeline"
            }
        }
    )