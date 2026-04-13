from .common import cl, PydanticOutputParser, llm_code, llm_code_claude
from schemas import AgentState, Code, SolutionMethod, ProblemClass
from prompts.prompts import (
    NEW_LOOP_CODE_PROMPT,
    NEW_LOOP_CODE_PROMPT_NO_DATA,
    NEW_LOOP_HEURISTIC_PROMPT,
)
from prompts.instuctions import *


async def new_loop_logic(state: AgentState) -> Code:
    inputs = state["purpose"]
    last_code = state["code"]
    last_output = state["result"]
    # Nollaa korjauslaskuri
    state["fixIterations"] = 0
    state["optimizedOnce"] = True

    problem_type = inputs.problem_class

    problem_guidance_map = {
        ProblemClass.CUTTING_STOCK: CUTTING_STOCK,
        ProblemClass.VRP: VRP,
        ProblemClass.KNAPSACK: KNAPSACK,
        ProblemClass.SHIFT_SCHEDULING: SHIFT_SCHEDULING,
        ProblemClass.WAREHOUSE_OPTIMIZATION: WAREHOUSE_OPTIMIZATION,
        ProblemClass.OTHER: OTHER,
    }

    def get_guidance(problem_type: ProblemClass) -> dict:
        return problem_guidance_map.get(problem_type, OTHER)

    guidance = get_guidance(problem_type)

    # Select the appropriate prompt based on the solution method
    if state["solution_method"] == SolutionMethod.HEURISTIC:
        prompt = NEW_LOOP_HEURISTIC_PROMPT.format(
            user_summary=inputs.user_summary,
            goal=inputs.goal,
            problem_type=inputs.problem_type,
            optimization_focus=inputs.optimization_focus,
            data=state["promptFiles"],
            previous_results=last_output.answer_description,
            previous_code=last_code.python_code,
            resource_requirements=inputs.resource_requirements,
            response_format=inputs.response_format,
            problem_specific_guidelines=guidance["guidelines"],
            problem_specific_example=guidance["example"],
        )
    else:
        if state["promptFiles"] == "":
            prompt = NEW_LOOP_CODE_PROMPT_NO_DATA.format(
                user_summary=inputs.user_summary,
                goal=inputs.goal,
                problem_type=inputs.problem_type,
                optimization_focus=inputs.optimization_focus,
                previous_results=last_output.answer_description,
                previous_code=last_code.python_code,
                resource_requirements=inputs.resource_requirements,
            )
        else:
            prompt = NEW_LOOP_CODE_PROMPT.format(
                user_summary=inputs.user_summary,
                goal=inputs.goal,
                problem_type=inputs.problem_type,
                optimization_focus=inputs.optimization_focus,
                data=state["promptFiles"],
                previous_results=last_output.answer_description,
                previous_code=last_code.python_code,
                resource_requirements=inputs.resource_requirements,
            )

    output_parser = PydanticOutputParser(pydantic_object=Code)
    format_instructions = output_parser.get_format_instructions()

    # Append format instructions to the prompt
    prompt += f"\n\n{format_instructions}"

    # Collect the full response from the LLM
    full_response = ""
    try:
        async for chunk in llm_code.astream(prompt):
            if hasattr(chunk, "content"):
                full_response += chunk.content
    except Exception as e:
        raise RuntimeError(f"Error during new optimization round: {e}")

    # Clean and parse the full response
    def clean_text(text):
        return text.encode("utf-8", "replace").decode("utf-8")

    cleaned_response = clean_text(full_response)

    try:
        response = output_parser.parse(cleaned_response)
    except Exception as e:
        raise ValueError(f"Error parsing new code response: {e}")

    return response  # Return the parsed response as Code


@cl.step(name="New Loop Agent")
async def new_loop_agent(state: AgentState) -> AgentState:
    print("*** NEW LOOP AGENT ***")
    current_step = cl.context.current_step
    inputs = state["purpose"]
    last_code = state["code"]
    last_output = state["result"]

    # Display input in the Chainlit interface
    current_step.input = (
        f"Starting a new optimization round with the following inputs:\n\n"
        f"User Summary: {inputs.user_summary}\n"
        f"Problem Type: {inputs.problem_type}\n"
        f"Optimization Focus: {inputs.optimization_focus}\n"
        f"Data: {state['promptFiles']}\n"
        f"Previous Results: {last_output.answer_description}\n"
        f"Previous Code:\n```python\n{last_code.python_code}\n```"
    )

    # Call the core logic function
    try:
        response = await new_loop_logic(state)
    except Exception as e:
        await cl.Message(content=f"Error during new optimization round: {e}").send()
        return state

    # Display the new code and requirements in Chainlit
    await cl.Message(
        content=f"New Generated Code:\n```python\n{response.python_code}\n```"
    ).send()
    await cl.Message(
        content=f"New Requirements:\n```\n{response.requirements}\n```"
    ).send()

    # Save the new code and requirements to files
    with open("generated/generated.py", "w", encoding="utf-8") as f:
        f.write(response.python_code)

    with open("generated/requirements.txt", "w", encoding="utf-8") as f:
        f.write(response.requirements)

    current_step.output = (
        f"New code and requirements generated.\n\n"
        f"Code:\n```python\n{response.python_code}\n```\n\n"
        f"Requirements:\n```\n{response.requirements}\n```"
    )

    state["code"] = response
    return state
