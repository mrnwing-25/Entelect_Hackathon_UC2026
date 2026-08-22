import json
import heapq
import math
import time
from collections import defaultdict


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

# Ore does not appear in Level 1 according to the specification,
# but keeping it here makes the validation more robust.
LEVEL_1_RESOURCES = {
    "wheat",
    "wood",
    "stone",
    "clay",
    "fish",
    "sheep",
}


# ============================================================
# Input
# ============================================================

def load_input(filename="1.txt"):
    """Load and validate the challenge input JSON."""

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file '{filename}' was not found."
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Input file '{filename}' is not valid JSON: {exc}"
        )

    validate_input_structure(data)

    return data


def validate_input_structure(data):
    """Validate the basic structure of the level JSON."""

    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object.")

    required_top_level = {"run", "towns", "nodes", "routes"}

    missing = required_top_level - set(data.keys())

    if missing:
        raise ValueError(
            f"Input is missing required fields: {sorted(missing)}"
        )

    run = data["run"]

    if not isinstance(run, dict):
        raise ValueError("'run' must be an object.")

    for field in ("total_ticks", "starting_town", "starting_enteloot"):
        if field not in run:
            raise ValueError(
                f"'run' is missing required field '{field}'."
            )

    if not isinstance(run["total_ticks"], int):
        raise ValueError("'total_ticks' must be an integer.")

    if run["total_ticks"] < 0:
        raise ValueError("'total_ticks' cannot be negative.")

    if not isinstance(run["starting_town"], str):
        raise ValueError("'starting_town' must be a string.")

    if run["starting_town"] not in data["towns"]:
        raise ValueError(
            f"Starting town '{run['starting_town']}' does not exist."
        )

    if not isinstance(run["starting_enteloot"], (int, float)):
        raise ValueError("'starting_enteloot' must be numeric.")

    if not isinstance(data["towns"], dict):
        raise ValueError("'towns' must be an object.")

    if not isinstance(data["nodes"], dict):
        raise ValueError("'nodes' must be an object.")

    if not isinstance(data["routes"], list):
        raise ValueError("'routes' must be an array.")

    for node_name, node in data["nodes"].items():

        if not isinstance(node, dict):
            raise ValueError(
                f"Node '{node_name}' must be an object."
            )

        for field in ("resource", "yield", "gather-time"):
            if field not in node:
                raise ValueError(
                    f"Node '{node_name}' is missing '{field}'."
                )

        if node["yield"] <= 0:
            raise ValueError(
                f"Node '{node_name}' must have a positive yield."
            )

        if node["gather-time"] <= 0:
            raise ValueError(
                f"Node '{node_name}' must have a positive gather time."
            )

    for route in data["routes"]:

        if not isinstance(route, dict):
            raise ValueError("Every route must be an object.")

        for field in ("between", "weight", "toll"):
            if field not in route:
                raise ValueError(
                    f"Route is missing '{field}'."
                )

        if (
            not isinstance(route["between"], list)
            or len(route["between"]) != 2
        ):
            raise ValueError(
                "'between' must contain exactly two vertices."
            )

        if route["weight"] < 0:
            raise ValueError("Route weight cannot be negative.")

        if route["toll"] < 0:
            raise ValueError("Route toll cannot be negative.")


# ============================================================
# Graph
# ============================================================

def build_graph(data):
    """
    Build an undirected weighted graph.

    Level 1 uses normal routes. Fast routes are a Level 3 mechanic,
    so they are deliberately ignored here.
    """

    graph = defaultdict(list)

    vertices = set(data["towns"]) | set(data["nodes"])

    for route in data["routes"]:

        a, b = route["between"]
        weight = route["weight"]
        toll = route["toll"]

        if a not in vertices:
            raise ValueError(
                f"Route references unknown vertex '{a}'."
            )

        if b not in vertices:
            raise ValueError(
                f"Route references unknown vertex '{b}'."
            )

        # Level 1 does not use fast routes.
        # A route with a toll represents a fast route in the
        # specification's example and is therefore ignored.
        if toll != 0:
            continue

        graph[a].append((b, weight))
        graph[b].append((a, weight))

    return graph


