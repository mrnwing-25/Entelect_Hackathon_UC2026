import json
import math
import heapq
import sys
import os
import time
from collections import Counter, defaultdict

# ============================================================
# LEVEL 4 GLOBAL CONSTANTS
# ============================================================

RAW = {
    "wheat": {"sell": 2, "buy": 4},
    "wood": {"sell": 3, "buy": 5},
    "stone": {"sell": 3, "buy": 5},
    "clay": {"sell": 4, "buy": 6},
    "fish": {"sell": 4, "buy": 6},
    "sheep": {"sell": 5, "buy": 8},
    "ore": {"sell": 6, "buy": None},
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
    "boots": {"inputs": {"iron-fittings": 2, "rope": 2}, "effect": "travel"},
    "pickaxe": {"inputs": {"iron-fittings": 2, "planks": 2}, "effect": "gather"},
}

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
    "police-station": {
        "boost": None, "components": {"bricks": 6, "stone-blocks": 4, "iron-fittings": 2},
        "cost": 2200, "time": 5, "score": 5000, "kind": "civic",
        "prerequisite": "fire-station",
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


# ============================================================
# INPUT & GRAPH ENGINE
# ============================================================

def load_input(filename):
    candidates = [filename, "4.txt", "level4.json", "level_4.json", "4.json", "input.json"]
    for cand in candidates:
        if os.path.exists(cand):
            with open(cand, "r", encoding="utf-8") as file:
                return json.load(file), cand
    raise FileNotFoundError("Could not find a valid Level 4 input file.")


class Graph:
    def __init__(self, data):
        self.adjacency = defaultdict(list)
        self.vertices = set(data["towns"]) | set(data["nodes"])
        self.standard_edges = {}
        self.fast_edges = {}
        self._build(data["routes"])

    def _build(self, routes):
        for route in routes:
            a, b = route["between"]
            weight = int(route["weight"])
            toll = int(route.get("toll", 0))

            edge = {"destination": b, "weight": weight, "toll": toll, "fast": toll > 0}
            rev_edge = {"destination": a, "weight": weight, "toll": toll, "fast": toll > 0}

            key = (a, b)
            rev_key = (b, a)

            if toll == 0:
                self.standard_edges[key] = edge
                self.standard_edges[rev_key] = rev_edge
            else:
                self.fast_edges[key] = edge
                self.fast_edges[rev_key] = rev_edge

            self.adjacency[a].append(edge)
            self.adjacency[b].append(rev_edge)

    def get_edge(self, u, v, fast=False):
        table = self.fast_edges if fast else self.standard_edges
        return table.get((u, v))


class PathFinder:
    def __init__(self, graph):
        self.graph = graph

    def edge_time(self, edge, has_boots=False):
        w = edge["weight"]
        return max(1, w - 1) if has_boots else w

    def shortest_path(self, start, end, has_boots=False, allow_fast=True, enteloot=None):
        if start == end:
            return {"time": 0, "toll": 0, "path": [start], "fast_flags": []}

        pq = [(0, 0, start)]
        distances = {start: (0, 0)}
        previous = {}

        while pq:
            cur_time, cur_toll, node = heapq.heappop(pq)
            known = distances.get(node)
            if known is None or cur_time != known[0] or cur_toll != known[1]:
                continue

            for edge in self.graph.adjacency.get(node, []):
                dest = edge["destination"]
                is_fast = edge["fast"]

                if is_fast and not allow_fast:
                    continue

                toll = edge["toll"] if is_fast else 0
                if is_fast and enteloot is not None and cur_toll + toll > enteloot:
                    continue

                w_time = self.edge_time(edge, has_boots)
                new_time = cur_time + w_time
                new_toll = cur_toll + toll

                candidate = (new_time, new_toll)
                old = distances.get(dest)

                if old is None or candidate < old:
                    distances[dest] = candidate
                    previous[dest] = (node, is_fast)
                    heapq.heappush(pq, (new_time, new_toll, dest))

        if end not in distances:
            return None

        path, fast_flags = [], []
        curr = end
        while curr != start:
            path.append(curr)
            prev_node, was_fast = previous[curr]
            fast_flags.append(was_fast)
            curr = prev_node

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
# SIMULATION ENGINE
# ============================================================

class SimulationEngine:
    def __init__(self, data, graph, pathfinder):
        self.data = data
        self.graph = graph
        self.pathfinder = pathfinder
        self.total_ticks = int(data["run"]["total_ticks"])
        self.start = data["run"]["starting_town"]
        self.towns = data["towns"]
        self.actions = []
        self.tick = 0
        self.loc = self.start
        self.inventory = Counter()
        self.enteloot = int(data["run"]["starting_enteloot"])
        self.built = defaultdict(set)
        self.tools = set()

        for name, town_info in self.towns.items():
            for upg in town_info.get("upgrades", []):
                self.built[name].add(upg)

        self.towns_states = {}
        for name in self.towns:
            self.towns_states[name] = {
                "boost_timer": 0,
                "ticks_since_production": 0,
                "ticks_since_enteloot": 0,
            }

    def has_tool(self, tool):
        return tool in self.tools

    def has_upgrade(self, town, upgrade):
        return upgrade in self.built[town]

    def advance(self, new_tick):
        if new_tick <= self.tick:
            return
        new_tick = min(new_tick, self.total_ticks)
        delta_ticks = new_tick - self.tick

        for _ in range(delta_ticks):
            self.tick += 1
            for town, state in self.towns_states.items():
                if state["boost_timer"] > 0:
                    state["boost_timer"] -= 1

                # Production trickle
                state["ticks_since_production"] += 1
                pr = int(self.towns[town]["production"]["rate"])
                if state["ticks_since_production"] >= pr:
                    state["ticks_since_production"] = 0
                    base_res = self.towns[town]["production"].get("resources", {})
                    prod_map = {
                        "farmhouse": "sheep", "pier": "fish", "fertilised-fields": "wheat",
                        "quarry": "stone", "woodlands": "wood", "pottery-house": "clay"
                    }
                    for r, amt in base_res.items():
                        mult = 2 if any(self.has_upgrade(town, u) and prod_map.get(u) == r for u in PRODUCTION_UPGRADES) else 1
                        self.inventory[r] += int(amt) * mult

                # Enteloot trickle
                state["ticks_since_enteloot"] += 1
                er = int(self.towns[town]["enteloot"]["rate"])
                if self.has_upgrade(town, "police-station"):
                    er = max(1, er - 2)

                if state["ticks_since_enteloot"] >= er:
                    state["ticks_since_enteloot"] = 0
                    base_amt = int(self.towns[town]["enteloot"]["amount"])
                    pct = 0
                    if self.has_upgrade(town, "rec-center"): pct += 20
                    if self.has_upgrade(town, "school"): pct += 50
                    if self.has_upgrade(town, "library"): pct += 50
                    amt = int(math.floor(base_amt * (100 + pct) / 100.0))
                    if state["boost_timer"] > 0:
                        amt *= 2
                    self.enteloot += amt

    def travel_to(self, target, allow_fast=True):
        if self.loc == target:
            return True

        has_b = self.has_tool("boots")
        res = self.pathfinder.shortest_path(self.loc, target, has_boots=has_b, allow_fast=allow_fast, enteloot=self.enteloot)
        if res is None:
            return False

        path = res["path"]
        fast_flags = res["fast_flags"]

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            is_fast = fast_flags[i]
            edge = self.graph.get_edge(u, v, fast=is_fast)
            if edge is None:
                return False

            w_time = self.pathfinder.edge_time(edge, has_b)
            if self.tick + w_time > self.total_ticks:
                return False

            if is_fast:
                if self.enteloot < edge["toll"]:
                    return False
                self.enteloot -= edge["toll"]
                self.actions.append({"type": "travel", "destination": v, "fast": True})
            else:
                self.actions.append({"type": "travel", "destination": v})

            self.advance(self.tick + w_time)
            self.loc = v
            self.check_and_upkeep()

        return True

    def check_and_upkeep(self):
        if self.loc not in self.towns:
            return
        state = self.towns_states[self.loc]
        if state["boost_timer"] <= 5 and (self.total_ticks - self.tick) > 30:
            if self.tick + 5 <= self.total_ticks:
                duration = 75 if self.has_upgrade(self.loc, "fire-station") else 50
                state["boost_timer"] = duration
                self.advance(self.tick + 5)
                self.actions.append({"type": "upkeep"})

    def gather_at_node(self, node, count):
        if count <= 0:
            return True
        if not self.travel_to(node):
            return False

        info = self.data["nodes"][node]
        g_time = int(info["gather-time"])
        if self.has_tool("pickaxe"):
            g_time = max(1, g_time - 1)
        y_amt = int(info["yield"])
        res = info["resource"]

        for _ in range(count):
            if self.tick + g_time > self.total_ticks:
                return False
            self.advance(self.tick + g_time)
            self.inventory[res] += y_amt
            self.actions.append({"type": "gather"})
        return True

    def craft_item(self, item, qty):
        if qty <= 0:
            return True
        recipe = RECIPES.get(item) or COMPONENTS.get(item) or TOOLS.get(item)
        if not recipe:
            return False

        req = recipe["inputs"]
        for r, n in req.items():
            if self.inventory[r] < n * qty:
                return False
        for r, n in req.items():
            self.inventory[r] -= n * qty

        craft_time = 1 if "crafting" in self.towns.get(self.loc, {}).get("affinities", []) else 2
        total_time = craft_time * qty
        if self.tick + total_time > self.total_ticks:
            return False

        self.advance(self.tick + total_time)
        if item in TOOLS:
            self.tools.add(item)
        else:
            self.inventory[item] += qty
        self.actions.append({"type": "craft", "item": item, "quantity": qty})
        return True

    def buy_item(self, item, qty):
        if qty <= 0:
            return True
        if self.loc not in self.towns:
            return False
        if item not in self.towns[self.loc]["production"].get("resources", {}):
            return False
        buy_p = RAW[item]["buy"]
        cost = buy_p * qty
        if self.enteloot < cost:
            return False
        if self.tick + 1 > self.total_ticks:
            return False

        self.enteloot -= cost
        self.advance(self.tick + 1)
        self.inventory[item] += qty
        self.actions.append({"type": "buy", "item": item, "quantity": qty})
        return True

    def sell_item(self, item, qty):
        if qty <= 0 or self.inventory[item] < qty:
            return False
        if self.loc not in self.towns:
            return False
        if self.tick + 1 > self.total_ticks:
            return False

        rate = RAW[item]["sell"] if item in RAW else self.towns[self.loc]["item-rates"].get(item, 0)
        self.inventory[item] -= qty
        self.advance(self.tick + 1)
        self.enteloot += rate * qty
        self.actions.append({"type": "sell", "item": item, "quantity": qty})
        return True

    def can_build(self, town, upgrade):
        if self.has_upgrade(town, upgrade):
            return False
        u = UPGRADES[upgrade]
        pre = u["prerequisite"]
        if pre == "any_1_prod":
            if sum(1 for x in self.built[town] if UPGRADES[x]["kind"] == "production") < 1:
                return False
        elif pre == "any_2_prod":
            if sum(1 for x in self.built[town] if UPGRADES[x]["kind"] == "production") < 2:
                return False
        elif pre and not self.has_upgrade(town, pre):
            return False

        return (
            self.enteloot >= u["cost"]
            and all(self.inventory[c] >= n for c, n in u["components"].items())
        )

    def build_upgrade(self, town, upgrade):
        if not self.can_build(town, upgrade):
            return False
        if not self.travel_to(town):
            return False

        u = UPGRADES[upgrade]
        for c, n in u["components"].items():
            self.inventory[c] -= n
        self.enteloot -= u["cost"]

        if self.tick + u["time"] > self.total_ticks:
            return False

        self.advance(self.tick + u["time"])
        self.built[town].add(upgrade)
        self.actions.append({"type": "build", "upgrade": upgrade})
        return True


# ============================================================
# COMPONENT DEPENDENCY ENGINE
# ============================================================

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


def expand_component_crafts(components):
    needed = Counter()
    def expand(name, qty):
        if name in RAW or name not in COMPONENTS:
            return
        for child, n in COMPONENTS[name]["inputs"].items():
            if child in COMPONENTS:
                expand(child, n * qty)
        needed[name] += qty

    for name, qty in components.items():
        expand(name, qty)
    return needed


# ============================================================
# DYNAMIC FINANCE & PRODUCTION ENGINE
# ============================================================

def select_best_node(data, sim, resource):
    candidates = [n for n, info in data["nodes"].items() if info.get("resource") == resource]
    best = None
    has_b = sim.has_tool("boots")
    has_p = sim.has_tool("pickaxe")
    for n in candidates:
        res = sim.pathfinder.shortest_path(sim.loc, n, has_boots=has_b, allow_fast=True, enteloot=sim.enteloot)
        if res is None:
            continue
        g_time = data["nodes"][n]["gather-time"]
        if has_p:
            g_time = max(1, g_time - 1)
        score = res["time"] * 2 + g_time * (100.0 / data["nodes"][n]["yield"])
        if best is None or score < best[0]:
            best = (score, n, data["nodes"][n])
    return (best[1], best[2]) if best else None


def find_best_trade_loop(data, sim):
    best_loop, best_eff = None, 0.0
    crafting_towns = [t for t, info in sim.towns.items() if "crafting" in info.get("affinities", [])]
    if not crafting_towns:
        crafting_towns = list(sim.towns.keys())

    has_b = sim.has_tool("boots")
    has_p = sim.has_tool("pickaxe")
    qty = 100

    for item, info in RECIPES.items():
        if not info.get("sellable", False):
            continue
        inputs = info["inputs"]
        input_nodes = {}
        for r in inputs:
            nodes = [n for n, n_info in data["nodes"].items() if n_info.get("resource") == r]
            if not nodes:
                break
            input_nodes[r] = max(nodes, key=lambda n: data["nodes"][n]["yield"] / data["nodes"][n]["gather-time"])
        if len(input_nodes) != len(inputs):
            continue

        best_sell_town, best_rate = None, 0
        for t, t_info in sim.towns.items():
            r = t_info["item-rates"].get(item, 0)
            if r > best_rate:
                best_rate, best_sell_town = r, t

        for c_town in crafting_towns:
            total_ticks, total_tolls = 0, 0
            cur = c_town
            for r, needed_per_item in inputs.items():
                node = input_nodes[r]
                res = sim.pathfinder.shortest_path(cur, node, has_boots=has_b, allow_fast=True)
                if not res:
                    total_ticks += 99999
                    continue
                total_ticks += res["time"]
                total_tolls += res["toll"]
                g_time = data["nodes"][node]["gather-time"]
                if has_p:
                    g_time = max(1, g_time - 1)
                y_amt = data["nodes"][node]["yield"]
                total_ticks += math.ceil((needed_per_item * qty) / y_amt) * g_time
                cur = node

            res_back = sim.pathfinder.shortest_path(cur, c_town, has_boots=has_b, allow_fast=True)
            if not res_back:
                continue
            total_ticks += res_back["time"] + qty * 1
            total_tolls += res_back["toll"]

            res_sell = sim.pathfinder.shortest_path(c_town, best_sell_town, has_boots=has_b, allow_fast=True)
            if not res_sell:
                continue
            total_ticks += res_sell["time"] + 1
            total_tolls += res_sell["toll"]

            profit = best_rate * qty - total_tolls
            eff = profit / max(1, total_ticks)
            if eff > best_eff:
                best_eff = eff
                best_loop = {
                    "item": item,
                    "inputs": inputs,
                    "input_nodes": input_nodes,
                    "craft_town": c_town,
                    "sell_town": best_sell_town,
                    "quantity": qty,
                }

    return best_loop


def generate_cash(sim, target_amount, best_loop, affinity_town):
    if target_amount <= 0:
        return True
    if not best_loop or sim.tick >= sim.total_ticks - 50:
        return False

    item = best_loop["item"]
    sell_town = best_loop["sell_town"]
    item_rate = sim.towns[sell_town]["item-rates"].get(item, 1)

    qty = max(20, math.ceil(target_amount / max(1, item_rate)))

    for r, needed_per_item in best_loop["inputs"].items():
        total_needed = needed_per_item * qty
        missing = total_needed - sim.inventory[r]
        if missing > 0:
            node = best_loop["input_nodes"][r]
            y_amt = sim.data["nodes"][node]["yield"]
            gathers = math.ceil(missing / y_amt)
            if not sim.gather_at_node(node, gathers):
                return False

    if not sim.travel_to(affinity_town):
        return False
    if not sim.craft_item(item, qty):
        return False

    if not sim.travel_to(sell_town):
        return False
    if not sim.sell_item(item, qty):
        return False

    return True


def prepare_and_build(sim, town, upgrade, best_loop, affinity_town):
    if sim.has_upgrade(town, upgrade):
        return True
    if sim.tick >= sim.total_ticks - 25:
        return False

    info = UPGRADES[upgrade]
    cost = info["cost"]

    # Prerequisite verification
    pre = info["prerequisite"]
    if pre == "any_1_prod":
        if sum(1 for u in PRODUCTION_UPGRADES if sim.has_upgrade(town, u)) < 1:
            return False
    elif pre == "any_2_prod":
        if sum(1 for u in PRODUCTION_UPGRADES if sim.has_upgrade(town, u)) < 2:
            return False
    elif pre and not sim.has_upgrade(town, pre):
        return False

    # 1. On-Demand Cash Generation
    if sim.enteloot < cost:
        short = cost - sim.enteloot + 500
        if not generate_cash(sim, short, best_loop, affinity_town):
            return False

    # 2. On-Demand Component Production
    missing_comps = Counter()
    for comp, amt in info["components"].items():
        if sim.inventory[comp] < amt:
            missing_comps[comp] = amt - sim.inventory[comp]

    if missing_comps:
        raw_req = DependencyPlanner().raw_requirements(missing_comps)
        for r, amt in raw_req.items():
            missing_raw = amt - sim.inventory[r]
            if missing_raw <= 0:
                continue

            if r == "ore":
                choice = select_best_node(sim.data, sim, "ore")
                if not choice:
                    return False
                node_name, node_info = choice
                gathers = math.ceil(missing_raw / node_info["yield"])
                if not sim.gather_at_node(node_name, gathers):
                    return False
            else:
                # Buy if town sells and surplus allows, else gather
                producing = [t for t, t_info in sim.towns.items() if r in t_info["production"].get("resources", {})]
                bought = False
                if producing and sim.enteloot > (cost + RAW[r]["buy"] * missing_raw):
                    best_t = min(producing, key=lambda t: sim.pathfinder.shortest_path(sim.loc, t, has_boots=sim.has_tool("boots"))["time"])
                    if sim.travel_to(best_t) and sim.buy_item(r, missing_raw):
                        bought = True
                if not bought:
                    choice = select_best_node(sim.data, sim, r)
                    if not choice:
                        return False
                    node_name, node_info = choice
                    gathers = math.ceil(missing_raw / node_info["yield"])
                    if not sim.gather_at_node(node_name, gathers):
                        return False

        if not sim.travel_to(affinity_town):
            return False

        crafts = expand_component_crafts(missing_comps)
        ordered_comps = ["mortar", "bricks", "rope", "fencing", "nets", "kiln-glass", "iron-fittings", "planks", "thatch", "stone-blocks"]
        for c in ordered_comps:
            if c in crafts and crafts[c] > 0:
                if not sim.craft_item(c, crafts[c]):
                    return False

    # 3. Travel & Construct
    if not sim.travel_to(town):
        return False

    return sim.build_upgrade(town, upgrade)


def craft_initial_tools(sim, data, affinity_town):
    """Craft Pickaxe and Boots immediately at start."""
    # We need 4 iron-fittings, 2 planks, 2 rope
    # 4 iron-fittings = 8 ore, 4 wood
    # 2 planks = 4 wood
    # 2 rope = 4 sheep
    # Total: 140 ore (bulk for entire game!), 8 wood, 4 sheep
    ore_node = select_best_node(data, sim, "ore")
    if ore_node:
        sim.gather_at_node(ore_node[0], 28) # 28 * 5 = 140 ore

    wood_node = select_best_node(data, sim, "wood")
    if wood_node:
        sim.gather_at_node(wood_node[0], 3)

    sheep_node = select_best_node(data, sim, "sheep")
    if sheep_node:
        sim.gather_at_node(sheep_node[0], 2)

    sim.travel_to(affinity_town)
    sim.craft_item("iron-fittings", 4)
    sim.craft_item("planks", 2)
    sim.craft_item("rope", 2)
    sim.craft_item("pickaxe", 1)
    sim.craft_item("boots", 1)


def choose_production(town_info, existing_upgrades=None):
    existing_upgrades = existing_upgrades or set()
    resources = set(town_info["production"]["resources"])
    candidates = [
        u for u in PRODUCTION_UPGRADES
        if UPGRADES[u]["boost"] in resources and u not in existing_upgrades
    ]
    if not candidates:
        candidates = [u for u in PRODUCTION_UPGRADES if u not in existing_upgrades]
    if not candidates:
        candidates = PRODUCTION_UPGRADES
    return min(candidates, key=lambda u: (UPGRADES[u]["cost"], u))


# ============================================================
# SOLVER IMPLEMENTATION
# ============================================================

def solve(data):
    graph = Graph(data)
    pathfinder = PathFinder(graph)
    sim = SimulationEngine(data, graph, pathfinder)
    towns = data["towns"]
    start = data["run"]["starting_town"]

    # 1. Crafting Affinity Hub
    affinity_town = next(
        (t for t, info in towns.items() if "crafting" in info.get("affinities", [])),
        start
    )

    # 2. Craft Tools & Extract Initial Bulk Ore
    craft_initial_tools(sim, data, affinity_town)

    # 3. Optimal Trade Loop Detector
    best_loop = find_best_trade_loop(data, sim)

    # 4. Generate Initial Capital
    if best_loop and sim.enteloot < 30000:
        generate_cash(sim, 35000, best_loop, affinity_town)

    # Ranked towns by civic Enteloot potential
    ranked_towns = sorted(
        towns.keys(),
        key=lambda t: (
            -towns[t]["enteloot"]["amount"] / max(1, towns[t]["enteloot"]["rate"]),
            t
        )
    )

    # ====================================================
    # CONTINUOUS GLOBAL INFRASTRUCTURE QUEUES
    # ====================================================

    # QUEUE 1: Build 2 production upgrades in every town (unlocks all civics + 100% spread)
    for town in ranked_towns:
        if sim.tick >= sim.total_ticks - 100:
            break
        while sum(1 for u in PRODUCTION_UPGRADES if sim.has_upgrade(town, u)) < 2:
            existing = {u for u in PRODUCTION_UPGRADES if sim.has_upgrade(town, u)}
            p = choose_production(towns[town], existing)
            if not prepare_and_build(sim, town, p, best_loop, affinity_town):
                break

    # QUEUE 2: Build Rec-Center across all towns (3,000 pts)
    for town in ranked_towns:
        if sim.tick >= sim.total_ticks - 100:
            break
        if not sim.has_upgrade(town, "rec-center"):
            prepare_and_build(sim, town, "rec-center", best_loop, affinity_town)

    # QUEUE 3: Build School across all towns (5,000 pts)
    for town in ranked_towns:
        if sim.tick >= sim.total_ticks - 100:
            break
        if sim.has_upgrade(town, "rec-center") and not sim.has_upgrade(town, "school"):
            prepare_and_build(sim, town, "school", best_loop, affinity_town)

    # QUEUE 4: Build Library across all towns (6,000 pts)
    for town in ranked_towns:
        if sim.tick >= sim.total_ticks - 100:
            break
        if sim.has_upgrade(town, "school") and not sim.has_upgrade(town, "library"):
            prepare_and_build(sim, town, "library", best_loop, affinity_town)

    # QUEUE 5: Build Fire-Station across all towns (4,000 pts)
    for town in ranked_towns:
        if sim.tick >= sim.total_ticks - 100:
            break
        if not sim.has_upgrade(town, "fire-station"):
            prepare_and_build(sim, town, "fire-station", best_loop, affinity_town)

    # QUEUE 6: Build Police-Station across all towns (5,000 pts)
    for town in ranked_towns:
        if sim.tick >= sim.total_ticks - 100:
            break
        if sim.has_upgrade(town, "fire-station") and not sim.has_upgrade(town, "police-station"):
            prepare_and_build(sim, town, "police-station", best_loop, affinity_town)

    # QUEUE 7: Build all remaining production upgrades across all towns (1,000 pts each)
    for town in ranked_towns:
        if sim.tick >= sim.total_ticks - 80:
            break
        for upg in PRODUCTION_UPGRADES:
            if sim.tick >= sim.total_ticks - 80:
                break
            if not sim.has_upgrade(town, upg):
                prepare_and_build(sim, town, upg, best_loop, affinity_town)

    # ====================================================
    # 100% TICK EXHAUSTION (CONTINUOUS TRADING & LIQUIDATION)
    # ====================================================
    # Squeeze all remaining ticks by running high-efficiency trade batches
    if best_loop:
        while sim.tick < sim.total_ticks - 60:
            # Batch gather
            for r, needed_per_item in best_loop["inputs"].items():
                if sim.tick >= sim.total_ticks - 50:
                    break
                node = best_loop["input_nodes"][r]
                y_amt = sim.data["nodes"][node]["yield"]
                gathers = math.ceil((needed_per_item * best_loop["quantity"]) / y_amt)
                sim.gather_at_node(node, gathers)

            if not sim.travel_to(best_loop["craft_town"]):
                break
            if not sim.craft_item(best_loop["item"], best_loop["quantity"]):
                break

            if not sim.travel_to(best_loop["sell_town"]):
                break
            if not sim.sell_item(best_loop["item"], best_loop["quantity"]):
                break

    # Final tick cleanup: liquidate all remaining raw inventory into Enteloot
    if sim.loc in towns:
        for r in sorted(RAW.keys(), key=lambda res: -RAW[res]["sell"]):
            if sim.tick >= sim.total_ticks:
                break
            if sim.inventory[r] > 0:
                sim.sell_item(r, sim.inventory[r])

    return sim.actions, sim.tick, sim.built, sim.enteloot, sim.inventory


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "4.txt"
    data, matched_path = load_input(input_file)

    print("=" * 60)
    print("LEVEL 4 OPTIMIZED SOLVER")
    print("=" * 60)
    print(f"Loaded input: {matched_path}")
    print(f"Total tick budget: {data['run']['total_ticks']}")
    print(f"Starting town: {data['run']['starting_town']}")

    start_time = time.perf_counter()
    actions, tick, built, enteloot, inventory = solve(data)
    runtime = time.perf_counter() - start_time

    output_file = "level4_submission.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"actions": actions}, f, indent=2)

    total_upgrades = sum(len(upgs) for upgs in built.values())
    infra_score = sum(UPGRADES[u]["score"] for upgs in built.values() for u in upgs)

    print("-" * 60)
    print(f"Generated actions: {len(actions)}")
    print(f"Ticks used: {tick} / {data['run']['total_ticks']}")
    print(f"Remaining ticks: {max(0, data['run']['total_ticks'] - tick)}")
    print(f"Total upgrades built: {total_upgrades}")
    print(f"Infrastructure score: {infra_score}")
    print(f"Final Enteloot: {enteloot}")
    print(f"Submission created: {os.path.abspath(output_file)}")
    print(f"Runtime: {runtime:.4f} seconds")
    print("=" * 60)


if __name__ == "__main__":
    main()