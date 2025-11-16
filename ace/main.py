from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict

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
    """Dependency to validate the API key."""
    if api_key not in settings["security"]["api_keys"]:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


class RunAceRequest(BaseModel):
    task: str

class RunAceResponse(BaseModel):
    new_insights: List[Dict]
    playbook_entries: List[PlaybookEntry]

@app.on_event("startup")
async def startup_event():
    """Initializes the database when the application starts."""
    await database.initialize_database()

@app.get("/")
async def root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the ACE Framework API!"}

@app.get("/playbook/", response_model=List[PlaybookEntry], dependencies=[Depends(get_api_key)])
async def get_playbook():
    """Retrieves all entries from the playbook."""
    playbook = Playbook()
    return await playbook.get_all_entries()

@app.post("/run-ace/", response_model=RunAceResponse, dependencies=[Depends(get_api_key)])
async def run_ace(request: RunAceRequest):
    """Runs the full ACE pipeline for a given task."""
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
    """Triggers the clustering and summarization process."""
    llm = get_language_model(settings)
    cluster_manager = ClusterManager(settings, llm)
    asyncio.create_task(cluster_manager.run_clustering())
    return {"message": "Clustering and summarization process started."}

@app.get("/clusters/", response_model=Dict[int, Dict], dependencies=[Depends(get_api_key)])
async def get_clusters_endpoint():
    """Retrieves all clusters, their summaries, and their entries."""
    llm = get_language_model(settings)
    cluster_manager = ClusterManager(settings, llm)
    return await cluster_manager.get_clusters()
