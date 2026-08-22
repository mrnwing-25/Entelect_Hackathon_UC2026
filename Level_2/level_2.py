import json
import math
import heapq
import sys

# Global Static Recipe Inputs & Crafting Data
RECIPES = {
    # Finished Goods
    "bread": {"inputs": {"wheat": 3}, "craft_time": 2, "sellable": True},
    "fish-n-chips": {"inputs": {"fish": 2, "wheat": 1}, "craft_time": 2, "sellable": True},
    "stew": {"inputs": {"sheep": 1, "fish": 1, "wheat": 1}, "craft_time": 2, "sellable": True},
    "wooden-crafts": {"inputs": {"wood": 4}, "craft_time": 2, "sellable": True},
    "furniture": {"inputs": {"wood": 3, "sheep": 1}, "craft_time": 2, "sellable": True},
    "stone-works": {"inputs": {"stone": 5}, "craft_time": 2, "sellable": True},
    "roof-tiles": {"inputs": {"clay": 3, "stone": 2}, "craft_time": 2, "sellable": True},
    "wool-garments": {"inputs": {"sheep": 3}, "craft_time": 2, "sellable": True},
    "pottery": {"inputs": {"clay": 4, "wood": 1}, "craft_time": 2, "sellable": True},
    # Construction Components
    "planks": {"inputs": {"wood": 2}, "craft_time": 2, "sellable": False},
    "thatch": {"inputs": {"wheat": 2}, "craft_time": 2, "sellable": False},
    "stone-blocks": {"inputs": {"stone": 3}, "craft_time": 2, "sellable": False},
    "mortar": {"inputs": {"clay": 1, "stone": 1}, "craft_time": 2, "sellable": False},
    "bricks": {"inputs": {"clay": 2, "mortar": 1}, "craft_time": 2, "sellable": False},
    "rope": {"inputs": {"sheep": 2}, "craft_time": 2, "sellable": False},
    "fencing": {"inputs": {"wood": 2, "rope": 1}, "craft_time": 2, "sellable": False},
    "kiln-glass": {"inputs": {"clay": 2, "wood": 2}, "craft_time": 2, "sellable": False},
    "nets": {"inputs": {"rope": 1, "fencing": 1}, "craft_time": 2, "sellable": False},
}

UPGRADES = {
    "farmhouse": {"boosts": "sheep", "components": {"planks": 3, "thatch": 2}, "enteloot_cost": 500, "build_time": 3, "prerequisite": None, "type": "production"},
    "pier": {"boosts": "fish", "components": {"planks": 4, "nets": 2}, "enteloot_cost": 600, "build_time": 3, "prerequisite": None, "type": "production"},
    "fertilised-fields": {"boosts": "wheat", "components": {"fencing": 2, "thatch": 2}, "enteloot_cost": 500, "build_time": 3, "prerequisite": None, "type": "production"},
    "quarry": {"boosts": "stone", "components": {"stone-blocks": 3, "planks": 2}, "enteloot_cost": 600, "build_time": 3, "prerequisite": None, "type": "production"},
    "woodlands": {"boosts": "wood", "components": {"fencing": 2, "rope": 2}, "enteloot_cost": 500, "build_time": 3, "prerequisite": None, "type": "production"},
    "pottery-house": {"boosts": "clay", "components": {"bricks": 4, "planks": 2}, "enteloot_cost": 700, "build_time": 3, "prerequisite": None, "type": "production"},
    "rec-center": {"components": {"planks": 4, "bricks": 3, "rope": 1}, "enteloot_cost": 1200, "build_time": 4, "prerequisite": "any_1_prod", "type": "civic"},
    "fire-station": {"components": {"bricks": 5, "stone-blocks": 3, "rope": 2}, "enteloot_cost": 1800, "build_time": 4, "prerequisite": "any_2_prod", "type": "civic"},
    "school": {"components": {"bricks": 6, "planks": 3, "kiln-glass": 2}, "enteloot_cost": 2000, "build_time": 5, "prerequisite": "rec-center", "type": "civic"},
    "library": {"components": {"bricks": 5, "planks": 5, "kiln-glass": 2}, "enteloot_cost": 2500, "build_time": 5, "prerequisite": "school", "type": "civic"},
}

