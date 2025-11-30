# ACE Framework: Current State Inventory

This document provides a detailed inventory of the ACE (Agentic Context Engineering) framework's current state, covering its architecture, data flows, logic, and third-party integrations.

## 1. Architecture

The ACE framework is currently implemented as a **monolithic Python application** built with the **FastAPI** web framework. While monolithic, it is designed with a clear, modular structure that conceptually separates its core components, making it a candidate for a future transition to a microservices architecture as outlined in the `docs/architecture.md` document.

-   **Core Components:**
    -   **Generator:** Generates reasoning trajectories for given tasks.
    -   **Reflector:** Distills insights from reasoning trajectories.
    -   **Curator:** Integrates insights into the playbook, preventing semantic duplication.
    -   **Playbook:** The central, curated knowledge base of the system.
-   **Web Interface:** A FastAPI application provides a RESTful API for interacting with the ACE framework.
-   **Command-Line Interface (CLI):** A CLI provides an alternative interface for running the ACE pipeline.
-   **Plugin System:** A plugin system allows for extending the framework's functionality without modifying the core code.
-   **Containerization:** The application is containerized using Docker and can be deployed with Docker Compose or Kubernetes.

## 2. Data Flows

The primary data flow in the ACE framework follows the **Generate, Reflect, Curate** cycle:

1.  A **task** is submitted to the system via the API or CLI.
2.  The **Generator** retrieves relevant entries from the **Playbook** (SQLite database) and uses them, along with the task, to generate a **reasoning trajectory**.
3.  The **Reflector** takes the trajectory and generates a list of **insights**.
4.  The **Curator** receives the insights, calculates their vector embeddings using the **Similarity Service**, and compares them to existing entries in the **Playbook**.
5.  If an insight is not semantically similar to any existing entry, it is saved to the **Playbook**.

## 3. Logic

The core logic of the ACE framework is implemented in the following modules:

-   `ace/core/generator.py`: Contains the logic for the Generator component.
-   `ace/core/reflector.py`: Contains the logic for the Reflector component.
-   `ace/core/curator.py`: Contains the logic for the Curator component.
-   `ace/similarity.py`: Contains the logic for the Similarity Service, which uses the `sentence-transformers` library to calculate embeddings and cosine similarity.
-   `ace/database.py`: Manages all interactions with the SQLite database using `aiosqlite`.
-   `ace/main.py`: The FastAPI application, which exposes the ACE pipeline through a RESTful API.
-   `ace/cli.py`: The command-line interface.

## 4. Third-Party Integrations

The ACE framework integrates with the following third-party libraries and services:

-   **FastAPI:** For the web interface.
-   **Uvicorn:** As the ASGI server for the FastAPI application.
-   **PyYAML:** For parsing the `config.yaml` file.
-   **aiosqlite:** For asynchronous interactions with the SQLite database.
-   **sentence-transformers:** For calculating vector embeddings.
-   **scikit-learn:** For clustering playbook entries.
-   **OpenAI (optional):** The system is designed to integrate with the OpenAI API for language model interactions, though it currently uses a mock implementation by default.
-   **Docker:** For containerization.
-   **Kubernetes:** The project includes manifest files for deployment to a Kubernetes cluster.

## 5. Paperwork & Compliance Artifacts

The project currently contains the following artifacts that could be considered part of a compliance or documentation package:

-   `README.md`: High-level overview of the project.
-   `docs/architecture.md`: Detailed description of the system's architecture and future vision.
-   `.gitignore`, `.dockerignore`: Standard project exclusion files.
-   `requirements.txt`: A list of all third-party dependencies.
-   `Dockerfile`, `docker-compose.yml`, `k8s/`: Deployment artifacts.

The project **lacks** any formal compliance documentation, such as:

-   Data privacy policies.
-   Security policies.
-   Service level agreements (SLAs).
-   Disaster recovery plans.
-   Formal architectural review documents.
-   Compliance certifications (e.g., SOC 2, ISO 27001).
