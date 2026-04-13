<<<<<<< HEAD
import json
import re
from .common import cl, PydanticOutputParser, llm_code, llm_code_claude, GENERATED_DIR, get_generated_path
=======
from .common import cl, PydanticOutputParser, llm_code, llm_code_claude
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc
from schemas import AgentState, Code, CodeFix
from prompts.prompts import CODE_FIXER_PROMPT


<<<<<<< HEAD
def _extract_json_object(text: str) -> str | None:
    """Try to recover a JSON object from the model response."""
    # Remove markdown fences and code blocks
    cleaned = re.sub(r"```(?:json|python)?\n", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n```", "", cleaned)

    # Scan for the first balanced JSON object
    start = cleaned.find("{")
    if start == -1:
        return None

    depth = 0
    for index, char in enumerate(cleaned[start:], start=start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = cleaned[start : index + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue
    return None


def _contains_chainlit_artifacts(code_text: str) -> bool:
    patterns = [
        r"\bimport\s+chainlit\b",
        r"\bfrom\s+chainlit\b",
        r"\bcl\.run\b",
        r"\bcl\.App\b",
        r"@cl\.on_message\b",
        r"@cl\.step\b",
    ]
    return any(re.search(pattern, code_text) for pattern in patterns)


=======
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc
# Code is split into two functions to allow for easier testing
async def fix_code_logic(code: Code, docker_output: str) -> Code:
    """
    Core logic to fix code using the LLM.

    Parameters:
    - code: Code object containing the code to be fixed.
    - docker_output: The error message from the docker execution.

    Returns:
    - A new Code object with the fixed code.
    """
    prompt = CODE_FIXER_PROMPT.format(
        code=code.python_code,
        requirements=code.requirements,
        resources=code.resources,
        docker_output=docker_output,
    )

    output_parser = PydanticOutputParser(pydantic_object=CodeFix)
    format_instructions = output_parser.get_format_instructions()
    prompt += f"\n\n{format_instructions}"

    full_response = ""

    # Interact with the LLM
    try:
        async for chunk in llm_code.astream(prompt):
            if hasattr(chunk, "content"):
                full_response += chunk.content
    except Exception as e:
        raise RuntimeError(f"Error during code generation: {e}")

    # Parse the LLM's response
    try:
        response = output_parser.parse(full_response)
    except Exception as e:
<<<<<<< HEAD
        # If the response contains extra text or markdown, try to recover the JSON payload.
        extracted_json = _extract_json_object(full_response)
        if extracted_json is not None:
            try:
                response = output_parser.parse(extracted_json)
            except Exception as inner_e:
                raise ValueError(
                    f"Error parsing code response after extracting JSON: {inner_e}. "
                    f"Raw response: {full_response[:1000]}"
                )
        else:
            raise ValueError(
                f"Error parsing code response: {e}. Raw response: {full_response[:1000]}"
            )
=======
        raise ValueError(f"Error parsing code response: {e}")
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc

    return response


@cl.step(name="Code Fixer Agent")
async def code_fixer_agent(state: AgentState):
    print("*** CODE FIXER AGENT ***")

    current_step = cl.context.current_step

    code = state["code"]
    docker_output = state["docker_output"]

    current_step.input = (
        "Fixing the code based on the error encountered during execution."
    )
    print("Fixing step input:", docker_output)

    try:
        # Call the core logic function
        print("CALLING the fix_code_logic")
        response = await fix_code_logic(code, docker_output)
    except Exception as e:
        await cl.Message(content=str(e)).send()
        return state

    # Convert CodeFix back to Code
    updated_code = Code(
        python_code=response.fixed_python_code,
        requirements=response.requirements,
        resources=code.resources,  # Keep resources the same if they were not modified
    )

<<<<<<< HEAD
    if _contains_chainlit_artifacts(updated_code.python_code):
        await cl.Message(
            content=(
                "Fixed code includes Chainlit or web framework artifacts, which are not allowed in the Docker executable. "
                "Please regenerate without Chainlit imports or app definitions."
            )
        ).send()
        raise RuntimeError("Fixed code contains forbidden Chainlit artifacts.")

=======
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc
    state["code"] = updated_code

    # Save the generated code to a Python file
    def clean_text(text):
        return text.encode("utf-8", "replace").decode("utf-8")

<<<<<<< HEAD
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    with open(get_generated_path("generated.py"), "w", encoding="utf-8") as f:
=======
    with open("generated/generated.py", "w", encoding="utf-8") as f:
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc
        f.write(clean_text(updated_code.python_code))

    # If requirements have changed, save to requirements.txt
    if response.requirements_changed:
<<<<<<< HEAD
        with open(get_generated_path("requirements.txt"), "w", encoding="utf-8") as f:
=======
        with open("generated/requirements.txt", "w", encoding="utf-8") as f:
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc
            f.write(response.requirements)
            
    state["fixIterations"] = state.get("fixIterations", 0) + 1
            
    current_step.output = response.fixed_python_code

    return state
