#!/usr/bin/env python3
import json, math, heapq, os
from collections import Counter, defaultdict

# ============================================================
# RULES
# ============================================================

DEFAULT = {
    "resources": {
        "wheat": {"sell_price": 2, "buy_price": 4},
        "wood": {"sell_price": 3, "buy_price": 5},
        "stone": {"sell_price": 3, "buy_price": 5},
        "clay": {"sell_price": 4, "buy_price": 6},
        "fish": {"sell_price": 4, "buy_price": 6},
        "sheep": {"sell_price": 5, "buy_price": 8},
        "ore": {"sell_price": 6, "buy_price": None},
    },
    "components": {
        "planks": {"inputs": {"wood": 2}},
        "thatch": {"inputs": {"wheat": 2}},
        "stone-blocks": {"inputs": {"stone": 3}},
        "mortar": {"inputs": {"clay": 1, "stone": 1}},
        "bricks": {"inputs": {"clay": 2, "mortar": 1}},
        "rope": {"inputs": {"sheep": 2}},
        "fencing": {"inputs": {"wood": 2, "rope": 1}},
        "kiln-glass": {"inputs": {"clay": 2, "wood": 2}},
        "nets": {"inputs": {"rope": 1, "fencing": 1}},
        "iron-fittings": {"inputs": {"ore": 2, "wood": 1}},
    },
    "tools": {
        "boots": {"inputs": {"iron-fittings": 2, "rope": 2}},
        "pickaxe": {"inputs": {"iron-fittings": 2, "planks": 2}},
    },
    "recipes": {
        "bread": {"inputs": {"wheat": 3}, "time": 2},
        "fish-n-chips": {"inputs": {"fish": 2, "wheat": 1}, "time": 2},
        "stew": {"inputs": {"sheep": 1, "fish": 1, "wheat": 1}, "time": 2},
        "wooden-crafts": {"inputs": {"wood": 4}, "time": 2},
        "furniture": {"inputs": {"wood": 3, "sheep": 1}, "time": 2},
        "stone-works": {"inputs": {"stone": 5}, "time": 2},
        "roof-tiles": {"inputs": {"clay": 3, "stone": 2}, "time": 2},
        "wool-garments": {"inputs": {"sheep": 3}, "time": 2},
        "pottery": {"inputs": {"clay": 4, "wood": 1}, "time": 2},
    },
}

PROD = {
    "farmhouse": "sheep",
    "pier": "fish",
    "fertilised-fields": "wheat",
    "quarry": "stone",
    "woodlands": "wood",
    "pottery-house": "clay",
}

# Scores / build costs from the specification.
UPGRADES = {
    "farmhouse": {
        "components": {"planks": 3, "thatch": 2},
        "cost": 500, "time": 3, "score": 1000,
        "pre": None,
    },
    "pier": {
        "components": {"planks": 4, "nets": 2},
        "cost": 600, "time": 3, "score": 1000,
        "pre": None,
    },
    "fertilised-fields": {
        "components": {"fencing": 2, "thatch": 2},
        "cost": 500, "time": 3, "score": 1000,
        "pre": None,
    },
    "quarry": {
        "components": {"stone-blocks": 3, "planks": 2},
        "cost": 600, "time": 3, "score": 1000,
        "pre": None,
    },
    "woodlands": {
        "components": {"fencing": 2, "rope": 2},
        "cost": 500, "time": 3, "score": 1000,
        "pre": None,
    },
    "pottery-house": {
        "components": {"bricks": 4, "planks": 2},
        "cost": 700, "time": 3, "score": 1000,
        "pre": None,
    },

    "rec-center": {
        "components": {"planks": 4, "bricks": 3, "rope": 1},
        "cost": 1200, "time": 4, "score": 3000,
        "pre": ("prod", 1),
    },
    "fire-station": {
        "components": {"bricks": 5, "stone-blocks": 3, "rope": 2},
        "cost": 1800, "time": 4, "score": 4000,
        "pre": ("prod", 2),
    },
    "school": {
        "components": {"bricks": 6, "planks": 3, "kiln-glass": 2},
        "cost": 2000, "time": 5, "score": 5000,
        "pre": "rec-center",
    },
    "police-station": {
        "components": {"bricks": 6, "stone-blocks": 4,
                        "iron-fittings": 2},
        "cost": 2200, "time": 5, "score": 5000,
        "pre": "fire-station",
    },
    "library": {
        "components": {"bricks": 5, "planks": 5,
                        "kiln-glass": 2},
        "cost": 2500, "time": 5, "score": 6000,
        "pre": "school",
    },
}

