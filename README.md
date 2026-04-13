
# GPT Lab Seinäjoki

** @'
# GPT Lab Seinäjoki Multi-Agent Optimization Demo

This repository is a Chainlit-based demonstration of a multi-agent system for combinatorial optimization tasks.

The project is based on the following research direction:

> This thesis examines how effective optimization algorithms for complex combinatorial optimization problems can be developed using a multi-agent system based on large language models. The work presents a fully automated system in which specialized agents collaborate to interpret user-defined problems, generate optimization code, and iteratively improve solutions through feedback. The system was evaluated on established benchmarks, such as the vehicle routing problem and the cutting stock problem, and was able to produce solutions that achieved optimal or near-optimal results. The findings show that composing the system into separate agents with clear roles is essential for handling complexity and ensuring that the end-to-end code generation process can correct itself. The performance of the system depends strongly on giving the agents precise, problem-specific instructions and enabling smooth cooperation between agents focused on analysis, code generation, execution, and error correction. This approach offers a good alternative to the time-consuming manual design of algorithms and allows domain experts to focus more on defining the problem, rather than writing detailed implementation. This research provides a validated example of how solving optimization tasks can be automated by distributing work between language model-based agents. The results give clear evidence that this approach is effective for tackling challenging computational problems. The contribution is relevant for both industry and academia, as it can help speed up development in operations research and support new applications of artificial intelligence in practice.

## Overview

The application lets a user describe an optimization problem and optionally upload supporting files. A set of specialized agents then:

- interpret the problem and classify it
- decide whether to use a heuristic path or direct code generation
- generate Python code and runtime requirements
- generate Docker files
- execute the generated solution in Docker
- analyze the output
- fix errors when execution fails
- optionally start a new optimization round
- produce a final report selecting the best result from all iterations

This is a demo-oriented research prototype rather than a production-hardened platform. It is best understood as an interactive proof of concept for automated optimization workflows driven by LLM agents.

## Architecture Summary

The application is built around a Chainlit UI and a LangGraph workflow defined in [`main.py`](./main.py).

### Runtime Components

- `Chainlit`
  - provides the web UI, chat session lifecycle, file uploads, and step-by-step visibility into the agents
- `LangGraph`
  - orchestrates the multi-agent workflow as a directed graph
- `OpenAI / Anthropic chat models`
  - provide reasoning, structured output generation, code generation, and repair
- `Docker`
  - runs generated code in an isolated execution environment

### Agents

The workflow currently registers the following agents from [`agents/__init__.py`](./agents/__init__.py):

- `problem_analyzer_agent`
  - analyzes the prompt and uploaded files, classifies the problem, and chooses a solution path
- `code_generator_agent`
  - generates Python code directly for optimization problems
- `heuristic_agent`
  - generates heuristic-based solutions for supported problem classes
- `docker_environment_files_agent`
  - generates a `Dockerfile` and `compose.yaml` for the generated solution
- `start_docker_container_agent`
  - builds and runs the generated solution with Docker
- `code_output_analyzer_agent`
  - interprets the execution output and asks whether another optimization round should start
- `code_fixer_agent`
  - attempts to repair code after execution failures
- `new_loop_agent`
  - performs a new optimization round using previous code and results
- `final_report_agent`
  - chooses the best result across optimization rounds and presents the final answer

### Startup Flow

The actual startup flow is:

1. Chainlit loads `main.py`.
2. `main.py` creates the `generated/` directory if it does not exist.
3. `main.py` imports the agent registry from `agents/__init__.py`.
4. `main.py` builds and compiles a `StateGraph` workflow.
5. On chat start, the app sends a short Finnish greeting message.
6. On each user message:
   - uploaded files are parsed and copied into `generated/`
   - file contents are converted into a `promptFiles` string
   - an `AgentState` object is created
   - the LangGraph workflow is invoked

### Workflow Shape

The current graph in `main.py` is:

1. `problem_analyzer`
2. `heuristic` or `code_generator`
3. `docker_files`
4. `start_docker`
5. if execution fails: `code_fixer`
6. if execution succeeds: `output_analyzer`
7. optional additional optimization via `new_loop`
8. `final_report`

## Supported Input Types

The current Chainlit app explicitly handles the following uploaded file types:

- `.xlsx`
- `.xls`
- `.py`
- `.vrp`

Behavior in the current code:

- Excel files are read into pandas data frames and serialized into JSON-like prompt content.
- Python files are read as source text and included in the prompt.
- VRP files are read line by line and included in the prompt.
- Uploaded files are also copied into the local `generated/` directory.