RAW_RESOURCE_PRICES = {
    "wheat": {"sell": 2, "buy": 4},
    "wood": {"sell": 3, "buy": 5},
    "stone": {"sell": 3, "buy": 5},
    "clay": {"sell": 4, "buy": 6},
    "fish": {"sell": 4, "buy": 6},
    "sheep": {"sell": 5, "buy": 8},
}


def load_input(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def build_graph(data):
    graph = {}
    for r in data["routes"]:
        u, v = r["between"]
        w = r["weight"]
        toll = r.get("toll", 0)
        # For Level 2, stick to standard routes (toll == 0)
        if toll > 0:
            continue
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append((v, w))
        graph[v].append((u, w))
    return graph


def get_shortest_path(graph, start, target):
    queue = [(0, start, [start])]
    visited = set()
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node == target:
            return cost, path
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))
    return float("inf"), []


def compute_raw_requirements(item_name, qty=1):
    reqs = {}
    def decompose(name, count):
        if name in RAW_RESOURCE_PRICES:
            reqs[name] = reqs.get(name, 0) + count
            return
        if name in RECIPES:
            for sub_item, sub_qty in RECIPES[name]["inputs"].items():
                decompose(sub_item, sub_qty * count)

    decompose(item_name, qty)
    return reqs


def get_component_craft_tree(item_name, qty=1):
    tree = []
    def build_tree(name, count):
        if name in RECIPES:
            for sub_item, sub_qty in RECIPES[name]["inputs"].items():
                build_tree(sub_item, sub_qty * count)
            tree.append((name, count))

    build_tree(item_name, qty)
    return tree


def find_nearest_node_for_resource(graph, current_loc, nodes, resource):
    best_cost = float("inf")
    best_node = None
    best_path = []
    for n_id, n_info in nodes.items():
        if n_info["resource"] == resource:
            cost, path = get_shortest_path(graph, current_loc, n_id)
            if cost < best_cost:
                best_cost = cost
                best_node = n_id
                best_path = path
    return best_node, best_cost, best_path


