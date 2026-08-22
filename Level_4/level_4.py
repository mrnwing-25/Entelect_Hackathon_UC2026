import json
import heapq
import math
import os
import sys
from collections import defaultdict, Counter

# ============================================================
# GLOBAL CONSTANTS
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
    "farmhouse": {
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
    "pier": {
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
    "fertilised-fields": {
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
    "quarry": {
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
    "woodlands": {
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
    "pottery-house": {
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
    "rec-center": {
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
    "fire-station": {
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
    "school": {
        "boost": "enteloot_amount_50",
        "components": {
            "bricks": 6,
            "planks": 3,
            "kiln-glass": 2,
        },
        "enteloot": 2000,
        "time": 5,
        "prerequisite": "rec-center",
        "score": 5000,
    },
    "police-station": {
        "boost": "enteloot_rate_minus_2",
        "components": {
            "bricks": 6,
            "stone-blocks": 4,
            "iron-fittings": 2,
        },
        "enteloot": 2200,
        "time": 5,
        "prerequisite": "fire-station",
        "score": 5000,
    },
    "library": {
        "boost": "enteloot_amount_50",
        "components": {
            "bricks": 5,
            "planks": 5,
            "kiln-glass": 2,
        },
        "enteloot": 2500,
        "time": 5,
        "prerequisite": "school",
        "score": 6000,
    },
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalise_name(value):
    return str(value).strip().lower().replace("_", "-")

# ============================================================
# GRAPH AND ROUTING
# ============================================================

class Graph:
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
        table = self.fast_edges if fast else self.standard_edges
        return table.get(self._edge_key(source, destination))

    def has_edge(self, source, destination, fast=False):
        return self.get_edge(source, destination, fast) is not None

    def neighbours(self, node):
        return self.adjacency.get(node, [])


class PathFinder:
    def __init__(self, graph):
        self.graph = graph

    def edge_time(self, edge, boots=False):
        if boots:
            return max(1, edge["weight"] - 1)
        return edge["weight"]

    def shortest_path(self, start, end, boots=False, allow_fast=False, enteloot=None):
        if start == end:
            return {
                "time": 0,
                "toll": 0,
                "path": [start],
                "fast_flags": [],
            }

        pq = [(0, 0, start)]
        distances = {start: (0, 0)}
        previous = {}

        while pq:
            current_time, current_toll, node = heapq.heappop(pq)
            known = distances.get(node)

            if known is None or current_time != known[0] or current_toll != known[1]:
                continue

            for edge in self.graph.neighbours(node):
                destination = edge["destination"]
                edge_fast = edge["fast"]

                if edge_fast and not allow_fast:
                    continue

                if edge_fast:
                    toll = edge["toll"]
                    if enteloot is not None and current_toll + toll > enteloot:
                        continue
                else:
                    toll = 0

                time = self.edge_time(edge, boots)
                new_time = current_time + time
                new_toll = current_toll + toll

                old = distances.get(destination)
                candidate = (new_time, new_toll)

                if old is None or candidate < old:
                    distances[destination] = candidate
                    previous[destination] = (node, edge_fast)
                    heapq.heappush(pq, (new_time, new_toll, destination))

        if end not in distances:
            return None

        path, fast_flags = [], []
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
# STATE TRACKING & SIMULATION ENGINE
# ============================================================

class PlannerState:
    def __init__(self, data):
        run = data["run"]
        self.data = data
        self.total_ticks = int(run["total_ticks"])
        self.tick = 0
        self.enteloot = int(run["starting_enteloot"])
        self.starting_town = run["starting_town"]
        self.location = self.starting_town
        self.inventory = Counter()
        self.upgrades = defaultdict(set)
        self.tools = set()
        self.action_count = 0

        # Initialize existing upgrades
        for name, town_info in data["towns"].items():
            for upg in town_info.get("upgrades", []):
                self.upgrades[name].add(normalise_name(upg))

        # Passive trickle and upkeep timers
        self.towns_states = {}
        for name, town_info in data["towns"].items():
            self.towns_states[name] = {
                "boost_timer": 0,
                "ticks_since_production": 0,
                "ticks_since_enteloot": 0,
            }

    def advance_tick(self):
        self.tick += 1
        if self.tick > self.total_ticks:
            return

        for town_name, town_state in self.towns_states.items():
            if town_state["boost_timer"] > 0:
                town_state["boost_timer"] -= 1

            # Production trickle
            town_state["ticks_since_production"] += 1
            prod_rate = self.get_production_rate(town_name)
            if town_state["ticks_since_production"] >= prod_rate:
                town_state["ticks_since_production"] = 0
                for resource, amount in self.get_production_resources(town_name).items():
                    self.inventory[resource] += amount

            # Enteloot trickle
            town_state["ticks_since_enteloot"] += 1
            enteloot_rate = self.get_enteloot_rate(town_name)
            if town_state["ticks_since_enteloot"] >= enteloot_rate:
                town_state["ticks_since_enteloot"] = 0
                enteloot_amount = self.get_enteloot_amount(town_name)
                self.enteloot += enteloot_amount

    def advance_ticks(self, ticks):
        for _ in range(ticks):
            self.advance_tick()

    def get_production_rate(self, town_name):
        return int(self.data["towns"][town_name]["production"]["rate"])

    def get_production_resources(self, town_name):
        resources = {}
        base_resources = self.data["towns"][town_name]["production"].get("resources", {})
        
        production_upgrade_map = {
            "farmhouse": "sheep",
            "pier": "fish",
            "fertilised-fields": "wheat",
            "quarry": "stone",
            "woodlands": "wood",
            "pottery-house": "clay",
        }
        
        for r, amt in base_resources.items():
            amt = int(amt)
            upgrade_for_r = None
            for upg, res in production_upgrade_map.items():
                if res == r:
                    upgrade_for_r = upg
                    break
            
            if upgrade_for_r and self.has_upgrade(town_name, upgrade_for_r):
                amt *= 2
            resources[r] = amt
        return resources

    def get_enteloot_rate(self, town_name):
        base_rate = int(self.data["towns"][town_name]["enteloot"]["rate"])
        if self.has_upgrade(town_name, "police-station"):
            base_rate = max(1, base_rate - 2)
        return base_rate

    def get_enteloot_amount(self, town_name):
        base_amount = int(self.data["towns"][town_name]["enteloot"]["amount"])
        percentage = 0
        if self.has_upgrade(town_name, "rec-center"):
            percentage += 20
        if self.has_upgrade(town_name, "school"):
            percentage += 50
        if self.has_upgrade(town_name, "library"):
            percentage += 50
            
        amount = int(math.floor(base_amount * (100 + percentage) / 100.0))
        if self.towns_states[town_name]["boost_timer"] > 0:
            amount *= 2
        return amount

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
            if not self.consume(item, amount):
                return False
        return True

    def has_upgrade(self, town, upgrade):
        return normalise_name(upgrade) in self.upgrades[town]

    def add_upgrade(self, town, upgrade):
        self.upgrades[town].add(normalise_name(upgrade))

    def has_tool(self, tool):
        return normalise_name(tool) in self.tools


# ============================================================
# ACTIONS & DISPATCHERS
# ============================================================

class ActionBuilder:
    def __init__(self):
        self.actions = []

    def travel(self, destination, fast=False):
        action = {"type": "travel", "destination": destination}
        if fast:
            action["fast"] = True
        self.actions.append(action)

    def gather(self):
        self.actions.append({"type": "gather"})

    def buy(self, item, quantity):
        if quantity <= 0:
            return
        self.actions.append({
            "type": "buy",
            "item": item,
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
        self.actions.append({"type": "upkeep"})


# ============================================================
# MANAGEMENT CLUSTERS
# ============================================================

class NodeManager:
    def __init__(self, data, pathfinder):
        self.data = data
        self.nodes = data["nodes"]
        self.pathfinder = pathfinder

    def nodes_for_resource(self, resource):
        return [node for node, info in self.nodes.items() if info.get("resource") == resource]

    def get_distance(self, start, end):
        path = self.pathfinder.shortest_path(start, end, boots=False, allow_fast=False)
        return path["time"] if path else float("inf")

    def best_resource_node(self, resource, current_location):
        best_node, best_score = None, float("-inf")
        for node_name, node in self.nodes.items():
            if node.get("resource") != resource:
                continue

            yield_amount = int(node.get("yield", 0))
            gather_time = int(node.get("gather-time", 999999))
            travel_time = self.get_distance(current_location, node_name)

            if math.isinf(travel_time):
                continue

            total_time = travel_time + gather_time
            if total_time <= 0:
                continue

            score = yield_amount / total_time
            if score > best_score:
                best_score = score
                best_node = node_name
        return best_node


class ResourcePlanner:
    def __init__(self, data, graph, pathfinder, state):
        self.data = data
        self.graph = graph
        self.pathfinder = pathfinder
        self.state = state
        self.node_manager = NodeManager(data, pathfinder)

    def nearest_node(self, resource, boots=False):
        candidates = self.node_manager.nodes_for_resource(resource)
        best = None
        for node in candidates:
            path = self.pathfinder.shortest_path(self.state.location, node, boots=boots, allow_fast=False)
            if path is None:
                continue
            score = path["time"] + self.data["nodes"][node]["gather-time"]
            if best is None or score < best[0]:
                best = (score, node, path)
        return best

    def gather_resource(self, resource, quantity, actions):
        quantity = int(math.ceil(quantity))
        if quantity <= 0:
            return True

        boots = self.state.has_tool("boots")
        pickaxe = self.state.has_tool("pickaxe")

        while self.state.inventory[resource] < quantity:
            choice = self.nearest_node(resource, boots=boots)
            if choice is None:
                return False

            _, node, path = choice
            if not self.move_using_path(path, actions):
                return False

            node_data = self.data["nodes"][node]
            gather_time = int(node_data["gather-time"])
            if pickaxe:
                gather_time = max(1, gather_time - 1)

            if self.state.tick + gather_time > self.state.total_ticks:
                return False

            actions.gather()
            self.state.advance_ticks(gather_time)
            self.state.action_count += 1
            self.state.add_resource(resource, node_data["yield"])
        return True

    def move_using_path(self, path, actions, strategy=None):
        vertices = path["path"]
        fast_flags = path["fast_flags"]

        for i in range(len(vertices) - 1):
            source = vertices[i]
            destination = vertices[i + 1]
            fast = fast_flags[i]

            edge = self.graph.get_edge(source, destination, fast=fast)
            if edge is None:
                return False

            travel_time = self.pathfinder.edge_time(edge, self.state.has_tool("boots"))
            if self.state.tick + travel_time > self.state.total_ticks:
                return False

            if fast:
                toll = edge["toll"]
                if self.state.enteloot < toll:
                    return False
                self.state.enteloot -= toll

            actions.travel(destination, fast=fast)
            self.state.advance_ticks(travel_time)
            self.state.location = destination
            self.state.action_count += 1

            if strategy:
                strategy.check_and_trigger_upkeep()
        return True


class CraftingPlanner:
    def __init__(self, data, state, actions):
        self.data = data
        self.state = state
        self.actions = actions

    def craft_time(self, town):
        town_data = self.data["towns"].get(town)
        if town_data is None:
            return 2
        return 1 if "crafting" in town_data.get("affinities", []) else 2

    def craft_component(self, component, quantity):
        quantity = int(quantity)
        if quantity <= 0:
            return True

        if component not in COMPONENTS:
            return False

        recipe = COMPONENTS[component]
        for ingredient, amount in recipe["inputs"].items():
            required = amount * quantity
            if ingredient in COMPONENTS:
                if self.state.inventory[ingredient] < required:
                    missing = required - self.state.inventory[ingredient]
                    if not self.craft_component(ingredient, missing):
                        return False

        for ingredient, amount in recipe["inputs"].items():
            if ingredient in COMPONENTS:
                continue
            required = amount * quantity
            if self.state.inventory[ingredient] < required:
                return False

        for ingredient, amount in recipe["inputs"].items():
            required = amount * quantity
            if not self.state.consume(ingredient, required):
                return False

        craft_time = self.craft_time(self.state.location)
        ticks = quantity * craft_time
        if self.state.tick + ticks > self.state.total_ticks:
            return False

        self.actions.craft(component, quantity)
        self.state.advance_ticks(ticks)
        self.state.action_count += 1
        self.state.inventory[component] += quantity
        return True

    def craft_good(self, item, quantity):
        if item not in RECIPES:
            return False

        quantity = int(quantity)
        recipe = RECIPES[item]

        for resource, amount in recipe["inputs"].items():
            required = amount * quantity
            if self.state.inventory[resource] < required:
                return False

        for resource, amount in recipe["inputs"].items():
            required = amount * quantity
            self.state.consume(resource, required)

        craft_time = self.craft_time(self.state.location)
        ticks = quantity * craft_time
        if self.state.tick + ticks > self.state.total_ticks:
            return False

        self.actions.craft(item, quantity)
        self.state.advance_ticks(ticks)
        self.state.action_count += 1
        self.state.inventory[item] += quantity
        return True


class UpgradeManager:
    PRODUCTION_UPGRADES = {
        "farmhouse",
        "pier",
        "fertilised-fields",
        "quarry",
        "woodlands",
        "pottery-house",
    }

    def __init__(self, data, state, actions, crafting):
        self.data = data
        self.state = state
        self.actions = actions
        self.crafting = crafting

    @staticmethod
    def prerequisite_satisfied(prerequisite, town_upgrades):
        if prerequisite is None:
            return True

        if isinstance(prerequisite, str):
            norm_prereq = normalise_name(prerequisite)
            if norm_prereq == "production":
                return len(town_upgrades & UpgradeManager.PRODUCTION_UPGRADES) >= 1
            if norm_prereq == "production2":
                return len(town_upgrades & UpgradeManager.PRODUCTION_UPGRADES) >= 2
            return norm_prereq in town_upgrades

        if isinstance(prerequisite, (list, tuple, set)):
            return all(normalise_name(item) in town_upgrades for item in prerequisite)

        if isinstance(prerequisite, dict):
            for key, value in prerequisite.items():
                norm_key = normalise_name(key)
                if norm_key == "any":
                    return any(normalise_name(item) in town_upgrades for item in value)
                elif norm_key == "all":
                    return all(normalise_name(item) in town_upgrades for item in value)
                elif norm_key == "production":
                    return len(town_upgrades & UpgradeManager.PRODUCTION_UPGRADES) >= int(value)
                else:
                    if value and norm_key not in town_upgrades:
                        return False
            return True
        return False

    def can_build(self, town, upgrade):
        norm_upgrade = normalise_name(upgrade)
        if norm_upgrade not in UPGRADES:
            return False

        if self.state.has_upgrade(town, norm_upgrade):
            return False

        info = UPGRADES[norm_upgrade]
        if not self.prerequisite_satisfied(info.get("prerequisite"), self.state.upgrades[town]):
            return False

        if self.state.enteloot < info["enteloot"]:
            return False

        return self.state.can_afford_components(info["components"])

    def build(self, town, upgrade):
        norm_upgrade = normalise_name(upgrade)
        if not self.can_build(town, norm_upgrade):
            return False

        info = UPGRADES[norm_upgrade]
        if not self.state.consume_components(info["components"]):
            return False

        self.state.enteloot -= info["enteloot"]
        ticks = int(info["time"])
        if self.state.tick + ticks > self.state.total_ticks:
            return False

        self.actions.build(norm_upgrade)
        self.state.advance_ticks(ticks)
        self.state.action_count += 1
        self.state.add_upgrade(town, norm_upgrade)
        return True


class ToolManager:
    def __init__(self, state, actions, crafting):
        self.state = state
        self.actions = actions
        self.crafting = crafting

    def craft_tool(self, tool):
        tool_key = normalise_name(tool)
        if tool_key in self.state.tools or tool_key not in TOOLS:
            return False

        info = TOOLS[tool_key]
        for item, amount in info["inputs"].items():
            if self.state.inventory[item] < amount:
                return False

        for item, amount in info["inputs"].items():
            self.state.consume(item, amount)

        craft_time = self.crafting.craft_time(self.state.location)
        if self.state.tick + craft_time > self.state.total_ticks:
            return False

        self.actions.craft(tool_key, 1)
        self.state.advance_ticks(craft_time)
        self.state.action_count += 1
        self.state.tools.add(tool_key)
        return True


class DependencyPlanner:
    def __init__(self):
        self.components = COMPONENTS

    def expand(self, item, quantity, result=None):
        if result is None:
            result = Counter()

        quantity = int(quantity)
        if item not in self.components:
            result[item] += quantity
            return result

        recipe = self.components[item]
        for ingredient, amount in recipe["inputs"].items():
            self.expand(ingredient, amount * quantity, result)
        return result

    def raw_requirements(self, requirements):
        result = Counter()
        for item, quantity in requirements.items():
            result.update(self.expand(item, quantity))
        return result


# ============================================================
# MASTER STRATEGY SOLVER (SCORE-FIRST GLOBAL PASSES)
# ============================================================

class Level4Strategy:
    def __init__(self, data):
        self.data = data
        self.graph = Graph(data)
        self.pathfinder = PathFinder(self.graph)
        self.node_manager = NodeManager(data, self.pathfinder)
        self.state = PlannerState(data)
        self.actions = ActionBuilder()
        self.crafting = CraftingPlanner(data, self.state, self.actions)
        self.resource_planner = ResourcePlanner(data, self.graph, self.pathfinder, self.state)
        self.upgrades = UpgradeManager(data, self.state, self.actions, self.crafting)
        self.tools = ToolManager(self.state, self.actions, self.crafting)

    def travel_to(self, destination, prefer_fast=False):
        if self.state.location == destination:
            return True

        boots = self.state.has_tool("boots")
        standard = self.pathfinder.shortest_path(self.state.location, destination, boots=boots, allow_fast=False)
        fast = None

        if prefer_fast:
            fast = self.pathfinder.shortest_path(
                self.state.location, destination, boots=boots, allow_fast=True, enteloot=self.state.enteloot
            )

        selected = standard
        if fast is not None:
            if standard is None:
                selected = fast
            else:
                time_saved = standard["time"] - fast["time"]
                toll = fast["toll"]
                if time_saved >= 1 and toll <= self.state.enteloot:
                    selected = fast

        if selected is None:
            return False

        return self.resource_planner.move_using_path(selected, self.actions, strategy=self)

    def towns_producing_resource(self, resource):
        return [
            town_name
            for town_name, town_info in self.data["towns"].items()
            if resource in town_info["production"].get("resources", {})
        ]

    def buy_resource(self, resource, quantity, town):
        town_info = self.data["towns"][town]
        if resource not in town_info["production"].get("resources", {}):
            return False

        buy_price = RESOURCE_BUY_PRICE.get(resource)
        if buy_price is None:
            return False

        total_cost = buy_price * quantity
        if self.state.enteloot < total_cost:
            return False

        if self.state.location != town:
            if not self.travel_to(town, prefer_fast=True):
                return False

        if self.state.tick + 1 > self.state.total_ticks:
            return False

        self.state.enteloot -= total_cost
        self.state.advance_ticks(1)
        self.actions.buy(resource, quantity)
        self.state.add_resource(resource, quantity)
        self.state.action_count += 1
        return True

    def sell_good(self, item, quantity):
        if self.state.tick + 1 > self.state.total_ticks:
            return False
        
        town = self.state.location
        rate = self.data["towns"][town]["item-rates"].get(item, 0)
        self.state.enteloot += rate * quantity
        self.state.consume(item, quantity)
        self.state.advance_ticks(1)
        self.actions.sell(item, quantity)
        self.state.action_count += 1
        return True

    def obtain_resources(self, requirements, reserve_enteloot=0):
        ordered = sorted(requirements.items(), key=lambda pair: (pair[0] != "ore", -pair[1]))

        for resource, amount in ordered:
            current = self.state.inventory[resource]
            missing = amount - current
            if missing <= 0:
                continue

            if resource == "ore":
                if not self.resource_planner.gather_resource(resource, missing, self.actions):
                    return False
                continue

            # Optimized raw materials purchase
            buy_price = RESOURCE_BUY_PRICE.get(resource)
            if buy_price is not None:
                cost = buy_price * missing
                if self.state.enteloot - cost >= reserve_enteloot:
                    producing_towns = self.towns_producing_resource(resource)
                    if producing_towns:
                        best_town, best_path_time = None, float("inf")
                        boots = self.state.has_tool("boots")
                        for town in producing_towns:
                            path = self.pathfinder.shortest_path(
                                self.state.location, town, boots=boots, allow_fast=False
                            )
                            if path and path["time"] < best_path_time:
                                best_path_time = path["time"]
                                best_town = town

                        if best_town and self.buy_resource(resource, missing, best_town):
                            continue

            # Gather fallback
            if not self.resource_planner.gather_resource(resource, missing, self.actions):
                return False
        return True

    def produce_component_tree(self, requirements):
        if not self.travel_to_crafting_town():
            return False

        ordered = [
            "mortar", "bricks", "rope", "fencing", "nets",
            "kiln-glass", "iron-fittings", "planks", "thatch", "stone-blocks"
        ]
        remaining = Counter(requirements)

        for component in ordered:
            amount = remaining.get(component, 0)
            if amount <= 0:
                continue

            current = self.state.inventory[component]
            missing = amount - current
            if missing <= 0:
                continue

            if not self.crafting.craft_component(component, missing):
                return False
        return True

    def travel_to_crafting_town(self):
        current = self.state.location
        if current in self.data["towns"]:
            if "crafting" in self.data["towns"][current].get("affinities", []):
                return True

        crafting_towns = [
            town for town, info in self.data["towns"].items()
            if "crafting" in info.get("affinities", [])
        ]
        if not crafting_towns:
            return False

        best_town, best_path = None, None
        boots = self.state.has_tool("boots")

        for town in crafting_towns:
            path = self.pathfinder.shortest_path(current, town, boots=boots, allow_fast=False)
            if path is None:
                continue
            if best_path is None or path["time"] < best_path["time"]:
                best_town = town
                best_path = path

        if best_town is None:
            return False

        return self.resource_planner.move_using_path(best_path, self.actions, strategy=self)

    def prepare_upgrade(self, town, upgrade):
        norm_upgrade = normalise_name(upgrade)
        if norm_upgrade not in UPGRADES:
            return False

        info = UPGRADES[norm_upgrade]
        build_cost = info["enteloot"]

        required_components = Counter(info["components"])
        missing_components = Counter()
        for component, amount in required_components.items():
            current = self.state.inventory[component]
            if current < amount:
                missing_components[component] = amount - current

        if not missing_components:
            return True

        raw_requirements = DependencyPlanner().raw_requirements(missing_components)
        if not self.obtain_resources(raw_requirements, reserve_enteloot=build_cost):
            return False

        if not self.travel_to_crafting_town():
            return False

        return self.produce_component_tree(missing_components)

    def prepare_and_build(self, town, upgrade):
        if self.state.has_upgrade(town, upgrade):
            return True

        info = UPGRADES[upgrade]
        build_cost = info["enteloot"]

        if self.state.enteloot < build_cost:
            return False

        required_components = Counter(info["components"])
        missing_components = Counter()
        for component, amount in required_components.items():
            current = self.state.inventory[component]
            if current < amount:
                missing_components[component] = amount - current

        if missing_components:
            raw_requirements = DependencyPlanner().raw_requirements(missing_components)
            
            for resource, amount in raw_requirements.items():
                current = self.state.inventory[resource]
                missing_res = amount - current
                if missing_res <= 0:
                    continue
                
                if resource == "ore":
                    if not self.resource_planner.gather_resource(resource, missing_res, self.actions):
                        return False
                else:
                    producing_towns = self.towns_producing_resource(resource)
                    if not producing_towns:
                        return False
                    
                    boots = self.state.has_tool("boots")
                    best_town = min(
                        producing_towns,
                        key=lambda t: (
                            self.pathfinder.shortest_path(self.state.location, t, boots=boots, allow_fast=True)["time"]
                            if self.pathfinder.shortest_path(self.state.location, t, boots=boots, allow_fast=True)
                            else float("inf")
                        )
                    )
                    if not self.buy_resource(resource, missing_res, best_town):
                        return False

            if not self.travel_to_crafting_town():
                return False

            if not self.produce_component_tree(missing_components):
                return False

        if self.state.location != town:
            if not self.travel_to(town, prefer_fast=True):
                return False

        self.check_and_trigger_upkeep()
        return self.upgrades.build(town, upgrade)

    def prepare_and_craft_tool(self, tool_name):
        tool_key = normalise_name(tool_name)
        if tool_key in self.state.tools:
            return True

        info = TOOLS.get(tool_key)
        if not info:
            return False

        required_inputs = Counter(info["inputs"])
        missing_inputs = Counter()
        for item, amount in required_inputs.items():
            current = self.state.inventory[item]
            if current < amount:
                missing_inputs[item] = amount - current

        if missing_inputs:
            raw_requirements = DependencyPlanner().raw_requirements(missing_inputs)
            if not self.obtain_resources(raw_requirements):
                return False

            if not self.travel_to_crafting_town():
                return False

            if not self.produce_component_tree(missing_inputs):
                return False

        if not self.travel_to_crafting_town():
            return False

        return self.tools.craft_tool(tool_name)

    # ============================================================
    # UPKEEP METRICS
    # ============================================================

    def upkeep_action(self):
        town = self.state.location
        if town not in self.data["towns"]:
            return False

        ticks = 5
        if self.state.tick + ticks > self.state.total_ticks:
            return False

        duration = 75 if self.state.has_upgrade(town, "fire-station") else 50
        self.state.towns_states[town]["boost_timer"] = duration

        self.state.advance_ticks(ticks)
        self.actions.upkeep()
        self.state.action_count += 1
        return True

    def check_and_trigger_upkeep(self):
        town = self.state.location
        if town not in self.data["towns"]:
            return False

        town_state = self.state.towns_states[town]
        if town_state["boost_timer"] <= 5:
            remaining_ticks = self.state.total_ticks - self.state.tick
            if remaining_ticks > 20:
                rate = self.state.get_enteloot_rate(town)
                amount = self.state.get_enteloot_amount(town)
                duration = 75 if self.state.has_upgrade(town, "fire-station") else 50
                # Upkeep is worthwhile when repeated refreshes can cover at
                # least one future Enteloot cycle. A single duration window
                # is too conservative because refreshes may be chained.
                future_cycles = max(0, (remaining_ticks - 5) // rate)
                extra_enteloot = future_cycles * amount
                refreshes = max(1, math.ceil(remaining_ticks / duration))

                if extra_enteloot > refreshes * 5:
                    return self.upkeep_action()
        return False

    # ============================================================
    # SCORE-FIRST GLOBAL PASS PROCEDURES
    # ============================================================

    def build_prerequisites_only(self, town):
        """
        PASS 1: Build exactly 2 production upgrades in the town.
        Satisfies Rec-center & Fire-station prereqs immediately.
        """
        prod_upgrades = [
            "farmhouse", "pier", "fertilised-fields", "quarry", "woodlands", "pottery-house"
        ]
        built_count = sum(1 for upg in prod_upgrades if self.state.has_upgrade(town, upg))
        for upg in prod_upgrades:
            if built_count >= 2:
                break
            if not self.state.has_upgrade(town, upg):
                if self.prepare_and_build(town, upg):
                    built_count += 1

    def build_civic_chain_only(self, town):
        """
        PASS 2: Build high-value points globally (Civic Chain).
        """
        civics = ["rec-center", "school", "library", "fire-station", "police-station"]
        for upg in civics:
            if not self.state.has_upgrade(town, upg):
                self.prepare_and_build(town, upg)

    def build_remaining_production_upgrades(self, town):
        """
        PASS 3: Build any remaining production upgrades.
        """
        prod_upgrades = [
            "farmhouse", "pier", "fertilised-fields", "quarry", "woodlands", "pottery-house"
        ]
        for upg in prod_upgrades:
            if not self.state.has_upgrade(town, upg):
                self.prepare_and_build(town, upg)

    def choose_infrastructure_towns(self):
        towns = list(self.data["towns"].keys())
        towns.sort(key=lambda t: (
            -self.data["towns"][t]["enteloot"]["amount"],
            self.data["towns"][t]["enteloot"]["rate"],
            t
        ))
        return towns

    # ============================================================
    # LOOP ALGORITHM DETECTOR
    # ============================================================

    def find_best_trade_loop(self):
        # Amortized large batch sizes (120+) to reduce routing overhead
        quantity = 120
        best_loop = None
        best_efficiency = 0.0

        boots = self.state.has_tool("boots")
        pickaxe = self.state.has_tool("pickaxe")

        crafting_towns = [
            town for town, info in self.data["towns"].items()
            if "crafting" in info.get("affinities", [])
        ]

        for recipe_name, recipe_info in RECIPES.items():
            inputs = recipe_info["inputs"]
            
            input_nodes = {}
            possible = True
            for resource in inputs.keys():
                nodes = self.node_manager.nodes_for_resource(resource)
                if not nodes:
                    possible = False
                    break
                
                best_n = max(nodes, key=lambda n: self.data["nodes"][n]["yield"] / self.data["nodes"][n]["gather-time"])
                input_nodes[resource] = best_n

            if not possible:
                continue

            best_sell_town = None
            best_rate = 0
            for town_name, town_info in self.data["towns"].items():
                rate = town_info["item-rates"].get(recipe_name, 0)
                if rate > best_rate:
                    best_rate = rate
                    best_sell_town = town_name

            if not best_sell_town:
                continue

            for craft_town in crafting_towns:
                total_travel_ticks = 0
                total_gather_ticks = 0
                total_tolls = 0
                
                curr_loc = craft_town
                for resource, req_qty in inputs.items():
                    node = input_nodes[resource]
                    path = self.pathfinder.shortest_path(curr_loc, node, boots=boots, allow_fast=True)
                    if not path:
                        total_travel_ticks += 999999
                        continue
                    total_travel_ticks += path["time"]
                    total_tolls += path["toll"]
                    
                    yield_amt = self.data["nodes"][node]["yield"]
                    g_time = self.data["nodes"][node]["gather-time"]
                    if pickaxe:
                        g_time = max(1, g_time - 1)
                    num_gathers = math.ceil((req_qty * quantity) / yield_amt)
                    total_gather_ticks += num_gathers * g_time
                    curr_loc = node

                path_back = self.pathfinder.shortest_path(curr_loc, craft_town, boots=boots, allow_fast=True)
                if path_back:
                    total_travel_ticks += path_back["time"]
                    total_tolls += path_back["toll"]
                else:
                    total_travel_ticks += 999999

                craft_ticks = quantity * 1

                path_sell = self.pathfinder.shortest_path(craft_town, best_sell_town, boots=boots, allow_fast=True)
                if path_sell:
                    total_travel_ticks += path_sell["time"]
                    total_tolls += path_sell["toll"]
                else:
                    total_travel_ticks += 999999

                sell_ticks = 1

                path_return = self.pathfinder.shortest_path(best_sell_town, craft_town, boots=boots, allow_fast=True)
                if path_return:
                    total_travel_ticks += path_return["time"]
                    total_tolls += path_return["toll"]
                else:
                    total_travel_ticks += 999999

                total_ticks_loop = total_travel_ticks + total_gather_ticks + craft_ticks + sell_ticks
                total_revenue = best_rate * quantity
                net_profit = total_revenue - total_tolls
                
                efficiency = net_profit / total_ticks_loop if total_ticks_loop > 0 else 0
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_loop = {
                        "recipe": recipe_name,
                        "craft_town": craft_town,
                        "sell_town": best_sell_town,
                        "inputs": inputs,
                        "input_nodes": input_nodes,
                        "quantity": quantity,
                        "efficiency": efficiency
                    }

        return best_loop

    # ============================================================
    # EXECUTION PIPELINE
    # ============================================================

    def run(self):
        # Starting Upkeep Check
        self.check_and_trigger_upkeep()

        # ====================================================
        # STEP 1: INITIAL TOOL & BULK ORE GATHERING
        # ====================================================
        
        # Travel to N1 Mine Node
        self.travel_to("Marrowfen")
        self.travel_to("Thornwood", prefer_fast=True)
        self.travel_to("N1")
        
        # Gather 130 Ore in one visit to satisfy all future upgrades
        for _ in range(26):
            if self.state.tick + 3 > self.state.total_ticks:
                break
            self.actions.gather()
            self.state.advance_ticks(3)
            self.state.add_resource("ore", 5)
            self.state.action_count += 1
            
        # Travel to N19 Pasture Node
        self.travel_to("Thornwood", prefer_fast=True)
        self.travel_to("N19", prefer_fast=True)
        
        # Gather 4 Sheep
        if self.state.tick + 2 <= self.state.total_ticks:
            self.actions.gather()
            self.state.advance_ticks(2)
            self.state.add_resource("sheep", 4)
            self.state.action_count += 1
            
        # Travel to Piltover (Wood purchase)
        self.travel_to("Thornwood", prefer_fast=True)
        self.travel_to("Piltover")
        
        # Buy 4 Wood
        self.buy_resource("wood", 4, "Piltover")
        
        # Travel back to Demacia
        self.travel_to("Thornwood", prefer_fast=True)
        self.travel_to("Marrowfen", prefer_fast=True)
        self.travel_to("Demacia")
        
        # Craft components for starting tools
        self.crafting.craft_component("iron-fittings", 4)
        self.crafting.craft_component("planks", 2)
        self.crafting.craft_component("rope", 2)
        
        # Craft Pickaxe and Boots
        self.tools.craft_tool("pickaxe")
        self.tools.craft_tool("boots")

        # ====================================================
        # STEP 2: DYNAMIC TRADING PHASE
        # ====================================================
        
        best_loop = self.find_best_trade_loop()
        if best_loop:
            while self.state.enteloot < 450000 and self.state.tick < 35000:
                for resource, req_qty_per_item in best_loop["inputs"].items():
                    node = best_loop["input_nodes"][resource]
                    needed_qty = req_qty_per_item * best_loop["quantity"]
                    if not self.resource_planner.gather_resource(resource, needed_qty, self.actions):
                        break
                
                if not self.travel_to(best_loop["craft_town"], prefer_fast=True):
                    break
                if not self.crafting.craft_good(best_loop["recipe"], best_loop["quantity"]):
                    break
                
                if not self.travel_to(best_loop["sell_town"], prefer_fast=True):
                    break
                if not self.sell_good(best_loop["recipe"], best_loop["quantity"]):
                    break

        # ====================================================
        # STEP 3: SCORE-FIRST GLOBAL BUILDING PHASE
        # ====================================================
        
        towns = self.choose_infrastructure_towns()
        
        # Pass 1: Build exactly 2 production upgrades in every town to satisfy prerequisites
        for town in towns:
            if self.state.tick >= self.state.total_ticks - 100:
                break
            self.build_prerequisites_only(town)
            
        # Pass 2: Secure high-value points globally (Civics) across all towns
        for town in towns:
            if self.state.tick >= self.state.total_ticks - 100:
                break
            self.build_civic_chain_only(town)
            
        # Pass 3: Cleanup remaining production upgrades with leftover ticks
        for town in towns:
            if self.state.tick >= self.state.total_ticks - 100:
                break
            self.build_remaining_production_upgrades(town)

        # Construction finishes early on the wide Level 4 map. Continue the
        # highest-margin trade loop so the remaining clock contributes to the
        # final Enteloot total instead of being left idle.
        if best_loop:
            while self.state.enteloot < 450000 and self.state.tick < self.state.total_ticks:
                self.check_and_trigger_upkeep()
                for resource, req_qty_per_item in best_loop["inputs"].items():
                    node = best_loop["input_nodes"][resource]
                    needed_qty = req_qty_per_item * best_loop["quantity"]
                    if not self.resource_planner.gather_resource(resource, needed_qty, self.actions):
                        break
                else:
                    if (
                        self.travel_to(best_loop["craft_town"], prefer_fast=True)
                        and self.crafting.craft_good(best_loop["recipe"], best_loop["quantity"])
                        and self.travel_to(best_loop["sell_town"], prefer_fast=True)
                        and self.sell_good(best_loop["recipe"], best_loop["quantity"])
                    ):
                        continue
                break

        return self.actions.actions


# ============================================================
# SOLVER RUNNER
# ============================================================

def main():
    input_candidates = ["level4.json", "level_4.json", "4.json", "4.txt", "input.json"]
    input_file = sys.argv[1] if len(sys.argv) > 1 else None

    if input_file is None:
        for filename in input_candidates:
            if os.path.exists(filename):
                input_file = filename
                break

    if input_file is None:
        json_files = [f for f in os.listdir(".") if f.endswith(".json")]
        if json_files:
            input_file = json_files[0]
        else:
            raise FileNotFoundError("Could not find any level JSON file.")

    print(f"Running strategy against Level 4 file: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    strategy = Level4Strategy(data)
    actions = strategy.run()

    output_file = sys.argv[2] if len(sys.argv) > 2 else "level4_submission.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"actions": actions}, f, indent=2)

    print(f"Successfully generated {len(actions)} actions.")
    print(f"Created submission: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()