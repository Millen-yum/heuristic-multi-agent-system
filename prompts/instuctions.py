CUTTING_STOCK = {
    "guidelines": """
=== General Guidelines for Cutting Stock Problems ===

The Cutting Stock Problem (CSP) involves cutting large stock materials (e.g., paper rolls, steel plates) into smaller required widths, such that customer demand is fulfilled with minimal waste and minimal number of rolls used.

=== Input Structure ===

You are given:
- A single stock item type: a roll with fixed width (e.g., 100 inches) and unlimited length.
- A list of required widths and their corresponding demand quantities.
- The objective is to design valid cutting patterns and determine how many times each pattern should be applied.

Inputs are typically:
- Excel or CSV files listing widths and demands.
- Each cutting pattern must not exceed the maximum stock width (e.g., 100 inches).
- All demands must be fulfilled exactly (no underproduction or overproduction is allowed).

=== Output Requirements ===

You must output:
- A list of cutting patterns used (each as a tuple of widths)
- How many times each pattern is applied
- Total number of rolls used (equals the sum of pattern usages)
- Total material waste
- A verification table with:
    - Required demand per width
    - Produced amount from patterns
    - Surplus/deficit (must be zero for a valid solution)

Any solution that does not meet demand exactly is considered invalid.

=== Demand Verification (Required Step) ===

After solving, construct a table comparing produced vs. required demand. You must verify that:
- No demand is left unmet (no underproduction)
- No excess units are produced (no overproduction)

Example:
Width | Required | Produced | Surplus/Deficit  
----- | -------- | -------- | ----------------  
36    | 610      | 610      | 0  

=== Heuristic and Optimization Methods ===

Pattern generation must use:
- First-Fit Decreasing (FFD)
- Best-Fit Decreasing (BFD)
- Combinations with replacement (filtered by max roll width)

Pattern selection must use:
- Integer Linear Programming (ILP) via `pulp` or `ortools`
- Metaheuristics (e.g., GA) only if demand match is strictly validated

=== Forbidden Practices ===

Never:
- Assign each width to its own roll
- Generate patterns that exceed roll width
- Omit post-solution validation
- Return solutions with surplus or missing units

=== Recommended Libraries ===

- `pandas`, `openpyxl`: Excel/CSV I/O
- `pulp`, `ortools`: ILP modeling
- `collections`, `numpy`: pattern enumeration

=== Code Format and Execution ===

- Define all functions before use
- Use only required libraries
- Format all output clearly with print statements
- Ensure results are reproducible in Python 3.9+

=== Summary ===

Your solution must:
- Minimize the number of rolls used
- Minimize total material waste
- Match customer demand exactly
- Output all results and verification
""",
    "example": """
### Example – Heuristic Code Generation for Cutting Stock

Input:
<structured_state id="cutting-stock-1">
  <user_summary>You have an unlimited-length roll with a fixed width of 100 inches. Minimize the number of rolls used to fulfill the specified width demands.</user_summary>
  <problem_type>Cutting stock</problem_type>
  <optimization_focus>Waste minimization</optimization_focus>
  <goal>Generate valid cutting patterns that fulfill each demand exactly without overproduction.</goal>
  <data>cutting_orders.xlsx</data>
  <resource_requirements>Widths: 45, 36, 31, 14; Demands: 97, 610, 395, 211</resource_requirements>
  <response_format>Excel</response_format>
</structured_state>

Output:
<assistant_response id="cutting-stock-1">
# Heuristic used: FFD pattern generation + ILP for pattern selection

from itertools import combinations_with_replacement
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpInteger
import pandas as pd

# Load data
widths = [45, 36, 31, 14]
demands = [97, 610, 395, 211]
roll_width = 100

# Generate feasible patterns
patterns = []
for r in range(1, 6):
    for combo in combinations_with_replacement(widths, r):
        if sum(combo) <= roll_width:
            patterns.append(tuple(sorted(combo)))

patterns = list(set(patterns))

# Create LP problem
prob = LpProblem("CuttingStock", LpMinimize)
vars = LpVariable.dicts("P", range(len(patterns)), 0, None, LpInteger)
prob += lpSum([vars[i] for i in range(len(patterns))]), "Minimize Rolls"

# Add demand constraints
for j, w in enumerate(widths):
    prob += lpSum([vars[i] * pattern.count(w) for i, pattern in enumerate(patterns)]) == demands[j]

prob.solve()

# Print results
print("Cutting Patterns Used:")
for i, count in vars.items():
    if count.varValue > 0:
        print(f"Pattern {patterns[i]} used {int(count.varValue)} times")

total_rolls = sum(count.varValue for count in vars.values())
total_waste = sum((roll_width - sum(patterns[i])) * vars[i].varValue for i in vars if vars[i].varValue > 0)

print(f"Total rolls used: {int(total_rolls)}")
print(f"Total material waste: {int(total_waste)} inches")

# Verification
print("\\nVerification Table:")
print("Width | Required | Produced | Surplus/Deficit")
for j, w in enumerate(widths):
    produced = sum([vars[i].varValue * patterns[i].count(w) for i in vars])
    print(f"{w} | {demands[j]} | {int(produced)} | {int(produced - demands[j])}")
</assistant_response>
""",
}


