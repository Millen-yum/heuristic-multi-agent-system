# pytest -s tests/agents/test_generate_code_agent.py

import pytest
from schemas import AgentState, Code, Purpose
from agents.heuristic_agent import apply_heuristic_logic
from dotenv import load_dotenv

load_dotenv()

## THIS PURPOSE IS TO GENERATE CODE USING PROVIDED FILES AND USER INPUT (WELL LLM GENERATED CONCLUSION OF WHAT USER WANTS)
# MOCK fileData (promptFiles) DOWN BELOW


@pytest.fixture
def mock_state():
    return AgentState(
        purpose=Purpose(
            user_summary="TThe user is looking to solve a vehicle routing problem (VRP) using the provided data file E-n51-k5.vrp, aiming for an optimal solution for logistics.",
            problem_type="Vehicle Routing Problem (VRP)",
            optimization_focus="The solution should minimize the total distance traveled by the trucks while adhering to a maximum truck capacity and the demand at each node.",
            chatbot_response="To solve the vehicle routing problem provided in the E-n51-k5.vrp file, we will focus on minimizing the total distance traveled by the fleet of trucks while ensuring that each truck does not exceed its capacity of 160 units. The problem has been classified as a CVRP (Capacitated Vehicle Routing Problem) with a known optimal value of 521. We will implement a heuristic approach to find a feasible solution and potentially refine it using advanced optimization techniques if necessary. The chosen heuristic will likely involve methods like the Nearest Neighbor algorithm initially, followed by further optimization for better results.",
            goal="The ultimate goal is to find a set of routes for the trucks that minimizes the total distance while satisfying capacity and demand constraints.",
            resource_requirements="The capacity of each truck is 160 units. The demands for delivery at each node vary, with the total demand needing to be met without exceeding truck capacity. Specific node coordinates and demands are outlined in the provided VRP file.",
            solution_method="heuristic",
        ),
        promptFiles=fileData,
    )


@pytest.mark.asyncio
async def test_code_generator_agent(mock_state):
    try:
        # Call `code_generator_agent` with the mock state
        response: Code = await apply_heuristic_logic(mock_state)

        # Assertions to check the response content
        assert response.python_code is not None, "Expected code output from LLM"

        # Print the response for verification
        print("\n" + response.python_code)
        print("\n" + response.requirements)
        print("\n" + response.resources)
    except Exception as e:
        pytest.fail(f"Test failed with unexpected error: {e}")


fileData = """
NAME : E-n51-k5
COMMENT : (Christophides and Eilon, Min no of trucks: 5, Optimal value: 521)
TYPE : CVRP
BEST_KNOWN: 521
DIMENSION : 51
EDGE_WEIGHT_TYPE : EUC_2D
CAPACITY : 160
NODE_COORD_SECTION
1 30 40
2 37 52
3 49 49
4 52 64
5 20 26
6 40 30
7 21 47
8 17 63
9 31 62
10 52 33
11 51 21
12 42 41
13 31 32
14 5 25
15 12 42
16 36 16
17 52 41
18 27 23
19 17 33
20 13 13
21 57 58
22 62 42
23 42 57
24 16 57
25 8 52
26 7 38
27 27 68
28 30 48
29 43 67
30 58 48
31 58 27
32 37 69
33 38 46
34 46 10
35 61 33
36 62 63
37 63 69
38 32 22
39 45 35
40 59 15
41 5 6
42 10 17
43 21 10
44 5 64
45 30 15
46 39 10
47 32 39
48 25 32
49 25 55
50 48 28
51 56 37
DEMAND_SECTION
1 0
2 7
3 30
4 16
5 9
6 21
7 15
8 19
9 23
10 11
11 5
12 19
13 29
14 23
15 21
16 10
17 15
18 3
19 41
20 9
21 28
22 8
23 8
24 16
25 10
26 28
27 7
28 15
29 14
30 6
31 19
32 11
33 12
34 23
35 26
36 17
37 6
38 9
39 15
40 14
41 7
42 27
43 13
44 11
45 16
46 10
47 5
48 25
49 17
50 18
51 10
DEPOT_SECTION
 1
 -1
EOF
"""