# ============================================================
# Dijkstra
# ============================================================

def dijkstra(graph, start):
    """
    Calculate shortest distances and predecessor information
    from start to every reachable vertex.
    """

    distances = {
        vertex: math.inf
        for vertex in graph
    }

    previous = {
        vertex: None
        for vertex in graph
    }

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

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbour)
                )

    return distances, previous


def reconstruct_path(previous, start, destination):
    """Reconstruct a shortest path from Dijkstra's results."""

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


# ============================================================
# Route calculation
# ============================================================

def calculate_all_routes(data, graph):
    """
    Calculate shortest paths between all relevant vertices.

    Dijkstra is run once from every vertex rather than repeatedly
    for every individual action.
    """

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

            path = reconstruct_path(
                previous,
                start,
                destination
            )

            if path is not None:
                routes[start][destination] = {
                    "distance": distances[destination],
                    "path": path,
                }

    return routes


# ============================================================
# Town helpers
# ============================================================

def get_towns_producing_resource(data, resource):
    """Return towns that produce the specified resource."""

    result = []

    for town_name, town in data["towns"].items():

        production = town.get("production", {})
        resources = production.get("resources", {})

        if resource in resources:
            result.append(town_name)

    return result


def get_best_selling_town(data, resource):
    """
    Level 1 raw resource selling uses a global sell price.

    Therefore every town pays the same raw-resource price.

    The specification mentions selling resources at towns that
    produce them least, but the raw-resource price itself is global.
    We therefore select the nearest producing town when one exists.
    """

    producing_towns = get_towns_producing_resource(
        data,
        resource
    )

    if producing_towns:
        return producing_towns

    return list(data["towns"].keys())


# ============================================================
# Node evaluation
# ============================================================

def evaluate_node(data, node_name, current_location, routes):
    """
    Calculate a simple economic value for gathering from a node.

    Value per gathering action:
        yield × raw resource sell price

    Cost:
        travel to node
        + gather
        + return to a town

    The score is therefore approximated by value per tick.

    This is intentionally a heuristic because the complete scoring
    equation is not supplied in the specification.
    """

    node = data["nodes"][node_name]

    resource = node["resource"]
    yield_amount = node["yield"]
    gather_time = node["gather-time"]

    if resource not in RESOURCE_SELL_PRICES:
        return None

    if current_location not in routes:
        return None

    if node_name not in routes[current_location]:
        return None

    travel_to = routes[current_location][node_name]["distance"]

    # Find the cheapest reachable town to return to.
    best_return = None

    for town_name in data["towns"]:

        if node_name not in routes:
            continue

        if town_name not in routes[node_name]:
            continue

        return_distance = routes[node_name][town_name]["distance"]

        if best_return is None or return_distance < best_return[1]:
            best_return = (town_name, return_distance)

    if best_return is None:
        return None

    return_town, travel_back = best_return

    value = yield_amount * RESOURCE_SELL_PRICES[resource]

    total_ticks = (
        travel_to
        + gather_time
        + travel_back
        + 1  # sell action
    )

    if total_ticks <= 0:
        return None

    value_per_tick = value / total_ticks

    return {
        "node": node_name,
        "resource": resource,
        "yield": yield_amount,
        "gather_time": gather_time,
        "travel_to": travel_to,
        "return_town": return_town,
        "travel_back": travel_back,
        "value": value,
        "value_per_tick": value_per_tick,
    }


# ============================================================
# Action helpers
# ============================================================

def add_travel_actions(actions, path):
    """Add travel actions for each edge in a path."""

    if not path:
        return

    for destination in path[1:]:
        actions.append({
            "type": "travel",
            "destination": destination,
        })


def add_gather_actions(actions, count):
    """Add repeated gather actions."""

    for _ in range(count):
        actions.append({
            "type": "gather"
        })


def add_sell_action(actions, resource, quantity):
    """Add a sell action."""

    if quantity <= 0:
        return

    actions.append({
        "type": "sell",
        "item": resource,
        "quantity": quantity,
    })


# ============================================================
# Action cost
# ============================================================

