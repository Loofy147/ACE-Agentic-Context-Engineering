# ACE: Agentic Context Engineering

This project is a Python implementation of the Agentic Context Engineering (ACE) framework, a novel approach to building self-improving language model systems.

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
- [x] **Deduplication**: The Curator prevents duplicate entries in the playbook.
- [x] **Command-Line Interface**: A CLI for interacting with the ACE pipeline.
- [x] **Unit Tests**: A suite of tests to ensure the robustness of the components.
- [x] **Professional Project Structure**: The project is organized as a proper Python package.

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

### Command-Line Interface

The CLI provides a simple way to run the ACE pipeline with a given task.

```bash
python ace/cli.py "Your task here"
```

If no task is provided, the CLI will use the `default_task` from the `config.yaml` file.

### As a Library

The ACE components can also be used as a library in your own Python projects.

```python
from ace.core.models import Playbook
from ace.core.generator import Generator
from ace.core.reflector import Reflector
from ace.core.curator import Curator
import yaml

# Load the configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize components
playbook = Playbook()
generator = Generator(model=None, config=config)
reflector = Reflector(model=None, config=config)
curator = Curator()

# Run the pipeline
task = "Your task here"
trajectory = generator.generate_trajectory(playbook, task)
insights = reflector.reflect(trajectory)
curator.curate(playbook, insights)

# Print the updated playbook
for entry in playbook.entries:
    print(f"- {entry.content}")
```

## Next Steps: High-Tech Level

This section outlines a high-level roadmap for the future development of the ACE framework.

### Phase 1: Core Enhancements

- [ ] **Integrate a Real Language Model**: Replace the mock model with a real language model (e.g., GPT, Llama).
- [ ] **Persistent Storage**: Implement a database (e.g., SQLite, PostgreSQL) to store the playbook.
- [ ] **Asynchronous Operations**: Refactor the pipeline to use asynchronous operations for improved performance.

### Phase 2: Advanced Features

- [ ] **Web Interface**: Build a web interface (e.g., using Flask or FastAPI) to interact with the ACE framework.
- [ ] **Plugin Architecture**: Develop a plugin architecture to allow for custom components and extensions.
- [ ] **Advanced Curation Strategies**: Implement more sophisticated curation strategies, such as clustering and summarization.

### Phase 3: Deployment and Scaling

- [ ] **Containerization**: Package the application using Docker for easy deployment.
- [ ] **Cloud Deployment**: Deploy the ACE framework to a cloud platform (e.g., AWS, GCP, Azure).
- [ ] **Scalability**: Implement a distributed architecture to handle large-scale workloads.
