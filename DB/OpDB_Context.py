from sqlalchemy.orm import Session
from DB.EntitaSQL_db import ContextDB


def create_context(db: Session, name: str, parent_id: int = None):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")
    if not name or not isinstance(name, str): raise ValueError("name must be a non-empty string")

    existing = db.query(ContextDB).filter(ContextDB.NAME_C == name.strip()).first()
    if existing:
        return existing

    context = ContextDB(
        NAME_C=name.strip(),
        PARENT_ID_C=parent_id
    )

    db.add(context)
    db.commit()
    db.refresh(context)

    return context


def get_context_by_id(db: Session, context_id: int):
    return db.query(ContextDB).filter(ContextDB.ID_C == context_id).first()


def get_all_contexts(db: Session):
    return db.query(ContextDB).all()


def get_context_hierarchy(db: Session, context_id: int) -> list[int]: #Restituisce la lista dei context_id: [contesto_corrente, parent, parent_del_parent, ..., root]

    hierarchy = []
    current = get_context_by_id(db, context_id)

    if not current: raise ValueError("Context not found")

    while current:
        hierarchy.append(current.ID_C)
        current = current.parent  # grazie alla relationship

    return hierarchy