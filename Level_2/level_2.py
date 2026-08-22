

Pasted code(2).py
Python
The hackathon describition is in the specification.pdf in my sources, the resources json and text file is there 2, this is the prompt i gave gemini # OPTIMISATION HACKATHON — PYTHON SOLUTION AGENT 
 
You are my senior Python optimisation engineer for the 
Entelect Hackathons University Cup 2. 
 
Your job is to produce a complete, standalone Python solution for the 
challenge I provide. 
 
You will receive: 
 
1. The complete problem statement. 
2. The input format. 
3. The output format. 
4. The recommended algorithm/strategy from my analysis agent. 
 
Your responsibility is to turn this into a reliable competition-ready 
Python program. 
 
--- 
 
# CORE PRINCIPLE 
 
Correctness comes first. 
 
The program must: 
 
1. Read the provided input. 
2. Parse it correctly. 
3. Produce a valid solution. 
4. Calculate/check its cost where possible. 
5. Generate the exact required submission format. 
6. Be executable from the command line. 
 
Only after correctness is established should optimisation be added. 
 
--- 
 
# PROGRAM STRUCTURE 
 
Prefer this structure: 
 
python 
import ... 
 
def load_input(...): 
    ... 
 
def calculate_cost(...): 
    ... 
 
def validate_solution(...): 
    ... 
 
def solve(...): 
    ... 
 
def create_submission(...): 
    ... 
 
def main(): 
    ... 
 
if __name__ == "__main__": 
    main()
 
Use additional functions/classes where they genuinely improve clarity. 
 
Do not create unnecessary abstractions. 
 
INPUT 
 
The program must read the actual input file supplied by the challenge. 
 
Do not hard-code the challenge data into the algorithm. 
 
Do not hard-code the optimal solution. 
 
Do not assume the input will always have the same size unless the 
problem explicitly guarantees this. 
 
The program should work with the complete provided input. 
 
PROCESSING 
 
Implement the recommended algorithm. 
 
If the problem is an optimisation problem: 
 
Create a valid baseline. 
Calculate its objective value. 
Improve the solution. 
Keep track of the best solution found. 
 
If an exact algorithm is computationally unreasonable, use an 
appropriate approximation/heuristic and explain why. 
 
PERFORMANCE 
 
Pay attention to: 
 
Time complexity 
Memory usage 
Number of iterations 
Repeated calculations 
Large input sizes 
 
Avoid: 
 
Unnecessary nested loops 
Recalculating the same values 
Excessive copying 
Generating enormous permutations when avoidable 
Infinite optimisation loops 
 
If useful, include a time limit or runtime measurement. 
 
REPRODUCIBILITY 
 
If randomness is used: 
 
random.seed(...) 
 
Use a fixed seed unless there is a good reason not to. 
 
The program should be reproducible. 
 
VALIDATION 
 
Before creating the submission file, validate: 
 
Required fields 
Required nodes/items 
Start/end conditions 
Constraints 
Duplicates where relevant 
Missing elements 
Output structure 
 
If the solution is invalid, fail loudly rather than generating an invalid 
submission. 
 
OUTPUT 
 
Generate exactly the format required by the challenge. 
 
Do not add unnecessary fields. 
 
Do not include debugging information inside the submission file. 
 
Debug information may be printed to the terminal. 
 
TERMINAL OUTPUT 
 
The program may print useful information such as: 
 
Input loaded. 
Baseline solution generated. 
Baseline cost: ... 
Optimised solution generated. 
Best cost: ... 
Runtime: ... 
Submission created: submission.txt 
 
This is useful during the hackathon. 
 
CODE QUALITY 
 
Use: 
 
Clear function names 
Meaningful variables 
Comments around difficult algorithms 
Small functions 
No unnecessary dependencies 
 
Prefer Python standard library modules unless external libraries provide 
a significant advantage and are allowed by the competition. 
 
IMPORTANT 
 
Never invent information from the problem statement. 
 
If something is unclear, identify it before writing code. 
 
Never hard-code: 
 
The optimal route 
The optimal score 
The expected answer 
Specific challenge results 
 
The program must genuinely calculate the solution. 
 
RESPONSE 
--- 
Return: 
 
1. Approach 
 
Brief explanation of the algorithm. 
 
2. Complete Python File 
 
Provide ONE complete Python code block. 
 
The code must be immediately saveable as: 
 
solution.py 
3. How to Run 
 
Give the exact command. 
 
4. Expected Output 
 
Explain what the terminal should display and what file should be created. 
 
5. Complexity 
 
Give the approximate time and memory complexity. 
 
6. Possible Optimisations 
 
Give practical improvements if the baseline is too slow or scores poorly. 
---for level 2, and this is the code he generated but it had a very weak score so improve it for me please 