# ============================================================
# HELPERS
# ============================================================

def norm(x):
    return str(x).strip().lower().replace("_", "-")


def load_rules():
    if os.path.exists("resources.json"):
        try:
            with open("resources.json", encoding="utf8") as f:
                r = json.load(f)["constants"]

            out = DEFAULT.copy()

            if "resources" in r:
                for k, v in r["resources"].items():
                    out["resources"][norm(k)] = {
                        "sell_price": v.get("sell_price", 0),
                        "buy_price": v.get("buy_price"),
                    }

            if "components" in r:
                out["components"] = {
                    norm(k): {
                        "inputs": {
                            norm(a): int(b)
                            for a, b in v["inputs"].items()
                        }
                    }
                    for k, v in r["components"].items()
                }

            return out
        except Exception:
            pass

    return DEFAULT


RULES = load_rules()
RES = RULES["resources"]
COMP = RULES["components"]
TOOLS = RULES["tools"]
RECIPES = RULES["recipes"]


def expand(items):
    out = Counter()

    def add(name, q):
        if q <= 0:
            return

        name = norm(name)

        if name not in COMP:
            out[name] += q
            return

        for x, n in COMP[name]["inputs"].items():
            add(x, q * int(n))

    for x, q in items.items():
        add(x, int(q))

    return out


def load_level():
    for f in ("level3.json", "level_3.json", "3.json",
              "3.txt", "input.json"):
        if os.path.exists(f):
            with open(f, encoding="utf8") as h:
                return json.load(h)

    raise FileNotFoundError("Level 3 JSON input not found.")


# ============================================================
# ACTIONS
# ============================================================

class Actions:
    def __init__(self):
        self.a = []

    def add(self, t, **kw):
        d = {"type": t}
        d.update(kw)
        self.a.append(d)

    def travel(self, x, fast=False):
        self.add("travel", destination=x, **({"fast": True} if fast else {}))

    def gather(self):
        self.add("gather")

    def buy(self, x, n):
        if n > 0:
            self.add("buy", item=x, quantity=int(n))

    def sell(self, x, n):
        if n > 0:
            self.add("sell", item=x, quantity=int(n))

    def craft(self, x, n):
        if n > 0:
            self.add("craft", item=x, quantity=int(n))

    def build(self, x):
        self.add("build", upgrade=x)

    def upkeep(self):
        self.add("upkeep")


# ============================================================
# MAP
# ============================================================

class Map:
    def __init__(self, data):
        self.adj = defaultdict(list)

        for r in data["routes"]:
            a, b = r["between"]
            w = int(r["weight"])
            toll = int(r.get("toll", 0))

            for x, y in ((a, b), (b, a)):
                self.adj[x].append({
                    "to": y,
                    "w": w,
                    "toll": toll,
                    "fast": toll > 0,
                })

    def path(self, start, end, boots=False,
             fast=True, loot=None):

        if start == end:
            return {"time": 0, "toll": 0, "nodes": [start],
                    "flags": []}

        pq = [(0, 0, start)]
        best = {start: (0, 0)}
        prev = {}

        while pq:
            t, c, u = heapq.heappop(pq)

            if best[u] != (t, c):
                continue

            if u == end:
                break

            for e in self.adj[u]:
                if e["fast"] and not fast:
                    continue

                nc = c + e["toll"]

                if loot is not None and nc > loot:
                    continue

                nt = t + max(
                    1,
                    e["w"] - (1 if boots else 0)
                )

                v = e["to"]

                if v not in best or (nt, nc) < best[v]:
                    best[v] = (nt, nc)
                    prev[v] = (u, e)
                    heapq.heappush(pq, (nt, nc, v))

        if end not in best:
            return None

        nodes, flags = [], []
        u = end

        while u != start:
            nodes.append(u)
            p, e = prev[u]
            flags.append(e["fast"])
            u = p

        nodes.append(start)
        nodes.reverse()
        flags.reverse()

        return {
            "time": best[end][0],
            "toll": best[end][1],
            "nodes": nodes,
            "flags": flags,
        }


