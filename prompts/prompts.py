from langchain_core.prompts import ChatPromptTemplate

TASK_ANALYSIS_PROMPT = ChatPromptTemplate.from_template(
    """
You are a reasoning assistant. Your task is to carefully analyze the user's input and any provided data to understand the problem they are trying to solve. The task could involve logistics process optimization (e.g., finding the shortest or fastest routes), the cutting stock problem, or other similar challenges.

### General Instructions
Carefully identify and fully understand all provided variables, constraints, values, and parameters that are relevant to successfully solving the user's task. Ensure these details are consistently and accurately applied in your analysis and the proposed solution.

### Step 1: Objective
- Identify the core purpose of the task and what the user ultimately wants to achieve.
- Summarize the user's real objective in your own words, based on the task description and any available data (Python code, Excel files, or no data at all).
- If no data is provided, identify what might be missing to solve the task.

User task description:  
{user_input}

Provided data (Python code, Excel files, VRP file, or may be empty):  
{data}

Examples:

<user_input id="example-1">
I need to optimize routes for 5 delivery vehicles, each with a max capacity of 160 units. The best-known solution for this problem is 521. Here's my E-n51-k5.vrp file.
</user_input>

<assistant_response id="example-1">
This is a Capacitated Vehicle Routing Problem (CVRP) with 51 locations and 5 vehicles. Each vehicle has a capacity limit of 160. The objective is to minimize total route cost, with a known optimal value of 521. A two-phase heuristic combining Clarke-Wright Savings initialization and Simulated Annealing refinement is recommended to approach the target efficiently.
</assistant_response>

<user_input id="example-2">
I need to cut large steel sheets into specific widths to fulfill 8 customer orders. How can I minimize waste?
</user_input>

<assistant_response id="example-2">
This is a Cutting Stock Problem. The objective is to minimize material waste while meeting all customer demands. Heuristic techniques like First-Fit Decreasing or Guided Local Search are effective for this use case.
</assistant_response>

### Step 1b: Variables and Constraints
- List and clearly define **all variables, constants, and parameters** involved in the task.
- Identify:
  - **Decision variables** (e.g., route assignments, cut patterns, delivery sequences)
  - **Problem parameters** (e.g., vehicle capacities, customer demands, item sizes, time limits)
  - **Fixed constants** (e.g., depot location, number of vehicles)
  - **Objective function components** (e.g., total cost, total distance, waste, lateness)
- Explicitly list all **hard constraints** (must be satisfied) and **soft constraints** (can be optimized).
- Ensure all variables and constraints are **consistent with the problem definition**, and that no critical parameter is missing or misinterpreted.

### Step 2: Target Value Handling
- Determine if the user has specified a target value for optimization (e.g., minimum distance, maximum efficiency, cost constraint).
- If a target value is given, analyze whether it is:
  - Feasible based on constraints
  - Challenging but possible with improved techniques
  - Unrealistic, requiring constraint or expectation changes
- If no target is explicitly given, infer what an optimal outcome might look like

### Step 3: Data Quality & Missing Information
- Analyze the data and determine if it is sufficient
- Identify any missing inputs, constraints, or parameters
- Suggest what additional data the user should provide if needed

### Step 4: Problem Classification
- Determine the problem type (e.g., vehicle routing, resource allocation, scheduling)
- Define the optimization focus: What should be improved? (cost, distance, fairness, etc.)
- Consider whether the problem allows for a strict mathematical formulation, or whether heuristics are more appropriate

### Step 5: Algorithm Selection & Justification
- Prioritize heuristic and metaheuristic methods (e.g., A*, simulated annealing, genetic algorithms)
- Use exact optimization only when strictly necessary (e.g., PuLP)
- Justify the heuristic approach based on:
  - Problem complexity (e.g., NP-hard)
  - Computational needs (e.g., real-time)
  - Real-world flexibility

### Step 6: Heuristic Optimization & Refinements
- If heuristics are used, determine whether refinements are needed
- If a simple heuristic is selected, suggest enhancements (e.g., guided local search, hybrid algorithms)
- If the target is difficult to reach, suggest:
  - Constraint adjustments
  - More advanced metaheuristics

### Step 7: Solution Type Evaluation
- Confirm whether a heuristic or exact solution is preferred
- Explain if a heuristic can reasonably reach the target
- Indicate if an exact method is needed and whether it is computationally feasible

### Step 8: Output Format
- Identify the expected response format (e.g., JSON, text, Excel, CSV)
- Ensure that any generated code or explanation aligns with this output format
- Clarify if the format refers to user-facing output or internal data representation

### Step 9: Problem Class Identification
Based on your full understanding of the task and data, classify the problem.

Choose **one** of the following:
{problem_class}

Respond in this exact format:
**problem_class**: <ONE_ENUM_VALUE>

### Final Summary
- What is the user trying to achieve?
- What is the purpose of solving this task?
- Is there a defined target value, and is it achievable with heuristics?
- How can the solution be optimized, prioritizing heuristics and practical efficiency?
- Are there any missing inputs that should be collected?
- Which heuristic or metaheuristic methods are most suitable, and why?
- Does the heuristic require refinement?
- Is an exact solution required, or is a heuristic approach better?
- What output format should the solution follow, and how should that affect implementation?

### Response formatting instruction:
Your response should follow the structure defined by each step above and use corresponding section headers (e.g., “Step 1: Objective”) in your answer.
    """
)