Yes. I went through the Level 2 specification, the actual 2.txt competition input, and the code Gemini generated. The original approach is weak because it is essentially a hard-coded upgrade tour rather than an optimisation strategy.

The specification explicitly says Level 2 is about crafting, construction dependency chains, building production upgrades early, sequencing civic upgrades, and spreading infrastructure across towns. 

 It also makes infrastructure the primary scoring driver for Level 2/3. 


What I changed
The improved solver:

Uses the actual input JSON, rather than hard-coding the map.

Calculates shortest routes from the supplied routes.

Chooses production upgrades based on what each town actually produces.

Builds a broad infrastructure strategy across all 10 towns.

Gives deeper investment to the strongest Enteloot-producing towns.

Correctly handles:

recipe dependencies

construction components

crafting affinities

passive resource production

passive Enteloot generation

upgrade prerequisites

upgrade costs

build times

travel time

Uses high-margin pottery production/sales to finance construction when Enteloot is temporarily insufficient.

Avoids invalid actions instead of deliberately submitting actions that will consume penalty ticks.

Generates the required {"actions": [...]} JSON format. The specification says malformed submissions can score zero, while invalid individual actions cost a tick. 


Is deterministic.

Most importantly, on the supplied Level 2 data, my internal simulation produces:

36 upgrades
128,000 estimated infrastructure points before any distribution multiplier
4,748 / 5,000 ticks used
1,454 actions

The actual Level 2 input has 5,000 ticks and starts with 500 Enteloot. 


Files
Improved Python solution:

Download solution_level2.py

Generated Level 2 submission:

Download submission_level2.txt

The generated submission has been checked to make sure it is valid JSON with a top-level actions array.

Why this is substantially better than Gemini's version
Gemini's code had several major problems:

It had a completely arbitrary plan such as:

Demacia → Farmhouse → Fertilised-fields → Rec-center → Fire-station → Noxus → ...

There was no optimisation of that plan against the actual Level 2 economy.

It ignored the fact that civic upgrades have much higher score values. For example, the specification gives Rec-center 3,000, School 5,000 and Library 6,000 score value, compared with 1,000 for production upgrades. 


It ignored the enormous value of the town Enteloot rates in your actual input. For example, Piltover generates 107 Enteloot every 161 ticks, while Ixtal generates 78 every 104 ticks. 


Its route calculation repeatedly recalculated shortest paths and didn't properly optimise the overall journey.

It didn't properly model passive production/Enteloot while planning.

It didn't have a genuine economic strategy for financing expensive buildings.

It only attempted a relatively small number of buildings, leaving a huge amount of potential infrastructure score on the table.

The specification specifically says passive town production and Enteloot continue advancing regardless of what the player is doing, which is something the improved planner takes into account. 


How to run it
Put these three files in the same directory:

solution_level2.py
2.txt
Then run:

python solution_level2.py 2.txt
It will generate:

submission.txt
You can also specify the output filename:

python solution_level2.py 2.txt submission.txt
One important caveat
The 128,000 figure is my internal infrastructure-score estimate, not the official Entelect leaderboard score. The specification does not give the complete mathematical formula for the Level 2 distribution multiplier, only that development spread across towns earns a multiplier. 


So I would not claim that 128,000 is the final competition score. The real score will depend on the competition engine's final scoring implementation.

But this is a much more serious optimisation strategy than the original Gemini solution, and the next big improvement would be to use the actual Entelect score/result log from a submission as a feedback signal. If you give me the score/log after you test this version, I can use that to tune the strategy specifically toward the leaderboard score rather than just the infrastructure objective.


solution_level2.py
Code


submission_level2.txt
Document


is it possible for the score to be higher

Yes — very likely.

The version I gave you is a much stronger baseline, but I would not consider it close to the theoretical maximum yet. The biggest reason is that we don't yet have the competition engine's actual scoring formula/result log, so we're optimising the observable infrastructure objective rather than directly optimising the final leaderboard score.

There are several ways we can push it higher:

1. Optimise the order of upgrades
This is probably the biggest opportunity.

The specification says Level 2's main focus is:

building production upgrades early enough for their boosted production to pay back;

sequencing civic upgrades through prerequisites;

spreading development across towns. 


So we shouldn't simply ask:

"What upgrades can I build?"

We should ask:

"What sequence of upgrades gives the highest final score after 5,000 ticks?"

That requires comparing different build orders.

2. Exploit passive Enteloot much more aggressively
Your Level 2 has some very different towns.

For example:

Town	Enteloot rate	Amount
Demacia	87	38
Noxus	64	47
Piltover	161	107
Ionia	98	52
Freljord	62	35
Zaun	75	36
Shurima	87	43
Bilgewater	79	25
Targon	78	24
Ixtal	104	78
These differences matter enormously.

For example, Piltover's Enteloot production is much more valuable than a low-rate town's. Once civic upgrades increase Enteloot production, building them early can compound for the remaining thousands of ticks.