Other file types are currently rejected in the app with an "unknown file type" message.

## Windows Setup

### Prerequisites

- Windows with PowerShell
- Python installed
- Docker Desktop installed and running
- An OpenAI API key
- Optional: an Anthropic API key

### Recommended Setup Steps

1. Clone the repository.
2. Open the project folder in VS Code or PowerShell.
3. Create a virtual environment:

```powershell
python -m venv .venv
```

4. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

5. Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

6. Install project dependencies:

```powershell
pip install -r requirements.txt
```

7. Make sure Docker Desktop is running before you start the app.

## Environment Variables

The code currently reads the following variables from `.env`:

### Required

- `OPENAI_API_KEY`

### Optional

- `CLAUDE_API_KEY`

Example `.env`:

```env
OPENAI_API_KEY=sk-proj-...
CLAUDE_API_KEY=sk-ant-...
```

Notes:

- The OpenAI key is required for the app to start properly.
- The Anthropic key is optional and only used if present.

## Running the Chainlit App

After activating the virtual environment and setting environment variables:

```powershell
chainlit run main.py -w
```

Then open:

```text
http://localhost:8000
```

## Demo Workflow for GPT Lab Seinäjoki

A practical demo flow for GPT Lab Seinäjoki is:

1. Start the Chainlit app.
2. Open the web UI in the browser.
3. Upload one of the supported input types:
   - an Excel workbook describing an optimization task
   - a Python file
   - a VRP benchmark instance
4. Describe the optimization goal in plain language.
5. Let the `problem_analyzer_agent` classify the problem and propose a path.
6. Confirm whether to continue with the proposed plan.
7. Let the workflow generate code or a heuristic solution.
8. Let the app generate Docker files and execute the solution.
9. Review the execution output and result analysis.
10. Choose whether to start a new optimization round.
11. Let the system produce a final report selecting the best run.

This demo works best when the uploaded data and prompt are specific. The system depends heavily on clear instructions and structured problem context.

## Common Troubleshooting

### `OPENAI_API_KEY` missing or invalid

Symptoms:

- app crashes during startup
- model client initialization fails

Check:

- `.env` exists
- `OPENAI_API_KEY` contains only the key value
- there is no leftover placeholder text

### Chainlit UI text or buttons render strangely

Symptoms:

- labels appear missing
- README button shows incorrectly

Likely cause:

- local Chainlit translation files do not match the installed Chainlit version

Fix:

- remove or back up `.chainlit/translations` so Chainlit falls back to built-in translations

### `docker-compose` command fails

Symptoms:

- Docker build or execution fails immediately

Check:

- Docker Desktop is running
- Docker CLI is available from PowerShell
- your environment still supports the `docker-compose` command used by this codebase

Note:

- the current implementation uses `docker-compose`, not `docker compose`

### Tests fail before running

Symptoms:

- `pytest` fails on startup or with async-related options

Likely cause:

- the test configuration and dependency set are currently fragile

Note:

- this repository includes tests, but they should be treated as experimental and may require maintenance after dependency upgrades

### Generated workflow stalls or behaves inconsistently

Possible causes:

- invalid or underspecified input data
- model output that does not match the expected schema
- Docker execution errors
- dependency drift after upgrading Chainlit, LangChain, or Pydantic

## Experimental / Fragile Areas

This repository is demoable, but some areas should be treated as experimental:

- dependency compatibility is sensitive to Chainlit, LangChain, and Pydantic version changes
- Docker execution relies on local CLI behavior and generated files
- the test suite is not fully robust against recent dependency upgrades
- some UI strings and source files still show encoding issues
- the workflow is designed for demonstration and research, not production reliability

## Repository Structure

```text
.
├── agents/                 # Agent implementations
├── prompts/                # Prompt templates and problem-specific instructions
├── tests/                  # Agent-focused tests
├── .chainlit/              # Chainlit configuration
├── main.py                 # Chainlit entrypoint and LangGraph workflow
├── schemas.py              # Shared Pydantic models and agent state schema
├── requirements.txt        # Python dependencies
└── chainlit.md             # Readme/help panel shown from the Chainlit UI
```

## Honest Status

What is present today:

- a real Chainlit app
- a real LangGraph-controlled multi-agent workflow
- support for multiple uploaded input types
- code generation, Docker execution, repair, and iterative improvement loops

What should be understood as still evolving:

- UI polish
- translation customization
- dependency stability
- test reliability
- Docker execution portability across machines
'@ | Set-Content README.md**

<img src="images/gptlab_sjk_logo.png" alt="GPT Lab Seinäjoki Logo" style="height: 150px; width: auto;">