CODE_PROMPT = ChatPromptTemplate.from_template(
    """
    Your task is to generate **fully functional, optimized Python code** that solves the optimization problem described by the user. The solution must be based on **exact mathematical optimization methods**.

    Based on the user's input and the provided files (e.g., Python code, Excel sheets), generate Python code that implements **either linear programming (LP) or integer programming (ILP/MILP)** using PuLP. If PuLP is unsuitable, consider **OR-Tools constraint programming** as an alternative.

    **Choosing the Right Optimization Approach**
    - **PuLP is the preferred method** for solving **Linear Programming (LP), Integer Programming (ILP), and Mixed-Integer Linear Programming (MILP)** problems.
    - **Use PuLP whenever possible.** Only use OR-Tools if PuLP cannot handle the problem's structure.
    - **The optimization model must be well-defined**, including:
      - **Decision variables**
      - **Objective function** (minimization or maximization)
      - **Constraints** (e.g., resource limits, time windows, scheduling conditions)
    - **Avoid heuristic-based methods**—the approach must be mathematically sound and guarantee optimality.

    **Ensuring Correct Use of PuLP**
    - **Define decision variables properly**, ensuring that they represent the key components of the optimization problem.
    - **Specify constraints explicitly**—use `LpConstraint` to define inequalities.
    - **Use `LpVariable(..., cat=LpInteger)`** for integer constraints when required.
    - **Validate feasibility**: If the model is infeasible, adjust constraints accordingly.
    - **If an LP/MILP model cannot be built, OR-Tools may be used** as an alternative.

    **Summary of the user's input:**
    {user_summary}
    
    The ultimate goal:
    {goal}

    **Problem type identified in earlier analysis:**
    {problem_type}

    **Optimization focus:**
    {optimization_focus}

    **Provided data (Python code, Excel files, or may be empty):**
    {data}
    
    **Resource Requirements:**
    {resource_requirements}
    
    **Format the output according to the user's specified response format:**
    {response_format}

    **Response Format**
    The output should be structured as a JSON object with the following fields:

    - **python_code**: The optimized, error-free Python code that solves the problem using PuLP (or OR-Tools if necessary).
    - **requirements**: A list of all required Python packages (e.g., `pandas`, `PuLP`, `ortools`). Do not include specific versions unless absolutely necessary.
    - **resources**: List any additional files, external datasets, or dependencies required for execution.
    - **optimization_analysis**: A brief explanation of why the chosen mathematical optimization method was used, comparing alternative methods.

    **Handling File Inputs & Data Processing**
    - If the provided files include **data sheets (Excel, CSV, etc.)**, ensure that:
      - **The correct file handling libraries (`pandas`, `openpyxl`) are included** in the requirements.
      - The code properly reads, processes, and integrates the data into the optimization model.
      - **The data format is preserved** to avoid errors (e.g., numerical precision issues, encoding conflicts).
    - **Avoid hardcoded paths**—ensure that input filenames are configurable.

    **Quality Assurance & Error Handling**
    - **Ensure the generated Python code is mathematically sound and produces optimal solutions.**
    - Validate that **all constraints and objective functions** are correctly formulated.
    - Before returning the final code, analyze it for **syntax errors, incorrect logic, or unbounded solutions**.
    - **Ensure all required dependencies are properly imported**.
    - Include **at least one test case using Python's `unittest`** to verify correctness.
    - If numerical results are involved, include **assertions that validate expected values**.
    - **Avoid brute-force or exhaustive search methods**—the approach must be mathematically optimized.

    **Example `requirements.txt` (flexible installation)**
    ```plaintext
    pandas
    PuLP
    numpy
    scipy
    openpyxl
    ortools
    ```

    - Avoid pinning specific versions unless required for compatibility.

    **Ensuring Correct Optimization**
    - If an error occurs during execution, analyze the failure, correct the issue, and return the fixed version.
    - If the generated solution is infeasible, refine constraints and try again.
    - **Clearly document assumptions and constraints** in the generated code.
    - If a better mathematical optimization method exists, reprocess and return the improved solution.

    **Final Requirement:** The generated Python code **must be structured, fully functional, and optimized for accuracy and efficiency**.
    """
)


