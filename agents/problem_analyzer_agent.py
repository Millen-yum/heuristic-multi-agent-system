# File: problem_analyzer_agent.py
import re
from prompts.prompts import (
    TASK_ANALYSIS_PROMPT,
)
from schemas import AgentState, Purpose, ProblemClass
from .common import cl, PydanticOutputParser, llm


# This agent function analyzes the problem based on user input and provided files.
# It uses Pydantic to structure and parse the response from the LLM.
@cl.step(name="Problem Analyzer Agent")  # Registers function as a Chainlit step
async def problem_analyzer_agent(state: AgentState):
    print("*** PROBLEM ANALYZER AGENT ***")
    current_step = cl.context.current_step  # Retrieves the current Chainlit step
    userInput = state["userInput"]
    prompt_files = state["promptFiles"]

    # Displays the user's input and any provided files in the Chainlit interface
    current_step.input = (
        f"Analyzing the problem for the following input:\n{userInput}\n\n"
        f"Prompt Files:\n{prompt_files}"
    )

    problem_class = "\n".join(f"- {cls.name}" for cls in ProblemClass)
    # Formats the prompt for the LLM based on user input and prompt files
    prompt = TASK_ANALYSIS_PROMPT.format(user_input=userInput, data=prompt_files, problem_class=problem_class)

    # Initialize Pydantic parser to structure the LLM's output in the Purpose model
    output_parser = PydanticOutputParser(pydantic_object=Purpose)
    format_instructions = (
        output_parser.get_format_instructions()
    )  # Retrieves LLM format instructions

    # Append format instructions to the prompt
    prompt += f"\n\n{format_instructions}"
    
    print("\nPrompt for LLM:\n")
    print(prompt)  # Debugging: prints the prompt to the console

    # Initialize empty response container for streaming LLM response
    full_response = ""

    # Streams the LLM's response in real-time chunks to the Chainlit interface
    async for chunk in llm.astream(prompt):
        if hasattr(chunk, "content"):
            await current_step.stream_token(chunk.content)  # Streams response to UI
            full_response += chunk.content

    # Parses full response using the Pydantic parser into the Purpose model
    try:
        response = output_parser.parse(full_response)
    except Exception as e:
        await cl.Message(content=f"Error parsing response: {e}").send()
        return state  # Returns the unmodified state on error

    state["purpose"] = response  # Stores parsed response in the state
    state["solution_method"] = response.solution_method    

    # Sends response to the user
    await cl.Message(content=f"{response.chatbot_response}").send()

    # Prompts the user to proceed or make a new plan
    res = await cl.AskActionMessage(
        content="Sounds good, proceed?!",
        actions=[
            cl.Action(name="continue", payload={"value": "continue"}, label="✅ Continue"),
            cl.Action(name="new", payload={"value": "new"}, label="❌ Create new plan"),
            cl.Action(name="cancel", payload={"value": "cancel"}, label="❌ Cancel and start over"),
        ],
    ).send()

    if res is None or "payload" not in res or "value" not in res["payload"]:
        await cl.Message(content="No valid response received. Ending session.").send()
        state["proceed"] = "cancel"
        return state

    selected_value = res["payload"]["value"]

    if selected_value == "continue":
        state["proceed"] = "continue"
    elif selected_value == "cancel":
        state["proceed"] = "cancel"
        await cl.Message(content="Alright, let's cancel this and start over!").send()
    else:
        state["proceed"] = "new"
        await cl.Message(content="Alright, let's create a new plan!").send()

    return state