VRP = {
    "guidelines": """
=== General Guidelines for Vehicle Routing Problems (VRP) ===

The Vehicle Routing Problem (VRP) involves determining optimal delivery routes for a fleet of vehicles serving a set of customers, often from a central depot. The objective is typically to minimize total travel distance, cost, or time, while satisfying various constraints such as vehicle capacity.

You must use all input data exactly as provided. It is strictly forbidden to alter, restructure, simplify, or replace the input content in any way.

=== Input Structure ===

Typical VRP input includes:
- Customer locations and demands
- Distance or time matrix
- Vehicle capacity and fleet size
- Depot location

**Understand whether the problem requires a single vehicle or multiple vehicles.**
- If `fleet size = 1`, the problem reduces to a **Traveling Salesman Problem (TSP)**.
- If `fleet size > 1`, treat it as a standard **CVRP or VRPTW** instance.

If input is given as a `.vrp` file or structured string, you must parse and use the data exactly as-is.
Replacing `.vrp` content with mockups, hardcoded strings, or altered versions is strictly forbidden.

If the input specifies `EDGE_WEIGHT_TYPE : EUC_2D`, you must compute all pairwise distances using the TSPLIB standard formula:
`int(sqrt((x1 - x2)^2 + (y1 - y2)^2) + 0.5)`. This rounding is part of the problem definition and must not be skipped.

**Important: Depot must not be added manually**
If the `.vrp` input already includes the depot node (e.g., `1 30 40` in `NODE_COORD_SECTION` and `1 0` in `DEMAND_SECTION`), you **must not insert the depot again** into the coordinates or demands list manually.

- Always preserve the original index alignment from the `.vrp` file:
  - `coordinates[i]` must correspond exactly to `demands[i]`
  - The depot is typically at index 0 — do not modify unless it is explicitly absent
- Inserting a depot manually with `coordinates.insert(0, ...)` or similar will break indexing and lead to silent logic errors, such as zero-valued route distances.

=== Objective Requirements ===

Your implementation must:
- Serve each customer exactly once
- Assign customers to vehicle routes starting and ending at the depot
- Ensure no vehicle exceeds its capacity
- Generate a feasible route for each vehicle (if fleet size is fixed)
- Minimize total distance or cost

Clearly state the heuristic used and briefly explain its suitability.

=== Recommended Heuristics ===

- For small/medium VRPs:
  - Nearest Neighbor
  - Clarke-Wright Savings
  - Sweep Algorithm

- For larger/more complex cases:
  - Simulated Annealing
  - Tabu Search
  - Genetic Algorithms
  - Hyperheuristics
  - Google OR-Tools Routing Solver

=== Forbidden Practices ===
- Use crossover operators suitable for list-of-routes structures (VRP). Operators like `cxOrdered` assume equal-length, flat permutations and may fail with VRP-specific data.
- Do not manually insert or reinsert the depot into coordinates or demands if it is already present in the input. This will misalign index references and silently corrupt distance or capacity calculations.

Never:
- Serve the same customer multiple times (unless explicitly allowed)
- Omit any customer
- Exceed vehicle capacity in any route
- Return raw distance matrices instead of structured routes
- Add units (e.g., km, kg) unless explicitly provided in the task

=== Recommended Libraries ===

- `ortools` (e.g., CVRP, VRPTW)
- `networkx`, `numpy` for graph and matrix handling
- `pandas`, `openpyxl` for I/O
- `matplotlib`, `folium` for optional visualization

=== Code Requirements ===

- All functions must be defined before they are used
- All required imports must be included
- Code must run in Python 3.9+ without modifications
- Only include packages actually used in `requirements.txt`
- Use flexible package versions (`>=x.y`), not exact pins (`==x.y`)
- Do not remove depot information from coordinates or demands. The depot must remain as index 0 in both lists.
- Ensure that the number of locations, demands, and routing manager indices match exactly. Misaligned data will prevent solution feasibility.
- If you use Google OR-Tools, always set a time limit (e.g., `search_parameters.time_limit.FromSeconds(30)`) to avoid infinite solving attempts if no solution is found.
  - The time limit should scale with the problem complexity — use 120 to 300 seconds for more demanding cases.
- If using OR-Tools with `GetArcCostForVehicle(...)`, ensure that:
  - A valid distance callback has been registered using `SetArcCostEvaluatorOfAllVehicles(...)`
  - If this is missing or incorrectly set, arc costs will be silently zero
  - You do **not** need `AddDimension(...)` unless modeling cumulative metrics (e.g. time, max distance, windows)

=== Output and Print Requirements ===

Your output must include:
- Total objective value (e.g., total route distance or cost)
- A human-readable route summary per vehicle
- Clear, valid print statements

Never do the following:
    - **Do NOT place `\n` inside a `.format()` placeholder or split it across lines .**
    - If a newline is needed, **use f-strings or concatenate explicitly (`+ "\\n"`) instead**.
    - Ensure that all `.format()` calls receive the correct number of arguments to prevent tuple index errors.
    - Verify that all string formatting operations (e.g., `.format()`, f-strings) correctly reference valid variables.

Correct:
    print(f"Truck 1 route: {{route1}}")
    print(f"Total distance: {{total_distance}}")

Incorrect:
    plan_output += ' {}\n\n'.format(x)  # Broken newline
    print("Distance: " + 123.4)         # TypeError

All output must be syntactically correct, safely formatted, and clearly convey the final result.
""",
    "example": """
### Example – Multi-vehicle routing (CVRP)

Input:
<structured_state id="vrp-1">
  <user_summary>Route optimization for 3 trucks delivering to 20 locations</user_summary>
  <problem_type>Vehicle routing</problem_type>
  <optimization_focus>Total distance minimization</optimization_focus>
  <goal>Generate optimized delivery routes</goal>
  <data>vrp_E-n20-k3.vrp</data>
  <resource_requirements>Truck cap: 100; Demands: per customer; Distance matrix included</resource_requirements>
  <response_format>Text summary + route details</response_format>
</structured_state>

Output:
<assistant_response id="vrp-1">
# Heuristic used: Clarke-Wright Savings Algorithm
# This heuristic computes "savings" for combining customer pairs into routes,
# starting from a separate route for each customer.

import pandas as pd
import networkx as nx

# Load and preprocess VRP data
# Parse .vrp file and extract depot, customers, capacities, and distance matrix

# Implement Clarke-Wright heuristic
# Build savings list and merge feasible routes

# Example output
print(f"Truck 1 route: [0, 3, 5, 8, 0]")
print(f"Truck 2 route: [0, 2, 7, 9, 0]")
print(f"Truck 3 route: [0, 4, 6, 1, 0]")
print(f"Total distance: 134.7")
</assistant_response>

### Example – Single-vehicle (TSP)

Input:
<structured_state id="vrp-tsp">
  <user_summary>Find shortest round trip for 1 truck visiting 15 customers</user_summary>
  <problem_type>Vehicle routing</problem_type>
  <optimization_focus>Minimize route length</optimization_focus>
  <goal>Generate a TSP tour visiting all points once</goal>
  <data>tsp_15_customers.vrp</data>
  <resource_requirements>Single truck; no capacity constraints</resource_requirements>
  <response_format>List of visited nodes + total cost</response_format>
</structured_state>

Output:
<assistant_response id="vrp-tsp">
# Heuristic used: 2-opt local search for TSP

# Parse TSP data and compute initial route
# Apply 2-opt swaps until no improvement
print(f"Route: [0, 3, 7, 12, ..., 0]")
print(f"Total distance: 378.2")
</assistant_response>
""",
}