# ============================================================
# STATE + PASSIVE ECONOMY
# ============================================================

class State:
    def __init__(self, data):
        r = data["run"]

        self.tick = 0
        self.total = int(r["total_ticks"])
        self.loot = int(r["starting_enteloot"])
        self.loc = r["starting_town"]

        self.inv = Counter()
        self.up = defaultdict(set)
        self.tools = set()

        self.prod_cycles = defaultdict(int)
        self.loot_cycles = defaultdict(int)


class Economy:
    def __init__(self, data, s):
        self.data = data
        self.s = s

    def prod(self, town, resource):
        t = self.data["towns"][town]
        amount = int(
            t.get("production", {})
             .get("resources", {})
             .get(resource, 0)
        )

        if resource in PROD.values():
            for u, r in PROD.items():
                if r == resource and u in self.s.up[town]:
                    amount *= 2

        return amount

    def loot_amount(self, town):
        t = self.data["towns"][town]
        amount = int(t["enteloot"]["amount"])

        bonus = 0
        if "rec-center" in self.s.up[town]:
            bonus += 20
        if "school" in self.s.up[town]:
            bonus += 50
        if "library" in self.s.up[town]:
            bonus += 50

        return math.floor(amount * (100 + bonus) / 100)

    def loot_rate(self, town):
        rate = int(self.data["towns"][town]["enteloot"]["rate"])

        if "police-station" in self.s.up[town]:
            rate = max(1, rate - 2)

        return rate

    def advance(self, new_tick):
        new_tick = min(new_tick, self.s.total)

        if new_tick <= self.s.tick:
            return

        for town, info in self.data["towns"].items():

            rate = int(
                info.get("production", {}).get("rate", 0)
            )

            if rate > 0:
                cycles = new_tick // rate
                old = self.s.prod_cycles[town]

                if cycles > old:
                    for r in info.get("production", {}).get(
                            "resources", {}):
                        self.s.inv[r] += (
                            cycles - old
                        ) * self.prod(town, r)

                    self.s.prod_cycles[town] = cycles

            rate = self.loot_rate(town)

            if rate > 0:
                cycles = new_tick // rate
                old = self.s.loot_cycles[town]

                if cycles > old:
                    self.s.loot += (
                        cycles - old
                    ) * self.loot_amount(town)

                    self.s.loot_cycles[town] = cycles

        self.s.tick = new_tick


# ============================================================
# ROUTE ENGINE
# ============================================================