def calculate_action_cost(action, data, graph):
    """
    Calculate the known tick cost of an action.

    This is used for our own validation/planning.

    Level 1 actions:
        travel = edge weight
        gather = node gather time
        buy = 1
        sell = 1

    Craft/build/upkeep are not used in Level 1.
    """

    action_type = action.get("type")

    if action_type == "travel":

        destination = action.get("destination")

        if destination not in graph:
            raise ValueError(
                f"Unknown travel destination '{destination}'."
            )

        return None

    if action_type in {"buy", "sell"}:
        return 1

    if action_type == "gather":
        return None

    return None


# ============================================================
# Solution validation
# ============================================================

def validate_solution(data, actions):
    """
    Validate the action sequence against the Level 1 rules.

    This is a local validation of the generated solution.
    The official engine remains the authoritative validator.
    """

    if not isinstance(actions, list):
        raise ValueError("Actions must be a list.")

    total_ticks = data["run"]["total_ticks"]

    graph = build_graph(data)

    current_location = data["run"]["starting_town"]

    inventory = defaultdict(int)

    elapsed_ticks = 0

    for index, action in enumerate(actions):

        if not isinstance(action, dict):
            raise ValueError(
                f"Action {index} is not an object."
            )

        action_type = action.get("type")

        if action_type == "travel":

            destination = action.get("destination")

            if destination not in graph:
                raise ValueError(
                    f"Action {index}: unknown destination "
                    f"'{destination}'."
                )

            neighbours = {
                neighbour: weight
                for neighbour, weight in graph[current_location]
            }

            if destination not in neighbours:
                raise ValueError(
                    f"Action {index}: cannot travel from "
                    f"'{current_location}' to '{destination}'."
                )

            cost = neighbours[destination]

            elapsed_ticks += cost
            current_location = destination

        elif action_type == "gather":

            if current_location not in data["nodes"]:
                raise ValueError(
                    f"Action {index}: gather attempted at "
                    f"non-resource node '{current_location}'."
                )

            node = data["nodes"][current_location]

            resource = node["resource"]
            quantity = node["yield"]
            cost = node["gather-time"]

            inventory[resource] += quantity
            elapsed_ticks += cost

        elif action_type == "sell":

            item = action.get("item")
            quantity = action.get("quantity")

            if item not in RESOURCE_SELL_PRICES:
                raise ValueError(
                    f"Action {index}: unknown resource '{item}'."
                )

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(
                    f"Action {index}: sell quantity must "
                    f"be a positive integer."
                )

            if inventory[item] < quantity:
                raise ValueError(
                    f"Action {index}: attempting to sell "
                    f"{quantity} {item}, but only "
                    f"{inventory[item]} available."
                )

            inventory[item] -= quantity
            elapsed_ticks += 1

        elif action_type == "buy":

            item = action.get("item")
            quantity = action.get("quantity")

            if item not in RESOURCE_SELL_PRICES:
                raise ValueError(
                    f"Action {index}: unknown resource '{item}'."
                )

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(
                    f"Action {index}: buy quantity must "
                    f"be a positive integer."
                )

            # Level 1 buys are valid only at towns that produce
            # the resource.
            if current_location not in data["towns"]:
                raise ValueError(
                    f"Action {index}: cannot buy at a resource node."
                )

            town_resources = (
                data["towns"][current_location]
                .get("production", {})
                .get("resources", {})
            )

            if item not in town_resources:
                raise ValueError(
                    f"Action {index}: town "
                    f"'{current_location}' does not produce "
                    f"'{item}'."
                )

            # Buying is not used by our strategy, but we account
            # for the inventory change.
            inventory[item] += quantity
            elapsed_ticks += 1

        else:
            raise ValueError(
                f"Action {index}: unsupported Level 1 "
                f"action '{action_type}'."
            )

        if elapsed_ticks > total_ticks:
            raise ValueError(
                f"Solution exceeds total tick limit at action "
                f"{index}: {elapsed_ticks} > {total_ticks}."
            )

    return {
        "valid": True,
        "ticks": elapsed_ticks,
        "remaining_ticks": total_ticks - elapsed_ticks,
        "inventory": dict(inventory),
        "final_location": current_location,
    }


