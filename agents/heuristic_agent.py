from prompts.prompts import HEURISTIC_PROMPT
from schemas import AgentState, Code, ProblemClass
from .common import cl, llm_code, llm_code_claude, GENERATED_DIR, get_generated_path
from prompts.instuctions import *
async def apply_heuristic_logic(state: AgentState) -> Code:
    inputs = state["purpose"]
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

    # Select the appropriate heuristic prompt
    prompt = HEURISTIC_PROMPT.format(
        user_summary=inputs.user_summary,
        problem_type=inputs.problem_type,
        optimization_focus=inputs.optimization_focus,
        goal=inputs.goal,
        data=state["promptFiles"],
        resource_requirements=inputs.resource_requirements,
        response_format=inputs.response_format,
        problem_specific_guidelines=guidance["guidelines"],
        problem_specific_example=guidance["example"],
    )

    # Interact with the LLM
    structured_llm = llm_code.with_structured_output(Code)
    response = structured_llm.invoke(prompt)

    return response


@cl.step(name="Heuristic Agent")
async def heuristic_agent(state: AgentState) -> AgentState:
    print("*** HEURISTIC AGENT ***")
    current_step = cl.context.current_step

    inputs = state["purpose"]
    current_step.input = (
        f"Applying heuristic optimization based on the following inputs:\n\n"
        f"User Summary: {inputs.user_summary}\n"
        f"Response format: {inputs.response_format}\n"
        f"Problem Type: {inputs.problem_type}\n"
        f"Optimization Focus: {inputs.optimization_focus}\n"
    )

    try:
        response = await apply_heuristic_logic(state)
    except Exception as e:
        await cl.Message(content=str(e)).send()
        return state

    # Päivitetään output Chainlitin näkymään
    current_step.output = (
        f"Heuristic optimization applied. Suggested solution:\n```python\n{response.python_code}\n```",
        f"Requirements:\n```\n{response.requirements}\n```",
        f"Resources:\n```\n{response.resources}\n```",
        f"Used heuristic:\n```\n{response.used_heuristic}\n```",
    )

    # Lisää heuristiikka kommenttina koodin alkuun, jos se on annettu
    if response.used_heuristic:
        response.python_code = (
            f"# Heuristic used: {response.used_heuristic}\n{response.python_code}"
        )

    # Päivitä tila ja tallenna tiedostot
    state["code"] = response

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    with open(get_generated_path("generated.py"), "w", encoding="utf-8") as f:
        f.write(response.python_code)

    with open(get_generated_path("requirements.txt"), "w", encoding="utf-8") as f:
        f.write(response.requirements)

    return state
