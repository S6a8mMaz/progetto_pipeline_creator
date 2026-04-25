from sqlalchemy.orm import Session
from DB.EntitaSQL_db import ObjectTypeDB, AlgorithmDB, PipelineDB, PipelineStepDB
from Models.Pipeline import Pipeline
from Models.ObjectType import ObjectType
from Models.Algorithm import Algorithm
from DB.OpDB_Context import get_context_hierarchy
from DB.EntitaSQL_db import ContextDB


def create_pipeline(db: Session, pipeline: Pipeline, name: str, context_id: int):
    if not isinstance(db, Session):
        raise ValueError("db must be a valid Session")

    if not isinstance(pipeline, Pipeline):
        raise ValueError("pipeline must be a Pipeline")

    context_hierarchy = get_context_hierarchy(db, context_id)

    start_type = db.query(ObjectTypeDB).filter(
        ObjectTypeDB.NAME_OT == pipeline.start_type.name,
        ObjectTypeDB.CONTEXT_ID_OT.in_(context_hierarchy)
    ).first()

    end_type = db.query(ObjectTypeDB).filter(
        ObjectTypeDB.NAME_OT == pipeline.get_last_output().name,
        ObjectTypeDB.CONTEXT_ID_OT.in_(context_hierarchy)
    ).first()

    if not start_type or not end_type:
        raise ValueError("ObjectType not found in DB")
    
    context = db.query(ContextDB).filter(ContextDB.ID_C == context_id).first()

    try:
        db_pipeline = PipelineDB(
            PIPELINE_NAME=name,
            START_TYPE_ID_P=start_type.ID_OT,
            END_TYPE_ID_P=end_type.ID_OT,
            TOTAL_COST_P=pipeline.get_total_cost(),
            CONTEXT_ID_P=context_id,
            CONTEXT_NAME_P=context.name
        )

        db.add(db_pipeline)
        db.flush()

        for i, step in enumerate(pipeline.steps, start=1):
            db_alg = db.query(AlgorithmDB).filter(
                AlgorithmDB.NAME_A == step.algorithm.name,
                AlgorithmDB.CONTEXT_ID_A.in_(context_hierarchy)
            ).first()

            if not db_alg:
                raise ValueError(f"Algorithm {step.algorithm.name} not found")

            db_step = PipelineStepDB(
                PIPELINE_ID=db_pipeline.ID_P,
                PIPELINE_NAME=db_pipeline.PIPELINE_NAME,
                ID_STEP=i,
                ALGORITHM_ID=db_alg.ID_A
            )

            db.add(db_step)

        db.commit()
        db.refresh(db_pipeline)

        return db_pipeline

    except Exception:
        db.rollback()
        raise


def get_pipeline(db: Session, pipeline_id: int):  # Ricostruisce una pipeline logica dal DB
    if not isinstance(db, Session):  # Controlla sessione
        raise ValueError("db must be a valid Session")  # Errore se non valida

    if not isinstance(pipeline_id, int):  # Controlla ID pipeline
        raise ValueError("pipeline_id must be an integer")  # Errore se non valido

    db_pipeline = db.query(PipelineDB).filter_by(ID_P=pipeline_id).first()  # Cerca pipeline nel DB
    if not db_pipeline:  # Se non esiste
        return None  # Restituisce None

    start = ObjectType(  # Ricrea il tipo iniziale runtime
        name=db_pipeline.start_type.name,  # Nome del tipo iniziale
        description=getattr(db_pipeline.start_type, "description", ""),  # Descrizione se presente
        id=getattr(db_pipeline.start_type, "id", None)  # ID se presente
    )

    pipeline = Pipeline(
        start,
        id=db_pipeline.id,
        name=db_pipeline.name  # 🔥 QUI
    ) # Crea pipeline runtime con ID DB
    steps = sorted(db_pipeline.steps, key=lambda s: s.ID_STEP)

    for step in steps:
        alg_db = step.algorithm

        input_type = ObjectType(name=alg_db.INPUT_TYPE_A)
        output_type = ObjectType(name=alg_db.OUTPUT_TYPE_A)

        alg = Algorithm(
            name=alg_db.NAME_A,
            input_type=input_type,
            output_type=output_type,
            cost=alg_db.COST_A
        )

        pipeline.add_step(alg)

    return pipeline  # Restituisce la pipeline ricostruita


def delete_pipeline(db: Session, name: str, context_id: int):

    pipeline = db.query(PipelineDB).filter(
        PipelineDB.PIPELINE_NAME == name,
        PipelineDB.CONTEXT_ID_P == context_id
    ).first()

    if not pipeline:
        return False

    db.delete(pipeline)
    db.commit()
    return True