CODE_PROMPT_NO_DATA = ChatPromptTemplate.from_template(
    """
    Your task is to generate Python code that solves the optimization problem described by the user, using either PuLP (for linear programming) or heuristic algorithms (e.g., genetic algorithms, simulated annealing) depending on the problem's complexity and requirements.

    Based on the user's input, generate Python code that implements either exact optimization (using PuLP) or heuristic algorithms where an approximate solution is more practical. The goal is to develop a solution that efficiently addresses the problem's constraints and objectives.

    The code must be fully functional and structured to solve the task optimally or near-optimally, depending on the method chosen. You should also define any necessary test parameters derived from the user input to validate the solution.

    Additionally, ensure that all packages specified in `requirements` include compatible version numbers to avoid conflicts. **The package versions must be compatible with each other to prevent dependency issues**. Research the compatibility requirements if needed and select versions that are widely compatible with standard dependencies (e.g., PuLP, pandas, openpyxl).

    In your response, generate the following fields:
    - **python_code**: The fully functional Python code that solves the user's problem.
    - **requirements**: A comprehensive list of all Python packages or dependencies (e.g., pandas, PuLP) needed to run the generated Python code. This will be used to create a requirements.txt file.

    Summary of the user's input:
    {user_summary}
    
    The ultimate goal:
    {goal}

    Problem type identified in earlier analysis:
    {problem_type}

    Optimization focus:
    {optimization_focus}
    
    Resource Requirements:
    {resource_requirements}
    
    Format the output according to the user's specified response format:
    {response_format}
    
    **Note:** The **Resource Requirements** section is very important for the generated code. It details the key resources available (e.g., materials, vehicles, personnel) and specific requirements (e.g., quantities, sizes) that must be fulfilled to solve the problem. The generated code must prioritize these resource requirements when forming the solution, ensuring that all available resources are utilized efficiently and constraints are respected.

    The code **must accurately represent the problem** based on the user's input, ensuring that all key factors (e.g., materials, quantities, constraints) relevant to the user's task are considered.

    ### Key Points to Address:
    - What is the optimization problem, and what constraints or requirements need to be considered?
    - Should the solution use PuLP for exact optimization, or is a heuristic algorithm more appropriate for solving this problem?
    - How should the code structure reflect the optimization method to ensure clarity and efficiency?
    - Define parameters for testing, based on user input, to validate the optimization approach.
    - What packages or libraries are required for requirements.txt to run the generated Python code, including any necessary for file handling (e.g., pandas, openpyxl) if provided data includes Excel or other files? Ensure to handle potential encoding issues in file reading to avoid errors.
    - **Ensure the `requirements` section lists all necessary Python packages without specifying exact versions unless required by specific compatibility needs. This allows pip to install the latest compatible versions automatically.**

    Example of how `requirements.txt` could look:

    ```plaintext
    pandas
    PuLP
    openpyxl
    ```

    - This example avoids version pinning and allows pip to install the latest compatible versions of the required packages.

    If version pinning is needed for specific reasons (e.g., due to compatibility issues or reproducibility requirements), here is an example of how to specify versions:

    ```plaintext
    pandas==2.1.1
    PuLP==2.9.0
    openpyxl==3.1.5
    ```

    - **Make sure the code outputs the final result clearly (e.g., using print statements or by returning the result in a structured format like a table or numerical answer).**
    """
)

HEURISTIC_PROMPT = ChatPromptTemplate.from_template(
    """
You are an AI assistant tasked with writing fully functional, error-free Python code that implements an efficient heuristic-based solution to the optimization problem described by the user. The code must execute correctly on Python 3.9+.

### Step 1: Understand the Problem and Requirements
Carefully read and process the entire problem description and provided data. Identify all relevant variables, constraints, values, parameters, and conditions. Do not omit or reinterpret any user-provided details. All provided data must be used as-is. Modifying, simplifying, or restructuring input is strictly forbidden.

Summary of the user's input:  
{user_summary}

Problem type identified in earlier analysis:  
{problem_type}

Provided data (Python code, Excel files, .vrp files, or may be empty):  
{data}

The ultimate goal:  
{goal}

Optimization focus:  
{optimization_focus}

Resource Requirements:  
{resource_requirements}

### Step 2: Select a Suitable Heuristic
Choose the most appropriate heuristic or metaheuristic based on the problem type and scale. Explain the selected approach briefly before the code. The heuristic must be correctly applied and must align with the user's goal and optimization focus.

You must also follow the domain-specific guidance provided below. These guidelines contain essential constraints, expectations, and best practices that apply to the specific type of problem.

**Failure to apply the instructions below accurately will result in an invalid solution. Do not skip or override any rule or requirement.**

Problem-Specific Guidelines:  
{problem_specific_guidelines}

### Step 3: Prepare the Python Code Structure
Structure the code modularly. Define all functions before they are used. Avoid deprecated functions and ensure all libraries used are compatible with Python 3.9+. All required imports must be present and error-free.

### Step 4: Handle File Input and Data Preprocessing
Use correct file-handling libraries (e.g., pandas, openpyxl). Do not use hardcoded file paths; filenames must be configurable. Ensure that input data is read and processed without altering the original structure or content.

### Step 5: Ensure Output Matches Format
Output must exactly follow this required format:  
{response_format}  
If Excel or other structured output is expected, do not combine multiple values into single fields. Output must be valid, structured, and ready to use without manual correction.

### Step 6: Validate Code Quality and Correctness
Code must run without syntax errors, undefined variables, or runtime issues. Use only installable packages from PyPI that are compatible with Python 3.9+. Do not use exact version pins (`==`). Use flexible versions (`>=`) only.

### Step 7: Required Output and Metrics
The generated code must print the final solution, relevant intermediate outputs if needed, and clear key metrics (e.g., total cost, distance, or execution time). Output must be human-readable and support visual validation of the result.

### Step 8: Requirements File
Provide an accurate and minimal `requirements.txt` that includes only the packages actually used in the code.

Example:
pandas>=1.3  
numpy>=1.21  
networkx>=2.6  
scipy>=1.7  
ortools>=9.2  
openpyxl>=3.0

### Step 9: Print Results for Validation
Always include print statements that display essential outputs. This includes the total objective value and a summary of the solution. If the result is also saved to a file, it must still be printed to the console. Always use f-strings or `str()` for number formatting. Direct concatenation of strings and numbers (e.g., "value: " + 5) is strictly forbidden.

### Step 10: Final Validation Pass
Before returning the final code, confirm that:
- All strings are well-formed (no unterminated strings)
- All `.format()` calls use correct arguments and are not broken across lines
- All control structures (if, for, while) are properly closed and correctly indented
- No `TypeError` occurs from improper print or string concatenation

### Reference Example for Structure and Style

Review the following example before writing your response.  
You must follow the structure, practices, and formatting shown in this example.

This includes:
- Variable naming and organization
- Import and library usage
- Output formatting and required print statements
- Adherence to data parsing and use instructions
- Requirements file structure

Do not replicate the content exactly, but follow its patterns and conventions strictly.

Example:
{problem_specific_example}

### Critical Errors to Avoid
Any of the following will result in an invalid response:
- Syntax errors or missing function/variable definitions
- Using "text" + number (must use `str()` or f-strings)
- Omitting required packages or including unused ones
- Ignoring input format or altering provided data
- Returning malformed or incomplete output
- Using deprecated, unavailable, or non-installable libraries
- Providing silent or ambiguous output without key metrics

Your response must include:
1. A brief explanation of the selected heuristic  
2. Complete, executable Python code  
3. A valid and minimal requirements.txt  
All outputs must run successfully in Python 3.9+ without manual editing.
"""
)

  