KNAPSACK = {
    "guidelines": """
General Guidelines for Knapsack Problems:

The Knapsack Problem is a classic combinatorial optimization task. The goal is to select a subset of items to maximize total value without exceeding a capacity constraint.

Problem structure:

1. Input includes:
   - A list of items with value and weight
   - A total capacity (e.g., weight limit)

2. Objective:
   - Maximize total value of selected items
   - Do not exceed the capacity constraint

Variants:
- 0/1 Knapsack: Each item can be selected at most once
- Fractional Knapsack: Items can be partially selected
- Multi-dimensional Knapsack: Multiple resource constraints
- Multiple knapsacks: Select items for several bags (e.g., bin packing)

Recommended heuristics:

- For 0/1 Knapsack:
  - Greedy heuristics based on value/weight ratio (approximate)
  - Dynamic programming (exact, but exponential in size)
  - Simulated Annealing, Genetic Algorithms for large instances

- For Fractional Knapsack:
  - Greedy method gives exact solution (value/weight sorted)

Avoid:
- Selecting items whose total weight exceeds the capacity
- Returning all items without applying any filtering or optimization
- Ignoring the value-to-weight trade-off

Recommended libraries:
- `pandas`, `numpy` for data handling
- `deap`, `random` for evolutionary/metaheuristics
- `pulp` or `ortools` for exact optimization if needed
""",
    "example": """
### Example – Heuristic Code Generation for Knapsack Problem

Input:
<structured_state id="knapsack-1">
  <user_summary>Select items to maximize value under a 50kg limit</user_summary>
  <problem_type>Knapsack</problem_type>
  <problem_class>knapsack</problem_class>
  <optimization_focus>Maximize value</optimization_focus>
  <goal>Heuristic-based item selection</goal>
  <data>items.csv</data>
  <resource_requirements>Each item has weight and value</resource_requirements>
  <response_format>List of selected items + total value</response_format>
</structured_state>

Output:
<assistant_response id="knapsack-1">
# Heuristic used: Greedy value/weight ratio

import pandas as pd

df = pd.read_csv("items.csv")
df["ratio"] = df["value"] / df["weight"]
df = df.sort_values(by="ratio", ascending=False)

capacity = 50
total_weight = 0
total_value = 0
selected = []

for _, row in df.iterrows():
    if total_weight + row["weight"] <= capacity:
        selected.append(row["item"])
        total_weight += row["weight"]
        total_value += row["value"]

print("Selected items:", selected)
print("Total value:", total_value)
</assistant_response>

Input:
<structured_state id="knapsack-2">
  <user_summary>Choose subset of products for delivery drone</user_summary>
  <problem_type>Knapsack</problem_type>
  <problem_class>knapsack</problem_class>
  <optimization_focus>Maximize delivered value</optimization_focus>
  <goal>Respect weight limit and select most valuable items</goal>
  <data>products.xlsx</data>
  <resource_requirements>Max weight 15kg</resource_requirements>
  <response_format>Excel file with selected items</response_format>
</structured_state>

Output:
<assistant_response id="knapsack-2">
# Heuristic used: Simulated Annealing for 0/1 Knapsack

# Initialize binary solution vector
# Perturb solution, evaluate, accept with probability
# Keep best-so-far solution based on value and weight feasibility
# Export selected items to Excel
</assistant_response>
""",
}

