from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB.ConfigDB import get_db
from DB import OpDB_ObjectType, OpDB_Algorithm, OpDB_Pipeline
from Models.ObjectType import ObjectType
from CatalogoGlobaleAlgoritmiDisponibili.Catalogo import AlgCatalog
from Schemas.Pipeline_schema import PipelineBuildRequest, PipelineResponse, SelectStepRequest, SavePipelineRequest
import uuid 
from Models.Pipeline import Pipeline
from Models.Algorithm import Algorithm
from DB.EntitaSQL_db import PipelineDB
from DB.OpDB_Context import get_context_hierarchy
from threading import Lock

catalog_lock = Lock()
active_sessions = {}
router = APIRouter()
catalog_cache = {}


@router.get("/{pipeline_id}", response_model=PipelineResponse) # Endpoint per recuperare pipeline
def get_pipeline_endpoint(pipeline_id: int, context_id: int, db: Session = Depends(get_db)): # Riceve ID e DB

    db_pipeline = db.query(PipelineDB).filter(
        PipelineDB.ID_P == pipeline_id
    ).first()

    if not db_pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    context_ids = get_context_hierarchy(db, context_id)

    if db_pipeline.CONTEXT_ID_P not in context_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    pipeline = OpDB_Pipeline.get_pipeline(db, pipeline_id)

    steps = [
        {
            "input_type": step.input_type.name,
            "algorithm": step.algorithm.name,
            "output_type": step.output_type.name
        }
        for step in pipeline.steps
    ]

    return PipelineResponse(
        id=pipeline_id,
        name=db_pipeline.PIPELINE_NAME,
        start_type=db_pipeline.start_type.name,
        end_type=db_pipeline.end_type.name,
        total_cost=db_pipeline.TOTAL_COST_P,
        steps=steps,
        context_id=db_pipeline.CONTEXT_ID_P,
        context_name=db_pipeline.CONTEXT_NAME_P
    )


@router.post("/start-composition") # Endpoint per iniziare una nuova composizione di pipeline
def start_composition(start_type: str, end_type: str, context_id: int, db: Session = Depends(get_db)): # Riceve tipo iniziale e finale

    context_hierarchy = get_context_hierarchy(db, context_id)
    db_objects = OpDB_ObjectType.get_object_types_by_contexts(db, context_hierarchy)
    valid_names = {obj.name for obj in db_objects}
    
    if start_type not in valid_names: raise HTTPException(status_code=404, detail="Start type not found in context")
    if end_type not in valid_names: raise HTTPException(status_code=404, detail="End type not found in context")
    
    # ===== COSTRUZIONE CATALOGO =====
    catalog = get_cached_catalog(db, context_hierarchy)

    session_id = str(uuid.uuid4()) # Genera un ID univoco per la sessione

    active_sessions[session_id] = {
        "start_type": start_type,
        "end_type": end_type,
        "context_id": context_id,
        "selected_algorithms": []
    }

    return { # Restituisce ID sessione al client
        "session_id": session_id
    }


@router.get("/next-steps/{session_id}") # Endpoint per ottenere gli algoritmi disponibili nello step corrente
def get_next_steps(session_id: str, db: Session = Depends(get_db)): # Riceve ID sessione

    if session_id not in active_sessions: # Controlla se la sessione esiste
        raise HTTPException(status_code=404, detail="Session not found") # Errore se non esiste

    session = active_sessions[session_id] # Recupera la sessione

    context_id = session["context_id"]
    context_hierarchy = get_context_hierarchy(db, context_id)
    catalog = get_cached_catalog(db, context_hierarchy)

    pipeline = rebuild_pipeline(session, catalog.db_algorithms)
    current_type = pipeline.get_last_output()

    visited_types = {pipeline.start_type.name}
    for step in pipeline.steps:
        visited_types.add(step.output_type.name)

    next_algorithms = [
        alg for alg in catalog.get_by_input(current_type)
        if alg.output_type.name not in visited_types
    ]

    # ===== STALLO CHECK =====
    is_stuck = False
    if not next_algorithms and current_type.name != session["end_type"]:
        is_stuck = True

    return {
        "current_type": current_type.name,
        "pipeline": [str(step) for step in pipeline.steps],
        "next_algorithms": [
            {
                "name": alg.name,
                "output_type": alg.output_type.name,
                "cost": alg.cost
            }
            for alg in next_algorithms
        ],
        "is_complete": current_type.name == session["end_type"],
        "is_stuck": is_stuck,
        "total_cost": pipeline.get_total_cost()
    }


