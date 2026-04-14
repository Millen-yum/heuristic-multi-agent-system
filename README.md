# Heuristic Multi-Agent System

A Chainlit-based demo showing how a multi-agent system uses large language models to solve combinatorial optimization problems.

## Overview

This project is built from a research direction in which specialized agents collaborate to solve optimization tasks. The system aims to automate the steps of problem understanding, solution generation, code execution, troubleshooting, and iterative improvement.

The main idea is:

- break the optimization workflow into focused agent roles
- use LLMs to interpret input data and user goals
- generate and run code automatically inside Docker
- repair the code when execution fails
- select and report the best result

This repository is a prototype for research and demonstration, not a production product.

## Key Features

- Interactive web UI powered by Chainlit
- Directed multi-agent workflow orchestrated by LangGraph
- Automatic code generation and repair
- Docker-based execution for generated solutions
- Support for uploading Excel, Python, and VRP input files
- Iterative optimization loops with final result selection

## Architecture

The workflow is defined in `main.py`.

### Core components

- `Chainlit`
  - runs the chat UI, handles user messages, and manages file uploads
- `LangGraph`
  - defines the step-by-step agent workflow as a graph
- `OpenAI / Anthropic` models
  - provide reasoning, code generation, and repair capabilities
- `Docker`
  - executes generated code in an isolated container environment

### Agents

The current system uses the following agents:

- `problem_analyzer_agent`
  - reads the prompt and uploaded input, classifies the task, and chooses the solution path
- `code_generator_agent`
  - writes Python code for direct optimization when the problem is suitable
- `heuristic_agent`
  - creates heuristic solutions for supported problem classes
- `docker_environment_files_agent`
  - generates Docker deployment assets such as `Dockerfile` and `compose.yaml`
- `start_docker_container_agent`
  - builds and launches the generated Docker environment
- `code_output_analyzer_agent`
  - analyzes execution output and decides whether to continue or rerun
- `code_fixer_agent`
  - repairs code when execution fails
- `new_loop_agent`
  - starts a new optimization cycle using previous results
- `final_report_agent`
  - selects the best final result and summarizes it for the user

### Workflow order

The app follows this ordered flow:

1. User submits a text prompt and optionally uploads input files
2. `problem_analyzer_agent` selects the best path
3. Either `heuristic_agent` or `code_generator_agent` produces a solution
4. `docker_environment_files_agent` creates Docker files
5. `start_docker_container_agent` runs the generated solution
6. If execution fails, `code_fixer_agent` attempts to repair
7. `code_output_analyzer_agent` reviews results
8. Optional `new_loop_agent` runs another iteration
9. `final_report_agent` returns the best output

## Supported Inputs

This project currently supports the following upload types:

- `.xlsx`
- `.xls`
- `.py`
- `.vrp`

Behavior:

- Excel files are parsed into structured prompt data
- Python files are included as source context
- VRP files are included as text input
- Uploaded files are copied into `generated/`

## Installation

### Prerequisites

- Windows with PowerShell
- Python 3.x
- Docker Desktop installed and running
- An OpenAI API key
- Optional: an Anthropic API key

### Install steps

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file with the values required by the app.

Required:

```env
OPENAI_API_KEY=sk-...
```

Optional:

```env
CLAUDE_API_KEY=sk-...
```

Notes:

- `OPENAI_API_KEY` is required for the app to work.
- `CLAUDE_API_KEY` is optional and only used if available.

## Windows Setup

1. Install Python and Docker Desktop.
2. Open PowerShell in the project directory.
3. Create and activate the virtual environment.
4. Install dependencies from `requirements.txt`.
5. Confirm Docker Desktop is running before starting the app.

## Running the App

Start the Chainlit app with:

```powershell
chainlit run main.py -w
```

Then open the app in your browser at:

```text
http://localhost:8000
```

If port `8000` is in use, run on a different port:

```powershell
chainlit run main.py --port 8001
```

## Demo Instructions

A clear demo order is:

1. Start the Chainlit app.
2. Open the browser UI.
3. Upload one supported input file (`.xlsx`, `.xls`, `.py`, `.vrp`).
4. Enter a clear optimization goal in the chat prompt.
5. Let `problem_analyzer_agent` classify the task and choose a path.
6. Review the chosen path and continue if it looks correct.
7. Watch the system generate Docker files and run the solution.
8. Observe the execution output and analysis.
9. If needed, allow the app to repair code or run a new optimization round.
10. Review the final report and selected best result.

## Common Troubleshooting / Known Issues

### Invalid or missing API key

- App fails to start without `OPENAI_API_KEY`.
- Check that `.env` exists and the key is correct.

### Upload problems

- Only `.xlsx`, `.xls`, `.py`, and `.vrp` files are accepted.
- If upload fails, refresh the UI and retry.
- Verify `.chainlit/config.toml` MIME settings if the browser rejects the file.

### Docker issues

- Ensure Docker Desktop is running.
- Confirm the Docker CLI works in PowerShell.
- The current code uses `docker-compose`, so Docker Desktop must support that command.

### Port conflicts

- If port `8000` is busy, start the app on another port.

### Experimental limitations

- The workflow is a prototype and may not handle every input reliably.
- Model output can be unpredictable and may require manual retry.
- Generated code repair is not guaranteed for all failures.

## Repository Structure

```text
.
├── agents/                 # Agent implementations
├── generated/              # Generated code and Docker files
├── prompts/                # Prompt templates and instructions
├── tests/                  # Agent tests
├── .chainlit/              # Chainlit configuration
├── main.py                 # Chainlit app entrypoint and workflow definition
├── schemas.py              # Shared Pydantic models and state schemas
├── requirements.txt        # Python dependencies
└── chainlit.md             # Chainlit help panel content
```

## Recommended start order

1. Read the Overview and Architecture sections to understand the workflow.
2. Install dependencies and configure `.env`.
3. Start Docker Desktop.
4. Run `chainlit run main.py -w`.
5. Upload input and provide a clear optimization prompt.
6. Follow the app’s generated workflow through solution generation, execution, and reporting.