DOCKER_FILES_PROMPT = ChatPromptTemplate.from_template(
    """
    Your task is to create the necessary Docker environment files to run the Python code generated for the optimization problem. This includes creating a Dockerfile and a compose.yaml file. The requirements.txt file (in the Generated requirements part) has defined the project's dependencies.

    Start by creating a Dockerfile that specifies the base image, environment setup, and commands needed to run the Python code. Ensure that the Dockerfile includes all the necessary configurations to execute the generated code successfully.

    Then, create a compose.yaml file that sets up the Docker container for the Python code. The compose.yaml should define the services and configurations needed to build and run the code.

    The generated Python code will always be saved as **generated.py**, so your Dockerfile and compose.yaml should be set up accordingly.

    For example:
    ```yaml
    services:
      app:
        build: .
        container_name: my-python-app
        command: python /app/generated.py  # Modify the command as per your project
    ```

    Generated Python code:
    {python_code}

    Generated requirements (requirements.txt):
    {requirements}
    
    Remember to include any additional resources or files that are required to run the Python code but are not listed in the main requirements.
    {resources}

    Key tasks:
    - Create a Dockerfile with the necessary configurations to run the generated Python code.
    - Create a compose.yaml file (Docker Compose V2) that defines the services to build and run the code.
    - Ensure the setup is ready for local testing by building and running the container.
    """
)

CODE_OUTPUT_ANALYSIS_PROMPT = ChatPromptTemplate.from_template(
    """
You are an assistant that specializes in analyzing Python code outputs related to optimization problems. Your task is to extract the relevant information from the code output, evaluate the result’s consistency and correctness, and summarize it in a way that directly answers the user's original goal.

### Step 1: Extract Numerical Results and Tables
- Identify and extract all relevant numerical values and structured outputs.
- Do **not infer or add units** (e.g., meters, km, $) unless explicitly stated in the output.
- Present the values as they appear — without changing wording or structure.
- Structure them in a way that supports downstream logic or decision-making.

### Step 2: Verify Against the User's Goal and Planned Steps
- Check whether the result covers all parts of the planned process.
- Identify any steps that appear missing, incomplete, or incorrect.
- Match results against the original question and goal.

### Step 3: Provide a Direct Answer to the User
- Give a clear and concise answer to the original question.
- Use only the information present in the output — do not speculate.

### Step 4: Evaluate Accuracy and Consistency
- Check for:
  - Logical errors
  - Internal inconsistencies
  - Missing outputs
  - Values that contradict the problem constraints
- Flag anything unusual or incomplete.

### Step 5: Recommend Improvements (if needed)
- Suggest better formatting, clearer structure, or more detailed outputs.
- Point out missing fields, units, or context.

---

**Original Question:**  
{user_summary}

**Original Goal:**  
{original_goal}

**Output of the Code:**  
{code_output}

---

### Example – Output Analysis (Simplified)

Input:
<output_analysis_input id="example-1">
  <user_summary>What was the final route cost?</user_summary>
  <original_goal>Minimize total distance in a 5-truck delivery task</original_goal>
  <code_output>
Final route cost: 534.8  
Truck 1 → 0 → 8 → 3 → 0  
Truck 2 → 0 → 2 → 5 → 6 → 0  
...
  </code_output>
</output_analysis_input>

Output:
<assistant_response id="example-1">
extracted_results:
- Final route cost: 534.8
- Routes per truck: listed

direct_answer:
The final route cost is 534.8, as reported by the output.

evaluation:
The result includes the total cost, as expected. However, no unit (e.g., km) was provided, which limits interpretability.

improvement_notes:
Recommend including the unit of measurement for route cost if available. Also, a summary of total demand served per vehicle could improve clarity.
</assistant_response>
"""
)