SHIFT_SCHEDULING = {
  "guidelines": """
=== General Guidelines for Shift Scheduling Problems ===

You are solving a real-world shift scheduling problem. Your task is to extend an existing schedule by generating valid staff assignments for a specified horizon (e.g., next 8 weeks) without altering any past data. All decisions must respect given inputs and constraints.

=== Input Specification ===
Inputs may include:
- Staff profiles: names, roles, assigned groups/units, weekly hour limits, availability, vacations
- Shift definitions: labels, time ranges, durations, days of week
- Demand data: required headcount per shift (static or varying by time)
- Existing schedule/template (e.g., Excel file)
- Holidays and non-working days
- Optional dynamic parameters (e.g., attendance, special weighting factors)

Always use the provided data exactly as-is. Do not invent, infer, or hardcode placeholder values. Read child attendance and staff profile data directly from the input files; do not use dummy counts or arbitrary defaults.

=== Hard Constraints ===
Your schedule must satisfy every constraint:
1. **One entry per cell:** Exactly one of: a staff name, "loma", "avustaja", or empty (if allowed). No lists or composites.
2. **No overlap:** No employee on two overlapping shifts in the same day.
3. **Minimum rest:** At least 11 hours between shift end and next start.
4. **Weekly hours:** Do not exceed each employee’s weekly limit (e.g., 38h15m).
5. **Availability:** Respect vacations, leaves, and other unavailability.
6. **Grouping:** Assign staff only to their own group/unit.
7. **Coverage:** Fill all required shifts unless explicitly waived.
8. **Holidays:** Do not assign on listed holidays unless allowed.

=== Time Parsing Rules ===
When parsing shift times (e.g., "6.30-14.30", "(7.00) 7.30"), do not cast to float. Clean strings with regex (remove parentheses/whitespace), then parse via `datetime.strptime` supporting ":" or "." separators.

=== Schedule Continuation Rules ===
- **Never overwrite** existing rows or cells. Save to a new file (e.g., `updated_...xlsx`).
- **Start at the first empty row** after the highest week number (column A).
- **Detect the highest week number** and begin new weeks at last + 1, generating exactly the requested number of weeks.
- **Append** new rows; do not modify historical data.
- **Output file** must contain only newly generated weeks; do not include or reproduce past weeks.

=== Output Requirements ===
- Use `openpyxl` for Excel I/O; preserve all formatting, headers, styles, formulas.
- Write each assignment via `ws.cell(row, col).value = ...`.
- Follow the template’s row/column structure exactly.

=== Recommended Scheduling Logic ===
Decisions must be data-driven:
1. **Compute staffing demand per shift dynamically:** for each time slot, sum children present (applying special needs multipliers) by group, then apply group-specific staffing ratios (e.g., 1:4 under‑3, 1:7 over‑3, 1:1.75 mixed) to determine number of staff required.
2. Identify eligible staff per shift (availability, group, hours, rest).
3. Select staff via heuristic or metaheuristic:
   - Greedy (least hours first)
   - Genetic algorithm, local search, or IP for complex cases
4. Track running totals: hours per week, last shift end.
5. Apply backtracking or repair to resolve violations.
6. Mark official holidays or vacation days as "loma" only. Do not use "loma" as a generic fallback. If a shift cannot be filled outside holidays, leave the cell empty or use an approved marker (e.g., "avustaja").

=== Few-Shot Examples ===
#### 1. Basic Weekly Rotation
Input:
<structured_state>
  <user_summary>Schedule 6 staff to two daily shifts for one week</user_summary>
  <problem_type>Shift scheduling</problem_type>
  <resource_requirements>Max 38h/week; min 11h rest</resource_requirements>
  <response_format>Excel with one row</response_format>
</structured_state>
Output:
# Greedy rotation: assign earliest idle staff per shift
# Save Excel with 1 new week

#### 2. Vacation Handling
Input:
<structured_state>
  <user_summary>Generate a one-week schedule skipping vacations</user_summary>
  <problem_type>Shift scheduling</problem_type>
  <resource_requirements>Preserve "loma" cells</resource_requirements>
  <response_format>Excel with 1 row</response_format>
</structured_state>
Output:
# Retain existing "loma"; assign remaining shifts fairly

#### 3. Multi-Week Extension
Input:
<structured_state>
  <user_summary>Extend schedule by 8 weeks for daycare</user_summary>
  <problem_type>Shift scheduling</problem_type>
  <resource_requirements>Group constraints; staffing ratios; 38h15m/week; holidays</resource_requirements>
  <response_format>Excel with 8 rows</response_format>
</structured_state>
Output:
# Identify last week; append 8 rows
# Assign per group, hours, rest; save new file
"""
  ,
  "example": """
### Few-Shot Examples – Shift Scheduling Heuristics

#### Example 1: Basic Weekly Rotation
Input:
<structured_state>
  <user_summary>Schedule 6 staff to two daily shifts for one week</user_summary>
  <problem_type>Shift scheduling</problem_type>
  <resource_requirements>Max 38h/week; min 11h rest</resource_requirements>
  <response_format>Excel with one row</response_format>
</structured_state>

Output:
# Greedy rotation: assign earliest idle staff per shift
# Save Excel with 1 new week

#### Example 2: Vacation Handling
Input:
<structured_state>
  <user_summary>Generate a one-week schedule skipping vacations</user_summary>
  <problem_type>Shift scheduling</problem_type>
  <resource_requirements>Preserve "loma" cells</resource_requirements>
  <response_format>Excel with 1 row</response_format>
</structured_state>

Output:
# Retain existing "loma"; assign remaining shifts fairly

#### Example 3: Multi-Week Extension
Input:
<structured_state>
  <user_summary>Extend schedule by 8 weeks for daycare</user_summary>
  <problem_type>Shift scheduling</problem_type>
  <resource_requirements>Group constraints; staffing ratios; 38h15m/week; holidays</resource_requirements>
  <response_format>Excel with 8 rows</response_format>
</structured_state>

Output:
# Identify last week; append 8 rows
# Assign per group, hours, rest; save new file
"""
}


