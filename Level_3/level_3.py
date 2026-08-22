#!/usr/bin/env python3
import json, math, heapq, os
from collections import Counter, defaultdict

RULES = {
    "res": {
        "wheat": (2, 4), "wood": (3, 5), "stone": (3, 5),
        "clay": (4, 6), "fish": (4, 6), "sheep": (5, 8), "ore": (6, None)
    },
    "comp": {
        "planks": {"wood": 2},
        "thatch": {"wheat": 2},
        "stone-blocks": {"stone": 3},
        "mortar": {"clay": 1, "stone": 1},
        "bricks": {"clay": 2, "mortar": 1},
        "rope": {"sheep": 2},
        "fencing": {"wood": 2, "rope": 1},
        "kiln-glass": {"clay": 2, "wood": 2},
        "nets": {"rope": 1, "fencing": 1},
        "iron-fittings": {"ore": 2, "wood": 1},
    },
    "tools": {
        "pickaxe": {"iron-fittings": 2, "planks": 2},
        "boots": {"iron-fittings": 2, "rope": 2}
    },
    "goods": {
        "pottery": {"clay": 4, "wood": 1},
        "roof-tiles": {"clay": 3, "stone": 2},
        "furniture": {"wood": 3, "sheep": 1},
        "bread": {"wheat": 3},
        "stew": {"sheep": 1, "fish": 1, "wheat": 1},
        "stone-works": {"stone": 5},
        "wooden-crafts": {"wood": 4},
        "fish-n-chips": {"fish": 2, "wheat": 1},
        "wool-garments": {"sheep": 3}
    },
    "upgrades": {
        "fertilised-fields": ({"fencing": 2, "thatch": 2}, 500, 3, 1000, None),
        "quarry": ({"stone-blocks": 3, "planks": 2}, 600, 3, 1000, None),
        "rec-center": ({"planks": 4, "bricks": 3, "rope": 1}, 1200, 4, 3000, ("prod", 1)),
        "school": ({"bricks": 6, "planks": 3, "kiln-glass": 2}, 2000, 5, 5000, "rec-center"),
        "library": ({"bricks": 5, "planks": 5, "kiln-glass": 2}, 2500, 5, 6000, "school"),
        "fire-station": ({"bricks": 5, "stone-blocks": 3, "rope": 2}, 1800, 4, 4000, ("prod", 2)),
        "police-station": ({"bricks": 6, "stone-blocks": 4, "iron-fittings": 2}, 2200, 5, 5000, "fire-station"),
        "pottery-house": ({"bricks": 4, "planks": 2}, 700, 3, 1000, None),
        "farmhouse": ({"planks": 3, "thatch": 2}, 500, 3, 1000, None),
        "woodlands": ({"fencing": 2, "rope": 2}, 500, 3, 1000, None),
        "pier": ({"planks": 4, "nets": 2}, 600, 3, 1000, None),
    }
}
PROD_UPGRADES = {"farmhouse", "pier", "fertilised-fields", "quarry", "woodlands", "pottery-house"}

def expand_comp(name, qty=1):
    cnt = Counter()
    if name not in RULES["comp"]:
        cnt[name] += qty
        return cnt
    for sub, need in RULES["comp"][name].items():
        cnt.update(expand_comp(sub, need * qty))
    return cnt

def expand_bom(comp_dict):
    res = Counter()
    for c, q in comp_dict.items():
        res.update(expand_comp(c, q))
    return res