NEW_LOOP_CODE_PROMPT = ChatPromptTemplate.from_template(
    """
    Your task is to generate a **fully optimized and improved version** of the Python code that solves the optimization problem described by the user. This new version must be based on previous iterations and must **explicitly enhance the previous solution by achieving a better objective value** (e.g., lower cost, shorter distance, higher efficiency).

    **Step 1: Analyze the Previous Solution**
    - Review the last used code and its results to determine if it **met the target goal**.
    - Identify why the previous solution was **not optimal**:
      - Did it fail to reach the given target?
      - Were there inefficiencies in the approach?
      - Could computational performance be improved?
    - If the previous solution met the goal, determine if **further improvements are still possible**.
    - Identify **which parts of the previous code were the main limitations** and require the most improvement.

    **Step 2: Generate an Improved Solution**
    - Produce a new version of the code that **strictly improves upon the last iteration**.
    - If the problem is a minimization problem (e.g., distance, cost), the new result **must be lower** than the previous one.
    - If the problem is a maximization problem (e.g., profit, efficiency), the new result **must be higher** than the previous one.
    - Avoid duplicating unnecessary parts of the previous code.
    - **Ensure the new code is computationally more efficient** (e.g., reduced time complexity, better memory handling).
    - If a different optimization technique can yield better results, **apply and justify the change**.
    - Clearly document all improvements with inline comments explaining why changes were made.

    **Step 3: Validate and Compare the Improvement**
    - **Run a comparison test** between the previous solution and the newly generated one.
    - If the new solution is **not strictly better**, retry optimization using a different approach.
    - Ensure that the new code is **computationally efficient** and does not introduce unnecessary complexity.
    - **If heuristics were used, determine whether a more advanced search method (e.g., simulated annealing, tabu search) can further enhance results**.
    - If the solution is **not consistently better**, introduce an iterative improvement mechanism.

    **Step 4: Ensure Full Docker Compatibility**
    - **All dependencies must be installable in Python 3.9+**.
    - **Check that all required packages exist in PyPI and are installable inside a Docker container**.
    - **Use flexible dependency versions (`>=latest_stable_version`) instead of exact version pins (`==`)**.
    - **Avoid deprecated functions and ensure all functions are defined before being called**.
    - **Before finalizing the code, confirm that it runs successfully inside a Python 3.9+ Docker container**.
    - **Ensure that `pip install -r requirements.txt` succeeds without errors**.

    **Example `requirements.txt` (ensure dependencies are available and installable):**
    pandas>=1.3
    numpy>=1.21
    networkx>=2.6
    deap>=1.3
    scipy>=1.7
    ortools>=9.2

    **Step 5: Output the Best Solution**
    Your response must include:

    - **python_code**: The fully optimized Python code that strictly improves the previous result.
    - **requirements**: A list of all Python dependencies needed to run the generated code, ensuring they are installable in Python 3.9+.
    - **performance_comparison**: A summary of how the new solution compares to the previous one.
    - **objective_value**: The final computed value of the objective function in both the previous and new versions.
    - **test_cases**: A brief description of test cases used to verify that the new solution is indeed better.
    - **Docker validation**: Confirmation that all dependencies can be installed and that the generated code runs successfully in a Python 3.9+ Docker environment.

    **Original user input:**
    {user_summary}

    **Original problem type:**
    {problem_type}
    
    **The Original ultimate goal:**
    {goal}

    **Optimization focus:**
    {optimization_focus}

    **Results from prior optimizations:**
    {previous_results}
    
    **Last used code:**
    {previous_code}

    **Provided data (Python code, Excel files, VRP file, or may be empty):**
    {data}
    
    **Resource Requirements:**
    {resource_requirements}

    **Final Requirements**
    - Ensure the generated code **is fully functional, free from syntax errors, and improves on the previous version**.
    - The new objective value **must be strictly better** than the previous one.
    - If the new solution is **not better**, retry with a different optimization method.
    - Ensure that the code outputs the **final computed objective value** clearly for easy comparison.
    - Automate testing: Generate test cases that verify the improvement.
    - Optimize runtime efficiency **without compromising solution quality**.
    - **Ensure that the code runs correctly in a Python 3.9+ Docker container**.
    """
)


