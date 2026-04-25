from pydantic import BaseModel, Field 
from pydantic import ConfigDict


class AlgorithmCreate(BaseModel):

    name: str = Field(..., min_length=1, description="Algorithm name")
    input_type: str = Field(..., min_length=1, description="Input type")
    output_type: str = Field(..., min_length=1, description="Output tyoe")
    cost: float = Field(..., ge=0, description="Algorithm cost")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "text_to_embedding",
                "input_type": "text",
                "output_type": "embedding",
                "cost": 1.0
            }
        }
    )

class AlgorithmResponse(BaseModel):

    id: int
    name: str
    input_type: str
    output_type: str
    cost: float
    context_id: int
    context_name: str

    model_config = ConfigDict(from_attributes=True)