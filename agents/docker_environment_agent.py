from prompts.prompts import (
    DOCKER_FILES_PROMPT,
)
from schemas import AgentState, DockerFiles
<<<<<<< HEAD
from .common import cl, PydanticOutputParser, llm, GENERATED_DIR, get_generated_path


def sanitize_compose_yaml(compose_text: str) -> str:
    """Remove obsolete version keys from generated Docker Compose YAML."""
    lines = compose_text.splitlines()
    sanitized_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("version:"):
            continue
        sanitized_lines.append(line)
    # Remove leading blank lines if present
    while sanitized_lines and sanitized_lines[0].strip() == "":
        sanitized_lines.pop(0)
    return "\n".join(sanitized_lines).rstrip() + "\n"
=======
from .common import cl, PydanticOutputParser, llm
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc


# Docker environment setup agent
# Generates necessary Docker files based on the generated code
@cl.step(name="Docker Environment Files Agent")
async def docker_environment_files_agent(state: AgentState):
    print("*** DOCKER ENVIRONMENT AGENT ***")
    current_step = cl.context.current_step
    inputs = state["code"]

    # Prepare the prompt
    prompt = DOCKER_FILES_PROMPT.format(
        python_code=inputs.python_code,
        requirements=inputs.requirements,
        resources=inputs.resources,
    )

    # Display input in the Chainlit interface
    current_step.input = (
        f"Generating Docker environment files based on the following inputs:\n\n"
        f"Python Code:\n```python\n{inputs.python_code}\n```\n"
        f"Requirements:\n```\n{inputs.requirements}\n```\n"
        f"Resources: {inputs.resources}"
    )

    # Set up the output parser
    output_parser = PydanticOutputParser(pydantic_object=DockerFiles)
    format_instructions = output_parser.get_format_instructions()

    # Append format instructions to the prompt
    prompt += f"\n\n{format_instructions}"

    # Collect the full response while streaming
    full_response = ""

    # Stream the response from the LLM
    try:
        async for chunk in llm.astream(prompt):
            if hasattr(chunk, "content"):
                await current_step.stream_token(chunk.content)
                full_response += chunk.content
    except Exception as e:
        await cl.Message(content=f"Error during Docker files generation: {e}").send()
        return state

    # Parse the full response
    try:
        response = output_parser.parse(full_response)
    except Exception as e:
        await cl.Message(content=f"Error parsing Docker files response: {e}").send()
        return state

<<<<<<< HEAD
    state["dockerFiles"] = response

    # Save the Dockerfile and Compose file
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    with open(get_generated_path("Dockerfile"), "w", encoding="utf-8") as f:
        f.write(response.dockerfile)

    compose_content = sanitize_compose_yaml(response.compose_file)
    with open(get_generated_path("compose.yaml"), "w", encoding="utf-8") as f:
        f.write(compose_content)
=======
    state["docker_files"] = response

    # Save the Dockerfile and Compose file
    with open("generated/Dockerfile", "w", encoding="utf-8") as f:
        f.write(response.dockerfile)

    with open("generated/compose.yaml", "w", encoding="utf-8") as f:
        f.write(response.compose_file)
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc

    return state