NEW_LOOP_CODE_PROMPT_NO_DATA = ChatPromptTemplate.from_template(
    """
    Your task is to generate Python code that solves the optimization problem described by the user, using either PuLP (for linear programming) or heuristic algorithms (e.g., genetic algorithms, simulated annealing) depending on the problem's complexity and requirements.

    You should also take into account the results from previous optimization iterations to further improve the solution. Analyze the previously generated results (e.g., cutting patterns, waste minimization, resource utilization) and incorporate those insights into the next round of optimization. Ensure that the new solution is an improvement over the prior result and **does not duplicate any previous code**.

    Based on the user's input and the outcomes from the previous iteration(s), generate Python code that implements either exact optimization (using PuLP) or heuristic algorithms where an approximate solution is more practical. The goal is to develop a solution that efficiently addresses the problem's constraints and objectives, while **explicitly improving on the last used code**.

    The new code must:
    - Be fully functional and structured to solve the task optimally or near-optimally, depending on the method chosen.
    - Avoid duplicating any parts of the previous code and **explicitly comment on what improvements have been made** in terms of efficiency, structure, or the optimization goal (e.g., less waste, faster routes).
    - Define any necessary test parameters derived from the user input and previous results to validate the new solution.

    In your response, generate the following fields:
    - **python_code**: The fully functional Python code that solves the user's problem, improving on previous iterations and avoiding duplication of the last used code.
    - **requirements**: A comprehensive list of all Python packages or dependencies (e.g., pandas, PuLP) needed to run the generated Python code.

    **Original user input:**
    {user_summary}

    **Original problem type:**
    {problem_type}

    **Original optimization focus:**
    {optimization_focus}

    **Results from prior optimizations:**
    {previous_results}
    
    **Last used code:**
    {previous_code}

    The code **must accurately represent the problem** based on the user's input, ensuring that all key factors (e.g., materials, quantities, constraints) relevant to the user's task are considered. The previous optimization results should also guide the current solution in refining the approach.

    Resource Requirements:
    {resource_requirements}
    
    **Note:** The **Resource Requirements** section is very important for the generated code. It details the key resources available (e.g., materials, vehicles, personnel) and specific requirements (e.g., quantities, sizes) that must be fulfilled to solve the problem. The generated code must prioritize these resource requirements when forming the solution, ensuring that all available resources are utilized efficiently and constraints are respected.

    Key points to address:
    - What is the optimization problem, and what constraints or requirements need to be considered?
    - Should the solution use PuLP for exact optimization, or is a heuristic algorithm more appropriate for solving this problem?
    - **How does the new code differ from the last used code?** What improvements have been made to avoid duplication and enhance the previous solution?
    - Define parameters for testing, based on user input and the results of previous optimizations, to validate the new solution.
    - What packages or libraries are required for requirements.txt to run the generated Python code?
    - **Make sure the code outputs the final result clearly (e.g., using print statements or by returning the result in a structured format like a table or numerical answer), with improvements from the previous iteration and no duplication.**
    - Ensure the generated Python code is **free from syntax errors**. All functions should be properly defined, and indentation should follow Python's strict indentation rules. Ensure all variables, function definitions, and imports are correctly structured.
    """
)

NEW_LOOP_HEURISTIC_PROMPT = ChatPromptTemplate.from_template(
    """
You are an AI assistant tasked with producing a **strictly improved heuristic-based solution** for the given optimization task.  
Your goal is to generate **Python code that performs better than the previous version** in one or more of the following:
- Objective value (e.g., lower cost, shorter distance, better fitness)
- Computational efficiency (e.g., faster runtime, fewer iterations)
- Structural quality of solution (e.g., fewer constraint violations, better distribution)

**A new version that performs the same or worse is not acceptable.**  
You must explore **a clearly more effective heuristic approach** or a significant refinement of the previous one.

### Step 1: Analyze the Previous Heuristic Solution
You are continuing an optimization process. Your next solution must **strictly improve** over the previous one in terms of cost, quality, or efficiency.
- Review the last used heuristic and its results.
- Determine whether the previous solution reached the target goal.
- Identify why the previous solution was **not optimal**:
  - Was the result subpar (e.g. too long route, too high cost)?
  - Could the algorithm's logic or parameters be improved?
  - Were simpler heuristics used that could be enhanced or replaced?
- If the result was acceptable, assess whether **further improvements** are still possible.
- Pinpoint the **main limitations** of the previous approach that should be addressed.

#### Redundancy Avoidance
- You must not simply re-use or replicate the previously applied heuristic with minor or superficial changes (e.g., renaming functions or reordering statements).
- If the previously used method (e.g., simulated annealing, genetic algorithm) has already been applied, you must either:
  - Extend it with a **clear structural improvement** (e.g., capacity handling, better crossover/mutation, adaptive parameters),
  - Or replace it with a **fundamentally different heuristic framework**.
- Generating two iterations with essentially the **same algorithm and logic is considered invalid**.

### Step 2a: Heuristic Selection Strategy
- Do **not** chain multiple metaheuristics blindly (e.g., NN → SA → Tabu → ACO).
- **Only apply one advanced heuristic or metaheuristic at a time**.
- Decide whether to:
  - Keep refining the current heuristic,
  - Replace it with a different one,
- **Avoid overfitting or redundant computation** by skipping heuristics that add no improvement.
- Document clearly **why the chosen heuristic was applied**, and **why others were not**.

- The primary goal is to improve performance **over the previous result**.  
- You must clearly justify how the new approach is expected to **outperform** the last one.
- If the new solution **does not improve** the objective value, it must be considered a failure, and another method should be attempted.

### Step 2b: Problem-Specific Guidelines
You must now apply problem-specific constraints and rules based on the type of optimization problem.
{problem_specific_guidelines}

### Step 3: Validate and Compare the Improvement
If the new solution does not **strictly outperform the previous result**, it must be rejected and replaced with a better heuristic. A regression or equivalent result is considered a failure in this context.
- Include logic to **compare** the new and previous solution performance.
- If the new solution is not better, retry with a different refinement.
- Compare:
  - Objective values (before and after)
  - Runtime or memory usage (if relevant)
  - Solution quality or feasibility
- If the previous method was too simple, try **metaheuristics** or multi-phase strategies.

### Step 4: Output the Best Heuristic Solution
At the top of the code output, include a short comment identifying the heuristic used
Your response must include the following structured output:

- **python_code**: The Python code implementing the improved heuristic.
- **requirements**: List of Python dependencies (e.g. numpy, networkx).

### Step 5: Handle Numerical Precision
- Distance and cost calculations must preserve full floating-point precision by default.
- However, if the problem definition explicitly specifies a discretized metric (e.g., EUC_2D in TSPLIB), you **must use** the rounding method defined by that metric.
  - For example, EUC_2D distances must be computed as `int(sqrt((x1 - x2)^2 + (y1 - y2)^2) + 0.5)`.
- Do **not** apply arbitrary rounding unless it is explicitly required by the problem specification.
- Avoid using `astype(int)`, `int()`, `round()` or similar unless justified.
- Preserving precision ensures that all comparisons between solutions are accurate and not distorted by rounding artifacts.

### Step 6: Handle Requirements Output
- Your response must include a `requirements` list with only the Python packages actually used in the code.
- Use flexible version specifiers (e.g., `pandas>=1.3`), **not pinned versions** (`==`).
- All packages must be compatible with Python 3.9+ and available via PyPI.
- Do **not** include unnecessary or unused dependencies.
- If a package is not available, choose a suitable alternative.

**Example `requirements.txt` (ensure dependencies are available and installable):**
pandas>=1.3
numpy>=1.21
networkx>=2.6
scipy>=1.7
ortools>=9.2
openpyxl>=3.0


### Step 7: Understand the Task Context

**Original user input:**  
{user_summary}

**The Original ultimate goal:**
{goal}

**Original problem type:**  
{problem_type}

**Optimization focus:**  
{optimization_focus}

**Results from prior heuristic solutions:**  
{previous_results}

**Last used heuristic-based code:**  
{previous_code}

**Provided data (Python code, Excel files, VRP file, or may be empty):**  
{data}

**Resource Requirements:**  
{resource_requirements}

**Output must conform to this required format:**
{response_format}

---
### Step 8: Understanding the example

{problem_specific_example}

### Step 9: Print Results for Validation
- Your generated Python code must include output that prints the resulting solution in a human-readable format.
- This applies **even if the result is also written to a file (e.g., Excel)**.
- At minimum, print:
  - The **total objective value** (e.g., total route distance, total cost, or fitness).
  - A **summary of the solution** (e.g., routes per vehicle, selected actions, or other domain-specific output).
- This output is required to facilitate quick visual inspection, debugging, and testing of the solution.
- Avoid silent or implicit results — make the outcome observable directly via `print()` statements.

### Step 10: Code Correctness and Executability
Before finalizing your response, verify that the generated code is:
- Fully executable in Python 3.9+ without syntax or runtime errors
- Functionally correct (i.e., it produces a result consistent with the optimization goal)
- Free of logic bugs, broken loops, undefined variables, or uninitialized structures
- Using correct and aligned data structures (e.g., distance matrices, capacity constraints)

You must simulate the code execution in your reasoning to ensure it behaves as intended.  
Producing non-executable or incorrect code will invalidate the response.
    """
)


