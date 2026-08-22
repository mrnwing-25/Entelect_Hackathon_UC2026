import json
import heapq
import math
import os
from collections import defaultdict, Counter


# ============================================================
# LEVEL 3 CONSTANTS
# ============================================================

RESOURCE_SELL_PRICE = {
    "wheat": 2,
    "wood": 3,
    "stone": 3,
    "clay": 4,
    "fish": 4,
    "sheep": 5,
    "ore": 6,
}

RESOURCE_BUY_PRICE = {
    "wheat": 4,
    "wood": 5,
    "stone": 5,
    "clay": 6,
    "fish": 6,
    "sheep": 8,
}

RECIPES = {
    "bread": {
        "inputs": {"wheat": 3},
        "time": 2,
    },
    "fish-n-chips": {
        "inputs": {
            "fish": 2,
            "wheat": 1,
        },
        "time": 2,
    },
    "stew": {
        "inputs": {
            "sheep": 1,
            "fish": 1,
            "wheat": 1,
        },
        "time": 2,
    },
    "wooden-crafts": {
        "inputs": {"wood": 4},
        "time": 2,
    },
    "furniture": {
        "inputs": {
            "wood": 3,
            "sheep": 1,
        },
        "time": 2,
    },
    "stone-works": {
        "inputs": {"stone": 5},
        "time": 2,
    },
    "roof-tiles": {
        "inputs": {
            "clay": 3,
            "stone": 2,
        },
        "time": 2,
    },
    "wool-garments": {
        "inputs": {"sheep": 3},
        "time": 2,
    },
    "pottery": {
        "inputs": {
            "clay": 4,
            "wood": 1,
        },
        "time": 2,
    },
}


COMPONENTS = {
    "planks": {
        "inputs": {"wood": 2},
        "time": 2,
    },
    "thatch": {
        "inputs": {"wheat": 2},
        "time": 2,
    },
    "stone-blocks": {
        "inputs": {"stone": 3},
        "time": 2,
    },
    "mortar": {
        "inputs": {
            "clay": 1,
            "stone": 1,
        },
        "time": 2,
    },
    "bricks": {
        "inputs": {
            "clay": 2,
            "mortar": 1,
        },
        "time": 2,
    },
    "rope": {
        "inputs": {"sheep": 2},
        "time": 2,
    },
    "fencing": {
        "inputs": {
            "wood": 2,
            "rope": 1,
        },
        "time": 2,
    },
    "kiln-glass": {
        "inputs": {
            "clay": 2,
            "wood": 2,
        },
        "time": 2,
    },
    "nets": {
        "inputs": {
            "rope": 1,
            "fencing": 1,
        },
        "time": 2,
    },
    "iron-fittings": {
        "inputs": {
            "ore": 2,
            "wood": 1,
        },
        "time": 2,
    },
}


TOOLS = {
    "boots": {
        "inputs": {
            "iron-fittings": 2,
            "rope": 2,
        },
        "effect": "travel",
    },
    "pickaxe": {
        "inputs": {
            "iron-fittings": 2,
            "planks": 2,
        },
        "effect": "gather",
    },
}


UPGRADES = {
    "Farmhouse": {
        "boost": "sheep",
        "components": {
            "planks": 3,
            "thatch": 2,
        },
        "enteloot": 500,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Pier": {
        "boost": "fish",
        "components": {
            "planks": 4,
            "nets": 2,
        },
        "enteloot": 600,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Fertilised-fields": {
        "boost": "wheat",
        "components": {
            "fencing": 2,
            "thatch": 2,
        },
        "enteloot": 500,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Quarry": {
        "boost": "stone",
        "components": {
            "stone-blocks": 3,
            "planks": 2,
        },
        "enteloot": 600,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Woodlands": {
        "boost": "wood",
        "components": {
            "fencing": 2,
            "rope": 2,
        },
        "enteloot": 500,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Pottery-house": {
        "boost": "clay",
        "components": {
            "bricks": 4,
            "planks": 2,
        },
        "enteloot": 700,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Rec-center": {
        "boost": "enteloot_amount_20",
        "components": {
            "planks": 4,
            "bricks": 3,
            "rope": 1,
        },
        "enteloot": 1200,
        "time": 4,
        "prerequisite": "production",
        "score": 3000,
    },
    "Fire-station": {
        "boost": "boost_duration_50",
        "components": {
            "bricks": 5,
            "stone-blocks": 3,
            "rope": 2,
        },
        "enteloot": 1800,
        "time": 4,
        "prerequisite": "production2",
        "score": 4000,
    },
    "School": {
        "boost": "enteloot_amount_50",
        "components": {
            "bricks": 6,
            "planks": 3,
            "kiln-glass": 2,
        },
        "enteloot": 2000,
        "time": 5,
        "prerequisite": "Rec-center",
        "score": 5000,
    },
    "Police-station": {
        "boost": "enteloot_rate_minus_2",
        "components": {
            "bricks": 6,
            "stone-blocks": 4,
            "iron-fittings": 2,
        },
        "enteloot": 2200,
        "time": 5,
        "prerequisite": "Fire-station",
        "score": 5000,
    },
    "Library": {
        "boost": "enteloot_amount_50",
        "components": {
            "bricks": 5,
            "planks": 5,
            "kiln-glass": 2,
        },
        "enteloot": 2500,
        "time": 5,
        "prerequisite": "School",
        "score": 6000,
    },
}


# ============================================================
# GENERAL UTILITIES
# ============================================================

