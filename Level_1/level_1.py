import json
import heapq
import math
import time
from collections import defaultdict, Counter

# ============================================================
# Constants from the Level 1 specification
# ============================================================

RESOURCE_SELL_PRICES = {
    "wheat": 2,
    "wood": 3,
    "stone": 3,
    "clay": 4,
    "fish": 4,
    "sheep": 5,
    "ore": 6,
}

RESOURCE_BUY_PRICES = {
    "wheat": 4,
    "wood": 5,
    "stone": 5,
    "clay": 6,
    "fish": 6,
    "sheep": 8,
}


# ============================================================
# Input Loading & Validation
# ============================================================

def load_input(filename="1.txt"):
    candidates = [filename, "level1.json", "level_1.json", "1.json", "input.json"]
    input_file = None
    for cand in candidates:
        try:
            with open(cand, "r", encoding="utf-8") as file:
                data = json.load(file)
                input_file = cand
                break
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    if input_file is None:
        raise FileNotFoundError("Could not find a valid Level 1 input file (e.g. '1.txt').")

    validate_input_structure(data)
    return data


def validate_input_structure(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object.")

    required_top_level = {"run", "towns", "nodes", "routes"}
    missing = required_top_level - set(data.keys())
    if missing:
        raise ValueError(f"Input is missing required fields: {sorted(missing)}")

    run = data["run"]
    if not isinstance(run, dict):
        raise ValueError("'run' must be an object.")

    for field in ("total_ticks", "starting_town", "starting_enteloot"):
        if field not in run:
            raise ValueError(f"'run' is missing required field '{field}'.")

    if not isinstance(run["total_ticks"], int) or run["total_ticks"] < 0:
        raise ValueError("'total_ticks' must be a non-negative integer.")

    if not isinstance(run["starting_town"], str) or run["starting_town"] not in data["towns"]:
        raise ValueError(f"Starting town '{run.get('starting_town')}' does not exist.")

    if not isinstance(run["starting_enteloot"], (int, float)):
        raise ValueError("'starting_enteloot' must be numeric.")


# ============================================================
# Graph & Dijkstra Pathfinding
# ============================================================

def build_graph(data):
    graph = defaultdict(list)
    vertices = set(data["towns"]) | set(data["nodes"])

    for route in data["routes"]:
        a, b = route["between"]
        weight = route["weight"]
        toll = route.get("toll", 0)

        if a not in vertices or b not in vertices:
            raise ValueError(f"Route references unknown vertices: {a}, {b}")

        if toll != 0:
            continue

        graph[a].append((b, weight))
        graph[b].append((a, weight))

    return graph


def dijkstra(graph, start):
    distances = {vertex: math.inf for vertex in graph}
    previous = {vertex: None for vertex in graph}
    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current = heapq.heappop(priority_queue)

        if current_distance != distances[current]:
            continue

        for neighbour, weight in graph[current]:
            new_distance = current_distance + weight

            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                previous[neighbour] = current
                heapq.heappush(priority_queue, (new_distance, neighbour))

    return distances, previous


def reconstruct_path(previous, start, destination):
    if start == destination:
        return [start]

    path = []
    current = destination

    while current is not None:
        path.append(current)
        if current == start:
            break
        current = previous[current]

    if not path or path[-1] != start:
        return None

    path.reverse()
    return path


def calculate_all_routes(data, graph):
    routes = {}
    vertices = list(graph.keys())

    for start in vertices:
        distances, previous = dijkstra(graph, start)
        routes[start] = {}

        for destination in vertices:
            if destination == start:
                routes[start][destination] = {
                    "distance": 0,
                    "path": [start],
                }
                continue

            if distances[destination] == math.inf:
                continue

            path = reconstruct_path(previous, start, destination)
            if path is not None:
                routes[start][destination] = {
                    "distance": distances[destination],
                    "path": path,
                }

    return routes


# ============================================================
# Action Helpers
# ============================================================

def add_travel_actions(actions, path):
    if not path:
        return
    for destination in path[1:]:
        actions.append({
            "type": "travel",
            "destination": destination,
        })


def add_gather_actions(actions, count):
    for _ in range(count):
        actions.append({"type": "gather"})


def add_sell_action(actions, resource, quantity):
    if quantity <= 0:
        return
    actions.append({
        "type": "sell",
        "item": resource,
        "quantity": int(quantity),
    })


def add_buy_action(actions, resource, quantity):
    if quantity <= 0:
        return
    actions.append({
        "type": "buy",
        "item": resource,
        "quantity": int(quantity),
    })


# ============================================================
# Passive Inventory Tracking
# ============================================================

def get_inventory_at_tick(data, t, gathered_resources, sold_resources):
    inventory = Counter()
    for town_name, town in data["towns"].items():
        production = town.get("production", {})
        rate = production.get("rate")
        resources = production.get("resources", {})
        if rate and rate > 0:
            cycles = t // rate
            for res, amount in resources.items():
                inventory[res] += cycles * amount

    for res, amount in gathered_resources.items():
        inventory[res] += amount

    for res, amount in sold_resources.items():
        inventory[res] -= amount

    return inventory


# ============================================================
# Solution Validation
# ============================================================

def validate_solution(data, actions):
    if not isinstance(actions, list):
        raise ValueError("Actions must be a list.")

    total_ticks = data["run"]["total_ticks"]
    graph = build_graph(data)
    current_location = data["run"]["starting_town"]
    
    gathered_resources = Counter()
    sold_resources = Counter()
    enteloot = data["run"]["starting_enteloot"]
    elapsed_ticks = 0
    total_items_sold = 0

    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise ValueError(f"Action {index} is not an object.")

        action_type = action.get("type")

        if action_type == "travel":
            destination = action.get("destination")
            if destination not in graph:
                raise ValueError(f"Action {index}: unknown destination '{destination}'.")

            neighbours = {neighbour: weight for neighbour, weight in graph[current_location]}
            if destination not in neighbours:
                raise ValueError(f"Action {index}: cannot travel from '{current_location}' to '{destination}'.")

            cost = neighbours[destination]
            elapsed_ticks += cost
            current_location = destination

        elif action_type == "gather":
            if current_location not in data["nodes"]:
                raise ValueError(f"Action {index}: gather attempted at non-resource node '{current_location}'.")

            node = data["nodes"][current_location]
            resource = node["resource"]
            quantity = node["yield"]
            cost = node["gather-time"]

            gathered_resources[resource] += quantity
            elapsed_ticks += cost

        elif action_type == "sell":
            item = action.get("item")
            quantity = action.get("quantity")

            if item not in RESOURCE_SELL_PRICES:
                raise ValueError(f"Action {index}: unknown resource '{item}'.")

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(f"Action {index}: sell quantity must be positive.")

            current_inv = get_inventory_at_tick(data, elapsed_ticks, gathered_resources, sold_resources)
            if current_inv[item] < quantity:
                raise ValueError(
                    f"Action {index}: attempting to sell {quantity} {item}, "
                    f"but only {current_inv[item]} available."
                )

            sold_resources[item] += quantity
            enteloot += quantity * RESOURCE_SELL_PRICES[item]
            total_items_sold += quantity
            elapsed_ticks += 1

        elif action_type == "buy":
            item = action.get("item")
            quantity = action.get("quantity")

            if item not in RESOURCE_SELL_PRICES:
                raise ValueError(f"Action {index}: unknown resource '{item}'.")

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(f"Action {index}: buy quantity must be positive.")

            if current_location not in data["towns"]:
                raise ValueError(f"Action {index}: cannot buy at a resource node.")

            town_resources = data["towns"][current_location].get("production", {}).get("resources", {})
            if item not in town_resources:
                raise ValueError(f"Action {index}: town '{current_location}' does not produce '{item}'.")

            buy_price = RESOURCE_BUY_PRICES.get(item, 0)
            cost_enteloot = buy_price * quantity
            if enteloot < cost_enteloot:
                raise ValueError(f"Action {index}: cannot afford to buy {quantity} {item}.")

            enteloot -= cost_enteloot
            gathered_resources[item] += quantity
            elapsed_ticks += 1

        else:
            raise ValueError(f"Action {index}: unsupported Level 1 action '{action_type}'.")

        if elapsed_ticks > total_ticks:
            raise ValueError(f"Solution exceeds tick limit at action {index}: {elapsed_ticks} > {total_ticks}.")

    final_inventory = get_inventory_at_tick(data, elapsed_ticks, gathered_resources, sold_resources)

    return {
        "valid": True,
        "ticks": elapsed_ticks,
        "remaining_ticks": total_ticks - elapsed_ticks,
        "inventory": dict(final_inventory),
        "final_location": current_location,
        "enteloot": enteloot,
        "total_items_sold": total_items_sold,
    }


# ============================================================
# Final Volume Multiplier Boost
# ============================================================

def apply_final_volume_boost(data, current_location, elapsed_ticks, total_ticks, current_enteloot, current_sold, gathered_resources, sold_resources, actions):
    """
    Use leftover ticks to execute an optimal volume trade:
    Buy Q* and Sell Q* to maximize (Enteloot) * (Items Sold Multiplier).
    """
    if current_location not in data["towns"]:
        return elapsed_ticks, current_enteloot

    if elapsed_ticks + 2 > total_ticks:
        return elapsed_ticks, current_enteloot

    town_resources = data["towns"][current_location].get("production", {}).get("resources", {})
    if not town_resources:
        return elapsed_ticks, current_enteloot

    # Find resource with minimum loss (buy_price - sell_price)
    best_res = None
    best_loss = math.inf
    for res in town_resources:
        buy_p = RESOURCE_BUY_PRICES.get(res)
        sell_p = RESOURCE_SELL_PRICES.get(res)
        if buy_p and sell_p:
            loss = buy_p - sell_p
            if loss < best_loss:
                best_loss = loss
                best_res = res

    if best_res is None or best_loss <= 0:
        return elapsed_ticks, current_enteloot

    # Q* = (Enteloot - loss * current_sold) / (2 * loss)
    optimal_Q = (current_enteloot - best_loss * current_sold) / (2.0 * best_loss)
    buy_p = RESOURCE_BUY_PRICES[best_res]
    sell_p = RESOURCE_SELL_PRICES[best_res]
    
    max_affordable_Q = current_enteloot // buy_p
    Q = int(math.floor(min(optimal_Q, max_affordable_Q)))

    if Q <= 0:
        return elapsed_ticks, current_enteloot

    # 1. Buy action (1 tick)
    add_buy_action(actions, best_res, Q)
    gathered_resources[best_res] += Q
    current_enteloot -= Q * buy_p
    elapsed_ticks += 1

    # 2. Sell action (1 tick)
    add_sell_action(actions, best_res, Q)
    sold_resources[best_res] += Q
    current_enteloot += Q * sell_p
    elapsed_ticks += 1

    return elapsed_ticks, current_enteloot


# ============================================================
# Optimized Solver
# ============================================================

def solve(data):
    graph = build_graph(data)
    routes = calculate_all_routes(data, graph)

    total_ticks = data["run"]["total_ticks"]
    current_location = data["run"]["starting_town"]

    gathered_resources = Counter()
    sold_resources = Counter()
    current_enteloot = data["run"]["starting_enteloot"]

    actions = []
    elapsed_ticks = 0

    passive_res_types = sorted(list(set(
        res for t_info in data["towns"].values()
        for res in t_info.get("production", {}).get("resources", {})
    )))
    K_passive = len(passive_res_types)
    # Reserve K_passive ticks for liquidation + 2 ticks for the volume boost
    K_buffer = K_passive + 2

    # Calculate passive background potential
    total_passive_inv = get_inventory_at_tick(data, total_ticks, Counter(), Counter())
    total_passive_enteloot = sum(qty * RESOURCE_SELL_PRICES.get(res, 0) for res, qty in total_passive_inv.items())
    total_passive_items = sum(total_passive_inv.values())

    while elapsed_ticks < total_ticks:
        remaining_ticks = total_ticks - elapsed_ticks
        available_budget = remaining_ticks - K_buffer

        best_trip = None
        best_trip_score = -1

        for node_name, node in data["nodes"].items():
            resource = node["resource"]
            yield_amount = node["yield"]
            gather_time = node["gather-time"]
            price = RESOURCE_SELL_PRICES.get(resource, 0)
            if price == 0:
                continue

            if current_location not in routes or node_name not in routes[current_location]:
                continue

            travel_to_ticks = routes[current_location][node_name]["distance"]
            travel_to_path = routes[current_location][node_name]["path"]

            best_return_town = None
            best_return_ticks = math.inf
            for town_name in data["towns"]:
                if node_name in routes and town_name in routes[node_name]:
                    d = routes[node_name][town_name]["distance"]
                    if d < best_return_ticks:
                        best_return_ticks = d
                        best_return_town = town_name

            if best_return_town is None:
                continue

            return_path = routes[node_name][best_return_town]["path"]

            min_trip_ticks = travel_to_ticks + gather_time + best_return_ticks + 1
            if min_trip_ticks > available_budget:
                if min_trip_ticks > remaining_ticks:
                    continue
                ticks_for_gathering = remaining_ticks - travel_to_ticks - best_return_ticks - 1
            else:
                ticks_for_gathering = available_budget - travel_to_ticks - best_return_ticks - 1

            num_gathers = ticks_for_gathering // gather_time
            if num_gathers <= 0:
                continue

            total_gathered = num_gathers * yield_amount
            trip_profit = total_gathered * price
            
            # Evaluate candidates on combined projected score: Enteloot * Items Sold
            proj_enteloot = current_enteloot + trip_profit + total_passive_enteloot
            proj_items = sum(sold_resources.values()) + total_gathered + total_passive_items
            score_metric = proj_enteloot * proj_items

            if score_metric > best_trip_score:
                best_trip_score = score_metric
                best_trip = {
                    "node_name": node_name,
                    "resource": resource,
                    "yield_amount": yield_amount,
                    "gather_time": gather_time,
                    "num_gathers": num_gathers,
                    "travel_to_path": travel_to_path,
                    "travel_to_ticks": travel_to_ticks,
                    "return_town": best_return_town,
                    "return_path": return_path,
                    "return_ticks": best_return_ticks,
                    "trip_profit": trip_profit,
                }

        if best_trip is None:
            break

        # 1. Travel
        add_travel_actions(actions, best_trip["travel_to_path"])
        elapsed_ticks += best_trip["travel_to_ticks"]

        # 2. Continuous Gathering
        add_gather_actions(actions, best_trip["num_gathers"])
        elapsed_ticks += best_trip["num_gathers"] * best_trip["gather_time"]
        gathered_qty = best_trip["num_gathers"] * best_trip["yield_amount"]
        gathered_resources[best_trip["resource"]] += gathered_qty

        # 3. Return to Town
        add_travel_actions(actions, best_trip["return_path"])
        elapsed_ticks += best_trip["return_ticks"]
        current_location = best_trip["return_town"]

        # 4. Sell Gathered Batch
        add_sell_action(actions, best_trip["resource"], gathered_qty)
        sold_resources[best_trip["resource"]] += gathered_qty
        current_enteloot += best_trip["trip_profit"]
        elapsed_ticks += 1

    # End-of-Run Bulk Liquidation Pass
    if current_location in data["towns"]:
        inv = get_inventory_at_tick(data, elapsed_ticks, gathered_resources, sold_resources)
        for res in sorted(inv.keys(), key=lambda r: -RESOURCE_SELL_PRICES.get(r, 0)):
            if elapsed_ticks >= total_ticks - 2: # Keep 2 ticks for the volume boost
                break
            qty = inv[res]
            if qty > 0:
                add_sell_action(actions, res, qty)
                sold_resources[res] += qty
                current_enteloot += qty * RESOURCE_SELL_PRICES.get(res, 0)
                elapsed_ticks += 1

    # End-of-Run Volume Multiplier Boost (uses the last 2 ticks)
    current_sold_count = sum(sold_resources.values())
    elapsed_ticks, current_enteloot = apply_final_volume_boost(
        data, current_location, elapsed_ticks, total_ticks, current_enteloot, current_sold_count, gathered_resources, sold_resources, actions
    )

    # Any remaining 1-tick cleanup
    if current_location in data["towns"] and elapsed_ticks < total_ticks:
        inv = get_inventory_at_tick(data, elapsed_ticks, gathered_resources, sold_resources)
        for res in sorted(inv.keys(), key=lambda r: -RESOURCE_SELL_PRICES.get(r, 0)):
            if elapsed_ticks >= total_ticks:
                break
            qty = inv[res]
            if qty > 0:
                add_sell_action(actions, res, qty)
                sold_resources[res] += qty
                elapsed_ticks += 1

    return actions, routes


# ============================================================
# Main Execution & Submission Output
# ============================================================

def create_submission(actions, filename="level1_submission.txt"):
    submission = {"actions": actions}
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(submission, file, indent=2)
    return filename


def main():
    start_time = time.perf_counter()
    print("Loading Level 1 input...")
    data = load_input("1.txt")

    print(f"Starting town: {data['run']['starting_town']}")
    print(f"Total ticks: {data['run']['total_ticks']}")
    print(f"Starting Enteloot: {data['run']['starting_enteloot']}")

    print("Optimising Level 1 strategy...")
    actions, routes = solve(data)

    validation = validate_solution(data, actions)

    print("-" * 50)
    print(f"Optimised actions: {len(actions)}")
    print(f"Ticks used: {validation['ticks']} / {data['run']['total_ticks']}")
    print(f"Remaining ticks: {validation['remaining_ticks']}")
    print(f"Final location: {validation['final_location']}")
    print(f"Final Enteloot: {validation['enteloot']}")
    print(f"Total Items Sold: {validation['total_items_sold']}")
    print(f"Unsold Inventory: {validation['inventory']}")
    print("-" * 50)

    output_file = create_submission(actions, "level1_submission.txt")
    print(f"Submission created: {output_file}")
    print(f"Runtime: {time.perf_counter() - start_time:.4f} seconds")


if __name__ == "__main__":
    main()