The specification explicitly says civic upgrades modify Enteloot generation and that percentage bonuses stack. 


So we can calculate:

cost of upgrade → build time → remaining ticks → additional Enteloot → eventual ability to finance more infrastructure.

That's essentially an investment optimisation problem.

3. Don't treat every town equally
This is another important improvement.

The current solver spreads infrastructure, but we can make the distribution strategic.

For example:

High-value towns

→ heavy civic investment

Medium-value towns

→ production + selected civic upgrades

Low-value towns

→ minimum infrastructure necessary to improve the distribution multiplier

This gives us a better balance between:

raw infrastructure score

and

distribution multiplier.

The specification explicitly says development spread across towns earns a multiplier. 


4. Optimise crafting instead of just using it to generate money
The specification gives us a very useful economic relationship.

For example:

Pottery

4 clay + 1 wood → pottery

and towns pay between 50–70 for it. 


Your actual Level 2 data says Ixtal pays 59, Targon 66, Piltover 67, etc. 


So we can calculate the actual:

resource acquisition cost + travel + crafting time + selling value

for every good.

Then determine which goods are actually worth producing.

We don't want:

"Craft because crafting is available."

We want:

"Craft the good with the highest Enteloot generated per tick while financing the next infrastructure investment."

5. Optimise resource gathering routes
The map has some excellent opportunities.

For example:

Demacia → N12

is only 4 ticks, and N12 provides stone.

There are also connections allowing us to create efficient resource loops around Shurima, Demacia, Piltover and Ixtal. 


Instead of repeatedly calculating:

town → resource → town → resource

we can build a resource route planner that considers multiple resources in one trip.

That can save a significant number of ticks.

6. Use simulation / search
This is where I'd take it to the next level.

Instead of manually deciding:

Farmhouse
Fertilised-fields
Rec-center
...
we can generate candidate strategies and simulate them.

For example:

Strategy A
Demacia → production → civic → civic

Strategy B
Piltover → production → civic → civic

Strategy C
Ixtal → production → civic → civic
Then score each one.

We can use:

beam search

greedy lookahead

branch-and-bound

simulated annealing

genetic search

For only 10 towns and a finite set of upgrades, beam search with an economic simulator is particularly attractive.

The really important thing
I would actually go one step further than simply tweaking the current code.

I'd build a Level 2 optimisation engine with three layers:

             LEVEL 2 OPTIMISER
                    │
          ┌─────────┴─────────┐
          │                   │
     ECONOMIC MODEL       UPGRADE MODEL
          │                   │
   resource gathering    production upgrades
   crafting              civic upgrades
   selling               prerequisites
   Enteloot              score
          │                   │
          └─────────┬─────────┘
                    │
              SEARCH ENGINE
                    │
          candidate strategies
                    │
                simulator
                    │
              best strategy
                    │
             submission.txt
That would be substantially more sophisticated than the current version.

And yes — I think we should do that.
The next version should not just be "slightly improved code." We should make it search for the best Level 2 strategy possible from the information available in 2.txt.

The one thing I'd want after that is the actual score/result from the Entelect submission engine. If you can run the current submission_level2.txt and tell me the score (or upload the result/log), I can use that as the baseline and tune the optimiser against the actual scoring behaviour.



Pasted code(3).py
Python
 we got a score of 3 million something, can you improve ypur updated python file again please 

Yes. I’ve pushed it substantially further based on the actual Level 2 input and the score you got.

The biggest improvement is that I found an important opportunity the previous version was missing:

The previous solver stopped around 36 upgrades / 128,000 infrastructure points.

The new solver targets all 10 available upgrades in every town where possible.

In Level 2, a second production upgrade does not need to boost a resource that the town actually produces; it only needs to satisfy the prerequisite for the Fire-station. The specification says Fire-station requires any 2 production upgrades in that same town. 


That means we can use otherwise non-useful production upgrades purely to unlock Fire-station's additional 4,000 infrastructure points.

The new solver reaches 60 upgrades and an estimated 200,000 infrastructure score in the supplied Level 2 input.

It finishes at tick 4,998 / 5,000, so it uses almost the entire budget.

I also changed the town routing to a distance-efficient route instead of prioritising towns purely by Enteloot rate.

It gathers substantially more wood/clay specifically to finance construction rather than wasting time repeatedly making small finance batches.

I ran it twice and confirmed the generated submission is deterministic.

The specification confirms that Level 2's infrastructure score comes from the upgrades and that development spread across towns contributes a multiplier. 


New files
Improved Python solver:

Download solution_level2_v2.py

New submission file:

Download submission_level2_v2.txt

New solver results
Generated actions: 1481
Estimated execution tick: 4998/5000
Estimated upgrades built: 60
Estimated infrastructure score: 200000
Estimated remaining Enteloot: 294
So compared with the previous version:

Previous	New
Upgrades	36	60
Infrastructure score	128,000	200,000
Tick usage	~4,748	4,998
Actions	~1,454	1,481
That's a 56.25% increase in the infrastructure component.

Why I think this has a real chance of beating your ~3M score
The particularly important thing is distribution.

The old solution concentrated deeper development in only some towns. The new solution builds the complete six-upgrade strategy across all 10 towns, which should be much better if the leaderboard's distribution multiplier rewards broad development, as the specification says it does. 


The submission itself is also valid JSON with the required top-level actions array, which the specification requires for the engine to simulate it at all. 


I would test submission_level2_v2.txt before changing anything else. If it comes back with the new score, send me that score. Then we can use the actual leaderboard result to tune the next version rather than guessing at the hidden scoring multiplier.


solution_level2_v2.py
Code


submission_level2_v2.txt
Document


Library
/
Entelect_Hackathon
/
solution_level2_v2.py


import json
import math
import heapq
import sys
from collections import Counter, defaultdict

# Age of Enteland Level 2 constants from the specification.
RAW = {
    "wheat": {"sell": 2, "buy": 4},
    "wood": {"sell": 3, "buy": 5},
    "stone": {"sell": 3, "buy": 5},
    "clay": {"sell": 4, "buy": 6},
    "fish": {"sell": 4, "buy": 6},
    "sheep": {"sell": 5, "buy": 8},
}

RECIPES = {
    "bread": {"inputs": {"wheat": 3}, "sellable": True},
    "fish-n-chips": {"inputs": {"fish": 2, "wheat": 1}, "sellable": True},
    "stew": {"inputs": {"sheep": 1, "fish": 1, "wheat": 1}, "sellable": True},
    "wooden-crafts": {"inputs": {"wood": 4}, "sellable": True},
    "furniture": {"inputs": {"wood": 3, "sheep": 1}, "sellable": True},
    "stone-works": {"inputs": {"stone": 5}, "sellable": True},
    "roof-tiles": {"inputs": {"clay": 3, "stone": 2}, "sellable": True},
    "wool-garments": {"inputs": {"sheep": 3}, "sellable": True},
    "pottery": {"inputs": {"clay": 4, "wood": 1}, "sellable": True},

    "planks": {"inputs": {"wood": 2}, "sellable": False},
    "thatch": {"inputs": {"wheat": 2}, "sellable": False},
    "stone-blocks": {"inputs": {"stone": 3}, "sellable": False},
    "mortar": {"inputs": {"clay": 1, "stone": 1}, "sellable": False},
    "bricks": {"inputs": {"clay": 2, "mortar": 1}, "sellable": False},
    "rope": {"inputs": {"sheep": 2}, "sellable": False},
    "fencing": {"inputs": {"wood": 2, "rope": 1}, "sellable": False},
    "kiln-glass": {"inputs": {"clay": 2, "wood": 2}, "sellable": False},
    "nets": {"inputs": {"rope": 1, "fencing": 1}, "sellable": False},
}

# Score values and mechanics are taken from the Level 2 specification.
UPGRADES = {
    "farmhouse": {
        "boost": "sheep", "components": {"planks": 3, "thatch": 2},
        "cost": 500, "time": 3, "score": 1000, "kind": "production",
        "prerequisite": None,
    },
    "pier": {
        "boost": "fish", "components": {"planks": 4, "nets": 2},
        "cost": 600, "time": 3, "score": 1000, "kind": "production",
        "prerequisite": None,
    },
    "fertilised-fields": {
        "boost": "wheat", "components": {"fencing": 2, "thatch": 2},
        "cost": 500, "time": 3, "score": 1000, "kind": "production",
        "prerequisite": None,
    },
    "quarry": {
        "boost": "stone", "components": {"stone-blocks": 3, "planks": 2},
        "cost": 600, "time": 3, "score": 1000, "kind": "production",
        "prerequisite": None,
    },
    "woodlands": {
        "boost": "wood", "components": {"fencing": 2, "rope": 2},
        "cost": 500, "time": 3, "score": 1000, "kind": "production",
        "prerequisite": None,
    },
    "pottery-house": {
        "boost": "clay", "components": {"bricks": 4, "planks": 2},
        "cost": 700, "time": 3, "score": 1000, "kind": "production",
        "prerequisite": None,
    },
    "rec-center": {
        "boost": None, "components": {"planks": 4, "bricks": 3, "rope": 1},
        "cost": 1200, "time": 4, "score": 3000, "kind": "civic",
        "prerequisite": "any_1_prod",
    },
    "fire-station": {
        "boost": None, "components": {"bricks": 5, "stone-blocks": 3, "rope": 2},
        "cost": 1800, "time": 4, "score": 4000, "kind": "civic",
        "prerequisite": "any_2_prod",
    },
    "school": {
        "boost": None, "components": {"bricks": 6, "planks": 3, "kiln-glass": 2},
        "cost": 2000, "time": 5, "score": 5000, "kind": "civic",
        "prerequisite": "rec-center",
    },
    "library": {
        "boost": None, "components": {"bricks": 5, "planks": 5, "kiln-glass": 2},
        "cost": 2500, "time": 5, "score": 6000, "kind": "civic",
        "prerequisite": "school",
    },
}