FINAL_REPORT_PROMPT = ChatPromptTemplate.from_template(
    """
    Given the user's task:
    {user_input}

    And the following optimization codes:
    {summaries_of_optimizations}

    Your final report should include:

    1. **Performance Comparison**: Evaluate and compare the results of each optimization method, focusing on key metrics such as speed, memory usage, and task accuracy.
    2. **Best Optimization**: Identify the best optimization for the task, providing a clear explanation of why it is the most effective based on the comparison.
    3. **Visualization**: If applicable, include a visualization that clearly illustrates the performance differences between the optimizations.
    4. **Conclusion and Recommendations**: Summarize your findings and suggest potential improvements or note any limitations.

    The report should be concise, structured, and actionable, with a focus on addressing the user's specific task.
    """
)

CODE_FIXER_PROMPT = ChatPromptTemplate.from_template(
    """
You are an experienced software engineer specializing in debugging and fixing Python code. Your task is to analyze and resolve errors in the provided code, which failed to execute in a Docker container.

### Response Format
Return a JSON object with the following fields:
- **fixed_python_code**: The corrected Python code after fixing the issue.
- **requirements**: List of required dependencies needed to run the fixed code.
- **requirements_changed**: Boolean indicating if the requirements were modified. This should be set to **true** even if the change was only a formatting fix (e.g., splitting dependencies onto separate lines or correcting commas).
- **fix_description**: Explanation of what was fixed and why.
- **original_error**: Summary of the error from Docker logs.

### Step 1: Error Analysis
- Examine the Docker logs to determine the exact cause of failure.
- Categorize the error into one of the following types:
  - **SyntaxError / IndentationError** → Formatting or syntax issue.
  - **ImportError / ModuleNotFoundError** → Missing, deprecated, or OS-incompatible package.
  - **TypeError / ValueError** → Incorrect data types or function misuse.
  - **RuntimeError** → Execution-related failure (e.g., missing variable, infinite loop).
  - **EnvironmentError** → Docker-related issue, such as incorrect file paths or missing system dependencies.
- If the error is related to package dependencies, verify that the requirements.txt file is formatted correctly:
  - **Important:** Each dependency should be listed on a separate line.
  - If the file contains dependencies separated by commas or incorrect line breaks, they must be corrected.
- Provide a clear explanation of why the error occurred before making any modifications.

#### Special Notes on Syntax Errors (e.g., SyntaxError: EOL while scanning string literal)
- These are often caused by:
  - Missing or unclosed quotes (' or ")
  - Improperly broken strings across lines
  - Newlines placed outside of strings rather than within (\\n)
- Ensure that:
  - All string literals ('text' or "text") are correctly closed.
  - Format strings are syntactically valid.
  - Look for concatenated strings that span multiple lines without explicit line breaks.
  - If a string is split across lines, use string concatenation or proper \\ line continuation.
  - Ensure that `.format()` calls do not contain misplaced newlines.

### Step 2: Dependency & Environment Fixes
- Review the `requirements.txt` file:
  - Ensure proper formatting (one dependency per line, no commas).
  - Use **flexible versions** (e.g., `pandas>=1.3`) instead of hard pins (`==`) unless necessary.
  - Ensure compatibility with **Python 3.9+**.
  - Remove unused dependencies and replace deprecated ones if needed.
  - If you make any change to the requirements file (even formatting), set `requirements_changed = true`.
- For Docker-related errors:
  - Fix incorrect or hardcoded file paths using relative paths.
  - Ensure required **system-level dependencies** are installed inside the Docker container.
  - Properly handle **missing environment variables**.
- Do **not** modify external files unless explicitly required.

### Step 3: Code Correction
- Address all errors related to:
  - Syntax (unclosed strings, indentation, etc.)
  - Missing or unused imports
  - Wrong data types, invalid parameters, misused functions
  - Logic errors, infinite loops, or uninitialized variables
- Apply **only necessary changes** to preserve original logic and structure.
- Avoid excessive rewrites or refactoring unless essential to make the code run.

### Step 4: Validation
- Verify that the corrected code executes **without errors** in a simulated environment.
- Ensure the solution is stable and does **not introduce new bugs**.
- If the fix attempt fails, provide an **alternative correction**.

### Step 5: Return Full Corrected Code
- You must return the full corrected version of the Python source file.
- This means the entire program — not just the modified lines or snippets — even if most of the code is unchanged.
- Include any required imports, function definitions, or structural code needed to make the file runnable on its own.
- This should be returned in the `fixed_python_code` field, as a complete and standalone script.

This is critically important:
- Do not use placeholder text such as "rest of the code remains unchanged" or "see above".
- Do not skip sections that were not directly modified.
- A complete response is required to ensure that the corrected code can be tested, executed, and reused as-is.

### Docker Container Logs (Error Details):
{docker_output}

### Original Code:
{code}

### Original Requirements:
{requirements}

### Original Resources (Do not modify unless required):
{resources}

You may add inline comments to explain what changes were made and why, so the user can understand the applied fixes.

### Example – Code Fix (1): Syntax Error

Input:
<codefix_input id="example-1">
  <docker_output>
SyntaxError: unterminated string literal (line 219)
  </docker_output>

  <code>
plan_output += ''.format(manager.IndexToNode(index))
  </code>

  <requirements>
pandas, numpy, ortools
  </requirements>
</codefix_input>

Output:
<assistant_response id="example-1">
Fixed Python Code:
plan_output += '' + str(manager.IndexToNode(index)) + '\\n'

Requirements (reformatted):
pandas>=1.3
numpy>=1.21
ortools>=9.2

Fix Description:
- Replaced broken format call with string concatenation.
- Reformatted requirements into separate lines.

Original Error:
SyntaxError: unterminated string literal (line 219)

Requirements Changed:
true
</assistant_response>

### Example – Code Fix (2): ValueError in NumPy reshape

Input:
<codefix_input id="example-2">
  <docker_output>
ValueError: cannot reshape array of size 10 into shape (3,3)
  </docker_output>

  <code>
import numpy as np
arr = np.arange(10)
reshaped = arr.reshape((3,3))
  </code>

  <requirements>
numpy
  </requirements>
</codefix_input>

Output:
<assistant_response id="example-2">
Fixed Python Code:
import numpy as np
arr = np.arange(9)
reshaped = arr.reshape((3,3))

Requirements (reformatted):
numpy>=1.21

Fix Description:
- Reshape to (3,3) requires 9 elements, not 10.
- Adjusted array size to np.arange(9) to make reshape valid.

Original Error:
ValueError: cannot reshape array of size 10 into shape (3,3)

Requirements Changed:
true
</assistant_response>

### Example – Code Fix (3): ModuleNotFoundError

Input:
<codefix_input id="example-3">
  <docker_output>
ModuleNotFoundError: No module named 'pandasx'
  </docker_output>

  <code>
import pandasx as pd

df = pd.read_csv("data.csv")
print(df.head())
  </code>

  <requirements>
pandasx
  </requirements>
</codefix_input>

Output:
<assistant_response id="example-3">
Fixed Python Code:
import pandas as pd

df = pd.read_csv("data.csv")
print(df.head())

Requirements (reformatted):
pandas>=1.3

Fix Description:
- Replaced incorrect import 'pandasx' with 'pandas'.
- Updated requirements to include valid package name.

Original Error:
ModuleNotFoundError: No module named 'pandasx'

Requirements Changed:
true
</assistant_response>
"""
)


