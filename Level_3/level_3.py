import json
import heapq


def load_input(filename):
    """Load the Bonus Level graph from the JSON input file."""
    with open(filename, "r") as file:
        return json.load(file)


def edge_cost(edge):
    """
    Calculate the effective cost of an edge.

    Bonus Level:
        effective cost = time + risk
    """
    return edge["time"] + edge["risk"]


def dijkstra(graph, start):
    """
    Run Dijkstra's algorithm from a starting node.

    Returns:
        distances:
            Shortest distance from start to every node.

        previous:
            Previous-node information used to reconstruct paths.
    """

    distances = {
        node: float("inf")
        for node in graph
    }

    previous = {
        node: None
        for node in graph
    }

    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:

        current_distance, current_node = heapq.heappop(
            priority_queue
        )

        # Ignore outdated entries.
        if current_distance > distances[current_node]:
            continue

        for neighbour_info in graph[current_node]:

            neighbour = neighbour_info["node"]

            cost = edge_cost(neighbour_info)

            new_distance = current_distance + cost

            if new_distance < distances[neighbour]:

                distances[neighbour] = new_distance
                previous[neighbour] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbour)
                )

    return distances, previous


def reconstruct_path(previous, start, end):
    """
    Reconstruct a shortest path using Dijkstra's previous-node data.
    """

    path = []

    current = end

    while current is not None:

        path.append(current)

        if current == start:
            break

        current = previous[current]

    path.reverse()

    if not path or path[0] != start:
        raise ValueError(
            f"No route found from {start} to {end}."
        )

    return path


def build_distance_matrix(
    graph,
    important_nodes
):
    """
    Run Dijkstra from every important node.

    The important nodes are:

        A
        S01 ... S24
        B

    Returns:

        distance_matrix:
            Shortest distance between important nodes.

        previous_paths:
            Dijkstra previous-node information for
            reconstructing the actual routes.
    """

    distance_matrix = {}
    previous_paths = {}

    for source in important_nodes:

        distances, previous = dijkstra(
            graph,
            source
        )

        distance_matrix[source] = {
            target: distances[target]
            for target in important_nodes
        }

        previous_paths[source] = previous

    return distance_matrix, previous_paths


def mst_cost(nodes, distance_matrix):
    """
    Calculate the minimum spanning tree cost for a set of nodes.

    This is used as part of the lower bound for
    branch-and-bound pruning.
    """

    if len(nodes) <= 1:
        return 0

    remaining = set(nodes)

    start = next(iter(remaining))
    remaining.remove(start)

    cheapest = {
        node: distance_matrix[start][node]
        for node in remaining
    }

    total = 0

    while remaining:

        next_node = min(
            remaining,
            key=lambda node: cheapest[node]
        )

        total += cheapest[next_node]

        remaining.remove(next_node)

        for node in remaining:

            new_distance = (
                distance_matrix[next_node][node]
            )

            if new_distance < cheapest[node]:
                cheapest[node] = new_distance

    return total


def lower_bound(
    current,
    unvisited,
    end,
    distance_matrix
):
    """
    Calculate a lower bound for completing a partial route.

    The lower bound contains:

        1. Cheapest connection from the current node
           to a remaining station.

        2. Minimum spanning tree connecting all
           remaining stations.

        3. Cheapest connection from a remaining station
           to the final destination.

    This allows branch-and-bound to eliminate
    routes that cannot improve the current best solution.
    """

    if not unvisited:
        return distance_matrix[current][end]

    unvisited_list = list(unvisited)

    connection_from_current = min(
        distance_matrix[current][node]
        for node in unvisited_list
    )

    connection_to_end = min(
        distance_matrix[node][end]
        for node in unvisited_list
    )

    tree_cost = mst_cost(
        unvisited_list,
        distance_matrix
    )

    return (
        connection_from_current
        + tree_cost
        + connection_to_end
    )


def greedy_route(
    start,
    end,
    required_stations,
    distance_matrix
):
    """
    Create an initial route using a nearest-neighbour
    greedy strategy.

    This route is not guaranteed to be optimal.

    Its purpose is to provide an initial upper bound
    for branch-and-bound.
    """

    current = start

    unvisited = set(required_stations)

    order = []

    total_cost = 0

    while unvisited:

        next_station = min(
            unvisited,
            key=lambda station:
                distance_matrix[current][station]
        )

        total_cost += (
            distance_matrix[current][next_station]
        )

        order.append(next_station)

        unvisited.remove(next_station)

        current = next_station

    total_cost += distance_matrix[current][end]

    return order, total_cost