@router.post("/select-step/{session_id}") # Endpoint per selezionare il prossimo step della pipeline
def select_step(session_id: str, request: SelectStepRequest, db: Session = Depends(get_db)): # Riceve sessione e body JSON

    algorithm_name = request.algorithm_name # Estrae nome algoritmo dal body JSON

    if session_id not in active_sessions: # Verifica esistenza sessione
        raise HTTPException(status_code=404, detail="Session not found") # Errore

    session = active_sessions[session_id] # Recupera sessione
    context_id = session["context_id"]
    context_hierarchy = get_context_hierarchy(db, context_id)

    # 🔁 Ricostruisce pipeline corrente
    catalog = get_cached_catalog(db, context_hierarchy)
    pipeline = rebuild_pipeline(session, catalog.db_algorithms)

    current_type = pipeline.get_last_output()

    visited_types = {pipeline.start_type.name}
    for step in pipeline.steps:
        visited_types.add(step.output_type.name)

    valid_algorithms = [
        alg.name
        for alg in catalog.get_by_input(current_type)
        if alg.output_type.name not in visited_types
    ]

    if algorithm_name not in valid_algorithms:
        raise HTTPException(status_code=400, detail="Invalid algorithm for this step")

    # Aggiunge nuovo step
    alg_db = next((a for a in catalog.db_algorithms if a.name == algorithm_name), None)
    if not alg_db:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    new_alg = Algorithm( # Ricrea algoritmo runtime
        name=alg_db.name,
        input_type=ObjectType(alg_db.input_type),
        output_type=ObjectType(alg_db.output_type),
        cost=alg_db.cost
    )

    pipeline.add_step(new_alg) # Aggiunge step alla pipeline

    session["selected_algorithms"].append(algorithm_name) # Aggiorna sessione

    # SE COMPLETA
    if pipeline.get_last_output().name == session["end_type"]:
        return {
            "message": "Pipeline completed",
            "pipeline": [str(step) for step in pipeline.steps],
            "total_cost": pipeline.get_total_cost()
        }

    return {
        "message": "Step aggiunto",
        "current_type": pipeline.get_last_output().name,
        "pipeline": [str(step) for step in pipeline.steps] # Stato corrente
    }


@router.post("/save-pipeline/{session_id}")
def save_pipeline(session_id: str, request: SavePipelineRequest, db: Session = Depends(get_db)):

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Sessione non trovata")

    session = active_sessions[session_id]
    context_id = session["context_id"]
    context_hierarchy = get_context_hierarchy(db, context_id)
    db_algorithms = OpDB_Algorithm.get_algorithms_by_contexts(db, context_hierarchy)
    pipeline = rebuild_pipeline(session, db_algorithms)

    # controllo completamento
    if pipeline.get_last_output().name != session["end_type"]:
        raise HTTPException(status_code=400, detail="Pipeline not complete")

    name = request.name.strip()

    db_pipeline = OpDB_Pipeline.create_pipeline(
        db,
        pipeline,
        name=name,
        context_id=session["context_id"]
    )

    del active_sessions[session_id]
    
    return {
        "message": "Pipeline saved",
        "pipeline_id": db_pipeline.ID_P
    }


@router.get("/", response_model=list[PipelineResponse])
def get_all_pipelines(context_id: int, db: Session = Depends(get_db)):

    context_ids = get_context_hierarchy(db, context_id)
    db_pipelines = db.query(PipelineDB).filter(
        PipelineDB.CONTEXT_ID_P.in_(context_ids)
    ).all()

    results = []

    for db_pipeline in db_pipelines:

        pipeline = OpDB_Pipeline.get_pipeline(db, db_pipeline.id)

        steps = [
            {
                "input_type": step.input_type.name,
                "algorithm": step.algorithm.name,
                "output_type": step.output_type.name
            }
            for step in pipeline.steps
        ]

        results.append(
            PipelineResponse(
                id=db_pipeline.id,
                name=db_pipeline.name,
                start_type=pipeline.start_type.name,
                end_type=db_pipeline.end_type.name,
                total_cost=db_pipeline.TOTAL_COST_P,
                steps=steps,
                context_id=db_pipeline.CONTEXT_ID_P,
                context_name=db_pipeline.CONTEXT_NAME_P 
            )
        )

    return results


@router.delete("/{pipeline_id}")
def delete_pipeline(pipeline_id: int, context_id: int, db: Session = Depends(get_db)):
    pipeline = db.query(PipelineDB).filter(PipelineDB.ID_P == pipeline_id).first()

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    if pipeline.CONTEXT_ID_P != context_id:
        raise HTTPException(status_code=403, detail="You can't delete others' contest pipelines")

    db.delete(pipeline)
    db.commit()

    return {"message": f"Pipeline '{pipeline.PIPELINE_NAME}' deleted"}


######################### Funzioni di supporto #########################

def rebuild_pipeline(session, db_algorithms):
    start = ObjectType(session["start_type"])
    pipeline = Pipeline(start)

    for alg_name in session["selected_algorithms"]:
        alg_db = next((a for a in db_algorithms if a.name == alg_name), None)
        if not alg_db:
            raise HTTPException(status_code=404, detail="Algorithm not found")

        alg = Algorithm(
            name=alg_db.name,
            input_type=ObjectType(alg_db.input_type),
            output_type=ObjectType(alg_db.output_type),
            cost=alg_db.cost
        )

        pipeline.add_step(alg)

    return pipeline

def get_cached_catalog(db: Session, context_hierarchy: list[int]):
    cache_key = tuple(sorted(context_hierarchy))

    with catalog_lock:
        if cache_key in catalog_cache:
            return catalog_cache[cache_key]

        catalog = AlgCatalog()
        db_algorithms = OpDB_Algorithm.get_algorithms_by_contexts(db, context_hierarchy)
        db_objects = OpDB_ObjectType.get_object_types_by_contexts(db, context_hierarchy)

        catalog.load_from_db(db_algorithms, db_objects)

        # salva anche gli algoritmi
        catalog.db_algorithms = db_algorithms

        catalog_cache[cache_key] = catalog

    return catalog