def load_input(filename):
    """Load the level JSON."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def normalise_name(value):
    """
    Convert names to a consistent comparison form.

    This is useful because JSON uses names such as:
        Fertilised-fields
        Rec-center
        iron-fittings

    while Python code may use other casing.
    """
    return str(value).strip().lower().replace("_", "-")


def deep_copy_dict(value):
    """Small dependency-free recursive dictionary copy."""
    if isinstance(value, dict):
        return {
            key: deep_copy_dict(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            deep_copy_dict(item)
            for item in value
        ]

    return value


# ============================================================
# GRAPH
# ============================================================

class Graph:
    """
    Graph supporting:

        - standard routes
        - fast routes
        - parallel edges
        - route reconstruction
    """

    def __init__(self, data):
        self.adjacency = defaultdict(list)

        self.vertices = set()

        self.standard_edges = {}
        self.fast_edges = {}

        self._build(data["routes"])

    def _build(self, routes):
        for route in routes:

            a, b = route["between"]

            weight = int(route["weight"])
            toll = int(route.get("toll", 0))

            self.vertices.add(a)
            self.vertices.add(b)

            edge = {
                "destination": b,
                "weight": weight,
                "toll": toll,
                "fast": toll > 0,
            }

            reverse_edge = {
                "destination": a,
                "weight": weight,
                "toll": toll,
                "fast": toll > 0,
            }

            key = self._edge_key(a, b)

            if toll == 0:
                self.standard_edges[key] = edge
                self.standard_edges[self._edge_key(b, a)] = reverse_edge
            else:
                self.fast_edges[key] = edge
                self.fast_edges[self._edge_key(b, a)] = reverse_edge

            self.adjacency[a].append(edge)
            self.adjacency[b].append(reverse_edge)

    @staticmethod
    def _edge_key(a, b):
        return (a, b)

    def get_edge(self, source, destination, fast=False):
        """
        Return the requested edge.

        Returns None when it doesn't exist.
        """

        table = (
            self.fast_edges
            if fast
            else self.standard_edges
        )

        return table.get(
            self._edge_key(source, destination)
        )

    def has_edge(self, source, destination, fast=False):
        return self.get_edge(
            source,
            destination,
            fast
        ) is not None

    def neighbours(self, node):
        return self.adjacency.get(node, [])


# ============================================================
# SHORTEST PATH
# ============================================================

class PathFinder:
    """
    Dijkstra shortest path engine.

    Level 3 supports Boots.

    Without Boots:
        normal edge weight

    With Boots:
        max(1, weight - 1)
    """

    def __init__(self, graph):
        self.graph = graph

    def edge_time(self, edge, boots=False):
        if boots:
            return max(
                1,
                edge["weight"] - 1
            )

        return edge["weight"]

    def shortest_path(
        self,
        start,
        end,
        boots=False,
        allow_fast=False,
        enteloot=None,
    ):
        """
        Find a shortest route.

        Fast routes are optional.

        When allow_fast=False:
            only standard routes are used.

        When allow_fast=True:
            fast routes are considered when their toll
            can be paid.
        """

        if start == end:
            return {
                "time": 0,
                "toll": 0,
                "path": [start],
                "fast_flags": [],
            }

        pq = [
            (0, 0, start)
        ]

        distances = {
            start: (0, 0)
        }

        previous = {}

        while pq:

            current_time, current_toll, node = heapq.heappop(pq)

            known = distances.get(node)

            if known is None:
                continue

            if (
                current_time != known[0]
                or current_toll != known[1]
            ):
                continue

            for edge in self.graph.neighbours(node):

                destination = edge["destination"]

                edge_fast = edge["fast"]

                if edge_fast and not allow_fast:
                    continue

                if edge_fast:
                    toll = edge["toll"]

                    if enteloot is not None:
                        if current_toll + toll > enteloot:
                            continue
                else:
                    toll = 0

                time = self.edge_time(
                    edge,
                    boots
                )

                new_time = (
                    current_time
                    + time
                )

                new_toll = (
                    current_toll
                    + toll
                )

                old = distances.get(
                    destination
                )

                candidate = (
                    new_time,
                    new_toll
                )

                if old is None or candidate < old:

                    distances[destination] = candidate

                    previous[destination] = (
                        node,
                        edge_fast
                    )

                    heapq.heappush(
                        pq,
                        (
                            new_time,
                            new_toll,
                            destination
                        )
                    )

        if end not in distances:
            return None

        path = []
        fast_flags = []

        current = end

        while current != start:

            path.append(current)

            previous_node, was_fast = previous[current]

            fast_flags.append(was_fast)

            current = previous_node

        path.append(start)

        path.reverse()
        fast_flags.reverse()

        return {
            "time": distances[end][0],
            "toll": distances[end][1],
            "path": path,
            "fast_flags": fast_flags,
        }


# ============================================================
# ACTION BUILDER
# ============================================================

class ActionBuilder:

    def __init__(self):
        self.actions = []

    def travel(self, destination, fast=False):
        action = {
            "type": "travel",
            "destination": destination,
        }

        if fast:
            action["fast"] = True

        self.actions.append(action)

    def gather(self):
        self.actions.append({
            "type": "gather"
        })

    def buy(self, resource, quantity):
        if quantity <= 0:
            return

        self.actions.append({
            "type": "buy",
            "resource": resource,
            "quantity": int(quantity),
        })

    def sell(self, item, quantity):
        if quantity <= 0:
            return

        self.actions.append({
            "type": "sell",
            "item": item,
            "quantity": int(quantity),
        })

    def craft(self, item, quantity):
        if quantity <= 0:
            return

        self.actions.append({
            "type": "craft",
            "item": item,
            "quantity": int(quantity),
        })

    def build(self, upgrade):
        self.actions.append({
            "type": "build",
            "upgrade": upgrade,
        })

    def upkeep(self):
        self.actions.append({
            "type": "upkeep"
        })


# ============================================================
# STATE
# ============================================================

class PlannerState:

    def __init__(self, data):

        run = data["run"]

        self.total_ticks = int(
            run["total_ticks"]
        )

        self.tick = 0

        self.enteloot = int(
            run["starting_enteloot"]
        )

        self.starting_town = (
            run["starting_town"]
        )

        self.location = self.starting_town

        self.inventory = Counter()

        self.upgrades = defaultdict(set)

        self.tools = set()

        self.action_count = 0

    def add_resource(self, resource, amount):
        self.inventory[resource] += int(amount)

    def consume(self, resource, amount):
        if self.inventory[resource] < amount:
            return False

        self.inventory[resource] -= amount

        if self.inventory[resource] <= 0:
            del self.inventory[resource]

        return True

    def can_afford_components(self, components):
        for item, amount in components.items():

            if self.inventory[item] < amount:
                return False

        return True

    def consume_components(self, components):
        for item, amount in components.items():

            if not self.consume(
                item,
                amount
            ):
                return False

        return True

    def has_upgrade(self, town, upgrade):
        return (
            upgrade in self.upgrades[town]
        )

    def add_upgrade(self, town, upgrade):
        self.upgrades[town].add(upgrade)

    def has_tool(self, tool):
        return (
            normalise_name(tool)
            in self.tools
        )


# ============================================================
# PRODUCTION / PASSIVE ECONOMY
# ============================================================

class Economy:

    def __init__(self, data):

        self.towns = data["towns"]

    def production_per_cycle(
        self,
        town,
        resource,
        state=None
    ):
        town_data = self.towns[town]

        amount = (
            town_data["production"]
            ["resources"]
            .get(resource, 0)
        )

        if state is not None:

            # Production upgrades double the
            # corresponding resource.
            production_upgrade = {
                "Farmhouse": "sheep",
                "Pier": "fish",
                "Fertilised-fields": "wheat",
                "Quarry": "stone",
                "Woodlands": "wood",
                "Pottery-house": "clay",
            }

            for upgrade, boosted_resource in (
                production_upgrade.items()
            ):

                if (
                    boosted_resource == resource
                    and state.has_upgrade(
                        town,
                        upgrade
                    )
                ):
                    amount *= 2

        return int(amount)

    def enteloot_per_cycle(
        self,
        town,
        state=None
    ):
        town_data = self.towns[town]

        amount = int(
            town_data["enteloot"]["amount"]
        )

        if state is None:
            return amount

        percentage = 0

        if state.has_upgrade(
            town,
            "Rec-center"
        ):
            percentage += 20

        if state.has_upgrade(
            town,
            "School"
        ):
            percentage += 50

        if state.has_upgrade(
            town,
            "Library"
        ):
            percentage += 50

        amount = (
            amount
            * (100 + percentage)
            / 100
        )

        amount = int(amount)

        production_upgrades = {
            "Farmhouse": "sheep",
            "Pier": "fish",
            "Fertilised-fields": "wheat",
            "Quarry": "stone",
            "Woodlands": "wood",
            "Pottery-house": "clay",
        }

        if any(
            state.has_upgrade(
                town,
                upgrade
            )
            for upgrade in production_upgrades
        ):
            # Production upgrades themselves do not
            # increase Enteloot according to the
            # specification, so do nothing here.
            pass

        return amount


# ============================================================
# NODE ANALYSIS
# ============================================================

# ============================================================
# NODE ANALYSIS
# ============================================================

class NodeManager:

    def __init__(
        self,
        data,
        pathfinder
    ):
        self.data = data
        self.nodes = data["nodes"]
        self.pathfinder = pathfinder

    def nodes_for_resource(self, resource):
        result = []

        for node, info in self.nodes.items():

            if info.get("resource") == resource:
                result.append(node)

        return result

    def get_distance(
        self,
        start,
        end
    ):
        """
        Return the shortest standard-route travel time
        between two locations.

        Boots are deliberately not assumed here because
        this method is used for general node ranking.
        """

        path = self.pathfinder.shortest_path(
            start,
            end,
            boots=False,
            allow_fast=False,
        )

        if path is None:
            return float("inf")

        return path["time"]

    def best_resource_node(
        self,
        resource,
        current_location
    ):
        """
        Select the resource node with the best economic
        efficiency.

        Score:

            resource yield
            -------------------------------
            travel time + gather time

        A higher score is better.
        """

        best_node = None
        best_score = float("-inf")

        for node_name, node in self.nodes.items():

            if node.get("resource") != resource:
                continue

            yield_amount = int(
                node.get("yield", 0)
            )

            gather_time = int(
                node.get("gather-time", 999999)
            )

            travel_time = self.get_distance(
                current_location,
                node_name
            )

            if math.isinf(travel_time):
                continue

            total_time = (
                travel_time
                + gather_time
            )

            if total_time <= 0:
                continue

            score = (
                yield_amount
                / total_time
            )

            if score > best_score:

                best_score = score
                best_node = node_name

        return best_node

    def ore_nodes(self):

        return [
            node
            for node, info in self.nodes.items()
            if info.get("resource") == "ore"
        ]


# ============================================================
# RESOURCE ACQUISITION
# ============================================================

class ResourcePlanner:

    def __init__(
            self,
            data,
            graph,
            pathfinder,
            state,
        ):

            self.data = data
            self.graph = graph
            self.pathfinder = pathfinder
            self.state = state

            self.node_manager = NodeManager(
                data,
                pathfinder
            )

    def nearest_node(
        self,
        resource,
        boots=False
    ):

        candidates = (
            self.node_manager
            .nodes_for_resource(resource)
        )

        best = None

        for node in candidates:

            path = self.pathfinder.shortest_path(
                self.state.location,
                node,
                boots=boots,
                allow_fast=False,
            )

            if path is None:
                continue

            score = (
                path["time"]
                + self.data["nodes"][node]["gather-time"]
            )

            if best is None or score < best[0]:

                best = (
                    score,
                    node,
                    path
                )

        return best

    def gather_resource(
        self,
        resource,
        quantity,
        actions,
    ):
        """
        Gather enough of a resource.

        This is deliberately deterministic.

        For ore, gathering is mandatory because it
        cannot be purchased.
        """

        quantity = int(
            math.ceil(quantity)
        )

        if quantity <= 0:
            return True

        boots = self.state.has_tool(
            "boots"
        )

        pickaxe = self.state.has_tool(
            "pickaxe"
        )

        while (
            self.state.inventory[resource]
            < quantity
        ):

            choice = self.nearest_node(
                resource,
                boots=boots
            )

            if choice is None:
                return False

            _, node, path = choice

            if not self.move_using_path(
                path,
                actions
            ):
                return False

            node_data = (
                self.data["nodes"][node]
            )

            gather_time = int(
                node_data["gather-time"]
            )

            if pickaxe:
                gather_time = max(
                    1,
                    gather_time - 1
                )

            if (
                self.state.tick
                + gather_time
                > self.state.total_ticks
            ):
                return False

            actions.gather()

            self.state.tick += gather_time
            self.state.action_count += 1

            self.state.add_resource(
                resource,
                node_data["yield"]
            )

        return True

    def move_using_path(
        self,
        path,
        actions
    ):
        """
        Convert a shortest-path result into
        travel actions.
        """

        vertices = path["path"]
        fast_flags = path["fast_flags"]

        for i in range(
            len(vertices) - 1
        ):

            source = vertices[i]
            destination = vertices[i + 1]

            fast = fast_flags[i]

            edge = self.graph.get_edge(
                source,
                destination,
                fast=fast
            )

            if edge is None:
                return False

            travel_time = (
                self.pathfinder.edge_time(
                    edge,
                    self.state.has_tool(
                        "boots"
                    )
                )
            )

            if (
                self.state.tick
                + travel_time
                > self.state.total_ticks
            ):
                return False

            if fast:

                toll = edge["toll"]

                if (
                    self.state.enteloot
                    < toll
                ):
                    return False

                self.state.enteloot -= toll

            actions.travel(
                destination,
                fast=fast
            )

            self.state.tick += travel_time
            self.state.action_count += 1

            self.state.location = destination

        return True


# ============================================================
# CRAFTING
# ============================================================

class CraftingPlanner:

    def __init__(
        self,
        data,
        state,
        actions
    ):

        self.data = data
        self.state = state
        self.actions = actions

    def craft_time(self, town):
        """
        Return crafting time for the current location.

        Nodes are not towns, so if the player is standing
        at a resource node, use the normal crafting time.
        """

        town_data = self.data["towns"].get(town)

        if town_data is None:
            return 2

        affinities = town_data.get(
            "affinities",
            []
        )

        if "crafting" in affinities:
            return 1

        return 2

    def craft_component(
        self,
        component,
        quantity
    ):
        """
        Craft a construction component.

        Dependencies are recursively crafted first.
        """

        quantity = int(quantity)

        if quantity <= 0:
            return True

        if component not in COMPONENTS:
            return False

        recipe = COMPONENTS[component]

        # First produce all component dependencies.
        for ingredient, amount in (
            recipe["inputs"].items()
        ):

            required = (
                amount * quantity
            )

            if ingredient in COMPONENTS:

                if self.state.inventory[
                    ingredient
                ] < required:

                    missing = (
                        required
                        - self.state.inventory[
                            ingredient
                        ]
                    )

                    if not self.craft_component(
                        ingredient,
                        missing
                    ):
                        return False

        # Raw resources must now exist.
        for ingredient, amount in (
            recipe["inputs"].items()
        ):

            if ingredient in COMPONENTS:
                continue

            required = (
                amount * quantity
            )

            if (
                self.state.inventory[
                    ingredient
                ]
                < required
            ):
                return False

        # Consume inputs.
        for ingredient, amount in (
            recipe["inputs"].items()
        ):

            required = (
                amount * quantity
            )

            if not self.state.consume(
                ingredient,
                required
            ):
                return False

        craft_time = self.craft_time(
            self.state.location
        )

        ticks = (
            quantity
            * craft_time
        )

        if (
            self.state.tick + ticks
            > self.state.total_ticks
        ):
            return False

        self.actions.craft(
            component,
            quantity
        )

        self.state.tick += ticks
        self.state.action_count += 1

        self.state.inventory[
            component
        ] += quantity

        return True

    def craft_good(
        self,
        item,
        quantity
    ):
        if item not in RECIPES:
            return False

        quantity = int(quantity)

        recipe = RECIPES[item]

        for resource, amount in (
            recipe["inputs"].items()
        ):

            required = (
                amount * quantity
            )

            if (
                self.state.inventory[
                    resource
                ] < required
            ):
                return False

        for resource, amount in (
            recipe["inputs"].items()
        ):

            required = (
                amount * quantity
            )

            self.state.consume(
                resource,
                required
            )

        craft_time = self.craft_time(
            self.state.location
        )

        ticks = (
            quantity
            * craft_time
        )

        if (
            self.state.tick + ticks
            > self.state.total_ticks
        ):
            return False

        self.actions.craft(
            item,
            quantity
        )

        self.state.tick += ticks
        self.state.action_count += 1

        self.state.inventory[
            item
        ] += quantity

        return True


# ============================================================
# UPGRADE MANAGER
# ============================================================

class UpgradeManager:

    PRODUCTION_UPGRADES = {
        "Farmhouse",
        "Pier",
        "Fertilised-fields",
        "Quarry",
        "Woodlands",
        "Pottery-house",
    }

    def __init__(
        self,
        data,
        state,
        actions,
        crafting
    ):

        self.data = data
        self.state = state
        self.actions = actions
        self.crafting = crafting

    # --------------------------------------------------------
    # FIX FOR YOUR ERROR
    # --------------------------------------------------------

    @staticmethod
    def prerequisite_satisfied(
        prerequisite,
        town_upgrades
    ):
        """
        Handle every supported prerequisite form.

        The previous code effectively did:

            prerequisites.get(...)

        but some prerequisites are represented as
        lists/strings rather than dictionaries.

        This function deliberately supports:

            None
            string
            list
            tuple
            set
            dictionary
        """

        if prerequisite is None:
            return True

        if isinstance(
            prerequisite,
            str
        ):
            if prerequisite == "production":
                return (
                    len(
                        town_upgrades
                        & UpgradeManager
                        .PRODUCTION_UPGRADES
                    )
                    >= 1
                )

            if prerequisite == "production2":
                return (
                    len(
                        town_upgrades
                        & UpgradeManager
                        .PRODUCTION_UPGRADES
                    )
                    >= 2
                )

            return (
                prerequisite
                in town_upgrades
            )

        if isinstance(
            prerequisite,
            (list, tuple, set)
        ):
            return all(
                item in town_upgrades
                for item in prerequisite
            )

        if isinstance(
            prerequisite,
            dict
        ):
            for key, value in (
                prerequisite.items()
            ):

                if key == "any":

                    if isinstance(
                        value,
                        (list, tuple, set)
                    ):
                        if not any(
                            item in town_upgrades
                            for item in value
                        ):
                            return False

                elif key == "all":

                    if isinstance(
                        value,
                        (list, tuple, set)
                    ):
                        if not all(
                            item in town_upgrades
                            for item in value
                        ):
                            return False

                elif key == "production":

                    count = len(
                        town_upgrades
                        & UpgradeManager
                        .PRODUCTION_UPGRADES
                    )

                    if count < int(value):
                        return False

                else:

                    if value and (
                        key not in town_upgrades
                    ):
                        return False

            return True

        return False

    def can_build(
        self,
        town,
        upgrade
    ):
        if upgrade not in UPGRADES:
            return False

        if self.state.has_upgrade(
            town,
            upgrade
        ):
            return False

        info = UPGRADES[upgrade]

        prerequisite = (
            info.get("prerequisite")
        )

        if not self.prerequisite_satisfied(
            prerequisite,
            self.state.upgrades[town]
        ):
            return False

        if self.state.enteloot < info["enteloot"]:
            return False

        if not self.state.can_afford_components(
            info["components"]
        ):
            return False

        return True

    def build(
        self,
        town,
        upgrade
    ):
        if not self.can_build(
            town,
            upgrade
        ):
            return False

        info = UPGRADES[upgrade]

        if not self.state.consume_components(
            info["components"]
        ):
            return False

        self.state.enteloot -= (
            info["enteloot"]
        )

        ticks = int(
            info["time"]
        )

        if (
            self.state.tick + ticks
            > self.state.total_ticks
        ):
            return False

        self.actions.build(
            upgrade
        )

        self.state.tick += ticks
        self.state.action_count += 1

        self.state.add_upgrade(
            town,
            upgrade
        )

        return True
# ============================================================
# RECIPE DEPENDENCY ENGINE
# ============================================================

class DependencyPlanner:

    def __init__(self):
        self.components = COMPONENTS

    def expand(
        self,
        item,
        quantity,
        result=None
    ):
        """
        Recursively expand a component recipe into
        raw resources.

        Example:

            bricks
              -> clay
              -> mortar
                   -> clay
                   -> stone
        """

        if result is None:
            result = Counter()

        quantity = int(quantity)

        # Raw resource
        if item not in self.components:
            result[item] += quantity
            return result

        recipe = self.components[item]

        for ingredient, amount in recipe["inputs"].items():

            self.expand(
                ingredient,
                amount * quantity,
                result
            )

        return result

    def raw_requirements(
        self,
        requirements
    ):
        """
        Convert component requirements into
        total raw resource requirements.
        """

        result = Counter()

        for item, quantity in requirements.items():

            expanded = self.expand(
                item,
                quantity
            )

            result.update(expanded)

        return result

# ============================================================
# TOOL MANAGER
# ============================================================

class ToolManager:

    def __init__(
        self,
        state,
        actions,
        crafting
    ):

        self.state = state
        self.actions = actions
        self.crafting = crafting

    def craft_tool(
        self,
        tool
    ):
        tool_key = normalise_name(tool)

        if tool_key in self.state.tools:
            return False

        if tool_key not in TOOLS:
            return False

        info = TOOLS[tool_key]

        for item, amount in (
            info["inputs"].items()
        ):

            if (
                self.state.inventory[item]
                < amount
            ):
                return False

        for item, amount in (
            info["inputs"].items()
        ):

            self.state.consume(
                item,
                amount
            )

        craft_time = (
            self.crafting.craft_time(
                self.state.location
            )
        )

        if (
            self.state.tick
            + craft_time
            > self.state.total_ticks
        ):
            return False

        self.actions.craft(
            tool,
            1
        )

        self.state.tick += craft_time
        self.state.action_count += 1

        self.state.tools.add(
            tool_key
        )

        return True


# ============================================================
# RAW RESOURCE REQUIREMENTS
# ============================================================

def total_raw_requirements_for_upgrades(
    upgrades
):
    """
    Determine the raw resource requirements for
    a collection of upgrades.

    This is used for planning rather than execution.
    """

    dependency = DependencyPlanner()

    component_requirements = Counter()

    for upgrade in upgrades:

        info = UPGRADES[upgrade]

        component_requirements.update(
            info["components"]
        )

    return dependency.raw_requirements(
        component_requirements
    )


# ============================================================
# STRATEGY
# ============================================================

class Level3Strategy:

    def __init__(self, data):

        self.data = data

        self.graph = Graph(data)

        self.pathfinder = PathFinder(
            self.graph
        )

        self.node_manager = NodeManager(
            data,
            self.pathfinder
        )

        self.state = PlannerState(
            data
        )

        self.actions = ActionBuilder()

        self.economy = Economy(
            data
        )

        self.crafting = CraftingPlanner(
            data,
            self.state,
            self.actions
        )

        self.resource_planner = (
            ResourcePlanner(
                data,
                self.graph,
                self.pathfinder,
                self.state
            )
        )

        self.upgrades = UpgradeManager(
            data,
            self.state,
            self.actions,
            self.crafting
        )

        self.tools = ToolManager(
            self.state,
            self.actions,
            self.crafting
        )

        self.actions = ActionBuilder()

        self.economy = Economy(
            data
        )

        self.crafting = CraftingPlanner(
            data,
            self.state,
            self.actions
        )

        self.resource_planner = (
            ResourcePlanner(
                data,
                self.graph,
                self.pathfinder,
                self.state
            )
        )

        self.upgrades = UpgradeManager(
            data,
            self.state,
            self.actions,
            self.crafting
        )

        self.tools = ToolManager(
            self.state,
            self.actions,
            self.crafting
        )

    # --------------------------------------------------------
    # TRAVEL
    # --------------------------------------------------------

    def travel_to(
        self,
        destination,
        prefer_fast=False
    ):
        """
        Travel from the current location.

        Fast routes are used only when they provide a
        meaningful time saving relative to their toll.
        """

        if (
            self.state.location
            == destination
        ):
            return True

        boots = self.state.has_tool(
            "boots"
        )

        standard = (
            self.pathfinder.shortest_path(
                self.state.location,
                destination,
                boots=boots,
                allow_fast=False,
            )
        )

        fast = None

        if prefer_fast:
            fast = (
                self.pathfinder.shortest_path(
                    self.state.location,
                    destination,
                    boots=boots,
                    allow_fast=True,
                    enteloot=self.state.enteloot,
                )
            )

        selected = standard

        if fast is not None:

            if standard is None:

                selected = fast

            else:

                time_saved = (
                    standard["time"]
                    - fast["time"]
                )

                toll = fast["toll"]

                # Fast route is worthwhile when the
                # saved ticks are substantial and the
                # toll is affordable.
                if (
                    time_saved >= 2
                    and toll <= max(
                        250,
                        time_saved * 50
                    )
                ):
                    selected = fast

        if selected is None:
            return False

        return self.resource_planner.move_using_path(
            selected,
            self.actions
        )

    # --------------------------------------------------------
    # RESOURCE COLLECTION
    # --------------------------------------------------------

    def obtain_resources(
        self,
        requirements
    ):
        """
        Obtain the required raw resources.

        Strategy:

        1. Use resource nodes where possible.
        2. Ore must always be gathered.
        3. Other resources are gathered from
           nodes rather than buying them.
        """

        ordered = sorted(
            requirements.items(),
            key=lambda pair: (
                pair[0] != "ore",
                -pair[1]
            )
        )

        for resource, amount in ordered:

            current = (
                self.state.inventory[
                    resource
                ]
            )

            missing = (
                amount - current
            )

            if missing <= 0:
                continue

            # Ore cannot be purchased.
            if resource == "ore":

                if not self.resource_planner.gather_resource(
                    resource,
                    missing,
                    self.actions
                ):
                    return False

                continue

            if not self.resource_planner.gather_resource(
                resource,
                missing,
                self.actions
            ):
                return False

        return True

    # --------------------------------------------------------
    # COMPONENT CRAFTING
    # --------------------------------------------------------

    def produce_component_tree(
    self,
    requirements
):
        """
        Produce all components in dependency order.

        Components can only be crafted at towns.

        If the strategy is currently at a resource node,
        return to the nearest town with crafting affinity
        before crafting.
        """

        # --------------------------------------------------------
        # Make sure we are at a town
        # --------------------------------------------------------

        if self.state.location not in self.data["towns"]:

            crafting_towns = [
                town_name
                for town_name, town_info
                in self.data["towns"].items()
                if "crafting"
                in town_info.get(
                    "affinities",
                    []
                )
            ]

            if not crafting_towns:
                return False

            best_town = None
            best_path = None

            for town in crafting_towns:

                path = self.pathfinder.shortest_path(
                    self.state.location,
                    town,
                    boots=self.state.has_tool(
                        "boots"
                    ),
                    allow_fast=False,
                )

                if path is None:
                    continue

                if (
                    best_path is None
                    or path["time"] < best_path["time"]
                ):
                    best_town = town
                    best_path = path

            if best_town is None:
                return False

            if not self.resource_planner.move_using_path(
                best_path,
                self.actions
            ):
                return False

        # --------------------------------------------------------
        # Components with deeper dependencies first
        # --------------------------------------------------------

        ordered = [
            "mortar",
            "bricks",
            "rope",
            "fencing",
            "nets",
            "kiln-glass",
            "iron-fittings",
            "planks",
            "thatch",
            "stone-blocks",
        ]

        remaining = Counter(
            requirements
        )

        # --------------------------------------------------------
        # Craft components
        # --------------------------------------------------------

        for component in ordered:

            amount = remaining.get(
                component,
                0
            )

            if amount <= 0:
                continue

            current = (
                self.state.inventory[
                    component
                ]
            )

            missing = (
                amount - current
            )

            if missing <= 0:
                continue

            if not self.crafting.craft_component(
                component,
                missing
            ):
                return False

        return True

    # --------------------------------------------------------
    # UPGRADE PLANNING
    # --------------------------------------------------------

    def production_upgrade_priority(
        self
    ):
        """
        Rank production upgrades according to how much
        passive production they can potentially improve.

        Targon and Shurima, for example, have high
        Enteloot production, but production upgrades
        affect resources rather than Enteloot directly.
        """

        result = []

        for town, info in (
            self.data["towns"].items()
        ):

            resources = (
                info["production"]["resources"]
            )

            for upgrade, upgrade_info in (
                UPGRADES.items()
            ):

                if upgrade_info[
                    "boost"
                ] in resources:

                    amount = resources[
                        upgrade_info["boost"]
                    ]

                    score = (
                        amount
                        * 100
                        + info["enteloot"]["amount"]
                    )

                    result.append(
                        (
                            score,
                            town,
                            upgrade
                        )
                    )

        result.sort(
            key=lambda x: (
                -x[0],
                x[1],
                x[2]
            )
        )

        return result

    def choose_infrastructure_towns(
        self
    ):
        """
        Prefer towns with strong Enteloot generation.

        Civic upgrades have a much larger infrastructure
        score value, so these towns are attractive targets.
        """

        towns = list(
            self.data["towns"].keys()
        )

        towns.sort(
            key=lambda town: (
                -self.data["towns"][town]
                ["enteloot"]["amount"],
                self.data["towns"][town]
                ["enteloot"]["rate"],
                town
            )
        )

        return towns
        
    def travel_to_crafting_town(self):
        """
        Move to the nearest town with crafting affinity.

        This method is safe when the current location is a
        resource node such as N19 or N21.
        """

        current = self.state.location

        # Already in a crafting town.
        if current in self.data["towns"]:

            affinities = (
                self.data["towns"][current]
                .get("affinities", [])
            )

            if "crafting" in affinities:
                return True

        crafting_towns = [
            town
            for town, info in self.data["towns"].items()
            if "crafting" in info.get(
                "affinities",
                []
            )
        ]

        if not crafting_towns:
            return False

        best_town = None
        best_path = None

        boots = self.state.has_tool("boots")

        for town in crafting_towns:

            path = self.pathfinder.shortest_path(
                current,
                town,
                boots=boots,
                allow_fast=False
            )

            if path is None:
                continue

            if (
                best_path is None
                or path["time"] < best_path["time"]
            ):
                best_town = town
                best_path = path

        if best_town is None:
            return False

        return self.resource_planner.move_using_path(
            best_path,
            self.actions
        )

    # --------------------------------------------------------
    # TOOLS
    # --------------------------------------------------------

    def plan_tools(self):
        """
        Level 3 tool order.

        Pickaxe is normally acquired first because it
        reduces the cost of every later gathering action.

        Boots then reduce future travel.
        """

        if not self.state.has_tool(
            "pickaxe"
        ):
            if self.tools.craft_tool(
                "pickaxe"
            ):
                pass

        if not self.state.has_tool(
            "boots"
        ):
            if self.tools.craft_tool(
                "boots"
            ):
                pass

    # --------------------------------------------------------
    # PREPARE FOR AN UPGRADE
    # --------------------------------------------------------

    def prepare_upgrade(
    self,
    town,
    upgrade
):
        """
        Gather and craft everything required for an upgrade.

        Resource nodes and towns are different location types.
        Therefore we always move to a crafting town before
        crafting components.
        """

        if upgrade not in UPGRADES:
            return False

        info = UPGRADES[upgrade]

        required_components = Counter(
            info["components"]
        )

        missing_components = Counter()

        for component, amount in required_components.items():

            current = self.state.inventory[component]

            if current < amount:
                missing_components[component] = (
                    amount - current
                )

        # --------------------------------------------------------
        # Nothing needs to be crafted.
        # --------------------------------------------------------

        if not missing_components:
            return True

        # --------------------------------------------------------
        # Determine raw resources required.
        # --------------------------------------------------------

        raw_requirements = (
            DependencyPlanner()
            .raw_requirements(
                missing_components
            )
        )

        # --------------------------------------------------------
        # Gather raw resources.
        #
        # This may move us to resource nodes such as N19,
        # N21, etc.
        # --------------------------------------------------------

        if not self.obtain_resources(
            raw_requirements
        ):
            return False

        # --------------------------------------------------------
        # Return to a crafting town.
        #
        # IMPORTANT:
        # self.state.location may currently be a node.
        # --------------------------------------------------------

        if not self.travel_to_crafting_town():
            return False

        # --------------------------------------------------------
        # Craft the required components.
        # --------------------------------------------------------

        if not self.produce_component_tree(
            missing_components
        ):
            return False

        return True

    # --------------------------------------------------------
    # BUILD PRODUCTION
    # --------------------------------------------------------

    def build_production_upgrades(self):
        """
        Build a useful first layer of production upgrades.

        We do not blindly attempt every upgrade because
        every build consumes Enteloot and ticks.
        """

        candidates = (
            self.production_upgrade_priority()
        )

        built = 0

        for _, town, upgrade in candidates:

            if self.state.has_upgrade(
                town,
                upgrade
            ):
                continue

            if not self.prepare_upgrade(
                town,
                upgrade
            ):
                continue

            if self.state.location != town:

                if not self.travel_to(
                    town,
                    prefer_fast=True
                ):
                    continue

            if self.upgrades.build(
                town,
                upgrade
            ):
                built += 1

            # Build a controlled first layer.
            if built >= 6:
                break

        return built

    # --------------------------------------------------------
    # CIVIC CHAIN
    # --------------------------------------------------------

    def build_civic_chain(
        self,
        town
    ):
        """
        Attempt:

            production upgrade(s)
                ↓
            Rec-center
                ↓
            School
                ↓
            Library

        and:

            two production upgrades
                ↓
            Fire-station
                ↓
            Police-station
        """

        # ----------------------------------------------------
        # First production upgrades
        # ----------------------------------------------------

        production = [
            upgrade
            for upgrade in UPGRADES
            if upgrade in (
                UpgradeManager
                .PRODUCTION_UPGRADES
            )
        ]

        built_here = 0

        for upgrade in production:

            if built_here >= 2:
                break

            if self.state.has_upgrade(
                town,
                upgrade
            ):
                built_here += 1
                continue

            # Only choose upgrades whose resource
            # the town actually produces.
            boost = UPGRADES[
                upgrade
            ]["boost"]

            if boost not in (
                self.data["towns"][town]
                ["production"]["resources"]
            ):
                continue

            if not self.prepare_upgrade(
                town,
                upgrade
            ):
                continue

            if self.state.location != town:

                if not self.travel_to(
                    town,
                    prefer_fast=True
                ):
                    return False

            if self.upgrades.build(
                town,
                upgrade
            ):
                built_here += 1

        # ----------------------------------------------------
        # Rec-center
        # ----------------------------------------------------

        civic_chain = [
            "Rec-center",
            "School",
            "Library",
        ]

        for upgrade in civic_chain:

            if self.state.has_upgrade(
                town,
                upgrade
            ):
                continue

            if not self.prepare_upgrade(
                town,
                upgrade
            ):
                continue

            if self.state.location != town:

                if not self.travel_to(
                    town,
                    prefer_fast=True
                ):
                    return False

            if not self.upgrades.build(
                town,
                upgrade
            ):
                return False

        # ----------------------------------------------------
        # Fire station
        # ----------------------------------------------------

        if not self.state.has_upgrade(
            town,
            "Fire-station"
        ):

            if self.prepare_upgrade(
                town,
                "Fire-station"
            ):

                if self.state.location != town:

                    if not self.travel_to(
                        town,
                        prefer_fast=True
                    ):
                        return False

                self.upgrades.build(
                    town,
                    "Fire-station"
                )

        # ----------------------------------------------------
        # Police station
        # ----------------------------------------------------

        if not self.state.has_upgrade(
            town,
            "Police-station"
        ):

            if self.prepare_upgrade(
                town,
                "Police-station"
            ):

                if self.state.location != town:

                    if not self.travel_to(
                        town,
                        prefer_fast=True
                    ):
                        return False

                self.upgrades.build(
                    town,
                    "Police-station"
                )

        return True

    # --------------------------------------------------------
    # KEEP TIME MOVING
    # --------------------------------------------------------

    def consume_remaining_ticks(self):
        """
        Use safe one-tick sell actions to advance time.

        Passive town production occurs according to current
        tick, so this allows the run to reach the final
        tick without invalid actions.

        We only do this while there is no better planned
        infrastructure action.
        """

        # Selling an item we actually have is safer than
        # trying to buy/sell nonexistent inventory.
        while self.state.tick < self.state.total_ticks:

            available = [
                item
                for item, amount
                in self.state.inventory.items()
                if amount > 0
            ]

            if not available:
                break

            item = sorted(
                available
            )[0]

            amount = self.state.inventory[
                item
            ]

            # Sell one at a time so we never overshoot
            # the tick budget.
            self.actions.sell(
                item,
                1
            )

            self.state.inventory[
                item
            ] -= 1

            if self.state.inventory[
                item
            ] <= 0:
                del self.state.inventory[
                    item
                ]

            self.state.tick += 1
            self.state.action_count += 1

    # --------------------------------------------------------
    # MAIN STRATEGY
    # --------------------------------------------------------

    def run(self):

        # ====================================================
        # PHASE 1
        # Acquire ore and basic resources.
        # ====================================================

        ore_node = self.node_manager.best_resource_node(
            "ore",
            self.state.location
        )

        if ore_node is not None:

            path = self.pathfinder.shortest_path(
                self.state.location,
                ore_node,
                boots=False,
                allow_fast=False,
            )

            if path is not None:

                self.resource_planner.move_using_path(
                    path,
                    self.actions
                )

                node_info = (
                    self.data["nodes"][ore_node]
                )

                # Enough ore for the two tools and
                # potentially police infrastructure.
                ore_target = 8

                while (
                    self.state.inventory["ore"]
                    < ore_target
                ):

                    gather_time = int(
                        node_info["gather-time"]
                    )

                    if (
                        self.state.tick
                        + gather_time
                        > self.state.total_ticks
                    ):
                        break

                    self.actions.gather()

                    self.state.tick += gather_time
                    self.state.action_count += 1

                    self.state.add_resource(
                        "ore",
                        node_info["yield"]
                    )

        # ====================================================
        # PHASE 2
        # Get the resources needed for tool crafting.
        # ====================================================

        tool_raw = {
            "rope": 2,
            "planks": 2,
            "wood": 2,
            "sheep": 2,
        }

        # We need iron fittings.
        iron_raw = {
            "ore": 4,
            "wood": 2,
        }

        self.obtain_resources(
            iron_raw
        )

        # Craft iron fittings.
        self.produce_component_tree(
            {
                "iron-fittings": 2
            }
        )

        # Gather raw tool resources.
        self.obtain_resources(
            tool_raw
        )

        # Craft rope/planks.
        self.produce_component_tree(
            {
                "rope": 2,
                "planks": 2
            }
        )

        # ====================================================
        # PHASE 3
        # Craft Pickaxe first.
        # ====================================================

        self.tools.craft_tool(
            "pickaxe"
        )

        # ====================================================
        # PHASE 4
        # Gather another batch of ore using Pickaxe.
        # ====================================================

        if self.state.inventory["ore"] < 8:

            self.obtain_resources(
                {
                    "ore":
                    8
                    - self.state.inventory["ore"]
                }
            )

        # ====================================================
        # PHASE 5
        # Boots.
        # ====================================================

        # Need another 2 iron fittings.
        if (
            self.state.inventory[
                "iron-fittings"
            ] < 2
        ):

            needed = (
                2
                - self.state.inventory[
                    "iron-fittings"
                ]
            )

            raw = {
                "ore": 2 * needed,
                "wood": 1 * needed,
            }

            self.obtain_resources(
                raw
            )

            self.produce_component_tree(
                {
                    "iron-fittings":
                    needed
                }
            )

        # Need rope.
        if self.state.inventory[
            "rope"
        ] < 2:

            needed = (
                2
                - self.state.inventory[
                    "rope"
                ]
            )

            self.obtain_resources(
                {
                    "sheep": 2 * needed
                }
            )

            self.produce_component_tree(
                {
                    "rope": needed
                }
            )

        self.tools.craft_tool(
            "boots"
        )

        # ====================================================
        # PHASE 6
        # Build production upgrades.
        # ====================================================

        self.build_production_upgrades()

        # ====================================================
        # PHASE 7
        # Civic infrastructure.
        # ====================================================

        towns = (
            self.choose_infrastructure_towns()
        )

        # Only attempt a limited number of civic chains
        # because each one requires a large amount of
        # construction material.
        civic_attempts = 0

        for town in towns:

            if civic_attempts >= 3:
                break

            if self.state.tick >= (
                self.state.total_ticks - 1000
            ):
                break

            if self.build_civic_chain(
                town
            ):
                civic_attempts += 1

        # ====================================================
        # PHASE 8
        # Final safe actions.
        # ====================================================

        self.consume_remaining_ticks()

        return self.actions.actions


# ============================================================
# VALIDATION
# ============================================================

class SubmissionValidator:

    def __init__(self, data):

        self.graph = Graph(data)

    def validate_action(
        self,
        action,
        current_location
    ):
        if not isinstance(
            action,
            dict
        ):
            return False, "Action is not a dictionary."

        action_type = action.get(
            "type"
        )

        if action_type == "travel":

            destination = action.get(
                "destination"
            )

            if destination is None:
                return False, (
                    "Travel action has no destination."
                )

            fast = bool(
                action.get(
                    "fast",
                    False
                )
            )

            if not self.graph.has_edge(
                current_location,
                destination,
                fast=fast
            ):
                return False, (
                    f"Invalid travel: "
                    f"{current_location} -> "
                    f"{destination}, "
                    f"fast={fast}"
                )

            return True, None

        if action_type == "gather":

            if current_location not in (
                self.graph.vertices
            ):
                return False, (
                    "Gather from invalid location."
                )

            return True, None

        if action_type in {
            "buy",
            "sell",
            "craft",
            "build",
            "upkeep",
        }:

            # These activities occur at towns.
            # The actual game engine performs the detailed
            # prerequisite validation.
            return True, None

        return False, (
            f"Unknown action type: "
            f"{action_type}"
        )

    def validate(
        self,
        actions,
        starting_town
    ):
        location = starting_town

        errors = []

        for index, action in enumerate(
            actions
        ):

            valid, error = (
                self.validate_action(
                    action,
                    location
                )
            )

            if not valid:

                errors.append(
                    (
                        index,
                        error
                    )
                )

                continue

            if action["type"] == "travel":

                location = action[
                    "destination"
                ]

        return errors


# ============================================================
# OUTPUT
# ============================================================

def create_submission(
    actions,
    filename
):
    """
    Create the exact competition JSON structure.
    """

    output = {
        "actions": actions
    }

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2
        )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    data,
    strategy,
    actions,
    validation_errors
):

    state = strategy.state

    print()
    print("=" * 70)
    print("LEVEL 3 SOLUTION")
    print("=" * 70)

    print(
        f"Starting town: "
        f"{data['run']['starting_town']}"
    )

    print(
        f"Total tick budget: "
        f"{data['run']['total_ticks']}"
    )

    print(
        f"Ticks used by planner: "
        f"{state.tick}"
    )

    print(
        f"Ticks remaining: "
        f"{max(0, state.total_ticks - state.tick)}"
    )

    print(
        f"Actions generated: "
        f"{len(actions)}"
    )

    print(
        f"Final planned Enteloot: "
        f"{state.enteloot}"
    )

    print()

    print("Tools:")

    if state.tools:
        for tool in sorted(
            state.tools
        ):
            print(
                f"  - {tool}"
            )
    else:
        print("  none")

    print()

    print("Upgrades:")

    total_upgrades = 0

    for town in sorted(
        state.upgrades
    ):

        upgrades = sorted(
            state.upgrades[town]
        )

        if upgrades:

            print(
                f"  {town}: "
                f"{', '.join(upgrades)}"
            )

            total_upgrades += len(
                upgrades
            )

    if total_upgrades == 0:
        print("  none")

    print()

    print(
        f"Total planned upgrades: "
        f"{total_upgrades}"
    )

    print()

    if validation_errors:

        print(
            "VALIDATION ERRORS:"
        )

        for index, error in (
            validation_errors[:20]
        ):

            print(
                f"  Action {index}: "
                f"{error}"
            )

        if len(validation_errors) > 20:

            print(
                f"  ... and "
                f"{len(validation_errors) - 20}"
                f" more."
            )

    else:

        print(
            "Action validation: PASS"
        )

    print()

    print(
        "Current location: "
        f"{state.location}"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Input file
    # --------------------------------------------------------

    input_candidates = [
        "level3.json",
        "level_3.json",
        "3.json",
        "3.txt",
        "input.json",
    ]

    input_file = None

    for filename in input_candidates:

        if os.path.exists(filename):

            input_file = filename
            break

    if input_file is None:

        raise FileNotFoundError(
            "Could not find the Level 3 input file.\n"
            "Expected one of:\n"
            + "\n".join(
                f"  - {name}"
                for name in input_candidates
            )
        )

    print(
        f"Loading Level 3 input: "
        f"{input_file}"
    )

    data = load_input(
        input_file
    )

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    required_top_level = {
        "run",
        "towns",
        "nodes",
        "routes",
    }

    missing = (
        required_top_level
        - set(data.keys())
    )

    if missing:

        raise ValueError(
            "Level JSON is missing fields: "
            + ", ".join(
                sorted(missing)
            )
        )

    print(
        f"Loaded "
        f"{len(data['towns'])} towns, "
        f"{len(data['nodes'])} nodes, "
        f"{len(data['routes'])} routes."
    )

    # --------------------------------------------------------
    # Strategy
    # --------------------------------------------------------

    print()
    print(
        "Generating Level 3 strategy..."
    )

    strategy = Level3Strategy(
        data
    )

    actions = strategy.run()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validator = SubmissionValidator(
        data
    )

    errors = validator.validate(
        actions,
        data["run"]["starting_town"]
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output_file = (
        "level3_submission.txt"
    )

    create_submission(
        actions,
        output_file
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_summary(
        data,
        strategy,
        actions,
        errors
    )

    print()
    print(
        "Submission file:"
    )
    print(
        os.path.abspath(
            output_file
        )
    )


if __name__ == "__main__":
    main()