def solve(data):
    total_ticks = data["total_ticks"]
    start_town = data["starting_town"]
    enteloot = data["starting_enteloot"]
    towns = data["towns"]
    nodes = data["nodes"]

    graph = build_graph(data)
    actions = []

    current_loc = start_town
    current_tick = 0
    inventory = {}

    # Identify affinity crafting town
    affinity_town = start_town
    for t_name, t_info in towns.items():
        if "crafting" in t_info.get("affinities", []):
            affinity_town = t_name
            break

    # Sequence of upgrades to target
    target_build_plan = [
        ("Demacia", "farmhouse"),
        ("Demacia", "fertilised-fields"),
        ("Demacia", "rec-center"),
        ("Demacia", "fire-station"),
        ("Noxus", "quarry"),
        ("Noxus", "woodlands"),
        ("Noxus", "rec-center"),
        ("Piltover", "pier"),
        ("Piltover", "pottery-house"),
        ("Piltover", "rec-center"),
    ]

    town_built_upgrades = {t: set() for t in towns}

    for town, upg_name in target_build_plan:
        upg_data = UPGRADES[upg_name]

        # Decompose build requirements
        raw_reqs = {}
        for comp, count in upg_data["components"].items():
            comp_raws = compute_raw_requirements(comp, count)
            for r_res, r_qty in comp_raws.items():
                raw_reqs[r_res] = raw_reqs.get(r_res, 0) + r_qty

        # 1. Gather raw resources
        for res, needed_qty in raw_reqs.items():
            have = inventory.get(res, 0)
            still_needed = needed_qty - have
            if still_needed <= 0:
                continue

            target_node, travel_cost, path = find_nearest_node_for_resource(graph, current_loc, nodes, res)
            if not target_node:
                continue

            node_yield = nodes[target_node]["yield"]
            g_time = nodes[target_node]["gather-time"]
            gathers_required = math.ceil(still_needed / node_yield)

            # Check tick limit
            est_ticks = travel_cost + (gathers_required * g_time)
            if current_tick + est_ticks >= total_ticks:
                break

            # Travel to node
            for step in path[1:]:
                actions.append({"type": "travel", "destination": step})
                current_tick += get_shortest_path(graph, current_loc, step)[0]
                current_loc = step

            # Gather
            for _ in range(gathers_required):
                if current_tick + g_time >= total_ticks:
                    break
                actions.append({"type": "gather"})
                current_tick += g_time
                inventory[res] = inventory.get(res, 0) + node_yield

        # 2. Travel to Crafting Town and Craft Components
        _, craft_path = get_shortest_path(graph, current_loc, affinity_town)
        if craft_path and len(craft_path) > 1:
            for step in craft_path[1:]:
                cost, _ = get_shortest_path(graph, current_loc, step)
                if current_tick + cost >= total_ticks:
                    break
                actions.append({"type": "travel", "destination": step})
                current_tick += cost
                current_loc = step

        for comp, count in upg_data["components"].items():
            craft_tree = get_component_craft_tree(comp, count)
            for c_item, c_qty in craft_tree:
                # Crafting at affinity town = 1 tick per item
                c_ticks = c_qty * 1
                if current_tick + c_ticks >= total_ticks:
                    break
                actions.append({"type": "craft", "item": c_item, "quantity": c_qty})
                current_tick += c_ticks
                inventory[c_item] = inventory.get(c_item, 0) + c_qty

        # 3. Travel to Target Town and Build
        _, build_path = get_shortest_path(graph, current_loc, town)
        if build_path and len(build_path) > 1:
            for step in build_path[1:]:
                cost, _ = get_shortest_path(graph, current_loc, step)
                if current_tick + cost >= total_ticks:
                    break
                actions.append({"type": "travel", "destination": step})
                current_tick += cost
                current_loc = step

        # Validate prerequisite check locally
        can_build = True
        prereq = upg_data["prerequisite"]
        if prereq == "any_1_prod":
            prod_built = sum(1 for u in town_built_upgrades[town] if UPGRADES[u]["type"] == "production")
            if prod_built < 1:
                can_build = False
        elif prereq == "any_2_prod":
            prod_built = sum(1 for u in town_built_upgrades[town] if UPGRADES[u]["type"] == "production")
            if prod_built < 2:
                can_build = False
        elif prereq and prereq not in town_built_upgrades[town]:
            can_build = False

        if can_build and current_tick + upg_data["build_time"] < total_ticks:
            actions.append({"type": "build", "upgrade": upg_name})
            current_tick += upg_data["build_time"]
            town_built_upgrades[town].add(upg_name)

    return actions, current_tick


def validate_solution(actions, total_ticks):
    if not isinstance(actions, list):
        raise ValueError("Actions must be a list.")
    if len(actions) == 0:
        raise ValueError("Action list is empty.")


def create_submission(actions, output_file="submission.txt"):
    submission_data = {"actions": actions}
    with open(output_file, "w") as f:
        json.dump(submission_data, f, indent=2)


def main():
    input_file = "level2.json"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    data = load_input(input_file)
    print(f"Input loaded from {input_file}.")

    actions, est_ticks = solve(data)
    print(f"Generated {len(actions)} actions.")
    print(f"Estimated total ticks used: {est_ticks}/{data['total_ticks']}")

    validate_solution(actions, data["total_ticks"])
    create_submission(actions, "submission.txt")
    print("Submission created: submission.txt")


if __name__ == "__main__":
    main()