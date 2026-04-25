from sqlalchemy.orm import Session
from DB.EntitaSQL_db import AlgorithmDB
from DB.EntitaSQL_db import ContextDB


def create_algorithm(db: Session, name: str, input_type: str, output_type: str, cost: float, context_id: int = None):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")
    if not name or not isinstance(name, str): raise ValueError("name must be a non-empty string")
    if not input_type or not isinstance(input_type, str): raise ValueError("input_type must be a non-empty string")
    if not output_type or not isinstance(output_type, str): raise ValueError("output_type must be a non-empty string")
    if not isinstance(cost, (int, float)) or cost < 0: raise ValueError("cost must be a non-negative number")
    if context_id is None: raise ValueError("context_id must be provided")

    existing = db.query(AlgorithmDB).filter(
        AlgorithmDB.NAME_A == name.strip(),
        AlgorithmDB.CONTEXT_ID_A == context_id
    ).first()

    if existing:
        return existing

    context = db.query(ContextDB).filter(ContextDB.ID_C == context_id).first()

    db_alg = AlgorithmDB(
        NAME_A=name,
        INPUT_TYPE_A=input_type,
        OUTPUT_TYPE_A=output_type,
        COST_A=cost,
        CONTEXT_ID_A=context_id,
        CONTEXT_NAME_A=context.name
    )

    db.add(db_alg)
    db.commit()
    db.refresh(db_alg)

    return db_alg


def get_algorithms(db: Session):  # Restituisce tutti gli algoritmi presenti nel database
    if not isinstance(db, Session):  # Controlla sessione
        raise ValueError("db must be a valid Session")  # Errore se non valida

    return db.query(AlgorithmDB).all()  # Restituisce tutti gli algoritmi


def get_algorithm_by_id(db: Session, algorithm_id: int):  # Recupera un AlgorithmDB dato il suo ID
    if not isinstance(db, Session):  # Controlla sessione
        raise ValueError("db must be a valid Session")  # Errore se non valida

    if not isinstance(algorithm_id, int):  # Controlla ID
        raise ValueError("algorithm_id must be an integer")  # Errore se non valido

    return db.query(AlgorithmDB).filter(AlgorithmDB.ID_A == algorithm_id).first()  # Cerca e restituisce il record


def delete_algorithm(db: Session, name: str, context_id: int):
    alg = db.query(AlgorithmDB).filter(
        AlgorithmDB.NAME_A == name,
        AlgorithmDB.CONTEXT_ID_A == context_id
    ).first()

    if not alg:
        return False

    db.delete(alg)
    db.commit()
    return True

def get_algorithms_by_contexts(db: Session, context_ids: list[int]):
    if not isinstance(db, Session): raise ValueError("db must be a valid Session")

    return db.query(AlgorithmDB).filter(
        AlgorithmDB.CONTEXT_ID_A.in_(context_ids)
    ).all()

def get_algorithm_by_name_and_context(db: Session, name: str, context_id: int):
    return db.query(AlgorithmDB).filter(
        AlgorithmDB.NAME_A == name.strip(),
        AlgorithmDB.CONTEXT_ID_A == context_id
    ).first()