class Engine:
    def __init__(self, data):
        self.data = data
        self.s = State(data)
        self.e = Economy(data, self.s)
        self.m = Map(data)
        self.a = Actions()

        self.nodes = defaultdict(list)

        for n, info in data["nodes"].items():
            r = norm(info.get("resource", ""))
            if r:
                self.nodes[r].append(n)

    def boots(self):
        return "boots" in self.s.tools

    def pickaxe(self):
        return "pickaxe" in self.s.tools

    def move(self, path):
        if not path:
            return False

        for i in range(len(path["nodes"]) - 1):
            u = path["nodes"][i]
            v = path["nodes"][i + 1]
            fast = path["flags"][i]

            edge = next(
                (
                    e for e in self.m.adj[u]
                    if e["to"] == v
                    and e["fast"] == fast
                ),
                None
            )

            if not edge:
                return False

            dt = max(
                1,
                edge["w"] - (1 if self.boots() else 0)
            )

            if self.s.tick + dt > self.s.total:
                return False

            if self.s.loot < edge["toll"]:
                return False

            self.s.loot -= edge["toll"]
            self.a.travel(v, fast)
            self.e.advance(self.s.tick + dt)
            self.s.loc = v

        return True

    # --------------------------------------------------------
    # WHOLE-ROUTE NODE SELECTION
    # --------------------------------------------------------

    def best_node(self, resource, quantity, target=None):
        best = None

        for node in self.nodes[resource]:
            p = self.m.path(
                self.s.loc, node,
                self.boots(),
                fast=True,
                loot=self.s.loot
            )

            if not p:
                continue

            info = self.data["nodes"][node]
            y = int(info["yield"])
            gt = int(info["gather-time"])

            if self.pickaxe():
                gt = max(1, gt - 1)

            n = max(1, math.ceil(quantity / y))

            back = self.m.path(
                node,
                target or self.s.loc,
                self.boots(),
                fast=True,
                loot=self.s.loot
            )

            if not back:
                continue

            total = p["time"] + n * gt + back["time"]

            # Prefer fewer ticks, then fewer tolls, then higher yield.
            key = (
                total,
                p["toll"] + back["toll"],
                -y
            )

            if best is None or key < best[0]:
                best = (key, node, p, y, gt)

        return best

    def gather(self, resource, quantity, destination=None):
        quantity = max(0, int(quantity))

        while self.s.inv[resource] < quantity:
            need = quantity - self.s.inv[resource]

            choice = self.best_node(
                resource,
                need,
                destination
            )

            if not choice:
                return False

            _, node, path, y, gt = choice

            if not self.move(path):
                return False

            # IMPORTANT:
            # Stay at the node and gather repeatedly.
            # This is one of the largest action/tick savings
            # over the old planner.
            n = max(1, math.ceil(need / y))

            for _ in range(n):
                if self.s.tick + gt > self.s.total:
                    return False

                self.a.gather()
                self.e.advance(self.s.tick + gt)
                self.s.inv[resource] += y

        return True

    # --------------------------------------------------------
    # BUY
    # --------------------------------------------------------

    def buy(self, resource, quantity):
        if resource == "ore":
            return False

        price = RES[resource]["buy_price"]

        if price is None:
            return False

        best = None

        for town, info in self.data["towns"].items():
            if resource not in info.get(
                    "production", {}).get("resources", {}):
                continue

            p = self.m.path(
                self.s.loc,
                town,
                self.boots(),
                fast=True,
                loot=self.s.loot
            )

            if not p:
                continue

            key = (p["time"], p["toll"], town)

            if best is None or key < best[0]:
                best = (key, town, p)

        if not best:
            return False

        _, town, path = best

        if not self.move(path):
            return False

        cost = price * quantity

        if self.s.loot < cost:
            return False

        if self.s.tick + 1 > self.s.total:
            return False

        self.s.loot -= cost
        self.a.buy(resource, quantity)
        self.e.advance(self.s.tick + 1)
        self.s.inv[resource] += quantity

        return True

    # --------------------------------------------------------
    # CRAFTING
    # --------------------------------------------------------

    def craft_time(self):
        if self.s.loc in self.data["towns"]:
            if "crafting" in self.data["towns"][
                    self.s.loc].get("affinities", []):
                return 1

        return 2

    def craft_component(self, item, quantity):
        if item not in COMP or quantity <= 0:
            return False

        recipe = COMP[item]["inputs"]

        # Recursively make dependencies.
        for x, n in recipe.items():
            need = n * quantity

            if x in COMP and self.s.inv[x] < need:
                if not self.craft_component(
                    x,
                    need - self.s.inv[x]
                ):
                    return False

        if any(
            self.s.inv[x] < n * quantity
            for x, n in recipe.items()
        ):
            return False

        dt = quantity * self.craft_time()

        if self.s.tick + dt > self.s.total:
            return False

        for x, n in recipe.items():
            self.s.inv[x] -= n * quantity

        self.a.craft(item, quantity)
        self.e.advance(self.s.tick + dt)
        self.s.inv[item] += quantity

        return True

    # --------------------------------------------------------
    # TOOL PLANNING
    # --------------------------------------------------------

    def make_tools(self):
        # Pickaxe saves gather ticks.
        # Boots save travel ticks.
        # Estimate based on map size and node count.
        nodes = len(self.data["nodes"])
        towns = len(self.data["towns"])

        order = (
            ["pickaxe", "boots"]
            if nodes > towns
            else ["boots", "pickaxe"]
        )

        for tool in order:
            if tool in self.s.tools:
                continue

            raw = expand(TOOLS[tool]["inputs"])

            for r, q in raw.items():
                missing = q - self.s.inv[r]

                if missing <= 0:
                    continue

                # Ore must always be gathered.
                if r == "ore":
                    if not self.gather(r, missing):
                        break
                else:
                    # Buy only when travel is much cheaper than
                    # a resource detour.
                    if not self.gather(r, missing):
                        self.buy(r, missing)

            # Move to a crafting town.
            if self.s.loc not in self.data["towns"] or \
               "crafting" not in self.data["towns"][
                   self.s.loc].get("affinities", []):

                candidates = []

                for town, info in self.data["towns"].items():
                    if "crafting" not in info.get(
                            "affinities", []):
                        continue

                    p = self.m.path(
                        self.s.loc, town,
                        self.boots(),
                        fast=True,
                        loot=self.s.loot
                    )

                    if p:
                        candidates.append((p["time"], town, p))

                if candidates:
                    _, _, p = min(candidates)
                    self.move(p)

            inp = TOOLS[tool]["inputs"]

            if all(self.s.inv[x] >= q for x, q in inp.items()):
                dt = self.craft_time()

                if self.s.tick + dt <= self.s.total:
                    for x, q in inp.items():
                        self.s.inv[x] -= q

                    self.a.craft(tool, 1)
                    self.e.advance(self.s.tick + dt)
                    self.s.tools.add(tool)

    # --------------------------------------------------------
    # UPGRADE PREREQUISITES
    # --------------------------------------------------------

    def can_pre(self, town, upgrade):
        p = UPGRADES[upgrade]["pre"]
        ups = self.s.up[town]

        if p is None:
            return True

        if isinstance(p, tuple):
            return len(ups & set(PROD)) >= p[1]

        return p in ups

    # --------------------------------------------------------
    # ROUTE-WIDE BOM
    # --------------------------------------------------------

    def component_plan(self, upgrade):
        """
        Expand the COMPLETE upgrade BOM rather than acquiring
        resources one at a time.
        """
        return expand(
            UPGRADES[upgrade]["components"]
        )

    def missing_raw(self, upgrade):
        raw = self.component_plan(upgrade)

        return Counter({
            r: q - self.s.inv[r]
            for r, q in raw.items()
            if q > self.s.inv[r]
        })

    # --------------------------------------------------------
    # UPGRADE VALUE
    # --------------------------------------------------------

    def upgrade_value(self, town, upgrade):
        info = UPGRADES[upgrade]

        remaining = self.s.total - self.s.tick

        # Direct score.
        value = info["score"] * 10

        # Civic chain is extremely valuable.
        if upgrade in PROD:
            value += 35000

            # Production itself compounds passive income.
            r = PROD[upgrade]
            base = int(
                self.data["towns"][town]
                .get("production", {})
                .get("resources", {})
                .get(r, 0)
            )
            rate = int(
                self.data["towns"][town]
                .get("production", {})
                .get("rate", 999)
            )

            if rate:
                value += (
                    remaining // rate
                    * base
                    * RES.get(r, {}).get("sell_price", 1)
                    * 3
                )

        elif upgrade == "rec-center":
            value += 30000
        elif upgrade == "fire-station":
            value += 35000
        elif upgrade == "school":
            value += 45000
        elif upgrade == "police-station":
            value += 40000
        elif upgrade == "library":
            value += 55000

        # Reward spreading upgrades across towns.
        if not self.s.up[town]:
            value *= 1.10

        # Prefer upgrades whose resources are already mostly present.
        missing = self.missing_raw(upgrade)
        value -= sum(missing.values()) * 100

        return value

    def candidates(self):
        out = []

        for town in self.data["towns"]:
            for upgrade in UPGRADES:

                if upgrade in self.s.up[town]:
                    continue

                if not self.can_pre(town, upgrade):
                    continue

                info = UPGRADES[upgrade]

                # Need enough time for construction itself.
                if self.s.tick + info["time"] > self.s.total:
                    continue

                v = self.upgrade_value(town, upgrade)

                out.append((v, town, upgrade))

        return sorted(
            out,
            key=lambda x: (-x[0], x[1], x[2])
        )

    # --------------------------------------------------------
    # PREPARE ENTIRE BOM
    # --------------------------------------------------------

    def acquire_bom(self, raw):
        """
        Acquire a complete batch of resources for the chosen
        upgrade. This is the major route-level optimisation.
        """

        # First use passive inventory.
        raw = Counter({
            r: max(0, q - self.s.inv[r])
            for r, q in raw.items()
        })

        # Rank by resource deficit so large shared dependencies
        # are collected together.
        for r, q in sorted(
            raw.items(),
            key=lambda x: (-x[1], x[0])
        ):
            if q <= 0:
                continue

            if r == "ore":
                if not self.gather(r, q):
                    return False
                continue

            # Compare gathering with buying.
            node = self.best_node(r, q)

            node_time = None
            if node:
                node_time = node[0][0]

            # Cheapest producer town.
            town_time = None

            for town, info in self.data["towns"].items():
                if r not in info.get(
                        "production", {}).get("resources", {}):
                    continue

                p = self.m.path(
                    self.s.loc,
                    town,
                    self.boots(),
                    fast=True,
                    loot=self.s.loot
                )

                if p:
                    t = p["time"] + 1
                    if town_time is None or t < town_time:
                        town_time = t

            buy_price = RES[r]["buy_price"]

            # Buy when it materially saves time and is affordable.
            if (
                town_time is not None
                and buy_price is not None
                and self.s.loot >= buy_price * q
                and (
                    node_time is None
                    or town_time + 2 < node_time
                )
            ):
                if not self.buy(r, q):
                    if not self.gather(r, q):
                        return False
            else:
                if not self.gather(r, q):
                    if not self.buy(r, q):
                        return False

        return True

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    def build(self, town, upgrade):
        info = UPGRADES[upgrade]

        if self.s.up[town].__contains__(upgrade):
            return False

        if not self.can_pre(town, upgrade):
            return False

        if self.s.loot < info["cost"]:
            return False

        if any(
            self.s.inv[x] < q
            for x, q in info["components"].items()
        ):
            return False

        if self.s.tick + info["time"] > self.s.total:
            return False

        if self.s.loc != town:
            p = self.m.path(
                self.s.loc,
                town,
                self.boots(),
                fast=True,
                loot=self.s.loot
            )

            if not p or not self.move(p):
                return False

        # Revalidate after travel.
        if self.s.loot < info["cost"]:
            return False

        if any(
            self.s.inv[x] < q
            for x, q in info["components"].items()
        ):
            return False

        for x, q in info["components"].items():
            self.s.inv[x] -= q

        self.s.loot -= info["cost"]

        self.a.build(upgrade)
        self.e.advance(self.s.tick + info["time"])
        self.s.up[town].add(upgrade)

        return True

    # --------------------------------------------------------
    # PROFITABLE SURPLUS
    # --------------------------------------------------------

    def sell_surplus(self):
        """
        Sell in batches. A single sell action can contain a large
        quantity, so selling one unit at a time wastes action
        opportunities without improving the economy.
        """

        sellable = [
            (x, q)
            for x, q in self.s.inv.items()
            if q > 0 and x not in COMP
            and x not in TOOLS
        ]

        if not sellable:
            return False

        # Prefer highest-value raw resource.
        sellable.sort(
            key=lambda x: (
                -RES.get(x[0], {}).get("sell_price", 0),
                x[0]
            )
        )

        item, quantity = sellable[0]

        # Find best selling town for crafted goods.
        if item in RECIPES:
            towns = []

            for town, info in self.data["towns"].items():
                price = int(
                    info.get("item-rates", {}).get(item, 0)
                )

                if price:
                    p = self.m.path(
                        self.s.loc,
                        town,
                        self.boots(),
                        fast=True,
                        loot=self.s.loot
                    )

                    if p:
                        towns.append(
                            (-price, p["time"], town, p)
                        )

            if towns:
                _, _, _, p = min(towns)
                self.move(p)

                price = -min(towns)[0]

            else:
                price = 0
        else:
            price = RES[item]["sell_price"]

        if self.s.tick + 1 > self.s.total:
            return False

        self.a.sell(item, quantity)
        self.s.inv[item] -= quantity
        self.e.advance(self.s.tick + 1)
        self.s.loot += price * quantity

        return True

    # --------------------------------------------------------
    # CRAFT SURPLUS
    # --------------------------------------------------------

    def craft_trade(self):
        best = None

        for item, rec in RECIPES.items():

            q = min(
                self.s.inv[r] // n
                for r, n in rec["inputs"].items()
            )

            if q <= 0:
                continue

            prices = [
                int(
                    info.get("item-rates", {}).get(item, 0)
                )
                for info in self.data["towns"].values()
            ]

            price = max(prices or [0])

            raw_value = sum(
                n * RES[r]["sell_price"]
                for r, n in rec["inputs"].items()
            )

            profit = price - raw_value

            if profit <= 0:
                continue

            score = profit / self.craft_time()

            candidate = (score, item, q)

            if best is None or candidate > best:
                best = candidate

        if not best:
            return False

        _, item, q = best

        # Keep construction flexibility.
        q = min(q, 30)

        rec = RECIPES[item]

        dt = q * self.craft_time()

        if self.s.tick + dt > self.s.total:
            return False

        for r, n in rec["inputs"].items():
            self.s.inv[r] -= n * q

        self.a.craft(item, q)
        self.e.advance(self.s.tick + dt)
        self.s.inv[item] += q

        return self.sell_surplus()

    # ========================================================
    # MAIN STRATEGY
    # ========================================================

    def run(self):

        # ----------------------------------------------------
        # 1. Tools first when their compounding saving is useful
        # ----------------------------------------------------
        self.make_tools()

        # ----------------------------------------------------
        # 2. Re-plan the ENTIRE route after every investment.
        # ----------------------------------------------------
        while self.s.tick < self.s.total:

            progress = False

            # Highest-value feasible infrastructure first.
            for _, town, upgrade in self.candidates():

                info = UPGRADES[upgrade]

                if self.s.loot < info["cost"]:
                    continue

                raw = self.component_plan(upgrade)

                if not self.acquire_bom(raw):
                    continue

                # Craft the COMPLETE component BOM at once.
                if self.s.loc not in self.data["towns"] or \
                   "crafting" not in self.data["towns"][
                       self.s.loc].get("affinities", []):

                    choices = []

                    for t, inf in self.data["towns"].items():
                        if "crafting" not in inf.get(
                                "affinities", []):
                            continue

                        p = self.m.path(
                            self.s.loc,
                            t,
                            self.boots(),
                            fast=True,
                            loot=self.s.loot
                        )

                        if p:
                            choices.append((p["time"], t, p))

                    if choices:
                        _, _, p = min(choices)
                        self.move(p)

                ok = True

                # Dependency-aware repeated pass.
                remaining = Counter(
                    info["components"]
                )

                guard = 0

                while remaining and guard < 100:
                    guard += 1
                    changed = False

                    for component in list(remaining):

                        q = remaining[component]

                        if self.s.inv[component] >= q:
                            del remaining[component]
                            changed = True
                            continue

                        before = self.s.inv[component]

                        if self.craft_component(component, q):
                            if self.s.inv[component] > before:
                                del remaining[component]
                                changed = True

                    if not changed:
                        break

                if remaining:
                    ok = False

                if ok and self.build(town, upgrade):
                    progress = True
                    break

            if progress:
                continue

            # ------------------------------------------------
            # 3. If infrastructure is temporarily blocked,
            #    generate Enteloot from profitable surplus.
            # ------------------------------------------------
            if self.craft_trade():
                continue

            if self.sell_surplus():
                continue

            # ------------------------------------------------
            # 4. Instead of stopping early, deliberately work
            #    toward the best remaining upgrade.
            # ------------------------------------------------
            candidates = self.candidates()

            if not candidates:
                break

            acquired = False

            for _, town, upgrade in candidates[:8]:

                raw = self.missing_raw(upgrade)

                if not raw:
                    continue

                # Acquire the largest shared deficit.
                r, q = max(
                    raw.items(),
                    key=lambda x: (x[1], x[0])
                )

                q = min(q, 50)

                if r == "ore":
                    ok = self.gather(r, q)
                else:
                    ok = self.gather(r, q)

                    if not ok:
                        ok = self.buy(r, q)

                if ok:
                    acquired = True
                    break

            if acquired:
                continue

            # No productive operation remains.
            break

        # ----------------------------------------------------
        # 5. Endgame:
        # invest whenever possible; otherwise sell remaining
        # inventory in large batches.
        # ----------------------------------------------------
        while self.s.tick < self.s.total:

            did = False

            for _, town, upgrade in self.candidates():
                info = UPGRADES[upgrade]

                if self.s.loot < info["cost"]:
                    continue

                raw = self.component_plan(upgrade)

                if self.acquire_bom(raw):
                    remaining = Counter(info["components"])

                    for c in list(remaining):
                        q = remaining[c]

                        if self.s.inv[c] < q:
                            break

                        if not self.craft_component(c, q):
                            break
                    else:
                        if self.build(town, upgrade):
                            did = True
                            break

            if did:
                continue

            if self.sell_surplus():
                continue

            break

        return self.a.a


