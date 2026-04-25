from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB.ConfigDB import get_db
from DB import OpDB_ObjectType, OpDB_Algorithm
from Schemas.Algorithm_schema import AlgorithmCreate, AlgorithmResponse
from DB.OpDB_Context import get_context_hierarchy
from API.PipelineAPI import catalog_cache

router = APIRouter()


@router.post("/", response_model=AlgorithmResponse)
def create_algorithm_endpoint(algorithm: AlgorithmCreate, context_id: int, db: Session = Depends(get_db)):

    try:
        context_hierarchy = get_context_hierarchy(db, context_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Context not found")
    
    db_objects = OpDB_ObjectType.get_object_types_by_contexts(db, context_hierarchy)
    valid_names = {obj.name for obj in db_objects}

    if algorithm.input_type not in valid_names: raise HTTPException(status_code=404, detail="Input type not found in context")
    if algorithm.output_type not in valid_names: raise HTTPException(status_code=404, detail="Output type not found in context")

    catalog_cache.clear()

    return OpDB_Algorithm.create_algorithm(
        db,
        algorithm.name,
        algorithm.input_type,
        algorithm.output_type,
        algorithm.cost,
        context_id=context_id
    )


@router.get("/", response_model=list[AlgorithmResponse])
def get_algorithms_endpoint(context_id: int, db: Session = Depends(get_db)):

    try:
        context_hierarchy = get_context_hierarchy(db, context_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Context not found")

    return OpDB_Algorithm.get_algorithms_by_contexts(db, context_hierarchy)


@router.delete("/{name}")
def delete_algorithm_endpoint(name: str, context_id: int, db: Session = Depends(get_db)):

    try:
        get_context_hierarchy(db, context_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Context not found")
    
    success = OpDB_Algorithm.delete_algorithm(db, name, context_id)

    if not success:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    catalog_cache.clear()

    return {"message": f"Algorithm '{name}' deleted"}