WAREHOUSE_OPTIMIZATION = {
    "guidelines": """
General Guidelines for Warehouse Optimization Problems:

Warehouse optimization problems typically involve routing mobile agents (e.g., robots, workers) to pick up and deliver items between storage locations and designated areas, while minimizing total movement, time, or energy. Problems may also include optimizing the placement of goods to reduce future travel.

Typical input includes:
- A list of items with pickup and dropoff points
- A warehouse map represented as a grid or graph (e.g., aisles, shelves)
- Robot or agent profiles (e.g., capacity, speed, start location)
- Time windows or priority levels for some items
- Constraints like collision avoidance or one-way paths

Objectives:
- Minimize total distance or time used by robots
- Maximize throughput (items delivered per hour)
- Minimize idle time or energy consumption
- Balance task load among multiple robots

Constraints:
- No collisions or overlapping paths
- Maximum capacity per robot (e.g., 1–5 items per trip)
- Allowed directions in narrow aisles
- Limited shift duration or battery time
- Item priorities or dependencies (e.g., item A before B)

Recommended approaches:
- A* or Dijkstra for shortest pathfinding on warehouse graphs
- Multi-agent pathfinding (MAPF) for simultaneous routing
- Simulated Annealing or Genetic Algorithms for slot assignment or task sequencing
- Integer or Constraint Programming (e.g., with OR-Tools) for small-scale exact formulations
- Hybrid greedy + local search for fast approximations

Avoid:
- Treating robots as independent if collision constraints apply
- Ignoring start/end positions when optimizing sequence
- Overfitting to fixed item layouts
- Hard-coding shelf positions instead of using a flexible data structure

Recommended libraries:
- `networkx` or `scipy.sparse.csgraph` for graph-based routing
- `numpy`, `pandas` for data handling
- `ortools` for constraint and routing solvers
- `heapq`, `collections`, `matplotlib` for task queues and visualization
""",
    "example": """
### Example – Heuristic Code Generation for Warehouse Routing

Input:
<structured_state id="warehouse-1">
  <user_summary>Minimize the movement of robots while delivering 10 items from entrance to shelf and from shelf to outbound dock</user_summary>
  <problem_type>Warehouse optimization</problem_type>
  <problem_class>warehouse_optimization</problem_class>
  <optimization_focus>Total distance traveled</optimization_focus>
  <goal>Move all items to their destination shelves with minimum motion</goal>
  <data>warehouse_map.json, items.csv</data>
  <resource_requirements>
  - Grid-based warehouse with shelves as nodes
  - 3 robots, each can carry 1 item at a time
  - Start location is (0, 0); outbound dock at (9, 9)
  - Items have storage targets like (2,3), (4,7), etc.
  </resource_requirements>
  <response_format>Python code that prints each robot's path and total cost</response_format>
</structured_state>

Output:
<assistant_response id="warehouse-1">
# Heuristic used: Task assignment + A* routing for each robot sequentially

import json, heapq
import networkx as nx
import pandas as pd

# Load warehouse layout
with open("warehouse_map.json") as f:
    warehouse = nx.node_link_graph(json.load(f))

items = pd.read_csv("items.csv")
robots = [{"id": i, "position": (0, 0), "path": [], "cost": 0} for i in range(3)]

# Assign each item to the robot with the lowest current load
for i, row in items.iterrows():
    dest = tuple(map(int, row["target"].split(",")))
    best_robot = min(robots, key=lambda r: r["cost"])
    path = nx.shortest_path(warehouse, source=best_robot["position"], target=dest, weight="weight")
    best_robot["path"] += path + [dest]
    best_robot["cost"] += nx.path_weight(warehouse, path, weight="weight")
    best_robot["position"] = dest

# Move to dock after deliveries
for robot in robots:
    path = nx.shortest_path(warehouse, source=robot["position"], target=(9, 9), weight="weight")
    robot["path"] += path
    robot["cost"] += nx.path_weight(warehouse, path, weight="weight")

# Print result
for r in robots:
    print(f"Robot {r['id']}: Path = {r['path']}, Cost = {r['cost']}")
</assistant_response>
""",
}

