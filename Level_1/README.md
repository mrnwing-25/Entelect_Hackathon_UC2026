# 🏆 Level 1 — Level 1

Short overview
- Competition: Entelect Hackathons — University Cup 2
- Level: Level 1
- Challenge identifier: `Level 1` (no explicit challenge name present in the repository)
- Main objective: generate a valid action sequence within the provided tick budget to gather and sell raw resources
- High-level algorithm: graph shortest-paths (Dijkstra) + greedy heuristic that maximises resource value-per-tick (with a baseline fallback)

---

# 🎯 Level Requirements

| Requirement | Value |
|---|---|
| Input file | `1.txt` (loaded by `run load_input()` in code) |
| Start node | Specified by input: `run.starting_town` |
| Towns / Nodes | Varies with input (`towns` and `nodes` objects) |
| Time budget | Specified by input: `run.total_ticks` |
| Actions allowed | travel, gather, sell, buy (buy only validated) |
| Output / submission file | `level1_submission.txt` |

Notes:
- The repository does not include an explicit human-readable challenge name: this README identifies the problem as "Level 1" to match the code and folder.

---

# 📋 Problem Description

This level requires producing a valid sequence of in-game actions that fits within a finite number of ticks. Actions include moving along graph edges (`travel`), gathering resources at resource nodes (`gather`), and selling resources at towns (`sell`). The program must obey the structural and tick-based rules encoded in the input JSON and must not exceed `run.total_ticks`.

What the solver must achieve
- Produce a valid action sequence (list of action objects) that is structurally valid and fits inside the tick budget.
- Prefer higher-value actions so that the generated submission is likely to score well in the official simulator.

Challenges
- The graph may contain many nodes and towns; travel costs make some nodes inefficient compared to others.
- The official competition score is not provided in this repository; the solver therefore uses a local proxy objective (inventory value) to guide optimisation.

Scoring
- The official simulator's score is not available here. The code uses a transparent local proxy: the sum of raw-resource sell prices × remaining inventory quantity (see `calculate_proxy_score()` in [Level_1/level_1.py](Level_1/level_1.py)). This proxy is conservative and intended for local heuristic tuning only.

---

# ⚙️ Input

- Expected input filename: `1.txt` in the working directory (JSON). The code reads this via `load_input("1.txt")`.
- Top-level JSON keys required by the code: `run`, `towns`, `nodes`, `routes`.
- Important `run` fields: `total_ticks`, `starting_town`, `starting_enteloot`.
- `towns` and `nodes` are objects keyed by name. Each `node` must include `resource`, `yield`, and `gather-time`.
- `routes` is an array of routes; each route must include `between` (pair), `weight` and `toll`.

Refer to `load_input()` and `validate_input_structure()` in [Level_1/level_1.py](Level_1/level_1.py) for full validation behaviour.

---

# 🧠 Processing / Algorithm

Core components implemented in `Level_1/level_1.py`:

- Graph building: `build_graph(data)` — builds an undirected adjacency list, ignoring routes with a non-zero `toll` (the level's fast-route mechanic is not used here).
- Shortest paths: `dijkstra(graph, start)` and `calculate_all_routes(data, graph)` — Dijkstra is run from every reachable vertex to compute shortest distances and paths to all other reachable vertices.
- Node evaluation: `evaluate_node(data, node_name, current_location, routes)` — computes a heuristic score for gathering at a node: expected raw sell value divided by estimated time to travel, gather and return.
- Baseline strategy: `generate_baseline(data, routes)` — simple guaranteed-valid strategy (travel to first reachable node, gather once, return and sell).
- Main solver: `solve(data)` — repeatedly selects the best candidate node (by deterministic tie-breaks on value-per-tick and other heuristics), calculates how many gathers to perform on that trip, returns to town and sells. The solver keeps a running best-action sequence according to the local proxy objective.

Adaptive gathering improvement (implemented in repository)
- The solver no longer always uses the maximum possible number of gathers for a trip. Instead, for each candidate it evaluates gather counts `g ∈ [1..possible_gathers]` and chooses the `g` that maximises trip value-per-tick (trip value = g × yield × raw price; trip ticks = travel + g × gather_time + return + sell). This balances long trips against diminishing returns and preserves ticks for higher-value future trips.

Proxy objective
- The code uses `calculate_proxy_score()` which computes the inventory raw-value by summing `quantity × RESOURCE_SELL_PRICES[resource]` for the remaining inventory. The solver keeps the best action prefix seen according to that proxy.

---

# 🐍 Python Implementation

- Main script: [Level_1/level_1.py](Level_1/level_1.py)
  - Entry point: `main()` — loads input, builds graph/routes, prints diagnostics, runs `solve()` and writes `level1_submission.txt` using `create_submission()`.
  - Important functions: `load_input`, `validate_input_structure`, `build_graph`, `dijkstra`, `calculate_all_routes`, `evaluate_node`, `solve`, `validate_solution`, `generate_baseline`, `calculate_proxy_score`, `create_submission`.
- Notebook: [Level_1/Level_1.ipynb](Level_1/Level_1.ipynb) (present in repository — may contain development notes). The README does not assume additional notebook-derived artefacts.

Dependencies
- The implementation uses only the Python standard library (`json`, `heapq`, `math`, `time`, `collections`). No external packages are required.

---

# 🧾 Why this algorithm was chosen

- Dijkstra for shortest paths is a correct, deterministic method to compute travel costs on weighted graphs; the code precomputes all pairs by running Dijkstra from every vertex to avoid repeated pathfinding during simulation.
- The problem is combinatorial and time-limited; an exact search (full state-space exploration) would be expensive. The implemented greedy heuristic (value-per-tick) provides a simple, explainable rule that produces valid, good-quality trips quickly.
- The adaptive gathering improvement addresses a common pitfall of greedy approaches (always fill a trip): by choosing the gather count that maximises value-per-tick for that single trip, the solver preserves time for higher-value future opportunities.

---

# 📤 Output / Submission

- Primary generated file: `level1_submission.txt` (JSON) created by `create_submission(actions, "level1_submission.txt")`.
- The submission file structure is:

```json
{
  "actions": [ /* array of action objects */ ]
}
```

- The program also prints diagnostics to stdout (baseline stats, optimised action counts, ticks used, remaining ticks, final inventory and location, runtime).

---

# ▶️ How to run the solution

From repository root (or `Level_1` directory):

```bash
python "Level_1/level_1.py"
```

Notes:
- The script expects `1.txt` to be present in the working directory. If your input file has a different name, edit the call to `load_input()` in `main()` or pass/modify the code accordingly.
- Python 3.8+ recommended; no third-party packages required.

Validation
- The script contains a local validator `validate_solution(data, actions)` that checks action structure and tick budget. You can call it directly from Python to validate custom action sequences.

---

# 📁 Generated files

- `level1_submission.txt` — the submission output (JSON) produced by the script.
- Console log containing diagnostics printed by `main()`.

---

# ⏱ Complexity

- Graph build: O(R) where R = number of routes (edges) to build adjacency lists.
- All-pairs shortest path (implemented as Dijkstra from every vertex): running Dijkstra V times gives approximately O(V × (E log V)) using a binary heap, where V is the number of reachable vertices and E is the number of edges.
- In `solve()`: each iteration scans all nodes to build candidates (O(N)), sorts candidates (O(N log N)), and evaluates gather-count loops per candidate. The number of solver iterations is bounded by how ticks are consumed; worst-case behaviour depends on `total_ticks` and node parameters.

Overall: the dominant cost is the repeated Dijkstra runs in `calculate_all_routes()` for dense/large graphs; the greedy solver is substantially cheaper than exhaustive search.

---

# ✅ Testing and Results

- The repository does not include official simulator scores or benchmarked results. No validated score or enteloot result is stored here.
- You can locally test and inspect behaviour by running the script with your `1.txt` input. The code prints baseline and optimised action counts and tick usage; use those to compare strategies.

Suggested quick checks
- Run the solver and inspect `level1_submission.txt`.
- Call `validate_solution(data, actions)` directly in a small driver to confirm ticks and inventory.

---

# Appendix — Relevant files

- [Level_1/level_1.py](Level_1/level_1.py) — solver implementation
- [Level_1/Level_1.ipynb](Level_1/Level_1.ipynb) — development notebook (present in repository)
- Input example: `1.txt` — expected to be in the working directory when running the script

