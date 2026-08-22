import json
import math
import heapq
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ============================================================
# GLOBAL RULE DATA FROM THE SPECIFICATION
# ============================================================

RESOURCE_SELL = {
    "wheat": 2,
    "wood": 3,
    "stone": 3,
    "clay": 4,
    "fish": 4,
    "sheep": 5,
    "ore": 6,
}

RESOURCE_BUY = {
    "wheat": 4,
    "wood": 5,
    "stone": 5,
    "clay": 6,
    "fish": 6,
    "sheep": 8,
    # Ore cannot be bought.
}

PRODUCTION_UPGRADES = {
    "Farmhouse": "sheep",
    "Pier": "fish",
    "Fertilised-fields": "wheat",
    "Quarry": "stone",
    "Woodlands": "wood",
    "Pottery-house": "clay",
}

RECIPES = {
    "bread": {
        "inputs": {"wheat": 3},
        "time": 2,
    },
    "fish-n-chips": {
        "inputs": {"fish": 2, "wheat": 1},
        "time": 2,
    },
    "stew": {
        "inputs": {"sheep": 1, "fish": 1, "wheat": 1},
        "time": 2,
    },
    "wooden-crafts": {
        "inputs": {"wood": 4},
        "time": 2,
    },
    "furniture": {
        "inputs": {"wood": 3, "sheep": 1},
        "time": 2,
    },
    "stone-works": {
        "inputs": {"stone": 5},
        "time": 2,
    },
    "roof-tiles": {
        "inputs": {"clay": 3, "stone": 2},
        "time": 2,
    },
    "wool-garments": {
        "inputs": {"sheep": 3},
        "time": 2,
    },
    "pottery": {
        "inputs": {"clay": 4, "wood": 1},
        "time": 2,
    },
}

COMPONENTS = {
    "planks": {"inputs": {"wood": 2}, "time": 2},
    "thatch": {"inputs": {"wheat": 2}, "time": 2},
    "stone-blocks": {"inputs": {"stone": 3}, "time": 2},
    "mortar": {"inputs": {"clay": 1, "stone": 1}, "time": 2},
    "bricks": {"inputs": {"clay": 2, "mortar": 1}, "time": 2},
    "rope": {"inputs": {"sheep": 2}, "time": 2},
    "fencing": {"inputs": {"wood": 2, "rope": 1}, "time": 2},
    "kiln-glass": {"inputs": {"clay": 2, "wood": 2}, "time": 2},
    "nets": {"inputs": {"rope": 1, "fencing": 1}, "time": 2},
    "iron-fittings": {"inputs": {"ore": 2, "wood": 1}, "time": 2},
}

TOOLS = {
    "boots": {
        "inputs": {"iron-fittings": 2, "rope": 2},
        "effect": "travel",
    },
    "pickaxe": {
        "inputs": {"iron-fittings": 2, "planks": 2},
        "effect": "gather",
    },
}

UPGRADES = {
    "Farmhouse": {
        "boost": "sheep",
        "components": {"planks": 3, "thatch": 2},
        "enteloot": 500,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Pier": {
        "boost": "fish",
        "components": {"planks": 4, "nets": 2},
        "enteloot": 600,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Fertilised-fields": {
        "boost": "wheat",
        "components": {"fencing": 2, "thatch": 2},
        "enteloot": 500,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Quarry": {
        "boost": "stone",
        "components": {"stone-blocks": 3, "planks": 2},
        "enteloot": 600,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Woodlands": {
        "boost": "wood",
        "components": {"fencing": 2, "rope": 2},
        "enteloot": 500,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Pottery-house": {
        "boost": "clay",
        "components": {"bricks": 4, "planks": 2},
        "enteloot": 700,
        "time": 3,
        "prerequisite": None,
        "score": 1000,
    },
    "Rec-center": {
        "boost": "enteloot_amount_20",
        "components": {"planks": 4, "bricks": 3, "rope": 1},
        "enteloot": 1200,
        "time": 4,
        "prerequisite": "production",
        "score": 3000,
    },
    "Fire-station": {
        "boost": "boost_duration_50",
        "components": {"bricks": 5, "stone-blocks": 3, "rope": 2},
        "enteloot": 1800,
        "time": 4,
        "prerequisite": "production2",
        "score": 4000,
    },
    "School": {
        "boost": "enteloot_amount_50",
        "components": {"bricks": 6, "planks": 3, "kiln-glass": 2},
        "enteloot": 2000,
        "time": 5,
        "prerequisite": "Rec-center",
        "score": 5000,
    },
    "Police-station": {
        "boost": "enteloot_rate_minus_2",
        "components": {"bricks": 6, "stone-blocks": 4, "iron-fittings": 2},
        "enteloot": 2200,
        "time": 5,
        "prerequisite": "Fire-station",
        "score": 5000,
    },
    "Library": {
        "boost": "enteloot_amount_50",
        "components": {"bricks": 5, "planks": 5, "kiln-glass": 2},
        "enteloot": 2500,
        "time": 5,
        "prerequisite": "School",
        "score": 6000,
    },
}


# ============================================================
# HELPERS
# ============================================================

def normalise_name(value: str) -> str:
    return str(value).strip().lower().replace("_", "-")


