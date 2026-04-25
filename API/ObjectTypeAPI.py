from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB.ConfigDB import get_db
from DB import OpDB_ObjectType
from Schemas.ObjectType_schema import ObjectTypeCreate, ObjectTypeResponse
from DB.OpDB_Context import get_context_hierarchy
from API.PipelineAPI import catalog_cache

router = APIRouter()


@router.post("/")
def create_object_type_endpoint(object_type: ObjectTypeCreate, context_id: int, db: Session = Depends(get_db)):

    try:
        get_context_hierarchy(db, context_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Context not found")

    existing = OpDB_ObjectType.get_object_type_by_name_and_context(
        db,
        object_type.name,
        context_id
    )
    if existing:
        return {
            "message": "⚠️ ObjectType already exists",
            "object": {
                "id": existing.id,
                "name": existing.name,
                "description": existing.description
            }
        }

    db_object_type = OpDB_ObjectType.create_object_type(
        db,
        object_type.name,
        object_type.description,
        context_id=context_id
    )

    catalog_cache.clear()

    return {
        "message": "✅ ObjectType created",
        "object": {
            "id": db_object_type.id,
            "name": db_object_type.name,
            "description": db_object_type.description
        }
    }


@router.get("/", response_model=list[ObjectTypeResponse])
def get_object_types_endpoint(context_id: int, db: Session = Depends(get_db)):    
    context_hierarchy = get_context_hierarchy(db, context_id)

    return OpDB_ObjectType.get_object_types_by_contexts(db, context_hierarchy)


@router.delete("/{name}")
def delete_object_type(name: str, context_id: int, db: Session = Depends(get_db)):
    
    try:
        get_context_hierarchy(db, context_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Context not found")
    
    success = OpDB_ObjectType.delete_object_type(db, name, context_id)

    if not success:
        raise HTTPException(status_code=404, detail="ObjectType not found")
    
    catalog_cache.clear()

    return {"message": "ObjectType eliminato"}