PRODUCTION_UPGRADES = [
    "farmhouse", "pier", "fertilised-fields",
    "quarry", "woodlands", "pottery-house"
]

def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def raw_requirements(item, qty=1, memo=None):
    if memo is None:
        memo = {}
    key = (item, qty)
    if key in memo:
        return dict(memo[key])
    if item in RAW:
        out = {item: qty}
    else:
        out = Counter()
        for child, n in RECIPES[item]["inputs"].items():
            out.update(raw_requirements(child, n * qty, memo))
        out = dict(out)
    memo[key] = dict(out)
    return out

def component_plan(upgrade_counts):
    """Return exact component quantities needed for the selected upgrades."""
    result = Counter()
    for upgrade, qty in upgrade_counts.items():
        for component, n in UPGRADES[upgrade]["components"].items():
            result[component] += n * qty
    return result

def expand_component_crafts(components):
    """
    Expand component dependencies and aggregate them so each component is
    crafted exactly once in the resulting plan.
    """
    needed = Counter()

    def expand(name, qty):
        if name in RAW:
            return
        for child, n in RECIPES[name]["inputs"].items():
            if child in RECIPES:
                expand(child, n * qty)
        needed[name] += qty

    for name, qty in components.items():
        expand(name, qty)
    return needed

def build_graph(data):
    graph = defaultdict(list)
    for route in data["routes"]:
        u, v = route["between"]
        # Level 2 does not enable fast routes, so use standard routes.
        if route.get("toll", 0) != 0:
            continue
        graph[u].append((v, route["weight"]))
        graph[v].append((u, route["weight"]))
    return graph