class BranchAndBoundSolver:

    def __init__(
        self,
        start,
        end,
        required_stations,
        distance_matrix
    ):
        self.start = start
        self.end = end
        self.required_stations = required_stations
        self.distance_matrix = distance_matrix

        # Initial upper bound.
        (
            self.best_order,
            self.best_cost
        ) = greedy_route(
            start,
            end,
            required_stations,
            distance_matrix
        )

        self.nodes_explored = 0
        self.branches_pruned = 0

    def search(
        self,
        current,
        unvisited,
        current_cost,
        order
    ):
        """
        Recursively search for the best station ordering.
        """

        self.nodes_explored += 1

        # All stations have been visited.
        if not unvisited:

            final_cost = (
                current_cost
                + self.distance_matrix[current][self.end]
            )

            if final_cost < self.best_cost:

                self.best_cost = final_cost
                self.best_order = order.copy()

            return

        # Calculate a lower bound.
        bound = (
            current_cost
            + lower_bound(
                current,
                unvisited,
                self.end,
                self.distance_matrix
            )
        )

        # The branch cannot improve the best route.
        if bound >= self.best_cost:

            self.branches_pruned += 1

            return

        # Try closer stations first.
        candidates = sorted(
            unvisited,
            key=lambda node:
                self.distance_matrix[current][node]
        )

        for next_station in candidates:

            travel_cost = (
                self.distance_matrix[current][next_station]
            )

            new_cost = current_cost + travel_cost

            # Simple cost pruning.
            if new_cost >= self.best_cost:

                self.branches_pruned += 1

                continue

            unvisited.remove(next_station)
            order.append(next_station)

            self.search(
                next_station,
                unvisited,
                new_cost,
                order
            )

            order.pop()
            unvisited.add(next_station)

    def solve(self):
        """Run the branch-and-bound optimisation."""

        unvisited = set(
            self.required_stations
        )

        self.search(
            self.start,
            unvisited,
            0,
            []
        )

        return (
            self.best_order,
            self.best_cost,
            self.nodes_explored,
            self.branches_pruned
        )


def build_complete_route(
    start,
    end,
    order,
    previous_paths
):
    """
    Convert the optimal station ordering into
    the actual route through the original graph.
    """

    checkpoints = (
        [start]
        + order
        + [end]
    )

    complete_route = []

    for i in range(len(checkpoints) - 1):

        leg_start = checkpoints[i]
        leg_end = checkpoints[i + 1]

        path = reconstruct_path(
            previous_paths[leg_start],
            leg_start,
            leg_end
        )

        if i == 0:
            complete_route.extend(path)
        else:
            # Skip duplicated connection node.
            complete_route.extend(path[1:])

    return complete_route


def validate_route(
    route,
    start,
    end,
    required_stations
):
    """Validate the final route."""

    if not route:
        raise ValueError("Route is empty.")

    if route[0] != start:
        raise ValueError(
            "Route does not start at A."
        )

    if route[-1] != end:
        raise ValueError(
            "Route does not end at B."
        )

    for station in required_stations:

        if station not in route:

            raise ValueError(
                f"Required station {station} "
                "was not visited."
            )


def create_submission(route, filename):
    """Create the required JSON submission file."""

    output = {
        "route": route
    }

    with open(filename, "w") as file:
        json.dump(
            output,
            file,
            indent=4
        )


def main():

    # =========================================================
    # 1. INPUT
    # =========================================================

    data = load_input("3.txt")

    graph = data["adjacency_list"]

    start = data["start"]
    end = data["end"]

    required_stations = data["required_stops"]

    # =========================================================
    # 2. IMPORTANT NODES
    # =========================================================

    important_nodes = (
        [start]
        + required_stations
        + [end]
    )

    # =========================================================
    # 3. SHORTEST-PATH PREPROCESSING
    # =========================================================

    print("Building distance matrix...")

    (
        distance_matrix,
        previous_paths
    ) = build_distance_matrix(
        graph,
        important_nodes
    )

    print("Distance matrix completed.")

    # =========================================================
    # 4. BRANCH-AND-BOUND
    # =========================================================

    print("Searching for optimal station order...")

    solver = BranchAndBoundSolver(
        start,
        end,
        required_stations,
        distance_matrix
    )

    (
        best_order,
        best_cost,
        nodes_explored,
        branches_pruned
    ) = solver.solve()

    # =========================================================
    # 5. RECONSTRUCT COMPLETE ROUTE
    # =========================================================

    best_path = build_complete_route(
        start,
        end,
        best_order,
        previous_paths
    )

    # =========================================================
    # 6. VALIDATE
    # =========================================================

    validate_route(
        best_path,
        start,
        end,
        required_stations
    )

    # =========================================================
    # 7. CREATE SUBMISSION
    # =========================================================

    output_file = "level3_submission.txt"

    create_submission(
        best_path,
        output_file
    )

    # =========================================================
    # 8. DISPLAY RESULT
    # =========================================================

    print()
    print("Bonus Level solution completed.")
    print()

    print("Start:", start)
    print("End:", end)

    print()

    print("Optimal station order:")
    print(" -> ".join(best_order))

    print()

    print("Complete route:")
    print(" -> ".join(best_path))

    print()

    print("Total effective cost:")
    print(best_cost)

    print()

    print("Search nodes explored:")
    print(nodes_explored)

    print()

    print("Branches pruned:")
    print(branches_pruned)

    print()

    print("Submission file:")
    print(output_file)


if __name__ == "__main__":
    main()