# ============================================================
# VALIDATION
# ============================================================

def validate(data, actions):
    errors = []
    m = Map(data)
    loc = data["run"]["starting_town"]

    for i, a in enumerate(actions):

        if not isinstance(a, dict):
            errors.append((i, "not an object"))
            continue

        t = a.get("type")

        if t == "travel":
            dst = a.get("destination")
            fast = bool(a.get("fast", False))

            edge = next(
                (
                    e for e in m.adj[loc]
                    if e["to"] == dst
                    and e["fast"] == fast
                ),
                None
            )

            if not edge:
                errors.append(
                    (i, f"invalid route {loc}->{dst}")
                )
            else:
                loc = dst

        elif t in {
            "gather", "upkeep"
        }:
            pass

        elif t in {
            "buy", "sell", "craft"
        }:
            if "item" not in a or "quantity" not in a:
                errors.append((i, f"{t} missing fields"))

        elif t == "build":
            if "upgrade" not in a:
                errors.append((i, "build missing upgrade"))

        else:
            errors.append((i, f"unknown action {t}"))

    return errors


# ============================================================
# OUTPUT
# ============================================================

def main():
    data = load_level()

    game = Engine(data)
    actions = game.run()

    errors = validate(data, actions)

    with open(
        "level3_submission.txt",
        "w",
        encoding="utf8"
    ) as f:
        json.dump(
            {"actions": actions},
            f,
            indent=2
        )

    s = game.s

    print("=" * 60)
    print("AGE OF ENTELAND - LEVEL 3 ROUTE OPTIMISER")
    print("=" * 60)
    print(f"Ticks:     {s.tick}/{s.total}")
    print(f"Actions:   {len(actions)}")
    print(f"Enteloot:  {s.loot}")
    print(f"Tools:     {', '.join(sorted(s.tools)) or 'none'}")

    upgrades = sum(
        len(x)
        for x in s.up.values()
    )

    print(f"Upgrades:  {upgrades}")

    for town in sorted(s.up):
        if s.up[town]:
            print(
                f"  {town}: "
                + ", ".join(sorted(s.up[town]))
            )

    print(
        "Validation:",
        "PASS" if not errors
        else f"{len(errors)} warnings"
    )

    if errors:
        for i, e in errors[:10]:
            print(f"  {i}: {e}")

    print("Written: level3_submission.txt")


if __name__ == "__main__":
    main()