def load_input(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def raw_requirements(requirements: Dict[str, int]) -> Counter:
    """
    Fully expand construction components to raw resources.
    """
    result = Counter()

    def expand(item: str, quantity: int) -> None:
        if quantity <= 0:
            return

        if item not in COMPONENTS:
            result[item] += quantity
            return

        for ingredient, amount in COMPONENTS[item]["inputs"].items():
            expand(ingredient, amount * quantity)

    for item, quantity in requirements.items():
        expand(item, int(quantity))

    return result


def raw_requirements_for_components(components: Dict[str, int]) -> Counter:
    return raw_requirements(components)


def production_resource_for_upgrade(upgrade: str) -> Optional[str]:
    return PRODUCTION_UPGRADES.get(upgrade)


# ============================================================
# ACTION OUTPUT
# ============================================================

class ActionBuilder:
    def __init__(self):
        self.actions: List[dict] = []

    def travel(self, destination: str, fast: bool = False) -> None:
        action = {
            "type": "travel",
            "destination": destination,
        }
        if fast:
            action["fast"] = True
        self.actions.append(action)

    def gather(self) -> None:
        self.actions.append({"type": "gather"})

    def buy(self, item: str, quantity: int) -> None:
        if quantity > 0:
            self.actions.append({
                "type": "buy",
                "item": item,
                "quantity": int(quantity),
            })

    def sell(self, item: str, quantity: int) -> None:
        if quantity > 0:
            self.actions.append({
                "type": "sell",
                "item": item,
                "quantity": int(quantity),
            })

    def craft(self, item: str, quantity: int) -> None:
        if quantity > 0:
            self.actions.append({
                "type": "craft",
                "item": item,
                "quantity": int(quantity),
            })

    def build(self, upgrade: str) -> None:
        self.actions.append({
            "type": "build",
            "upgrade": upgrade,
        })

    def upkeep(self) -> None:
        self.actions.append({"type": "upkeep"})


# ============================================================
# GRAPH
# ============================================================

class Graph:
    def __init__(self, data: dict):
        self.adjacency = defaultdict(list)
        self.standard_edges = {}
        self.fast_edges = {}
        self.vertices = set()

        for route in data["routes"]:
            a, b = route["between"]
            weight = int(route["weight"])
            toll = int(route.get("toll", 0))
            fast = toll > 0

            e1 = {
                "destination": b,
                "weight": weight,
                "toll": toll,
                "fast": fast,
            }
            e2 = {
                "destination": a,
                "weight": weight,
                "toll": toll,
                "fast": fast,
            }

            self.vertices.update((a, b))

            table = self.fast_edges if fast else self.standard_edges
            table[(a, b)] = e1
            table[(b, a)] = e2

            self.adjacency[a].append(e1)
            self.adjacency[b].append(e2)

    def get_edge(self, source, destination, fast=False):
        table = self.fast_edges if fast else self.standard_edges
        return table.get((source, destination))

    def has_edge(self, source, destination, fast=False):
        return self.get_edge(source, destination, fast) is not None


# ============================================================
# PATH FINDING
# ============================================================

class PathFinder:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.cache = {}

    @staticmethod
    def edge_time(edge, boots=False):
        if boots:
            return max(1, int(edge["weight"]) - 1)
        return int(edge["weight"])

    def shortest_path(
        self,
        start: str,
        end: str,
        boots: bool = False,
        allow_fast: bool = False,
        enteloot: Optional[int] = None,
    ) -> Optional[dict]:

        if start == end:
            return {
                "time": 0,
                "toll": 0,
                "path": [start],
                "fast_flags": [],
            }

        # We deliberately do not cache enteloot-dependent paths
        # aggressively; this avoids stale affordability assumptions.
        key = (
            start,
            end,
            bool(boots),
            bool(allow_fast),
            None if enteloot is None else int(enteloot),
        )

        if key in self.cache:
            return self.cache[key]

        # Dijkstra objective:
        # primarily time, then toll.
        pq = [(0, 0, start)]
        dist = {start: (0, 0)}
        previous = {}

        while pq:
            time_so_far, toll_so_far, node = heapq.heappop(pq)

            if dist.get(node) != (time_so_far, toll_so_far):
                continue

            if node == end:
                break

            for edge in self.graph.adjacency.get(node, []):
                is_fast = edge["fast"]

                if is_fast and not allow_fast:
                    continue

                toll = int(edge["toll"]) if is_fast else 0

                if enteloot is not None:
                    if toll_so_far + toll > int(enteloot):
                        continue

                edge_time = self.edge_time(edge, boots)
                new_time = time_so_far + edge_time
                new_toll = toll_so_far + toll

                dest = edge["destination"]
                candidate = (new_time, new_toll)

                if dest not in dist or candidate < dist[dest]:
                    dist[dest] = candidate
                    previous[dest] = (node, is_fast)
                    heapq.heappush(
                        pq,
                        (new_time, new_toll, dest),
                    )

        if end not in dist:
            return None

        path = []
        fast_flags = []
        cur = end

        while cur != start:
            path.append(cur)
            prev, was_fast = previous[cur]
            fast_flags.append(was_fast)
            cur = prev

        path.append(start)
        path.reverse()
        fast_flags.reverse()

        result = {
            "time": dist[end][0],
            "toll": dist[end][1],
            "path": path,
            "fast_flags": fast_flags,
        }

        self.cache[key] = result
        return result


# ============================================================
# ECONOMIC STATE
# ============================================================

class PlannerState:
    """
    Planner-side representation of the competition state.

    Important:
    passive town production and Enteloot are credited whenever
    the global clock advances.
    """

    def __init__(self, data: dict):
        run = data["run"]

        self.total_ticks = int(run["total_ticks"])
        self.tick = 0
        self.enteloot = int(run["starting_enteloot"])
        self.location = run["starting_town"]

        self.inventory = Counter()
        self.upgrades = defaultdict(set)
        self.tools = set()
        self.action_count = 0

        # Number of passive production cycles already credited.
        self.resource_cycles = defaultdict(int)
        self.enteloot_cycles = defaultdict(int)

    def has_upgrade(self, town, upgrade):
        return upgrade in self.upgrades[town]

    def add_upgrade(self, town, upgrade):
        self.upgrades[town].add(upgrade)

    def has_tool(self, tool):
        return normalise_name(tool) in self.tools

    def add_resource(self, resource, amount):
        if amount > 0:
            self.inventory[resource] += int(amount)

    def consume(self, item, amount) -> bool:
        amount = int(amount)
        if amount <= 0:
            return True

        if self.inventory[item] < amount:
            return False

        self.inventory[item] -= amount

        if self.inventory[item] <= 0:
            del self.inventory[item]

        return True

    def can_afford(self, items: Dict[str, int]) -> bool:
        return all(
            self.inventory[item] >= int(amount)
            for item, amount in items.items()
        )

    def snapshot(self):
        return (
            self.tick,
            self.enteloot,
            Counter(self.inventory),
            defaultdict(set, {
                town: set(upgrades)
                for town, upgrades in self.upgrades.items()
            }),
            set(self.tools),
            self.location,
            dict(self.resource_cycles),
            dict(self.enteloot_cycles),
        )

    def restore(self, snapshot):
        (
            self.tick,
            self.enteloot,
            inventory,
            upgrades,
            tools,
            location,
            resource_cycles,
            enteloot_cycles,
        ) = snapshot

        self.inventory = Counter(inventory)
        self.upgrades = defaultdict(
            set,
            {
                town: set(items)
                for town, items in upgrades.items()
            },
        )
        self.tools = set(tools)
        self.location = location
        self.resource_cycles = defaultdict(
            int,
            resource_cycles,
        )
        self.enteloot_cycles = defaultdict(
            int,
            enteloot_cycles,
        )


# ============================================================
# PASSIVE ECONOMY
# ============================================================

class Economy:
    def __init__(self, data):
        self.data = data

    def production_amount(self, town, resource, state) -> int:
        info = self.data["towns"][town]
        amount = int(
            info.get("production", {})
            .get("resources", {})
            .get(resource, 0)
        )

        for upgrade, boosted_resource in PRODUCTION_UPGRADES.items():
            if boosted_resource == resource and state.has_upgrade(
                town, upgrade
            ):
                amount *= 2

        return int(amount)

    def enteloot_amount(self, town, state) -> int:
        info = self.data["towns"][town]
        amount = int(info["enteloot"]["amount"])

        bonus = 0

        if state.has_upgrade(town, "Rec-center"):
            bonus += 20

        if state.has_upgrade(town, "School"):
            bonus += 50

        if state.has_upgrade(town, "Library"):
            bonus += 50

        amount = math.floor(amount * (100 + bonus) / 100)
        return int(amount)

    def enteloot_rate(self, town, state) -> int:
        info = self.data["towns"][town]
        rate = int(info["enteloot"]["rate"])

        if state.has_upgrade(town, "Police-station"):
            rate = max(1, rate - 2)

        return rate

    def advance_to(self, state: PlannerState, new_tick: int):
        """
        Apply passive systems for all cycles crossed by the clock.

        The specification uses:
            floor(current_tick / rate) * amount
        """
        if new_tick <= state.tick:
            return

        new_tick = min(int(new_tick), state.total_ticks)

        for town in sorted(self.data["towns"]):
            info = self.data["towns"][town]

            # Resource production.
            production_rate = int(
                info.get("production", {}).get("rate", 0)
            )

            if production_rate > 0:
                cycles = new_tick // production_rate
                old_cycles = state.resource_cycles[town]

                if cycles > old_cycles:
                    completed = cycles - old_cycles

                    for resource in sorted(
                        info.get("production", {})
                        .get("resources", {})
                    ):
                        amount = self.production_amount(
                            town,
                            resource,
                            state,
                        )
                        state.inventory[resource] += (
                            completed * amount
                        )

                    state.resource_cycles[town] = cycles

            # Enteloot generation.
            enteloot_rate = self.enteloot_rate(town, state)

            if enteloot_rate > 0:
                cycles = new_tick // enteloot_rate
                old_cycles = state.enteloot_cycles[town]

                if cycles > old_cycles:
                    completed = cycles - old_cycles
                    amount = self.enteloot_amount(town, state)
                    state.enteloot += completed * amount
                    state.enteloot_cycles[town] = cycles

        state.tick = new_tick


# ============================================================
# RESOURCE NODE PLANNER
# ============================================================

class ResourcePlanner:
    def __init__(self, data, graph, pathfinder, state, economy):
        self.data = data
        self.graph = graph
        self.pathfinder = pathfinder
        self.state = state
        self.economy = economy

        self.nodes_by_resource = defaultdict(list)
        for node, info in data["nodes"].items():
            resource = info.get("resource")
            if resource:
                self.nodes_by_resource[resource].append(node)

    def best_node(
        self,
        resource: str,
        quantity: int = 1,
    ) -> Optional[Tuple[str, dict, int]]:

        boots = self.state.has_tool("boots")
        candidates = []

        for node in sorted(self.nodes_by_resource.get(resource, [])):
            path = self.pathfinder.shortest_path(
                self.state.location,
                node,
                boots=boots,
                allow_fast=False,
            )

            if path is None:
                continue

            info = self.data["nodes"][node]
            yield_amount = int(info["yield"])
            gather_time = int(info["gather-time"])

            gathers = max(
                1,
                math.ceil(quantity / max(1, yield_amount)),
            )

            # Round trip estimate is more useful than one-way
            # efficiency when collecting construction resources.
            back = self.pathfinder.shortest_path(
                node,
                self.state.location,
                boots=boots,
                allow_fast=False,
            )

            back_time = back["time"] if back else path["time"]

            total_time = (
                path["time"]
                + gathers * max(
                    1,
                    gather_time
                    - (1 if self.state.has_tool("pickaxe") else 0),
                )
                + back_time
            )

            # Higher yield per tick is better.
            efficiency = (
                gathers * yield_amount
            ) / max(1, total_time)

            candidates.append(
                (
                    -efficiency,
                    total_time,
                    node,
                    path,
                )
            )

        if not candidates:
            return None

        candidates.sort()
        _, _, node, path = candidates[0]
        return node, path, int(self.data["nodes"][node]["yield"])

    def gather(self, resource: str, quantity: int, actions) -> bool:
        quantity = int(quantity)

        if quantity <= 0:
            return True

        while self.state.inventory[resource] < quantity:
            remaining = (
                quantity
                - self.state.inventory[resource]
            )

            choice = self.best_node(
                resource,
                remaining,
            )

            if choice is None:
                return False

            node, path, yield_amount = choice

            if not self.move_path(path, actions):
                return False

            info = self.data["nodes"][node]

            gather_time = int(info["gather-time"])

            if self.state.has_tool("pickaxe"):
                gather_time = max(1, gather_time - 1)

            if (
                self.state.tick + gather_time
                > self.state.total_ticks
            ):
                return False

            actions.gather()
            self.economy.advance_to(
                self.state,
                self.state.tick + gather_time,
            )
            self.state.add_resource(
                resource,
                int(info["yield"]),
            )
            self.state.action_count += 1

        return True

    def move_path(self, path: dict, actions) -> bool:
        vertices = path["path"]
        flags = path["fast_flags"]

        for i in range(len(vertices) - 1):
            source = vertices[i]
            destination = vertices[i + 1]
            fast = bool(flags[i])

            edge = self.graph.get_edge(
                source,
                destination,
                fast=fast,
            )

            if edge is None:
                return False

            travel_time = self.pathfinder.edge_time(
                edge,
                boots=self.state.has_tool("boots"),
            )

            if (
                self.state.tick + travel_time
                > self.state.total_ticks
            ):
                return False

            toll = int(edge["toll"]) if fast else 0

            if self.state.enteloot < toll:
                return False

            self.state.enteloot -= toll

            actions.travel(
                destination,
                fast=fast,
            )

            self.economy.advance_to(
                self.state,
                self.state.tick + travel_time,
            )

            self.state.location = destination
            self.state.action_count += 1

        return True


# ============================================================
# CRAFTING
# ============================================================

class CraftingPlanner:
    def __init__(self, data, state, actions, economy):
        self.data = data
        self.state = state
        self.actions = actions
        self.economy = economy

    def craft_time(self) -> int:
        town = self.state.location

        if town in self.data["towns"]:
            affinities = self.data["towns"][town].get(
                "affinities",
                [],
            )
            if "crafting" in affinities:
                return 1

        return 2

    def craft_component(self, component: str, quantity: int) -> bool:
        quantity = int(quantity)

        if quantity <= 0:
            return True

        if component not in COMPONENTS:
            return False

        # Ensure component dependencies first.
        recipe = COMPONENTS[component]

        for ingredient, amount in recipe["inputs"].items():
            if ingredient in COMPONENTS:
                required = amount * quantity
                missing = required - self.state.inventory[ingredient]

                if missing > 0:
                    if not self.craft_component(
                        ingredient,
                        missing,
                    ):
                        return False

        # All raw inputs must exist.
        for ingredient, amount in recipe["inputs"].items():
            required = amount * quantity
            if self.state.inventory[ingredient] < required:
                return False

        ticks = quantity * self.craft_time()

        if self.state.tick + ticks > self.state.total_ticks:
            return False

        # Consume only after every validation succeeds.
        for ingredient, amount in recipe["inputs"].items():
            if not self.state.consume(
                ingredient,
                amount * quantity,
            ):
                return False

        self.actions.craft(component, quantity)

        self.economy.advance_to(
            self.state,
            self.state.tick + ticks,
        )

        self.state.inventory[component] += quantity
        self.state.action_count += 1

        return True


# ============================================================
# UPGRADE MANAGER
# ============================================================

class UpgradeManager:
    def __init__(
        self,
        data,
        state,
        actions,
        economy,
        crafting,
        resource_planner,
        pathfinder,
    ):
        self.data = data
        self.state = state
        self.actions = actions
        self.economy = economy
        self.crafting = crafting
        self.resources = resource_planner
        self.pathfinder = pathfinder

    @staticmethod
    def prerequisite_satisfied(
        prerequisite,
        town_upgrades,
    ) -> bool:

        if prerequisite is None:
            return True

        if isinstance(prerequisite, str):
            if prerequisite == "production":
                return len(
                    town_upgrades
                    & set(PRODUCTION_UPGRADES)
                ) >= 1

            if prerequisite == "production2":
                return len(
                    town_upgrades
                    & set(PRODUCTION_UPGRADES)
                ) >= 2

            return prerequisite in town_upgrades

        if isinstance(prerequisite, (list, tuple, set)):
            return all(
                item in town_upgrades
                for item in prerequisite
            )

        if isinstance(prerequisite, dict):
            for key, value in prerequisite.items():
                if key == "any":
                    if not any(
                        item in town_upgrades
                        for item in value
                    ):
                        return False
                elif key == "all":
                    if not all(
                        item in town_upgrades
                        for item in value
                    ):
                        return False
                elif key == "production":
                    count = len(
                        town_upgrades
                        & set(PRODUCTION_UPGRADES)
                    )
                    if count < int(value):
                        return False
                elif value and key not in town_upgrades:
                    return False

            return True

        return False

    def can_build(self, town, upgrade) -> bool:
        if town not in self.data["towns"]:
            return False

        if upgrade not in UPGRADES:
            return False

        if self.state.has_upgrade(town, upgrade):
            return False

        info = UPGRADES[upgrade]

        if not self.prerequisite_satisfied(
            info["prerequisite"],
            self.state.upgrades[town],
        ):
            return False

        if self.state.enteloot < info["enteloot"]:
            return False

        if not self.state.can_afford(info["components"]):
            return False

        if self.state.tick + int(info["time"]) > self.state.total_ticks:
            return False

        return True

    def ensure_crafting_town(self) -> bool:
        if self.state.location in self.data["towns"]:
            if "crafting" in self.data["towns"][
                self.state.location
            ].get("affinities", []):
                return True

        candidates = []

        for town in sorted(self.data["towns"]):
            if "crafting" not in self.data["towns"][town].get(
                "affinities",
                [],
            ):
                continue

            path = self.pathfinder.shortest_path(
                self.state.location,
                town,
                boots=self.state.has_tool("boots"),
                allow_fast=False,
            )

            if path is not None:
                candidates.append(
                    (path["time"], town, path)
                )

        if not candidates:
            return False

        candidates.sort(key=lambda x: (x[0], x[1]))
        _, _, path = candidates[0]

        return self.resources.move_path(
            path,
            self.actions,
        )

    def prepare_components(self, components: Dict[str, int]) -> bool:
        missing = Counter()

        for component, amount in components.items():
            deficit = int(amount) - self.state.inventory[component]
            if deficit > 0:
                missing[component] = deficit

        if not missing:
            return True

        # Work out all raw resources required.
        raw = raw_requirements_for_components(missing)

        # Prefer passive inventory first. Only gather actual deficits.
        raw_missing = Counter()

        for resource, amount in raw.items():
            deficit = int(amount) - self.state.inventory[resource]
            if deficit > 0:
                raw_missing[resource] = deficit

        # Ore cannot be bought and must be gathered.
        # For all other resources, gathering is still usually
        # preferable to buying when large construction quantities
        # are involved.
        for resource in sorted(raw_missing):
            amount = raw_missing[resource]

            if resource == "ore":
                if not self.resources.gather(
                    resource,
                    amount,
                    self.actions,
                ):
                    return False
            else:
                # Use nodes for large requirements.
                # For tiny requirements, buy at a producing town
                # if doing so avoids a long detour.
                if not self.acquire_resource_efficiently(
                    resource,
                    amount,
                ):
                    return False

        if not self.ensure_crafting_town():
            return False

        # Craft in dependency-safe order.
        pending = Counter(missing)

        # Repeatedly craft any component whose inputs are now ready.
        made_progress = True

        while pending and made_progress:
            made_progress = False

            for component in sorted(list(pending)):
                amount = pending[component]

                if amount <= 0:
                    del pending[component]
                    continue

                if self.state.inventory[component] >= amount:
                    del pending[component]
                    made_progress = True
                    continue

                before = self.state.inventory[component]

                if self.crafting.craft_component(
                    component,
                    amount,
                ):
                    if self.state.inventory[component] > before:
                        del pending[component]
                        made_progress = True

        return not pending

    def acquire_resource_efficiently(self, resource, amount) -> bool:
        """
        Decide between:
            passive inventory,
            gathering,
            buying.

        Passive inventory has already been removed from 'amount'.

        Buying is only used when the nearest producing town is
        materially cheaper in ticks than a node detour.
        """
        if amount <= 0:
            return True

        # Ore cannot be bought.
        if resource == "ore":
            return self.resources.gather(
                resource,
                amount,
                self.actions,
            )

        # Best resource node.
        node_choice = self.resources.best_node(
            resource,
            amount,
        )

        node_time = None
        if node_choice is not None:
            _, path, yield_amount = node_choice
            node_info = self.data["nodes"][
                node_choice[0]
            ]

            gather_time = int(node_info["gather-time"])
            if self.state.has_tool("pickaxe"):
                gather_time = max(1, gather_time - 1)

            gathers = max(
                1,
                math.ceil(amount / max(1, yield_amount)),
            )

            back = self.pathfinder.shortest_path(
                node_choice[0],
                self.state.location,
                boots=self.state.has_tool("boots"),
                allow_fast=False,
            )

            node_time = (
                path["time"]
                + gathers * gather_time
                + (back["time"] if back else path["time"])
            )

        # Find nearest producing town.
        producing = []

        for town in sorted(self.data["towns"]):
            resources = self.data["towns"][town].get(
                "production",
                {},
            ).get("resources", {})

            if resource not in resources:
                continue

            path = self.pathfinder.shortest_path(
                self.state.location,
                town,
                boots=self.state.has_tool("boots"),
                allow_fast=False,
            )

            if path is not None:
                producing.append((path["time"], town, path))

        buy_time = None
        buy_town = None
        buy_path = None

        if producing:
            producing.sort(key=lambda x: (x[0], x[1]))
            buy_time, buy_town, buy_path = producing[0]

            # One buy action is 1 tick regardless of quantity.
            buy_time += 1

        # Gathering usually saves Enteloot. Buying is attractive
        # only when it saves a substantial amount of travel/gather time.
        use_buy = (
            buy_time is not None
            and (
                node_time is None
                or buy_time + 3 < node_time
            )
            and self.state.enteloot
            >= RESOURCE_BUY[resource] * amount
        )

        if use_buy:
            if not self.resources.move_path(
                buy_path,
                self.actions,
            ):
                return False

            cost = RESOURCE_BUY[resource] * amount

            if self.state.enteloot < cost:
                return False

            self.state.enteloot -= cost
            self.actions.buy(resource, amount)

            self.economy.advance_to(
                self.state,
                self.state.tick + 1,
            )
            self.state.inventory[resource] += amount
            self.state.action_count += 1
            return True

        return self.resources.gather(
            resource,
            amount,
            self.actions,
        )

    def build(self, town, upgrade) -> bool:
        """
        Transaction-safe build.

        Crucially, time is checked BEFORE consuming components
        or Enteloot.
        """
        if not self.can_build(town, upgrade):
            return False

        if self.state.location != town:
            path = self.pathfinder.shortest_path(
                self.state.location,
                town,
                boots=self.state.has_tool("boots"),
                allow_fast=True,
                enteloot=self.state.enteloot,
            )

            if path is None:
                return False

            if not self.resources.move_path(
                path,
                self.actions,
            ):
                return False

        # Location may have changed, so validate again.
        if not self.can_build(town, upgrade):
            return False

        info = UPGRADES[upgrade]
        build_time = int(info["time"])

        if self.state.tick + build_time > self.state.total_ticks:
            return False

        if not self.state.can_afford(info["components"]):
            return False

        if self.state.enteloot < int(info["enteloot"]):
            return False

        # Commit only now.
        for component, amount in info["components"].items():
            if not self.state.consume(component, amount):
                return False

        self.state.enteloot -= int(info["enteloot"])
        self.actions.build(upgrade)

        self.economy.advance_to(
            self.state,
            self.state.tick + build_time,
        )

        self.state.add_upgrade(town, upgrade)
        self.state.action_count += 1
        return True


# ============================================================
# STRATEGY
# ============================================================

class Level3Strategy:
    """
    Dynamic Level 3 strategy.

    The planner does not hard-code "six production upgrades"
    or "three civic towns".

    It repeatedly asks:
        Which feasible infrastructure investment gives the
        strongest combination of immediate score, future
        Enteloot, civic-chain unlocks and tick efficiency?
    """

    def __init__(self, data):
        self.data = data
        self.graph = Graph(data)
        self.pathfinder = PathFinder(self.graph)

        self.state = PlannerState(data)
        self.actions = ActionBuilder()
        self.economy = Economy(data)

        self.resources = ResourcePlanner(
            data,
            self.graph,
            self.pathfinder,
            self.state,
            self.economy,
        )

        self.crafting = CraftingPlanner(
            data,
            self.state,
            self.actions,
            self.economy,
        )

        self.upgrades = UpgradeManager(
            data,
            self.state,
            self.actions,
            self.economy,
            self.crafting,
            self.resources,
            self.pathfinder,
        )

    # --------------------------------------------------------
    # Town ranking
    # --------------------------------------------------------

    def town_value(self, town) -> float:
        info = self.data["towns"][town]

        enteloot_rate = int(info["enteloot"]["rate"])
        enteloot_amount = int(info["enteloot"]["amount"])

        if enteloot_rate <= 0:
            passive = 0
        else:
            passive = enteloot_amount / enteloot_rate

        production_count = len(
            info.get("production", {}).get("resources", {})
        )

        crafting_bonus = (
            800
            if "crafting" in info.get("affinities", [])
            else 0
        )

        return (
            passive * 100
            + production_count * 250
            + crafting_bonus
        )

    def infrastructure_towns(self) -> List[str]:
        return sorted(
            self.data["towns"],
            key=lambda town: (
                -self.town_value(town),
                town,
            ),
        )

    # --------------------------------------------------------
    # Tool planning
    # --------------------------------------------------------

    def estimate_future_gathers(self) -> int:
        """
        Estimate the number of future gather actions implied
        by construction requirements for the high-value civic
        chains.
        """
        # Conservative estimate. It intentionally favours
        # tools when the map has many nodes and construction
        # requirements are large.
        return max(
            20,
            len(self.data["nodes"]) // 2,
        )

    def estimate_future_travel_edges(self) -> int:
        return max(
            30,
            len(self.data["towns"]),
        )

    def tool_priority(self) -> List[str]:
        pickaxe_value = self.estimate_future_gathers()
        boots_value = self.estimate_future_travel_edges()

        if pickaxe_value > boots_value:
            return ["pickaxe", "boots"]

        if boots_value > pickaxe_value:
            return ["boots", "pickaxe"]

        return ["boots", "pickaxe"]

    def required_tool_resources(self, tool_order) -> Counter:
        required = Counter()

        # Each tool requires 2 iron-fittings.
        # Each iron-fitting requires 2 ore + 1 wood.
        for tool in tool_order:
            required["iron-fittings"] += 2
            required["rope" if tool == "boots" else "planks"] += 2

        # Expand fittings to raw.
        expanded = raw_requirements(required)
        return expanded

    def prepare_tools(self):
        """
        Acquire enough raw materials for both tools and craft
        the more useful one first.

        We only do this if the map/run has enough budget.
        """
        order = self.tool_priority()

        missing_tools = [
            tool for tool in order
            if not self.state.has_tool(tool)
        ]

        if not missing_tools:
            return

        raw_needed = self.required_tool_resources(
            missing_tools
        )

        # Use passive inventory first.
        deficits = Counter()

        for resource, amount in raw_needed.items():
            deficit = amount - self.state.inventory[resource]
            if deficit > 0:
                deficits[resource] = deficit

        for resource in sorted(deficits):
            self.upgrades.acquire_resource_efficiently(
                resource,
                deficits[resource],
            )

        # Craft at the best available crafting town.
        self.upgrades.ensure_crafting_town()

        # Build fittings first.
        fittings_needed = 2 * len(missing_tools)

        if self.state.inventory["iron-fittings"] < fittings_needed:
            missing = (
                fittings_needed
                - self.state.inventory["iron-fittings"]
            )

            self.crafting.craft_component(
                "iron-fittings",
                missing,
            )

        for tool in order:
            if self.state.has_tool(tool):
                continue

            info = TOOLS[tool]

            if not self.state.can_afford(info["inputs"]):
                continue

            craft_time = self.crafting.craft_time()

            if self.state.tick + craft_time > self.state.total_ticks:
                continue

            for item, amount in info["inputs"].items():
                self.state.consume(item, amount)

            self.actions.craft(tool, 1)

            self.economy.advance_to(
                self.state,
                self.state.tick + craft_time,
            )

            self.state.tools.add(normalise_name(tool))
            self.state.action_count += 1

    # --------------------------------------------------------
    # Upgrade valuation
    # --------------------------------------------------------

    def future_enteloot_value(
        self,
        town: str,
        upgrade: str,
    ) -> float:

        remaining = max(
            0,
            self.state.total_ticks - self.state.tick,
        )

        info = UPGRADES[upgrade]
        boost = info["boost"]

        current_rate = self.economy.enteloot_rate(
            town,
            self.state,
        )
        current_amount = self.economy.enteloot_amount(
            town,
            self.state,
        )

        if current_rate <= 0:
            return 0

        before_cycles = remaining // current_rate

        before = before_cycles * current_amount

        if boost == "enteloot_amount_20":
            after_amount = math.floor(
                current_amount * 1.20
            )
            after = before_cycles * after_amount

        elif boost == "enteloot_amount_50":
            after_amount = math.floor(
                current_amount * 1.50
            )
            after = before_cycles * after_amount

        elif boost == "enteloot_rate_minus_2":
            after_rate = max(1, current_rate - 2)
            after_cycles = remaining // after_rate
            after = after_cycles * current_amount

        else:
            after = before

        return max(0, after - before)

    def civic_chain_bonus(
        self,
        town: str,
        upgrade: str,
    ) -> int:

        current = self.state.upgrades[town]
        production_count = len(
            current & set(PRODUCTION_UPGRADES)
        )

        # Value of what this upgrade unlocks next.
        if upgrade in PRODUCTION_UPGRADES:
            if production_count == 0:
                return 3000 + 5000 + 6000
            if production_count == 1:
                return 4000 + 5000
            return 0

        if upgrade == "Rec-center":
            return 5000 + 6000

        if upgrade == "School":
            return 6000

        if upgrade == "Fire-station":
            return 5000

        return 0

    def production_upgrade_value(
        self,
        town: str,
        upgrade: str,
    ) -> float:

        resource = PRODUCTION_UPGRADES[upgrade]
        info = self.data["towns"][town]

        base = int(
            info.get("production", {})
            .get("resources", {})
            .get(resource, 0)
        )

        if base <= 0:
            return float("-inf")

        rate = int(info["production"]["rate"])

        if rate <= 0:
            return float("-inf")

        remaining = max(
            0,
            self.state.total_ticks - self.state.tick,
        )

        future_cycles = remaining // rate
        extra_resource = future_cycles * base

        raw_value = (
            extra_resource
            * RESOURCE_SELL.get(resource, 0)
        )

        return raw_value

    def estimate_upgrade_cost_ticks(
        self,
        town: str,
        upgrade: str,
    ) -> Optional[int]:

        info = UPGRADES[upgrade]

        # Estimate travel.
        travel_path = self.pathfinder.shortest_path(
            self.state.location,
            town,
            boots=self.state.has_tool("boots"),
            allow_fast=False,
        )

        travel_time = (
            travel_path["time"]
            if travel_path is not None
            else None
        )

        if travel_time is None:
            return None

        raw = raw_requirements(
            info["components"]
        )

        gather_time = 0

        for resource, quantity in raw.items():
            if resource == "ore":
                node_choice = self.resources.best_node(
                    resource,
                    quantity,
                )
                if node_choice is None:
                    return None

                node, path, yield_amount = node_choice
                gather_time += path["time"]

                gather = max(
                    1,
                    math.ceil(
                        quantity
                        / max(1, yield_amount)
                    ),
                )

                gt = int(
                    self.data["nodes"][node]["gather-time"]
                )

                if self.state.has_tool("pickaxe"):
                    gt = max(1, gt - 1)

                gather_time += gather * gt

            else:
                # Use a rough node estimate.
                node_choice = self.resources.best_node(
                    resource,
                    quantity,
                )

                if node_choice is not None:
                    node, path, yield_amount = node_choice
                    gather_time += path["time"]

                    gather = max(
                        1,
                        math.ceil(
                            quantity
                            / max(1, yield_amount)
                        ),
                    )

                    gt = int(
                        self.data["nodes"][node]["gather-time"]
                    )

                    if self.state.has_tool("pickaxe"):
                        gt = max(1, gt - 1)

                    gather_time += gather * gt
                else:
                    # Could be supplied passively.
                    gather_time += 0

        craft_time = sum(
            max(1, quantity)
            for quantity in info["components"].values()
        )

        # This is intentionally an estimate used for ranking.
        return (
            travel_time
            + gather_time
            + craft_time
            + int(info["time"])
        )

    def evaluate_upgrade(
        self,
        town: str,
        upgrade: str,
    ) -> Optional[float]:

        if not self.upgrades.can_build(town, upgrade):
            # A future candidate can still be valuable even when
            # components/money aren't currently available, but it
            # must satisfy static prerequisites.
            info = UPGRADES.get(upgrade)
            if info is None:
                return None

            if self.state.has_upgrade(town, upgrade):
                return None

            if not self.upgrades.prerequisite_satisfied(
                info["prerequisite"],
                self.state.upgrades[town],
            ):
                return None

        info = UPGRADES[upgrade]

        direct = int(info["score"])

        chain = self.civic_chain_bonus(
            town,
            upgrade,
        )

        passive = self.future_enteloot_value(
            town,
            upgrade,
        )

        production = 0

        if upgrade in PRODUCTION_UPGRADES:
            production = self.production_upgrade_value(
                town,
                upgrade,
            )

        cost_ticks = self.estimate_upgrade_cost_ticks(
            town,
            upgrade,
        )

        if cost_ticks is None:
            return None

        # We deliberately give infrastructure score the greatest
        # weight because the specification says it is the primary
        # Level 3 scoring driver.
        total_value = (
            direct
            + chain
            + passive
            + 0.25 * production
        )

        # Tick efficiency.
        return total_value / max(1, cost_ticks)

    # --------------------------------------------------------
    # Upgrade execution
    # --------------------------------------------------------

    def candidate_upgrades(self) -> List[Tuple[float, str, str]]:
        candidates = []

        for town in sorted(self.data["towns"]):
            for upgrade in sorted(UPGRADES):
                if self.state.has_upgrade(town, upgrade):
                    continue

                value = self.evaluate_upgrade(
                    town,
                    upgrade,
                )

                if value is None:
                    continue

                candidates.append(
                    (value, town, upgrade)
                )

        candidates.sort(
            key=lambda x: (
                -x[0],
                x[1],
                x[2],
            )
        )

        return candidates

    def execute_best_feasible_upgrade(self) -> bool:
        """
        Choose a currently executable upgrade by score/tick value.
        """
        candidates = self.candidate_upgrades()

        for _, town, upgrade in candidates:
            info = UPGRADES[upgrade]

            # Don't commit to a build whose raw materials are
            # obviously impossible inside the remaining budget.
            estimate = self.estimate_upgrade_cost_ticks(
                town,
                upgrade,
            )

            if estimate is None:
                continue

            remaining = (
                self.state.total_ticks
                - self.state.tick
            )

            if estimate > remaining:
                continue

            # Prepare components.
            if not self.upgrades.prepare_components(
                info["components"],
            ):
                continue

            # Move/build.
            if self.upgrades.build(
                town,
                upgrade,
            ):
                return True

        return False

    # --------------------------------------------------------
    # Profitable crafting
    # --------------------------------------------------------

    def best_craft_trade(self):
        """
        If construction cannot currently be executed, use
        surplus passive resources to create a sellable good.

        This prevents the planner from idling with large amounts
        of unused raw resources.
        """
        if self.state.location not in self.data["towns"]:
            return False

        town = self.state.location
        affinity = "crafting" in self.data["towns"][town].get(
            "affinities",
            [],
        )

        craft_time = 1 if affinity else 2

        best = None

        for item, recipe in RECIPES.items():
            quantity = math.inf

            for resource, amount in recipe["inputs"].items():
                quantity = min(
                    quantity,
                    self.state.inventory[resource] // amount,
                )

            if quantity == math.inf or quantity <= 0:
                continue

            quantity = int(min(quantity, 1000))

            prices = [
                int(
                    self.data["towns"][sell_town]
                    .get("item-rates", {})
                    .get(item, 0)
                )
                for sell_town in self.data["towns"]
            ]

            if not prices:
                continue

            best_price = max(prices)

            raw_value = sum(
                amount
                * RESOURCE_SELL.get(resource, 0)
                for resource, amount in recipe["inputs"].items()
            )

            profit = best_price - raw_value

            if profit <= 0:
                continue

            score = (
                profit
                / max(1, craft_time)
            )

            candidate = (
                score,
                item,
                quantity,
                best_price,
            )

            if best is None or candidate > best:
                best = candidate

        if best is None:
            return False

        _, item, quantity, _ = best
        recipe = RECIPES[item]

        # Craft only a bounded batch to preserve flexibility for
        # construction.
        quantity = min(quantity, 50)

        for resource, amount in recipe["inputs"].items():
            if self.state.inventory[resource] < amount * quantity:
                return False

        for resource, amount in recipe["inputs"].items():
            self.state.consume(
                resource,
                amount * quantity,
            )

        ticks = quantity * craft_time

        if self.state.tick + ticks > self.state.total_ticks:
            return False

        self.actions.craft(item, quantity)

        self.economy.advance_to(
            self.state,
            self.state.tick + ticks,
        )

        self.state.inventory[item] += quantity
        self.state.action_count += 1

        # Sell at best-paying town.
        sell_candidates = []

        for sell_town in sorted(self.data["towns"]):
            price = int(
                self.data["towns"][sell_town]
                .get("item-rates", {})
                .get(item, 0)
            )

            if price <= 0:
                continue

            path = self.pathfinder.shortest_path(
                self.state.location,
                sell_town,
                boots=self.state.has_tool("boots"),
                allow_fast=True,
                enteloot=self.state.enteloot,
            )

            if path is not None:
                sell_candidates.append(
                    (-price, path["time"], sell_town, path)
                )

        if not sell_candidates:
            return True

        sell_candidates.sort()
        _, _, sell_town, path = sell_candidates[0]

        if not self.resources.move_path(
            path,
            self.actions,
        ):
            return True

        self.actions.sell(item, quantity)

        # Selling costs 1 tick and creates Enteloot.
        price = int(
            self.data["towns"][sell_town]
            .get("item-rates", {})
            .get(item, 0)
        )

        if self.state.tick + 1 <= self.state.total_ticks:
            self.economy.advance_to(
                self.state,
                self.state.tick + 1,
            )
            self.state.enteloot += price * quantity
            self.state.inventory[item] -= quantity
            if self.state.inventory[item] <= 0:
                del self.state.inventory[item]

        self.state.action_count += 1
        return True

    # --------------------------------------------------------
    # Final safe advancement
    # --------------------------------------------------------

    def advance_final_window(self):
        """
        We never deliberately submit malformed actions.

        If resources exist, sell them in a valid one-tick action.
        Otherwise, stop: the engine will advance passive systems
        when the final valid action reaches its endpoint.
        """
        while self.state.tick < self.state.total_ticks:
            available = [
                item
                for item, quantity in self.state.inventory.items()
                if quantity > 0
                and item not in COMPONENTS
            ]

            if not available:
                break

            item = sorted(available)[0]

            # Selling one is always a one-tick action.
            self.actions.sell(item, 1)

            price = RESOURCE_SELL.get(item)

            if price is None:
                # Crafted good.
                towns = [
                    int(
                        self.data["towns"][town]
                        .get("item-rates", {})
                        .get(item, 0)
                    )
                    for town in self.data["towns"]
                ]
                price = max(towns) if towns else 0

            self.state.consume(item, 1)

            self.economy.advance_to(
                self.state,
                self.state.tick + 1,
            )

            self.state.enteloot += price
            self.state.action_count += 1

    # --------------------------------------------------------
    # Main
    # --------------------------------------------------------

    def run(self) -> List[dict]:

        # ----------------------------------------------------
        # Stage 1:
        # Let passive production accumulate while obtaining
        # enough resources to make Level 3 tools worthwhile.
        # ----------------------------------------------------

        self.prepare_tools()

        # ----------------------------------------------------
        # Stage 2:
        # Main infrastructure loop.
        # ----------------------------------------------------

        failed_rounds = 0

        while self.state.tick < self.state.total_ticks:
            before = self.state.snapshot()

            if self.execute_best_feasible_upgrade():
                failed_rounds = 0
                continue

            # If no build is currently feasible, try a profitable
            # craft/sell cycle with surplus resources.
            if self.best_craft_trade():
                failed_rounds = 0
                continue

            # If we cannot immediately invest, acquire a small
            # amount of the most useful missing resource for the
            # best high-value upgrade.
            candidates = self.candidate_upgrades()

            acquired = False

            for _, town, upgrade in candidates[:10]:
                info = UPGRADES[upgrade]

                raw = raw_requirements(info["components"])

                deficits = {
                    resource: amount - self.state.inventory[resource]
                    for resource, amount in raw.items()
                    if amount > self.state.inventory[resource]
                }

                if not deficits:
                    continue

                # Acquire the largest economically useful deficit.
                resource, amount = sorted(
                    deficits.items(),
                    key=lambda x: (-x[1], x[0]),
                )[0]

                amount = min(amount, 25)

                if self.upgrades.acquire_resource_efficiently(
                    resource,
                    amount,
                ):
                    acquired = True
                    break

            if acquired:
                continue

            # No useful operation found.
            failed_rounds += 1

            if failed_rounds >= 2:
                break

            self.state.restore(before)
            break

        # ----------------------------------------------------
        # Stage 3:
        # Use any remaining sellable inventory without creating
        # invalid actions.
        # ----------------------------------------------------

        self.advance_final_window()

        return self.actions.actions


# ============================================================
# SUBMISSION VALIDATION
# ============================================================

class SubmissionValidator:
    """
    Lightweight structural validator.

    It deliberately does not pretend to reproduce every server-side
    economic rule. The actual competition engine remains authoritative.
    """

    def __init__(self, data):
        self.data = data
        self.graph = Graph(data)

    def validate(self, actions) -> List[Tuple[int, str]]:
        errors = []
        location = self.data["run"]["starting_town"]

        for index, action in enumerate(actions):
            if not isinstance(action, dict):
                errors.append((index, "Action is not an object."))
                continue

            action_type = action.get("type")

            if action_type == "travel":
                destination = action.get("destination")
                if destination is None:
                    errors.append((index, "Travel has no destination."))
                    continue

                fast = bool(action.get("fast", False))

                if not self.graph.has_edge(
                    location,
                    destination,
                    fast=fast,
                ):
                    errors.append(
                        (
                            index,
                            f"Invalid route {location} -> "
                            f"{destination}, fast={fast}",
                        )
                    )
                else:
                    location = destination

            elif action_type == "gather":
                if location not in self.data["nodes"]:
                    errors.append(
                        (
                            index,
                            "Gather action is not at a resource node.",
                        )
                    )

            elif action_type == "buy":
                if "item" not in action or "quantity" not in action:
                    errors.append(
                        (index, "Buy must contain item and quantity.")
                    )

            elif action_type == "sell":
                if "item" not in action or "quantity" not in action:
                    errors.append(
                        (index, "Sell must contain item and quantity.")
                    )

            elif action_type == "craft":
                if "item" not in action or "quantity" not in action:
                    errors.append(
                        (index, "Craft must contain item and quantity.")
                    )

            elif action_type == "build":
                if "upgrade" not in action:
                    errors.append(
                        (index, "Build must contain upgrade.")
                    )

            elif action_type == "upkeep":
                pass

            else:
                errors.append(
                    (index, f"Unknown action type: {action_type}")
                )

        return errors


# ============================================================
# OUTPUT
# ============================================================

def write_submission(actions, filename="level3_submission.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            {"actions": actions},
            f,
            indent=2,
        )


def print_summary(strategy: Level3Strategy, errors):
    state = strategy.state

    print("=" * 72)
    print("AGE OF ENTELAND - OPTIMISED LEVEL 3")
    print("=" * 72)

    print(f"Tick: {state.tick}/{state.total_ticks}")
    print(f"Actions: {len(strategy.actions.actions)}")
    print(f"Enteloot: {state.enteloot}")

    print()
    print("Tools:")
    for tool in sorted(state.tools):
        print(f"  {tool}")
    if not state.tools:
        print("  none")

    print()
    print("Upgrades:")
    total = 0
    for town in sorted(state.upgrades):
        upgrades = sorted(state.upgrades[town])
        if upgrades:
            print(f"  {town}: {', '.join(upgrades)}")
            total += len(upgrades)

    if total == 0:
        print("  none")

    print(f"\nTotal upgrades: {total}")

    print()
    print("Top inventory:")
    for item, amount in sorted(
        state.inventory.items(),
        key=lambda x: (-x[1], x[0]),
    )[:20]:
        print(f"  {item}: {amount}")

    print()
    if errors:
        print(f"VALIDATION WARNINGS: {len(errors)}")
        for index, message in errors[:20]:
            print(f"  Action {index}: {message}")
    else:
        print("STRUCTURAL VALIDATION: PASS")

    print("=" * 72)


# ============================================================
# MAIN
# ============================================================

def find_input_file() -> str:
    candidates = [
        "level3.json",
        "level_3.json",
        "3.json",
        "3.txt",
        "input.json",
    ]

    for filename in candidates:
        if os.path.exists(filename):
            return filename

    raise FileNotFoundError(
        "Could not find the Level 3 JSON input.\n"
        "Expected one of:\n"
        + "\n".join(f"  - {x}" for x in candidates)
    )


def main():
    input_file = find_input_file()

    print(f"Loading: {input_file}")

    data = load_input(input_file)

    required = {"run", "towns", "nodes", "routes"}
    missing = required - set(data)

    if missing:
        raise ValueError(
            "Input missing required fields: "
            + ", ".join(sorted(missing))
        )

    print(
        f"Loaded {len(data['towns'])} towns, "
        f"{len(data['nodes'])} nodes, "
        f"{len(data['routes'])} routes."
    )

    strategy = Level3Strategy(data)
    actions = strategy.run()

    validator = SubmissionValidator(data)
    errors = validator.validate(actions)

    output_file = "level3_submission.txt"
    write_submission(actions, output_file)

    print_summary(strategy, errors)

    print()
    print(f"Submission written to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    main()