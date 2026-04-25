from sqlalchemy.orm import Session
from DB.EntitaSQL_db import ObjectTypeDB
from DB.EntitaSQL_db import ContextDB
from DB.OpDB_Context import get_context_hierarchy


def create_object_type(db: Session, name: str, description: str = "", context_id: int = None):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")
    if not name or not isinstance(name, str): raise ValueError("name must be a non-empty string")
    if context_id is None: raise ValueError("context_id must be provided")

    context_ids = get_context_hierarchy(db, context_id)
    existing = db.query(ObjectTypeDB).filter(
        ObjectTypeDB.NAME_OT == name.strip(),
        ObjectTypeDB.CONTEXT_ID_OT.in_(context_ids)
    ).first()

    if existing:
        raise ValueError("ObjectType already exists in context hierarchy")
    
    existing = db.query(ObjectTypeDB).filter(
        ObjectTypeDB.NAME_OT == name.strip(),
        ObjectTypeDB.CONTEXT_ID_OT == context_id
    ).first()
    if existing:
        return existing    

    context = db.query(ContextDB).filter(ContextDB.ID_C == context_id).first()

    db_obj = ObjectTypeDB(
        NAME_OT=name,
        DESCRIPTION_OT=description,
        CONTEXT_ID_OT=context_id,
        CONTEXT_NAME_OT=context.name
    )

    db.add(db_obj)  # Aggiunge l'oggetto alla sessione
    db.commit()  # Salva nel database
    db.refresh(db_obj)  # Aggiorna l'oggetto con i dati generati dal DB

    return db_obj  # Restituisce l'oggetto creato


def get_object_type_by_name(db: Session, name: str):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")
    if not name or not isinstance(name, str): raise ValueError("name must be a non-empty string")

    return db.query(ObjectTypeDB).filter(ObjectTypeDB.NAME_OT == name.strip()).first()


def get_object_type_by_id(db: Session, object_type_id: int):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")
    if not isinstance(object_type_id, int): raise ValueError("object_type_id must be an integer")

    return db.query(ObjectTypeDB).filter(ObjectTypeDB.ID_OT == object_type_id).first()


def get_object_types(db: Session):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")

    return db.query(ObjectTypeDB).all()


def delete_object_type(db: Session, name: str, context_id: int):
    obj = db.query(ObjectTypeDB).filter(
        ObjectTypeDB.NAME_OT == name,
        ObjectTypeDB.CONTEXT_ID_OT == context_id
    ).first()

    if not obj:
        return False

    db.delete(obj)
    db.commit()
    return True

def get_object_types_by_contexts(db: Session, context_ids: list[int]):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")

    return db.query(ObjectTypeDB).filter(
        ObjectTypeDB.CONTEXT_ID_OT.in_(context_ids)
    ).all()

def get_object_type_by_name_and_context(db: Session, name: str, context_id: int):
    return db.query(ObjectTypeDB).filter(
        ObjectTypeDB.NAME_OT == name.strip(),
        ObjectTypeDB.CONTEXT_ID_OT == context_id
    ).first()