import json
import heapq
import sys
import os
from itertools import count
from pathlib import Path
from collections import defaultdict, Counter

# ============================================================
# GLOBAL CONSTANTS & DATA STRUCTURES
# ============================================================

RESOURCE_BUY_PRICE = {"wheat": 4, "wood": 5, "stone": 5, "clay": 6, "fish": 6, "sheep": 8}
RESOURCE_SELL_PRICE = {"wheat": 2, "wood": 3, "stone": 3, "clay": 4, "fish": 4, "sheep": 5, "ore": 6}

RECIPES = {
    "bread": {"inputs": {"wheat": 3}, "time": 2},
    "fish-n-chips": {"inputs": {"fish": 2, "wheat": 1}, "time": 2},
    "stew": {"inputs": {"sheep": 1, "fish": 1, "wheat": 1}, "time": 2},
    "wooden-crafts": {"inputs": {"wood": 4}, "time": 2},
    "furniture": {"inputs": {"wood": 3, "sheep": 1}, "time": 2},
    "stone-works": {"inputs": {"stone": 5}, "time": 2},
    "roof-tiles": {"inputs": {"clay": 3, "stone": 2}, "time": 2},
    "wool-garments": {"inputs": {"sheep": 3}, "time": 2},
    "pottery": {"inputs": {"clay": 4, "wood": 1}, "time": 2},
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

# Mapping resources to the production upgrade that boosts them
RES_TO_UPG = {
    "sheep": "farmhouse", "fish": "pier", "wheat": "fertilised-fields",
    "stone": "quarry", "wood": "woodlands", "clay": "pottery-house"
}

UPGRADES = {
    "farmhouse": {"cost": 500, "comp": {"planks": 3, "thatch": 2}, "time": 3, "type": "prod"},
    "pier": {"cost": 600, "comp": {"planks": 4, "nets": 2}, "time": 3, "type": "prod"},
    "fertilised-fields": {"cost": 500, "comp": {"fencing": 2, "thatch": 2}, "time": 3, "type": "prod"},
    "quarry": {"cost": 600, "comp": {"stone-blocks": 3, "planks": 2}, "time": 3, "type": "prod"},
    "woodlands": {"cost": 500, "comp": {"fencing": 2, "rope": 2}, "time": 3, "type": "prod"},
    "pottery-house": {"cost": 700, "comp": {"bricks": 4, "planks": 2}, "time": 3, "type": "prod"},
    "rec-center": {"cost": 1200, "comp": {"planks": 4, "bricks": 3, "rope": 1}, "time": 4, "pre": "any1"},
    "fire-station": {"cost": 1800, "comp": {"bricks": 5, "stone-blocks": 3, "rope": 2}, "time": 4, "pre": "any2"},
    "school": {"cost": 2000, "comp": {"bricks": 6, "planks": 3, "kiln-glass": 2}, "time": 5, "pre": "rec-center"},
    "police-station": {"cost": 2200, "comp": {"bricks": 6, "stone-blocks": 4, "iron-fittings": 2}, "time": 5, "pre": "fire-station"},
    "library": {"cost": 2500, "comp": {"bricks": 5, "planks": 5, "kiln-glass": 2}, "time": 5, "pre": "school"},
}

class Level4Solver:
    def __init__(self, data):
        self.data = data
        self.adj = defaultdict(list)
        for r in data["routes"]:
            u, v = r["between"]
            self.adj[u].append({"to": v, "w": r["weight"], "toll": r.get("toll", 0)})
            self.adj[v].append({"to": u, "w": r["weight"], "toll": r.get("toll", 0)})
        
        self.tick = 0
        self.total_ticks = data["run"]["total_ticks"]
        self.enteloot = data["run"]["starting_enteloot"]
        self.loc = data["run"]["starting_town"]
        self.inventory = Counter()
        self.actions = []
        self.tools = set()
        self.upgrades_built = defaultdict(set)
        self.upkeep_expiry = defaultdict(int)

    def travel(self, dest):
        if self.loc == dest: return
        sequence = count()
        pq = [(0, 0, next(sequence), self.loc, [])]
        visited = {self.loc: 0}
        
        while pq:
            t, cost, _, curr, path = heapq.heappop(pq)
            if curr == dest:
                for step in path:
                    self.tick += step["w"]
                    self.enteloot -= step["toll"]
                    self.actions.append({"type": "travel", "destination": step["to"], "fast": step["fast"]})
                self.loc = dest
                return
            for edge in self.adj[curr]:
                # Boots reduce travel time
                w = max(1, edge["w"] - (1 if "boots" in self.tools else 0))
                new_t = t + w
                if new_t < visited.get(edge["to"], 1e18):
                    if self.enteloot >= cost + edge["toll"]:
                        visited[edge["to"]] = new_t
                        heapq.heappush(pq, (new_t, cost + edge["toll"], next(sequence), edge["to"], path + [{"to": edge["to"], "fast": edge["toll"] > 0, "toll": edge["toll"], "w": w}]))

    def obtain(self, item, qty):
        needed = qty - self.inventory[item]
        if needed <= 0: return
        
        # BUY logic (Priority in Level 4)
        if self.enteloot > 15000 and item != "ore":
            sellers = [t for t, d in self.data["towns"].items() if item in d["production"]["resources"]]
            if sellers:
                self.travel(sellers[0])
                self.tick += 1
                self.enteloot -= RESOURCE_BUY_PRICE[item] * needed
                self.inventory[item] += needed
                self.actions.append({"type": "buy", "item": item, "quantity": needed})
                return

        # GATHER logic
        nodes = [n for n, d in self.data["nodes"].items() if d["resource"] == item]
        if nodes:
            node = nodes[0]
            self.travel(node)
            yield_val = self.data["nodes"][node]["yield"]
            g_time = max(1, self.data["nodes"][node]["gather-time"] - (1 if "pickaxe" in self.tools else 0))
            while self.inventory[item] < qty and self.tick < self.total_ticks:
                self.tick += g_time
                self.inventory[item] += yield_val
                self.actions.append({"type": "gather"})

    def craft_batch(self, item, qty):
        recipe = COMPONENTS.get(item) or RECIPES.get(item)
        if not recipe: return
        
        # Resolve dependencies
        for ing, amt in recipe["inputs"].items():
            if self.inventory[ing] < amt * qty:
                if ing in COMPONENTS: self.craft_batch(ing, (amt * qty) - self.inventory[ing])
                else: self.obtain(ing, amt * qty)
        
        # Craft at nearest affinity town
        target = next((t for t, d in self.data["towns"].items() if "crafting" in d["affinities"]), "Demacia")
        self.travel(target)
        unit_time = 1 if "crafting" in self.data["towns"][self.loc]["affinities"] else 2
        
        self.tick += unit_time * qty
        for ing, amt in recipe["inputs"].items(): self.inventory[ing] -= amt * qty
        self.inventory[item] += qty
        self.actions.append({"type": "craft", "item": item, "quantity": qty})

    def run_upkeep(self):
        if self.loc in self.data["towns"] and self.tick >= self.upkeep_expiry[self.loc]:
            self.tick += 5
            self.actions.append({"type": "upkeep"})
            duration = 75 if "fire-station" in self.upgrades_built[self.loc] else 50
            self.upkeep_expiry[self.loc] = self.tick + duration

    def build_upgrade(self, town, upg_name):
        if upg_name in self.upgrades_built[town] or self.tick > self.total_ticks - 1000: return
        info = UPGRADES[upg_name]
        
        # Prerequisite validation
        built = self.upgrades_built[town]
        if info.get("pre") == "any1" and not any(u in built for u in RES_TO_UPG.values()): return
        if info.get("pre") == "any2" and len([u for u in built if u in RES_TO_UPG.values()]) < 2: return
        if info.get("pre") and info["pre"] not in built and "any" not in info["pre"]: return

        # Prep components
        for c_name, c_qty in info["comp"].items():
            if self.inventory[c_name] < c_qty:
                self.craft_batch(c_name, c_qty - self.inventory[c_name])
        
        self.travel(town)
        if self.enteloot >= info["cost"]:
            self.run_upkeep() # Boost production before building
            self.tick += info["time"]
            self.enteloot -= info["cost"]
            for c_name, c_qty in info["comp"].items(): self.inventory[c_name] -= c_qty
            self.upgrades_built[town].add(upg_name)
            self.actions.append({"type": "build", "upgrade": upg_name})

    def solve(self):
        # 1. RUSH TOOLS
        self.craft_batch("iron-fittings", 4)
        self.craft_batch("planks", 2)
        self.craft_batch("rope", 2)
        # Crafting tools manually (1 tick at affinity town)
        for t in ["boots", "pickaxe"]:
            self.tick += 1
            self.tools.add(t)
            self.actions.append({"type": "craft", "item": t, "quantity": 1})

        # 2. SEED CAPITAL (Trade Pottery)
        while self.enteloot < 150000 and self.tick < 40000:
            self.craft_batch("pottery", 50)
            best_sell = max(self.data["towns"].keys(), key=lambda t: self.data["towns"][t]["item-rates"]["pottery"])
            self.travel(best_sell)
            self.enteloot += self.data["towns"][self.loc]["item-rates"]["pottery"] * 50
            self.inventory["pottery"] -= 50
            self.actions.append({"type": "sell", "item": "pottery", "quantity": 50})
            self.tick += 1

        # 3. GLOBAL EXPANSION
        sorted_towns = sorted(self.data["towns"].keys(), key=lambda t: self.data["towns"][t]["enteloot"]["amount"], reverse=True)
        
        # Priority 1: One production upgrade in every town (Multiplier start)
        for town in sorted_towns:
            res = list(self.data["towns"][town]["production"]["resources"].keys())
            if res: self.build_upgrade(town, RES_TO_UPG[res[0]])

        # Priority 2: Civic chain in high-yield towns
        civics = ["rec-center", "fire-station", "school", "police-station", "library"]
        for civic in civics:
            for town in sorted_towns:
                if self.tick > 95000: break
                self.build_upgrade(town, civic)

        # 4. FINAL LIQUIDATION
        if self.tick < self.total_ticks - 100:
            for item, qty in list(self.inventory.items()):
                if qty > 0 and self.loc in self.data["towns"] and item in self.data["towns"][self.loc]["item-rates"]:
                    self.actions.append({"type": "sell", "item": item, "quantity": qty})
                    self.tick += 1

        return {"actions": self.actions}

def main():
    level_dir = Path(__file__).resolve().parent
    input_file = Path(sys.argv[1]) if len(sys.argv) > 1 else level_dir / "4.txt"
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    with input_file.open("r") as f: data = json.load(f)
    solver = Level4Solver(data)
    result = solver.solve()
    with (level_dir / "level4_submission.txt").open("w") as f: json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()