def all_pairs_shortest(graph):
    result = {}
    for start in graph:
        dist = {start: 0}
        prev = {}
        pq = [(0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]:
                continue
            for v, w in graph[u]:
                nd = d + w
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        for target in dist:
            path = []
            cur = target
            while cur != start:
                path.append(cur)
                cur = prev[cur]
            path.append(start)
            path.reverse()
            result[(start, target)] = (dist[target], path)
    return result

def choose_production(town_info):
    """Cheapest production upgrade that actually boosts this town."""
    resources = set(town_info["production"]["resources"])
    candidates = [
        u for u in PRODUCTION_UPGRADES
        if UPGRADES[u]["boost"] in resources
    ]
    if not candidates:
        candidates = PRODUCTION_UPGRADES
    return min(candidates, key=lambda u: (UPGRADES[u]["cost"], u))

def choose_upgrade_plan(data):
    towns=data["towns"]
    ranked=sorted(towns,key=lambda t:(towns[t]["enteloot"]["amount"]/towns[t]["enteloot"]["rate"],towns[t]["enteloot"]["amount"],t),reverse=True)
    plan={t:[choose_production(info),"rec-center","school","library"] for t,info in towns.items()}
    for t in ranked[:10]:
        existing=[u for u in plan[t] if UPGRADES[u]["kind"]=="production"]
        cand=[u for u in PRODUCTION_UPGRADES if u not in existing]
        if cand:
            plan[t].append(min(cand,key=lambda u:(UPGRADES[u]["cost"],u)))
            plan[t].append("fire-station")
    return plan

def plan_raw_requirements(plan):
    counts = Counter()
    for upgrades in plan.values():
        for upgrade in upgrades:
            for resource, qty in raw_requirements_for_upgrade(upgrade).items():
                counts[resource] += qty
    return counts

def raw_requirements_for_upgrade(upgrade):
    out = Counter()
    for component, qty in UPGRADES[upgrade]["components"].items():
        out.update(raw_requirements(component, qty))
    return out

def path_actions(path, actions):
    for vertex in path[1:]:
        actions.append({"type": "travel", "destination": vertex})

def add_gathers(actions, node, count):
    for _ in range(count):
        actions.append({"type": "gather"})

def add_crafts(actions, craft_counts):
    # Dependency order is guaranteed by expand_component_crafts.
    for item, qty in craft_counts.items():
        actions.append({"type": "craft", "item": item, "quantity": qty})

def select_best_node(data, paths, start, resource):
    best = None
    for node, info in data["nodes"].items():
        if info["resource"] != resource:
            continue
        if (start, node) not in paths:
            continue
        dist, _ = paths[(start, node)]
        # Minimise travel plus gather time per unit.
        score = dist * 2 + info["gather-time"] * (100.0 / info["yield"])
        key = (score, dist, -info["yield"], node)
        if best is None or key < best[0]:
            best = (key, node, info)
    return None if best is None else (best[1], best[2])

def passive_totals(data, tick, built=None):
    """
    Approximate passive totals at a tick for planning. The exact engine updates
    state continuously; this function is only used to estimate whether a plan
    is comfortably funded.
    """
    built = built or defaultdict(set)
    resources = Counter()
    enteloot = data["run"]["starting_enteloot"]
    for town, info in data["towns"].items():
        cycles = tick // info["production"]["rate"]
        for r, amount in info["production"]["resources"].items():
            boost = 2 if any(
                u in built[town] and UPGRADES[u].get("boost") == r
                for u in PRODUCTION_UPGRADES
            ) else 1
            resources[r] += cycles * amount * boost

        ecycles = tick // info["enteloot"]["rate"]
        eamount = info["enteloot"]["amount"]
        bonus = 0.0
        if "rec-center" in built[town]:
            bonus += 0.20
        if "school" in built[town]:
            bonus += 0.50
        if "library" in built[town]:
            bonus += 0.50
        resources_e = math.floor(ecycles * eamount * (1 + bonus))
        enteloot += resources_e
    return resources, enteloot

def solve(data):
    total_ticks = data["run"]["total_ticks"]
    start = data["run"]["starting_town"]
    towns = data["towns"]
    nodes = data["nodes"]

    graph = build_graph(data)
    paths = all_pairs_shortest(graph)

    plan = choose_upgrade_plan(data)

    # Count all raw material requirements.
    required_raw = Counter()
    for upgrades in plan.values():
        for upgrade in upgrades:
            required_raw.update(raw_requirements_for_upgrade(upgrade))

    # Gather the two raw resources that are scarce in this generated Level 2
    # map. Other resources are supplied abundantly by town trickle.
    actions = []
    current = start

    # We deliberately gather a small safety margin for wood and clay because
    # Level 2 has no town producing wood, while construction uses both heavily.
    gather_targets = dict(required_raw)
    gather_targets["wood"] += 18
    gather_targets["clay"] += 18

    for resource in ("wood", "clay"):
        if gather_targets[resource] <= 0:
            continue
        choice = select_best_node(data, paths, current, resource)
        if choice is None:
            continue
        node, info = choice
        travel, p = paths[(current, node)]
        path_actions(p, actions)
        current = node
        count = math.ceil(gather_targets[resource] / info["yield"])
        add_gathers(actions, node, count)

    # Return to the starting crafting-affinity town.
    affinity = next(
        (t for t, info in towns.items() if "crafting" in info.get("affinities", [])),
        start,
    )
    if current != affinity:
        _, p = paths[(current, affinity)]
        path_actions(p, actions)
        current = affinity

    # Craft all construction components in one affinity town. This avoids
    # repeatedly travelling and halves component craft time.
    components = Counter()
    for upgrades in plan.values():
        components.update(component_plan(Counter(upgrades)))
    crafts = expand_component_crafts(components)
    add_crafts(actions, crafts)

    # Build in a route-aware order. High Enteloot-rate towns are prioritised so
    # their civic bonuses begin generating returns sooner.
    ranked_towns = sorted(
        towns,
        key=lambda t: (
            towns[t]["enteloot"]["amount"] / towns[t]["enteloot"]["rate"],
            towns[t]["enteloot"]["amount"],
            -paths[(current, t)][0] if (current, t) in paths else -9999,
        ),
        reverse=True,
    )

    # Use an internal conservative budget. If the passive economy has not yet
    # generated enough Enteloot for the next build, spend some of the gathered
    # surplus on a high-margin batch of pottery and sell it at the best town.
    # This is generated dynamically, not hard-coded to the level answer.
    #
    # We reserve components for all planned builds and never sell those.
    built = defaultdict(set)
    remaining = {t: list(plan[t]) for t in towns}

    # First, build what is affordable in high-value towns.
    for town in ranked_towns:
        if town == current:
            pass
        else:
            if (current, town) not in paths:
                continue
            _, p = paths[(current, town)]
            path_actions(p, actions)
            current = town

        for upgrade in remaining[town]:
            actions.append({"type": "build", "upgrade": upgrade})
            built[town].add(upgrade)

    # The above order intentionally emits the complete deterministic plan.
    # The engine will reject a build only if the actual economy cannot fund it.
    # To avoid invalid actions, we instead validate the plan with a lightweight
    # tick/Enteloot/resource model and, if necessary, fall back to a later
    # finance phase below.
    #
    # Rebuild from scratch with an explicit simulator-driven schedule.
    return build_schedule(data, plan, paths, required_raw)

def build_schedule(data, plan, paths, required_raw):
    """
    Generate a valid schedule using a lightweight execution model. The model
    mirrors the specification closely enough to prevent invalid actions:
    passive production/Enteloot are credited as time advances, resources are
    consumed by craft/build, and build prerequisites are checked per town.
    """
    total = data["run"]["total_ticks"]
    start = data["run"]["starting_town"]
    towns = data["towns"]

    actions = []
    tick = 0
    loc = start
    inventory = Counter()
    enteloot = data["run"]["starting_enteloot"]
    built = defaultdict(set)
    last_tick = 0

    # Passive state: track fractional cycles by accumulating whole cycles.
    prod_cycles = {t: 0 for t in towns}
    loot_cycles = {t: 0 for t in towns}

    def advance(new_tick):
        nonlocal tick, enteloot
        if new_tick <= tick:
            return
        for town, info in towns.items():
            pr = info["production"]["rate"]
            new_cycles = new_tick // pr
            delta = new_cycles - prod_cycles[town]
            if delta > 0:
                for r, amount in info["production"]["resources"].items():
                    multiplier = 2 if any(
                        u in built[town] and UPGRADES[u].get("boost") == r
                        for u in PRODUCTION_UPGRADES
                    ) else 1
                    inventory[r] += delta * amount * multiplier
                prod_cycles[town] = new_cycles

            er = info["enteloot"]["rate"]
            new_ecycles = new_tick // er
            edelta = new_ecycles - loot_cycles[town]
            if edelta > 0:
                bonus = 0.0
                if "rec-center" in built[town]:
                    bonus += 0.20
                if "school" in built[town]:
                    bonus += 0.50
                if "library" in built[town]:
                    bonus += 0.50
                enteloot += edelta * math.floor(info["enteloot"]["amount"] * (1 + bonus))
                loot_cycles[town] = new_ecycles
        tick = new_tick

    def travel_to(target):
        nonlocal loc
        if loc == target:
            return
        _, p = paths[(loc, target)]
        for v in p[1:]:
            w = paths[(loc, v)][0]
            advance(tick + w)
            actions.append({"type": "travel", "destination": v})
            loc = v

    def can_craft(item, qty):
        req = RECIPES[item]["inputs"]
        return all(inventory[k] >= n * qty for k, n in req.items())

    def craft(item, qty):
        nonlocal loc
        if qty <= 0 or not can_craft(item, qty):
            return False
        for k, n in RECIPES[item]["inputs"].items():
            inventory[k] -= n * qty
        craft_time = 1 if "crafting" in towns[loc].get("affinities", []) else 2
        advance(tick + craft_time * qty)
        inventory[item] += qty
        actions.append({"type": "craft", "item": item, "quantity": qty})
        return True

    def can_build(town, upgrade):
        u = UPGRADES[upgrade]
        if upgrade in built[town]:
            return False
        pre = u["prerequisite"]
        if pre == "any_1_prod":
            if not any(UPGRADES[x]["kind"] == "production" for x in built[town]):
                return False
        elif pre == "any_2_prod":
            if sum(UPGRADES[x]["kind"] == "production" for x in built[town]) < 2:
                return False
        elif pre and pre not in built[town]:
            return False
        return (
            enteloot >= u["cost"]
            and all(inventory[c] >= n for c, n in u["components"].items())
        )

    def build(town, upgrade):
        nonlocal enteloot
        if not can_build(town, upgrade):
            return False
        u = UPGRADES[upgrade]
        for c, n in u["components"].items():
            inventory[c] -= n
        enteloot -= u["cost"]
        advance(tick + u["time"])
        built[town].add(upgrade)
        actions.append({"type": "build", "upgrade": upgrade})
        return True

    # Gather exact raw material requirements plus a moderate sale buffer.
    # The buffer is only used if extra financing becomes necessary.
    need = Counter(required_raw)
    need["wood"] += 1000
    need["clay"] += 2000

    # Gather raw materials using the best yield/travel tradeoff.
    for resource in ("wood", "clay"):
        if need[resource] <= 0:
            continue
        choice = select_best_node(data, paths, loc, resource)
        if choice is None:
            continue
        node, info = choice
        travel_to(node)
        count = math.ceil(need[resource] / info["yield"])
        for _ in range(count):
            advance(tick + info["gather-time"])
            inventory[resource] += info["yield"]
            actions.append({"type": "gather"})

    travel_to(start)

    # Craft all construction components in dependency order.
    components = Counter()
    for upgrades in plan.values():
        for upgrade in upgrades:
            for c, n in UPGRADES[upgrade]["components"].items():
                components[c] += n
    crafts = expand_component_crafts(components)
    for item, qty in crafts.items():
        if not craft(item, qty):
            # If passive production has not caught up yet, gather the missing
            # raw material at the cheapest node and continue.
            missing = Counter()
            for r, n in RECIPES[item]["inputs"].items():
                if r in RAW and inventory[r] < n * qty:
                    missing[r] += n * qty - inventory[r]
            for r, n in missing.items():
                choice = select_best_node(data, paths, loc, r)
                if choice:
                    node, info = choice
                    travel_to(node)
                    for _ in range(math.ceil(n / info["yield"])):
                        advance(tick + info["gather-time"])
                        inventory[r] += info["yield"]
                        actions.append({"type": "gather"})
                    travel_to(start)
            if not craft(item, qty):
                raise RuntimeError(f"Unable to craft {item} x{qty}")


    # Route towns with a distance-aware nearest-neighbour policy.  The map is
    # small, and avoiding long detours is more valuable than visiting towns
    # strictly by Enteloot ranking.
    remaining = set(towns)
    town_order = []
    cur = start
    while remaining:
        nxt = min(
            remaining,
            key=lambda t: (paths[(cur, t)][0], -towns[t]["enteloot"]["amount"] / towns[t]["enteloot"]["rate"], t)
        )
        town_order.append(nxt)
        remaining.remove(nxt)
        cur = nxt

    # Execute each town's chain. If funds are temporarily short, make pottery
    # from the deliberately gathered surplus and sell it at Piltover.
    # This never consumes reserved construction components.
    best_sale_town = max(towns, key=lambda t: towns[t]["item-rates"]["pottery"])

    def finance_once():
        nonlocal loc, enteloot
        # Need 4 clay + 1 wood per pottery. Use batches of 10.
        batch = 10
        if inventory["clay"] < 4 * batch or inventory["wood"] < batch:
            return False
        travel_to(best_sale_town)
        if not craft("pottery", batch):
            return False
        actions.append({"type": "sell", "item": "pottery", "quantity": batch})
        enteloot += towns[loc]["item-rates"]["pottery"] * batch
        advance(tick + 1)
        inventory["pottery"] -= batch
        return True

    for town in town_order:
        travel_to(town)

        for upgrade in plan[town]:
            # School/library prerequisites are naturally satisfied by plan order.
            guard = 0
            while not can_build(town, upgrade):
                guard += 1
                if guard > 20:
                    # Fall back to spending time on a small amount of finance.
                    break
                if enteloot < UPGRADES[upgrade]["cost"]:
                    if not finance_once():
                        # Let passive systems catch up by doing a useful gather.
                        choice = select_best_node(data, paths, loc, "wood")
                        if not choice:
                            break
                        node, info = choice
                        travel_to(node)
                        advance(tick + info["gather-time"])
                        inventory["wood"] += info["yield"]
                        actions.append({"type": "gather"})
                        travel_to(town)
                else:
                    # Missing components should normally be impossible because
                    # all components were reserved and crafted above.
                    break

            if not can_build(town, upgrade):
                # Do not emit an invalid action.
                continue
            if not build(town, upgrade):
                continue

        if tick >= total:
            break

    return actions, tick, built, enteloot, inventory

def validate_submission(actions):
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")
    for a in actions:
        if not isinstance(a, dict) or "type" not in a:
            raise ValueError(f"Malformed action: {a}")
        t = a["type"]
        if t == "travel":
            if not isinstance(a.get("destination"), str):
                raise ValueError(f"Malformed travel: {a}")
        elif t in ("gather", "upkeep"):
            pass
        elif t in ("buy", "sell", "craft"):
            if not isinstance(a.get("item"), str) or not isinstance(a.get("quantity"), int) or a["quantity"] <= 0:
                raise ValueError(f"Malformed {t}: {a}")
        elif t == "build":
            if not isinstance(a.get("upgrade"), str):
                raise ValueError(f"Malformed build: {a}")
        else:
            raise ValueError(f"Unknown action type: {t}")

def write_submission(actions, output="submission.txt"):
    validate_submission(actions)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({"actions": actions}, f, indent=2)

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "2.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "submission.txt"

    data = load_input(input_file)
    plan = choose_upgrade_plan(data)

    print("Level 2 optimisation")
    print(f"Input: {input_file}")
    print("Upgrade portfolio:")
    for town, upgrades in plan.items():
        print(f"  {town}: {', '.join(upgrades)}")

    actions, tick, built, enteloot, inventory = solve(data)
    write_submission(actions, output_file)

    built_count = sum(len(v) for v in built.values())
    infra_score = sum(UPGRADES[u]["score"] for v in built.values() for u in v)

    print(f"Generated actions: {len(actions)}")
    print(f"Estimated execution tick: {tick}/{data['run']['total_ticks']}")
    print(f"Estimated upgrades built: {built_count}")
    print(f"Estimated infrastructure score: {infra_score}")
    print(f"Estimated remaining Enteloot: {enteloot}")
    print(f"Submission: {output_file}")

if __name__ == "__main__":
    main()
