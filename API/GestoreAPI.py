from fastapi import APIRouter
from API.ObjectTypeAPI import router as object_type_router
from API.AlgorithmsAPI import router as algorithm_router
from API.PipelineAPI import router as pipeline_router
from API.ContextAPI import router as context_router

# router principale
router = APIRouter()

# include i sotto-router con prefix e tag
router.include_router(
    object_type_router,
    prefix="/object-types",
    tags=["Object Types"]
)

router.include_router(
    algorithm_router,
    prefix="/algorithms",
    tags=["Algorithms"]
)

router.include_router(
    pipeline_router,
    prefix="/pipelines",
    tags=["Pipelines"]
)

router.include_router(
    context_router,
    prefix="/contexts",
    tags=["Contexts"]
)