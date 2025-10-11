from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

from ace import database
from ace.core.models import Playbook, PlaybookEntry
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace.llm import get_language_model
from ace.plugins.manager import plugin_manager
import yaml

app = FastAPI(
    title="ACE Framework API",
    description="An API for interacting with the Agentic Context Engineering (ACE) framework.",
    version="1.0.0",
)

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

@app.get("/playbook/", response_model=List[PlaybookEntry])
async def get_playbook():
    """Retrieves all entries from the playbook."""
    playbook = Playbook()
    return await playbook.get_all_entries()

@app.post("/run-ace/", response_model=RunAceResponse)
async def run_ace(request: RunAceRequest):
    """Runs the full ACE pipeline for a given task."""
    await plugin_manager.execute_hook("on_pipeline_start", task=request.task)

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    playbook = Playbook()
    llm = get_language_model(config)
    generator = Generator(llm=llm)
    reflector = Reflector(llm=llm)
    curator = Curator()

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