# ============================================================
# Baseline
# ============================================================

def generate_baseline(data, routes):
    """
    Baseline strategy:

    Travel to the first reachable resource node,
    gather once, return to a town and sell.

    This gives us a simple guaranteed strategy against which
    the improved heuristic can be compared.
    """

    start = data["run"]["starting_town"]

    for node_name in data["nodes"]:

        if start not in routes:
            continue

        if node_name not in routes[start]:
            continue

        resource = data["nodes"][node_name]["resource"]
        quantity = data["nodes"][node_name]["yield"]

        return_towns = get_best_selling_town(
            data,
            resource
        )

        for town in return_towns:

            if town not in routes[node_name]:
                continue

            actions = []

            add_travel_actions(
                actions,
                routes[start][node_name]["path"]
            )

            add_gather_actions(actions, 1)

            add_travel_actions(
                actions,
                routes[node_name][town]["path"]
            )

            add_sell_action(
                actions,
                resource,
                quantity
            )

            try:
                validate_solution(data, actions)
                return actions
            except ValueError:
                continue

    # A zero-action solution is always structurally valid.
    return []


# ============================================================
# Optimised Level 1 strategy
# ============================================================

def solve(data):
    """
    Generate a deterministic Level 1 solution.

    Strategy:

    - Use Dijkstra for travel.
    - Evaluate every resource node.
    - Select the best value-per-tick gathering opportunity.
    - Gather as many times as possible while retaining enough
      time to return and sell.
    - Sell before continuing.
    - Repeat.

    This is a heuristic because the specification does not provide
    the complete numerical scoring formula.
    """

    graph = build_graph(data)

    routes = calculate_all_routes(
        data,
        graph
    )

    baseline = generate_baseline(
        data,
        routes
    )

    baseline_result = validate_solution(
        data,
        baseline
    )

    best_actions = baseline
    best_proxy_score = calculate_proxy_score(
        data,
        baseline_result
    )

    total_ticks = data["run"]["total_ticks"]

    current_location = data["run"]["starting_town"]

    inventory = defaultdict(int)

    actions = []
    elapsed_ticks = 0

    while elapsed_ticks < total_ticks:

        candidates = []

        for node_name in data["nodes"]:

            evaluation = evaluate_node(
                data,
                node_name,
                current_location,
                routes
            )

            if evaluation is None:
                continue

            candidates.append(evaluation)

        if not candidates:
            break

        # Deterministic tie-breaking:
        # 1. Highest value/tick
        # 2. Highest raw value
        # 3. Shortest travel
        # 4. Node name
        candidates.sort(
            key=lambda item: (
                -item["value_per_tick"],
                -item["value"],
                item["travel_to"],
                item["node"],
            )
        )

        selected = None
        gather_count = 0

        for candidate in candidates:

            node_name = candidate["node"]
            resource = candidate["resource"]

            if (
                current_location not in routes
                or node_name not in routes[current_location]
            ):
                continue

            return_town = candidate["return_town"]

            travel_to_path = routes[current_location][node_name]["path"]
            return_path = routes[node_name][return_town]["path"]

            travel_to_ticks = routes[current_location][node_name]["distance"]
            return_ticks = routes[node_name][return_town]["distance"]

            gather_time = candidate["gather_time"]
            yield_amount = candidate["yield"]

            # At least one gathering action must fit together
            # with travel to the node, return, and selling.
            minimum_ticks = (
                travel_to_ticks
                + gather_time
                + return_ticks
                + 1
            )

            if elapsed_ticks + minimum_ticks > total_ticks:
                continue

            remaining_ticks = total_ticks - elapsed_ticks

            # Number of gathers that can fit before the final sell.
            available_for_gathering = (
                remaining_ticks
                - travel_to_ticks
                - return_ticks
                - 1
            )

            possible_gathers = (
                available_for_gathering // gather_time
            )

            if possible_gathers <= 0:
                continue

            selected = candidate
            gather_count = possible_gathers
            break

        if selected is None:
            break

        node_name = selected["node"]
        resource = selected["resource"]
        return_town = selected["return_town"]

        travel_to_path = routes[current_location][node_name]["path"]
        return_path = routes[node_name][return_town]["path"]

        # Travel to node.
        add_travel_actions(
            actions,
            travel_to_path
        )

        elapsed_ticks += selected["travel_to"]

        # Gather.
        add_gather_actions(
            actions,
            gather_count
        )

        elapsed_ticks += (
            gather_count * selected["gather_time"]
        )

        gathered_quantity = (
            gather_count * selected["yield"]
        )

        inventory[resource] += gathered_quantity

        # Return to town.
        add_travel_actions(
            actions,
            return_path
        )

        elapsed_ticks += selected["travel_back"]

        # Sell everything of this resource gathered in this trip.
        add_sell_action(
            actions,
            resource,
            gathered_quantity
        )

        elapsed_ticks += 1

        inventory[resource] -= gathered_quantity

        current_location = return_town

        # ----------------------------------------------------
        # Compare the current strategy against the best one.
        # ----------------------------------------------------

        try:
            result = validate_solution(
                data,
                actions
            )
        except ValueError:
            # Should never happen because actions are generated
            # through validated routes.
            break

        proxy_score = calculate_proxy_score(
            data,
            result
        )

        if proxy_score > best_proxy_score:

            best_proxy_score = proxy_score
            best_actions = list(actions)

    return best_actions, baseline, routes


