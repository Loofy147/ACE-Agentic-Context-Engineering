# ACE Framework Architecture

This document provides a deep dive into the architecture, principles, and concepts of the Agentic Context Engineering (ACE) framework.

## 1. Core Philosophy

The ACE framework is built on a simple yet powerful philosophy: **intelligent systems improve by iteratively refining their context**. This is achieved through a continuous cycle of **Generate, Reflect, and Curate**.

-   **Generate:** Given a task, the system uses its current context (the "playbook") to generate a response or a plan (a "trajectory").
-   **Reflect:** The system analyzes this trajectory to extract key learnings, successful strategies, and potential errors. These are distilled into structured "insights."
-   **Curate:** These insights are then intelligently integrated back into the playbook, enriching the context for future tasks. The Curator ensures the playbook remains coherent, non-redundant, and useful.

This cycle allows the system to learn from its experiences, continuously improving the quality of its context and, therefore, its performance over time.

## 2. Component Deep Dive

The ACE framework is composed of several key components that work together to execute the core philosophy.

### 2.1. The Playbook

The **Playbook** is the heart of the ACE framework. It is not just a simple log or memory; it is a curated, ever-evolving knowledge base.

-   **Concept:** It represents the system's "second brain" or its refined context.
-   **Implementation:** It is a collection of `PlaybookEntry` objects, persistently stored in a SQLite database. Each entry contains a piece of knowledge (the `content`), its vector embedding (for semantic understanding), and arbitrary metadata.
-   **Relation:** It is the primary data source for the `Generator` and the primary target for the `Curator`.

### 2.2. The Generator

The **Generator** is responsible for the "Generate" phase of the cycle.

-   **Concept:** It is the primary "doer" or "actor" in the system.
-   **Implementation:** It takes a task and the current playbook, constructs a detailed prompt, and uses a pluggable `LanguageModel` to generate a reasoning trajectory.
-   **Relation:** It reads from the `Playbook` and uses the `LanguageModel` interface.

### 2.3. The Reflector

The **Reflector** handles the "Reflect" phase.

-   **Concept:** It is the "analyzer" or "learner" of the system.
-   **Implementation:** It takes the trajectory produced by the Generator and uses a `LanguageModel` to analyze it. It extracts key learnings and structures them as a list of "insights" (dictionaries with `content` and `metadata`).
-   **Relation:** It processes the output of the `Generator` and provides the input for the `Curator`.

### 2.4. The Curator & Similarity Service

The **Curator** and its companion, the **Similarity Service**, are responsible for the crucial "Curate" phase.

-   **Concept:** The Curator is the "gatekeeper" or "librarian" of the playbook, ensuring its quality.
-   **Implementation:** The Curator receives insights from the Reflector. For each insight, it uses the `SimilarityService` to calculate a vector embedding. The `SimilarityService` then compares this embedding to the embeddings of all existing entries in the playbook.
-   **Curation Rule:** The Curator will only add the new insight if it is not semantically similar to any existing entry, based on a configurable cosine similarity threshold. This prevents conceptual redundancy.
-   **Relation:** The Curator writes to the `Playbook` (via the database layer) after consulting the `SimilarityService`.

## 3. Integration Rules and Concepts

The components are tied together by a set of well-defined integration points and rules.

### 3.1. Database Integration

-   **Rule:** All persistent state is stored in the SQLite database.
-   **Concept:** The `ace/database.py` module provides a single, asynchronous interface for all database operations. Core components should not interact with the database directly, but rather through the `Playbook` model where appropriate.

### 3.2. Language Model Integration

-   **Rule:** All interactions with language models must go through the `LanguageModel` interface defined in `ace/llm/base.py`.
-   **Concept:** This defines a pluggable architecture. The specific LLM to be used (e.g., `mock`, `openai`) is determined by the `config.yaml` file. The `get_language_model` factory function handles the dynamic loading of the correct model.

### 3.3. Plugin System

-   **Rule:** The core pipeline logic triggers asynchronous "hooks" at key stages (e.g., `on_pipeline_start`, `on_after_generation`).
-   **Concept:** This allows for the extension of the framework's functionality without modifying the core code. The `PluginManager` automatically discovers and registers any plugins placed in the `ace/plugins/` directory, executing their implemented hooks.

## 4. Future Vision: Microservices Architecture

While the current implementation is a monolithic application, its modular design and asynchronous nature make it a prime candidate for decomposition into a microservices architecture. This would provide significant benefits in terms of scalability, resilience, and independent deployability.

### 4.1. Conceptual Services

The ACE framework could be broken down into the following conceptual microservices:

-   **Playbook Service:**
    -   **Responsibility:** Owns the playbook database. Manages all CRUD operations for playbook entries.
    -   **API:** Exposes endpoints like `GET /entries`, `POST /entries`, `GET /entries/{id}`.
    -   **Technology:** A simple, robust web framework (like FastAPI) connected to a scalable database (e.g., PostgreSQL, a vector database like Weaviate or Pinecone).

-   **Generation Service:**
    -   **Responsibility:** Handles the "Generate" phase. Interacts with a language model to create trajectories.
    -   **API:** Exposes an endpoint like `POST /generate` that takes a task and playbook context.
    -   **Technology:** A Python service that can manage a pool of connections to a powerful, scaled-out language model (e.g., via OpenAI, an open-source model hosted on a GPU cluster).

-   **Reflection Service:**
    -   **Responsibility:** Handles the "Reflect" phase. Interacts with a language model to extract insights.
    -   **API:** Exposes an endpoint like `POST /reflect` that takes a trajectory.
    -   **Technology:** Similar to the Generation Service, but could be scaled independently based on the complexity of the reflection task.

-   **Similarity Service:**
    -   **Responsibility:** A specialized, computationally-focused service for calculating and comparing vector embeddings.
    -   **API:** Exposes endpoints like `POST /embedding` and `POST /similarity-check`.
    -   **Technology:** A Python service with direct access to NLP models (like `sentence-transformers`), potentially running on specialized hardware (GPUs).

-   **Curation Service:**
    -   **Responsibility:** Orchestrates the "Curate" phase. It is the intelligent gatekeeper.
    -   **API:** Receives insights (perhaps via a message queue) and decides whether to add them to the playbook.
    -   **Technology:** A service that interacts with the `Similarity Service` and the `Playbook Service` to enforce curation rules.

### 4.2. Communication and Data Flow

In this architecture, services would communicate via a combination of synchronous RESTful API calls for direct requests and asynchronous messaging (e.g., using RabbitMQ or Kafka) for event-driven workflows. For example, a new insight could be published to a message queue, which the Curation Service would then consume and process.