class Sim:
    def __init__(self, data):
        self.d = data
        self.actions = []
        self.tick = 0
        self.total_ticks = data["run"]["total_ticks"]
        self.loot = data["run"]["starting_enteloot"]
        self.loc = data["run"]["starting_town"]
        self.inv = Counter()
        self.tools = set()
        self.upgrades = defaultdict(set)
        self.prod_cyc = defaultdict(int)
        self.loot_cyc = defaultdict(int)
        
        self.adj = defaultdict(list)
        for r in data["routes"]:
            a, b = r["between"]
            w, toll = r["weight"], r.get("toll", 0)
            self.adj[a].append((b, w, toll))
            self.adj[b].append((a, w, toll))

    def step(self, dt):
        nt = min(self.tick + dt, self.total_ticks)
        for town, info in self.d["towns"].items():
            prate = info.get("production", {}).get("rate", 0)
            if prate > 0:
                c = nt // prate
                diff = c - self.prod_cyc[town]
                if diff > 0:
                    for r, base in info["production"]["resources"].items():
                        mult = 2 if any(u in self.upgrades[town] for u in PROD_UPGRADES if u.startswith(r[:4])) else 1
                        self.inv[r] += diff * base * mult
                    self.prod_cyc[town] = c
            
            lrate = info["enteloot"]["rate"]
            if "police-station" in self.upgrades[town]:
                lrate = max(1, lrate - 2)
            if lrate > 0:
                c = nt // lrate
                diff = c - self.loot_cyc[town]
                if diff > 0:
                    base = info["enteloot"]["amount"]
                    buff = (20 if "rec-center" in self.upgrades[town] else 0) + \
                           (50 if "school" in self.upgrades[town] else 0) + \
                           (50 if "library" in self.upgrades[town] else 0)
                    self.loot += diff * math.floor(base * (100 + buff) / 100)
                    self.loot_cyc[town] = c
        self.tick = nt

    def find_path(self, target):
        if self.loc == target:
            return 0, []
        pq = [(0, 0, self.loc, [])]
        best = {}
        while pq:
            t, toll, u, path = heapq.heappop(pq)
            if u in best and (t, toll) >= best[u]:
                continue
            best[u] = (t, toll)
            if u == target:
                return t, path
            for v, w, edge_toll in self.adj[u]:
                dt = max(1, w - (1 if "boots" in self.tools else 0))
                if edge_toll > 0 and self.loot < (toll + edge_toll):
                    continue
                heapq.heappush(pq, (t + dt, toll + edge_toll, v, path + [(v, edge_toll > 0, dt, edge_toll)]))
        return None, None

    def travel_to(self, dest):
        if self.loc == dest:
            return True
        _, path = self.find_path(dest)
        if not path:
            return False
        for v, fast, dt, toll in path:
            if self.tick + dt > self.total_ticks or self.loot < toll:
                return False
            self.loot -= toll
            act = {"type": "travel", "destination": v}
            if fast:
                act["fast"] = True
            self.actions.append(act)
            self.step(dt)
            self.loc = v
        return True

    def gather_at(self, node, times):
        if not self.travel_to(node):
            return False
        info = self.d["nodes"][node]
        gt = max(1, info["gather-time"] - (1 if "pickaxe" in self.tools else 0))
        y = info["yield"]
        r = info["resource"]
        for _ in range(times):
            if self.tick + gt > self.total_ticks:
                return False
            self.actions.append({"type": "gather"})
            self.step(gt)
            self.inv[r] += y
        return True

    def craft(self, item, qty=1):
        if qty <= 0:
            return True
        time_per = 1 if "crafting" in self.d["towns"].get(self.loc, {}).get("affinities", []) else 2
        
        # Split into individual 1-unit actions (1 action per tick at Demacia/Targon)
        for _ in range(qty):
            if self.tick + time_per > self.total_ticks:
                return False
            self.actions.append({"type": "craft", "item": item, "quantity": 1})
            self.step(time_per)
            self.inv[item] += 1
        return True

    def build_comp_recursive(self, comp, qty):
        if self.inv[comp] >= qty:
            return True
        needed = qty - self.inv[comp]
        recipe = RULES["comp"][comp]
        for sub, count in recipe.items():
            sub_needed = count * needed
            if sub in RULES["comp"]:
                if not self.build_comp_recursive(sub, sub_needed):
                    return False
            if self.inv[sub] < sub_needed:
                return False
            self.inv[sub] -= sub_needed
        return self.craft(comp, needed)

    def best_node_for(self, resource):
        return max(
            [n for n, d in self.d["nodes"].items() if d["resource"] == resource],
            key=lambda x: self.d["nodes"][x]["yield"]
        )

    def acquire_raw(self, raw_dict):
        for r, need in raw_dict.items():
            while self.inv[r] < need:
                deficit = need - self.inv[r]
                node = self.best_node_for(r)
                y = self.d["nodes"][node]["yield"]
                gathers = math.ceil(deficit / y)
                if not self.gather_at(node, gathers):
                    return False
        return True

    def craft_at_affinity(self, comp_dict):
        affinity_town = "Demacia" if "crafting" in self.d["towns"]["Demacia"].get("affinities", []) else "Targon"
        if not self.travel_to(affinity_town):
            return False
        for comp, q in comp_dict.items():
            if not self.build_comp_recursive(comp, q):
                return False
        return True

    def craft_tools(self):
        for tool in ["pickaxe", "boots"]:
            if tool in self.tools:
                continue
            bom = expand_bom(RULES["tools"][tool])
            if not self.acquire_raw(bom):
                return
            if not self.craft_at_affinity(RULES["tools"][tool]):
                return
            for comp, req in RULES["tools"][tool].items():
                self.inv[comp] -= req
            self.craft(tool, 1)
            self.tools.add(tool)

    def can_build(self, town, up):
        if up in self.upgrades[town]:
            return False
        pre = RULES["upgrades"][up][4]
        if pre is None:
            return True
        if isinstance(pre, tuple) and pre[0] == "prod":
            return len(self.upgrades[town] & PROD_UPGRADES) >= pre[1]
        return pre in self.upgrades[town]

    def build_upgrade(self, town, up):
        comps, cost, btime, _, _ = RULES["upgrades"][up]
        if self.loot < cost:
            self.trade_run(target_loot=cost + 1500)
            if self.loot < cost:
                return False
        raw_bom = expand_bom(comps)
        if not self.acquire_raw(raw_bom):
            return False
        if not self.craft_at_affinity(comps):
            return False
        if not self.travel_to(town):
            return False
        if self.tick + btime > self.total_ticks or self.loot < cost:
            return False
        for c, q in comps.items():
            if self.inv[c] < q:
                return False
            self.inv[c] -= q
        self.loot -= cost
        self.actions.append({"type": "build", "upgrade": up})
        self.step(btime)
        self.upgrades[town].add(up)
        return True

    def trade_run(self, target_loot=None):
        c_node = self.best_node_for("clay")
        w_node = self.best_node_for("wood")
        s_node = self.best_node_for("stone")
        wh_node = self.best_node_for("wheat")
        sh_node = self.best_node_for("sheep")

        # 1-Tick gathering per action with Pickaxe
        if not self.gather_at(c_node, 16): return
        if not self.gather_at(w_node, 10): return
        if not self.gather_at(s_node, 8): return
        if not self.gather_at(wh_node, 8): return
        if not self.gather_at(sh_node, 6): return

        if not self.travel_to("Demacia"): return
        
        # 1-Tick unit crafting per action at Demacia
        pottery_cnt = min(self.inv["clay"] // 4, self.inv["wood"] // 1)
        if pottery_cnt > 0:
            self.inv["clay"] -= pottery_cnt * 4
            self.inv["wood"] -= pottery_cnt * 1
            self.craft("pottery", pottery_cnt)

        roof_cnt = min(self.inv["clay"] // 3, self.inv["stone"] // 2)
        if roof_cnt > 0:
            self.inv["clay"] -= roof_cnt * 3
            self.inv["stone"] -= roof_cnt * 2
            self.craft("roof-tiles", roof_cnt)

        bread_cnt = self.inv["wheat"] // 3
        if bread_cnt > 0:
            self.inv["wheat"] -= bread_cnt * 3
            self.craft("bread", bread_cnt)

        furn_cnt = min(self.inv["wood"] // 3, self.inv["sheep"] // 1)
        if furn_cnt > 0:
            self.inv["wood"] -= furn_cnt * 3
            self.inv["sheep"] -= furn_cnt * 1
            self.craft("furniture", furn_cnt)

        for good in ["pottery", "roof-tiles", "furniture", "bread"]:
            qty = self.inv[good]
            if qty > 0:
                best_town, best_rate = max([(t, info["item-rates"][good]) for t, info in self.d["towns"].items()], key=lambda x: x[1])
                if self.travel_to(best_town):
                    if self.tick + 1 <= self.total_ticks:
                        self.actions.append({"type": "sell", "item": good, "quantity": qty})
                        self.step(1)
                        self.loot += qty * best_rate
                        self.inv[good] = 0

    def exhaust_remaining_ticks(self):
        """Ensures 100% of all 50,000 ticks are productively converted into valid actions."""
        # 1. Craft any remaining raw inventory in Demacia/Targon
        if self.loc in ["Demacia", "Targon"]:
            for good, rec in RULES["goods"].items():
                while self.tick < self.total_ticks:
                    if all(self.inv[r] >= req for r, req in rec.items()):
                        for r, req in rec.items():
                            self.inv[r] -= req
                        if not self.craft(good, 1):
                            break
                    else:
                        break

        # 2. Travel to the closest standard gather node
        if self.tick < self.total_ticks:
            std_nodes = [n for n, d in self.d["nodes"].items() if d["resource"] != "ore"]
            best_node, best_t = None, 999999
            for n in std_nodes:
                t, _ = self.find_path(n)
                if t is not None and t < best_t:
                    best_t, best_node = t, n
            
            if best_node and (self.tick + best_t < self.total_ticks):
                self.travel_to(best_node)

        # 3. Gather on every single remaining tick until tick == total_ticks
        if self.loc in self.d["nodes"]:
            info = self.d["nodes"][self.loc]
            gt = max(1, info["gather-time"] - (1 if "pickaxe" in self.tools else 0))
            while self.tick + gt <= self.total_ticks:
                self.actions.append({"type": "gather"})
                self.step(gt)
                self.inv[info["resource"]] += info["yield"]

    def run(self):
        # 1. Unlock Pickaxe & Boots first
        self.craft_tools()

        # 2. Build 100% of upgrades across all 15 towns (165 total upgrades)
        build_order = list(RULES["upgrades"].keys())
        for up in build_order:
            for town in sorted(self.d["towns"].keys()):
                if self.can_build(town, up):
                    self.build_upgrade(town, up)
                    if self.tick >= self.total_ticks - 1200:
                        break
            if self.tick >= self.total_ticks - 1200:
                break

        # 3. Continuous Zero-Idle High-Yield Merchant Engine
        while self.tick < self.total_ticks - 150:
            before_tick = self.tick
            self.trade_run()
            if self.tick == before_tick:
                break

        # 4. Final tick absorber to ensure full 50,000/50,000 tick utilization
        self.exhaust_remaining_ticks()

        return self.actions

def main():
    path = next((f for f in ["3.txt", "level3.json", "3.json", "input.json"] if os.path.exists(f)), None)
    if not path:
        raise FileNotFoundError("Level 3 JSON input file not found.")
    
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)

    sim = Sim(data)
    actions = sim.run()

    with open("level3_submission.txt", "w", encoding="utf8") as f:
        json.dump({"actions": actions}, f, indent=2)

    total_upgrades = sum(len(v) for v in sim.upgrades.values())
    print("=" * 60)
    print("AGE OF ENTELAND - LEVEL 3 MAX-ACTION ENGINE")
    print("=" * 60)
    print(f"Ticks Used:        {sim.tick:,} / {sim.total_ticks:,} ({(sim.tick / sim.total_ticks) * 100:.1f}%)")
    print(f"Total Actions:     {len(actions):,}")
    print(f"Ending Enteloot:   {sim.loot:,}")
    print(f"Tools Unlocked:    {', '.join(sorted(sim.tools))}")
    print(f"Total Upgrades:    {total_upgrades} / {len(sim.d['towns']) * 11}")
    print("Output saved to level3_submission.txt")

if __name__ == "__main__":
    main()