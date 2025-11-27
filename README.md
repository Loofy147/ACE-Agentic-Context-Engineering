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
- [x] **Self-Healing**: A mechanism to automatically detect and correct outdated or incorrect entries in the playbook.

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

## Self-Healing

The ACE framework includes a self-healing mechanism that automatically reviews and corrects playbook entries to ensure they remain accurate and relevant over time. This process is handled by the `SelfHealing` component, which can be triggered via an API endpoint.

### Triggering Self-Healing

To start the self-healing process, you can send a POST request to the `/self-heal/` endpoint. This will initiate a background task that analyzes and corrects the playbook entries.

```bash
curl -X POST "http://127.0.0.1:8000/self-heal/" -H "X-API-Key: your-api-key"
```

## API Reference

The ACE framework provides a RESTful API for interacting with the system.

### Authentication

All API endpoints are protected with an API key. You must include your API key in the `X-API-Key` header of your requests.

### Endpoints

- **`GET /`**: A simple root endpoint to confirm the API is running.
- **`GET /playbook/`**: Retrieves all entries from the playbook.
- **`POST /run-ace/`**: Runs the full ACE pipeline for a given task.
  - **Request Body**: `{"task": "Your task here"}`
  - **Response Body**: `{"new_insights": [...], "playbook_entries": [...]}`
- **`POST /clusters/run`**: Triggers the clustering and summarization process.
- **`GET /clusters/`**: Retrieves all clusters, their summaries, and their entries.
- **`POST /self-heal/`**: Triggers the self-healing process.

## Next Steps: High-Tech Level

This section outlines a high-level roadmap for the future development of the ACE framework.

### Phase 1: Core Enhancements

- [x] **Integrate a Real Language Model**: A pluggable architecture is in place.
- [x] **Persistent Storage**: Implemented with SQLite.
- [x] **Asynchronous Operations**: The framework is now fully asynchronous.

### Phase 2: Advanced Features

- [x] **Web Interface**: A basic FastAPI is implemented. Further enhancements can be added.
- [x] **Plugin Architecture**: A flexible plugin system has been implemented.
- [ ] **Advanced Curation Strategies**:
    - [x] Semantic Deduplication
    - [ ] Clustering and Summarization (In Progress)

### Phase 3: Deployment and Scaling

- [x] **Containerization**: The application is containerized with Docker.
- [x] **Cloud Deployment**: The application is ready for Kubernetes deployment.
- [ ] **Scalability**: Implement a distributed architecture to handle large-scale workloads.

## Deployment with Docker

This project is configured to run with Docker and Docker Compose for easy and consistent deployment.

### Prerequisites

-   Docker
-   Docker Compose

### Running the Application

1.  **Build and Run the Container:**

    Use Docker Compose to build the image and run the container in detached mode:

    ```bash
    docker-compose up --build -d
    ```

2.  **Accessing the API:**

    The API will be available at `http://127.0.0.1:8000`.

3.  **Stopping the Application:**

    To stop the running services, use:

    ```bash
    docker-compose down
    ```

## Deployment with Kubernetes

The `k8s/` directory contains manifest files to deploy the ACE framework to a Kubernetes cluster.

### Prerequisites

-   A running Kubernetes cluster (e.g., Minikube, Docker Desktop, or a cloud provider's managed Kubernetes service).
-   `kubectl` configured to connect to your cluster.

### Running the Application

1.  **Update the Image Path:**

    Before you deploy, you must update the `image` field in `k8s/deployment.yaml` to point to the location where you have pushed your ACE Docker image.

    ```yaml
    # in k8s/deployment.yaml
    image: your-docker-registry/ace-framework:latest
    ```

2.  **Apply the Manifests:**

    Apply the deployment and service configurations to your cluster:

    ```bash
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    ```

3.  **Accessing the Service:**

    It may take a few minutes for the cloud provider to provision the LoadBalancer. You can check the status by running:

    ```bash
    kubectl get service ace-service
    ```

    Once the `EXTERNAL-IP` is available, you can access the API at that IP address on port 80.