OTHER = {
    "guidelines": """
No specific problem class was identified. Apply general best practices for heuristic-based optimization.

Recommended heuristics by problem family:

- VRP / TSP: Nearest Neighbor, Clarke-Wright, Simulated Annealing, Tabu Search, Genetic Algorithms, Ant Colony Optimization
- Cutting stock: First-Fit Decreasing (FFD), Best-Fit Decreasing (BFD), Simulated Annealing, Genetic Algorithms
- Scheduling: Iterated Local Search (ILS), Variable Neighborhood Search (VNS), Tabu Search, Hyperheuristics
- Multi-objective: NSGA-II (Non-dominated Sorting Genetic Algorithm II)

General advice:
- Use greedy construction methods when applicable
- Combine with local improvement or metaheuristics
- Use problem-specific constraints to prune the solution space

Avoid:
- Applying complex metaheuristics without justification
- Ignoring constraints or objective definition
- Generating trivial solutions (e.g., all items selected, no optimization)
""",
    "example": """
### Example – Heuristic Code Generation (Generic)

Input:
<structured_state id="example-1">
  <user_summary>Allocate resources to minimize total cost across tasks</user_summary>
  <problem_type>Resource allocation</problem_type>
  <problem_class>other</problem_class>
  <optimization_focus>Cost minimization</optimization_focus>
  <goal>Heuristic-based assignment</goal>
  <data>task_input.csv</data>
  <resource_requirements>Task costs and limits</resource_requirements>
  <response_format>CSV</response_format>
</structured_state>

Output:
<assistant_response id="example-1">
# Heuristic used: Greedy allocation based on cost-benefit ratio

import pandas as pd

df = pd.read_csv("task_input.csv")
df["ratio"] = df["benefit"] / df["cost"]
df = df.sort_values(by="ratio", ascending=False)

# Allocate resources to tasks with highest benefit/cost first
selected = []
total_cost = 0
budget = 100

for _, row in df.iterrows():
    if total_cost + row["cost"] <= budget:
        selected.append(row["task_id"])
        total_cost += row["cost"]

print("Selected tasks:", selected)
print("Total cost:", total_cost)
</assistant_response>
""",
}
