from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Any

from ace import database
from ace.core.models import Playbook, PlaybookEntry
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace.llm import get_language_model
from ace.plugins.manager import plugin_manager
from ace.cluster_manager import ClusterManager
from ace.config import settings
import asyncio

app = FastAPI(
    title="ACE Framework API",
    description="An API for interacting with the Agentic Context Engineering (ACE) framework.",
    version="1.0.0",
)

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency to validate the API key.

    This function is used by FastAPI's dependency injection system to protect
    endpoints. It checks if the provided API key is in the list of valid keys
    defined in the configuration.

    Args:
        api_key: The API key provided in the 'X-API-Key' header.

    Raises:
        HTTPException: If the API key is invalid or missing.

    Returns:
        The validated API key.
    """
    if api_key not in settings["security"]["api_keys"]:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


from pydantic import BaseModel, validator

class RunAceRequest(BaseModel):
    task: str

    @validator('task')
    def task_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Task must not be empty')
        return v

class RunAceResponse(BaseModel):
    new_insights: List[Dict[str, Any]]
    playbook_entries: List[PlaybookEntry]

@app.on_event("startup")
async def startup_event():
    """
    Initializes the database connection and tables when the application starts.
    """
    await database.db_connect()
    await database.initialize_database()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Closes the database connection when the application shuts down.
    """
    await database.db_close()

@app.get("/")
async def root():
    """
    A simple root endpoint to confirm that the API is running.
    """
    return {"message": "Welcome to the ACE Framework API!"}

@app.get("/playbook/", response_model=List[PlaybookEntry], dependencies=[Depends(get_api_key)])
async def get_playbook():
    """
    Retrieves all entries from the playbook.
    """
    playbook = Playbook()
    return await playbook.get_all_entries()

@app.post("/run-ace/", response_model=RunAceResponse, dependencies=[Depends(get_api_key)])
async def run_ace(request: RunAceRequest):
    """
    Runs the full ACE pipeline for a given task.

    This endpoint orchestrates the entire ACE process:
    1. Generates a reasoning trajectory for the task.
    2. Reflects on the trajectory to extract insights.
    3. Curates the insights into the playbook.
    """
    await plugin_manager.execute_hook("on_pipeline_start", task=request.task)

    playbook = Playbook()
    llm = get_language_model(settings)
    generator = Generator(llm=llm)
    reflector = Reflector(llm=llm)
    curator = Curator(config=settings)

    await plugin_manager.execute_hook("on_before_generation", playbook=playbook, task=request.task)
    trajectory = await generator.generate_trajectory(playbook, request.task)
    await plugin_manager.execute_hook("on_after_generation", trajectory=trajectory)

    await plugin_manager.execute_hook("on_before_reflection", trajectory=trajectory)
    insights = await reflector.reflect(trajectory)
    await plugin_manager.execute_hook("on_after_reflection", insights=insights)

    await plugin_manager.execute_hook("on_before_curation", insights=insights)
    await curator.curate(playbook, insights)
    await plugin_manager.execute_hook("on_after_curation")

    all_entries = await playbook.get_all_entries()

    await plugin_manager.execute_hook("on_pipeline_end")

    return RunAceResponse(
        new_insights=insights,
        playbook_entries=all_entries,
    )

@app.post("/clusters/run", status_code=202, dependencies=[Depends(get_api_key)])
async def run_clustering_endpoint():
    """
    Triggers the clustering and summarization process in the background.
    """
    llm = get_language_model(settings)
    cluster_manager = ClusterManager(settings, llm)
    asyncio.create_task(cluster_manager.run_clustering())
    return {"message": "Clustering and summarization process started."}

@app.get("/clusters/", response_model=Dict[int, Dict[str, Any]], dependencies=[Depends(get_api_key)])
async def get_clusters_endpoint():
    """
    Retrieves all clusters, their summaries, and their associated entries.
    """
    llm = get_language_model(settings)
    cluster_manager = ClusterManager(settings, llm)
    return await cluster_manager.get_clusters()

from ace.similarity import get_similarity_service

@app.post("/self-heal/", status_code=202, dependencies=[Depends(get_api_key)])
async def run_self_healing_endpoint():
    """
    Triggers the self-healing process in the background.
    """
    llm = get_language_model(settings)
    playbook = Playbook()
    similarity_service = get_similarity_service(settings)
    from ace.self_healing import SelfHealing
    self_healing = SelfHealing(llm, playbook, similarity_service)
    asyncio.create_task(self_healing.analyze_and_correct())
    return {"message": "Self-healing process started."}