# ============================================================
# Proxy objective
# ============================================================

def calculate_proxy_score(data, validation_result):
    """
    Calculate a transparent proxy objective.

    IMPORTANT:
    This is NOT claimed to be the official competition score.

    The supplied specification states that Level 1 scoring involves:
        - Enteloot generation
        - final item value
        - a multiplier based on items sold

    However, the exact formula is not supplied.

    Therefore we use the value of remaining inventory as a
    conservative local proxy.

    The official simulator should be used to obtain the actual score.
    """

    inventory = validation_result["inventory"]

    inventory_value = 0

    for resource, quantity in inventory.items():

        price = RESOURCE_SELL_PRICES.get(resource, 0)

        inventory_value += quantity * price

    return inventory_value


# ============================================================
# Submission
# ============================================================

def create_submission(actions, filename="level1_submission.txt"):
    """Write the exact required submission structure."""

    submission = {
        "actions": actions
    }

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            submission,
            file,
            indent=2
        )

    return filename


# ============================================================
# Main
# ============================================================

def main():

    start_time = time.perf_counter()

    print("Loading Level 1 input...")

    data = load_input("1.txt")

    print("Input loaded.")
    print(
        f"Starting town: {data['run']['starting_town']}"
    )
    print(
        f"Total ticks: {data['run']['total_ticks']}"
    )
    print(
        f"Starting Enteloot: "
        f"{data['run']['starting_enteloot']}"
    )

    print("Building map...")

    graph = build_graph(data)

    print(
        f"Map contains {len(graph)} reachable vertices."
    )

    print("Generating baseline solution...")

    routes = calculate_all_routes(
        data,
        graph
    )

    baseline = generate_baseline(
        data,
        routes
    )

    baseline_result = validate_solution(
        data,
        baseline
    )

    print(
        f"Baseline actions: {len(baseline)}"
    )

    print(
        f"Baseline ticks: "
        f"{baseline_result['ticks']}"
    )

    print("Optimising Level 1 strategy...")

    best_actions, baseline, routes = solve(data)

    print(
        f"Optimised actions: {len(best_actions)}"
    )

    validation = validate_solution(
        data,
        best_actions
    )

    print(
        f"Optimised ticks: "
        f"{validation['ticks']}"
    )

    print(
        f"Remaining ticks: "
        f"{validation['remaining_ticks']}"
    )

    print(
        f"Final location: "
        f"{validation['final_location']}"
    )

    print(
        f"Final inventory: "
        f"{validation['inventory']}"
    )

    output_file = create_submission(
        best_actions,
        "level1_submission.txt"
    )

    print(
        f"Submission created: {output_file}"
    )

    runtime = time.perf_counter() - start_time

    print(
        f"Runtime: {runtime:.4f} seconds"
    )


if __name__ == "__main__":
    main()