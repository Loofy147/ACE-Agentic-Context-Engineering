# ACE: Agentic Context Engineering

This project is a Python implementation of the Agentic Context Engineering (ACE) framework, a novel approach to building self-improving language model systems.

## Overview

ACE treats contexts as evolving "playbooks" that accumulate, refine, and organize strategies through a modular process of generation, reflection, and curation. This implementation provides the core components of the ACE framework:

- **Generator**: Generates reasoning trajectories for given tasks.
- **Reflector**: Distills insights from reasoning trajectories.
- **Curator**: Integrates insights into the playbook.

## Directory Structure

- `ace/core/`: Contains the core components of the ACE framework (Generator, Reflector, Curator, and data models).
- `ace/tests/`: Contains tests for the ACE components.
- `ace/docs/`: Contains documentation for the project.

## How to Use

To use the ACE pipeline, you will need to:

1.  Initialize the core components (Generator, Reflector, Curator).
2.  Create a `Playbook` object.
3.  Run the generation, reflection, and curation cycle to evolve the playbook.

See `ace/tests/test_ace_pipeline.py` for a complete example.
