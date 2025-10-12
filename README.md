# ACE: Agentic Context Engineering

This project is a Python implementation of the Agentic Context Engineering (ACE) framework, a novel approach to building self-improving language model systems.

For a deep dive into the principles, concepts, and future vision of the framework, please see the [**Architecture Document**](docs/architecture.md).

## Overview

ACE treats contexts as evolving "playbooks" that accumulate, refine, and organize strategies through a modular process of generation, reflection, and curation. This implementation provides a professional, configurable, and extensible scaffold for the ACE framework.

The core components are:
- **Generator**: Generates reasoning trajectories for given tasks.
- **Reflector**: Distills insights from reasoning trajectories.
- **Curator**: Integrates insights into the playbook.

## Features Checklist

- [x] **Modular Architecture**: Separate components for Generation, Reflection, and Curation.
- [x] **Configuration-Driven**: System behavior is controlled by a `config.yaml` file.
- [x] **Extensible Data Models**: `Playbook` and `PlaybookEntry` classes can be extended.
- [x] **Advanced Curation**: The Curator uses semantic similarity to prevent conceptually similar insights from being added.
- [x] **Command-Line Interface**: A CLI for interacting with the ACE pipeline.
- [x] **Unit Tests**: A suite of tests to ensure the robustness of the components.
- [x] **Professional Project Structure**: The project is organized as a proper Python package.
- [x] **Persistent Storage**: The playbook is stored in a SQLite database.
- [x] **Asynchronous Operations**: The entire pipeline is built with `asyncio` for performance.
- [x] **Pluggable Language Models**: A modular architecture for swapping language models.

## Getting Started

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

The ACE framework is configured through the `config.yaml` file. This file allows you to define the mock responses for the `Generator` and `Reflector`, as well as settings for the CLI.

## Usage

### Web Interface (API)

The project includes a FastAPI web interface to interact with the ACE framework.

**Running the Web Server:**

1.  Make sure you have installed the dependencies from `requirements.txt`.
2.  Run the Uvicorn server from the project root:

    ```bash
    uvicorn ace.main:app --reload
    ```
3.  The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

### Command-Line Interface

The CLI provides a simple way to run the ACE pipeline with a given task.

```bash
python ace/cli.py "Your task here"
```

If no task is provided, the CLI will use the `default_task` from the `config.yaml` file.

### As a Library

The ACE components can also be used as a library in your own Python projects.

```python
import asyncio
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
from ace.llm import get_language_model
import yaml

async def run_ace_as_library():
    # Load the configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Initialize components
    playbook = Playbook()
    llm = get_language_model(config)
    generator = Generator(llm=llm)
    reflector = Reflector(llm=llm)
    curator = Curator()

    # Run the pipeline
    task = "Your task here"
    trajectory = await generator.generate_trajectory(playbook, task)
    insights = await reflector.reflect(trajectory)
    await curator.curate(playbook, insights)

    # Print the updated playbook
    for entry in await playbook.get_all_entries():
        print(f"- {entry.content}")

if __name__ == "__main__":
    asyncio.run(run_ace_as_library())
```

## Plugins

The ACE framework includes a plugin system that allows you to extend its functionality without modifying the core code. Plugins can hook into various stages of the ACE pipeline to add logging, modify data, or trigger external events.

### Creating a Plugin

1.  Create a new Python file in the `ace/plugins/` directory.
2.  Define a class that inherits from `ace.plugins.base.Plugin`.
3.  Implement any of the asynchronous hook methods defined in the `Plugin` base class.

The `PluginManager` will automatically discover and register any valid plugin classes in the `ace/plugins/` directory.

### Example Plugin

The `ace/plugins/logging_plugin.py` provides a simple example of a plugin that logs each stage of the pipeline.

## Next Steps: High-Tech Level

This section outlines a high-level roadmap for the future development of the ACE framework.

### Phase 1: Core Enhancements

- [x] **Integrate a Real Language Model**: A pluggable architecture is in place.
- [x] **Persistent Storage**: Implemented with SQLite.
- [x] **Asynchronous Operations**: The framework is now fully asynchronous.

### Phase 2: Advanced Features

- [x] **Web Interface**: A basic FastAPI is implemented. Further enhancements can be added.
- [x] **Plugin Architecture**: A flexible plugin system has been implemented.
- [ ] **Advanced Curation Strategies**: Implement more sophisticated curation strategies, such as clustering and summarization.

### Phase 3: Deployment and Scaling

- [ ] **Containerization**: Package the application using Docker for easy deployment.
- [ ] **Cloud Deployment**: Deploy the ACE framework to a cloud platform (e.g., AWS, GCP, Azure).
- [ ] **Scalability**: Implement a distributed architecture to handle large-scale workloads.
