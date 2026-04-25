from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB.ConfigDB import get_db
from DB.OpDB_Context import get_all_contexts
from pydantic import BaseModel
from DB.OpDB_Context import create_context, get_context_by_id


router = APIRouter()

@router.get("/")
def get_contexts(db: Session = Depends(get_db)):
    contexts = get_all_contexts(db)

    return [
        {
            "id": c.id,
            "name": c.name,
            "parent_id": c.parent_id
        }
        for c in contexts
    ]

class ContextCreate(BaseModel):
    name: str
    parent_id: int | None = None


@router.post("/")
def create_context_endpoint(context: ContextCreate, db: Session = Depends(get_db)):

    parent = None
    if context.parent_id:
        parent = get_context_by_id(db, context.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent context not found")

    new_context = create_context(
        db,
        name=context.name,
        parent_id=context.parent_id
    )

    return {
        "id": new_context.id,
        "name": new_context.name,
        "parent_id": new_context.parent_id
    }


@router.delete("/{context_id}")
def delete_context(context_id: int, db: Session = Depends(get_db)):

    context = get_context_by_id(db, context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    db.delete(context)
    db.commit()

    return {"message": f"Context {context_id} deleted"}