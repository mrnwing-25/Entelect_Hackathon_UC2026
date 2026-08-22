import json
import math
import heapq
import sys
from collections import Counter, defaultdict

# Age of Enteland Level 2 constants from the specification.
RAW = {
    "wheat": {"sell": 2, "buy": 4},
    "wood": {"sell": 3, "buy": 5},
    "stone": {"sell": 3, "buy": 5},
    "clay": {"sell": 4, "buy": 6},
    "fish": {"sell": 4, "buy": 6},
    "sheep": {"sell": 5, "buy": 8},
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

    "planks": {"inputs": {"wood": 2}, "sellable": False},
    "thatch": {"inputs": {"wheat": 2}, "sellable": False},
    "stone-blocks": {"inputs": {"stone": 3}, "sellable": False},
    "mortar": {"inputs": {"clay": 1, "stone": 1}, "sellable": False},
    "bricks": {"inputs": {"clay": 2, "mortar": 1}, "sellable": False},
    "rope": {"inputs": {"sheep": 2}, "sellable": False},
    "fencing": {"inputs": {"wood": 2, "rope": 1}, "sellable": False},
    "kiln-glass": {"inputs": {"clay": 2, "wood": 2}, "sellable": False},
    "nets": {"inputs": {"rope": 1, "fencing": 1}, "sellable": False},
}

# Score values and mechanics are taken from the Level 2 specification.
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


def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_graph(data):
    graph = defaultdict(list)
    for route in data["routes"]:
        if route.get("toll", 0) != 0:
            continue
        u, v = route["between"]
        graph[u].append((v, route["weight"]))
        graph[v].append((u, route["weight"]))
    return graph


def shortest_paths(graph):
    paths = {}
    for start in graph:
        dist = {start: 0}
        prev = {}
        pq = [(0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]:
                continue
            for v, w in graph[u]:
                nd = d + w
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        for target in dist:
            cur = target
            path = []
            while cur != start:
                path.append(cur)
                cur = prev[cur]
            path.append(start)
            path.reverse()
            paths[(start, target)] = (dist[target], path)
    return paths


def raw_requirements_for_upgrade(upgrade):
    result = Counter()
    for component, qty in UPGRADES[upgrade]["components"].items():
        result.update(raw_requirements(component, qty))
    return result


def raw_requirements(item, qty=1, memo=None):
    if memo is None:
        memo = {}
    key = (item, qty)
    if key in memo:
        return Counter(memo[key])
    if item in RAW:
        result = Counter({item: qty})
    else:
        result = Counter()
        for child, amount in RECIPES[item]["inputs"].items():
            result.update(raw_requirements(child, amount * qty, memo))
    memo[key] = dict(result)
    return result


def expand_components(components):
    """Return every required component, including recursively required ones."""
    needed = Counter()

    def expand(item, qty):
        if item in RAW:
            return
        needed[item] += qty
        for child, amount in RECIPES[item]["inputs"].items():
            if child in RECIPES:
                expand(child, amount * qty)

    for item, qty in components.items():
        expand(item, qty)

    order = [
        "rope", "fencing", "nets", "thatch", "planks",
        "mortar", "bricks", "stone-blocks", "kiln-glass"
    ]
    return [(item, needed[item]) for item in order if needed[item] > 0]


def choose_upgrade_plan(data):
    return {town:["farmhouse","fertilised-fields","rec-center","school","library","fire-station"] for town in data["towns"]}

def choose_town_order(data, paths):
    # This order was selected by deterministic simulation of the supplied
    # Level-2 input.  It keeps the highest-value civic towns early while
    # exploiting the rounding behaviour of the passive Enteloot cycles.
    return [
        "Ixtal", "Noxus", "Freljord", "Ionia", "Piltover",
        "Shurima", "Demacia", "Zaun", "Targon", "Bilgewater",
    ]

class Simulator:
    """
    Lightweight deterministic mirror of the Level 2 execution rules.

    The important detail is that passive production is applied tick-by-tick
    using the upgrades that are active during that tick. This prevents the
    common mistake of retroactively applying a newly-built upgrade to earlier
    production.
    """

    def __init__(self, data):
        self.data = data
        self.towns = data["towns"]
        self.total_ticks = data["run"]["total_ticks"]
        self.tick = 0
        self.location = data["run"]["starting_town"]
        self.enteloot = data["run"]["starting_enteloot"]
        self.inventory = Counter()
        self.built = defaultdict(set)
        self.actions = []

    def _passive_tick(self, t):
        for town, info in self.towns.items():
            if t % info["production"]["rate"] == 0:
                for resource, amount in info["production"]["resources"].items():
                    multiplier = 1
                    if any(
                        u in self.built[town]
                        and UPGRADES[u].get("boost") == resource
                        for u in PRODUCTION_UPGRADES
                    ):
                        multiplier = 2
                    self.inventory[resource] += amount * multiplier

            if t % info["enteloot"]["rate"] == 0:
                amount = info["enteloot"]["amount"]
                bonus = 0.0
                if "rec-center" in self.built[town]:
                    bonus += 0.20
                if "school" in self.built[town]:
                    bonus += 0.50
                if "library" in self.built[town]:
                    bonus += 0.50
                self.enteloot += math.floor(amount * (1.0 + bonus))

    def advance(self, ticks):
        if ticks < 0:
            raise ValueError("negative time")
        target = min(self.total_ticks, self.tick + ticks)
        for t in range(self.tick + 1, target + 1):
            self._passive_tick(t)
        self.tick = target

    def travel(self, target, paths):
        if target == self.location:
            return
        _, path = paths[(self.location, target)]
        for vertex in path[1:]:
            w = paths[(self.location, vertex)][0]
            self.advance(w)
            self.actions.append({"type": "travel", "destination": vertex})
            self.location = vertex

    def gather(self, quantity):
        node = self.data["nodes"][self.location]
        for _ in range(quantity):
            self.advance(node["gather-time"])
            self.inventory[node["resource"]] += node["yield"]
            self.actions.append({"type": "gather"})

    def craft(self, item, quantity):
        if quantity <= 0:
            return False
        recipe = RECIPES[item]
        if any(
            self.inventory[k] < n * quantity
            for k, n in recipe["inputs"].items()
        ):
            return False

        for k, n in recipe["inputs"].items():
            self.inventory[k] -= n * quantity

        craft_time = 1 if "crafting" in self.towns[self.location].get("affinities", []) else 2
        self.advance(craft_time * quantity)
        self.inventory[item] += quantity
        self.actions.append({
            "type": "craft",
            "item": item,
            "quantity": quantity,
        })
        return True

    def sell(self, item, quantity):
        if quantity <= 0 or self.inventory[item] < quantity:
            return False
        if item not in self.towns[self.location]["item-rates"]:
            return False
        self.inventory[item] -= quantity
        self.enteloot += self.towns[self.location]["item-rates"][item] * quantity
        self.advance(1)
        self.actions.append({
            "type": "sell",
            "item": item,
            "quantity": quantity,
        })
        return True

    def can_build(self, town, upgrade):
        if upgrade in self.built[town]:
            return False

        u = UPGRADES[upgrade]
        pre = u["prerequisite"]

        if pre == "any_1_prod":
            if not any(
                UPGRADES[x]["kind"] == "production"
                for x in self.built[town]
            ):
                return False
        elif pre == "any_2_prod":
            if sum(
                UPGRADES[x]["kind"] == "production"
                for x in self.built[town]
            ) < 2:
                return False
        elif pre and pre not in self.built[town]:
            return False

        if self.enteloot < u["cost"]:
            return False

        return all(
            self.inventory[c] >= n
            for c, n in u["components"].items()
        )

    def build(self, town, upgrade):
        if self.location != town or not self.can_build(town, upgrade):
            return False

        u = UPGRADES[upgrade]

        for c, n in u["components"].items():
            self.inventory[c] -= n

        self.enteloot -= u["cost"]
        self.advance(u["time"])
        self.built[town].add(upgrade)
        self.actions.append({"type": "build", "upgrade": upgrade})
        return True


def gather_raw_materials(sim, data, paths, raw_needed):
    """
    Gather the genuinely scarce raw materials.

    Town trickle supplies wheat/sheep/stone over time. Wood is never produced
    by a town, so all required wood must be gathered. Clay is slow enough on
    this level that gathering a controlled reserve saves hundreds of ticks.
    A modest stone reserve prevents the component phase from having to wait
    for the slow stone trickle.
    """
    # Best nodes for this exact map are selected dynamically by yield/travel.
    targets = {
        "wood": raw_needed["wood"],
        "clay": max(0, raw_needed["clay"] - 60),
        "stone": max(0, raw_needed["stone"] - 120),
    }

    current = sim.location

    for resource in ("stone", "wood", "clay"):
        amount = targets[resource]
        if amount <= 0:
            continue

        candidates = []
        for node, info in data["nodes"].items():
            if info["resource"] != resource:
                continue
            if (current, node) not in paths:
                continue

            dist = paths[(current, node)][0]
            # Prefer high yield, but account for the one-time travel.
            batches = math.ceil(amount / info["yield"])
            score = dist * 2 + batches * info["gather-time"]
            candidates.append((score, dist, -info["yield"], node))

        if not candidates:
            raise RuntimeError(f"No gathering node for {resource}")

        _, _, _, node = min(candidates)
        sim.travel(node, paths)
        info = data["nodes"][node]
        batches = math.ceil(amount / info["yield"])
        sim.gather(batches)
        current = node

    # Construction workshop: Ixtal has crafting affinity.
    sim.travel("Ixtal", paths)


def craft_all_components(sim, components):
    for item, quantity in expand_components(components):
        if not sim.craft(item, quantity):
            raise RuntimeError(
                f"Unable to craft {item} x{quantity} at tick {sim.tick}; "
                f"missing resources."
            )


def finance_at_ixtal(sim, required_enteloot, paths):
    """
    Raise only enough Enteloot for the next construction target.

    Fish-n-chips is the key Level-2 financing good here:
      - one wheat + two fish
      - Ixtal pays 49, the best Level-2 rate in this input
      - both crafting and selling happen quickly at the affinity/sale town
      - it consumes no wood, preserving wood for construction.

    Wheat is the limiting input and is passively produced. If a rare shortage
    occurs, the function gathers wheat from the nearest good node rather than
    emitting invalid actions.
    """
    if sim.enteloot >= required_enteloot:
        return

    if sim.location != "Ixtal":
        sim.travel("Ixtal", paths)

    price = sim.towns["Ixtal"]["item-rates"]["fish-n-chips"]
    deficit = required_enteloot - sim.enteloot

    # Craft only what is currently financeable, then reassess after passive
    # production has advanced the clock.
    while sim.enteloot < required_enteloot and sim.tick < sim.total_ticks:
        need = math.ceil((required_enteloot - sim.enteloot) / price)
        available = min(
            sim.inventory["wheat"],
            sim.inventory["fish"] // 2,
        )
        qty = min(need, available)

        if qty > 0:
            if not sim.craft("fish-n-chips", qty):
                raise RuntimeError("Fish-n-chips craft unexpectedly failed")
            if not sim.sell("fish-n-chips", qty):
                raise RuntimeError("Fish-n-chips sale unexpectedly failed")
            continue

        # If inventory is temporarily short on wheat/fish, gather wheat from
        # the best node. This is a fallback; normal Level-2 input reaches the
        # target through passive production.
        candidates = []
        for node, info in sim.data["nodes"].items():
            if info["resource"] != "wheat":
                continue
            dist = paths[(sim.location, node)][0]
            candidates.append(
                (dist * 2 + 100 / info["yield"], node)
            )
        if not candidates:
            raise RuntimeError("Cannot finance construction: no wheat source")

        _, node = min(candidates)
        sim.travel(node, paths)
        sim.gather(1)
        sim.travel("Ixtal", paths)

        if sim.tick >= sim.total_ticks:
            break



def liquidate_remaining_time(sim, data, paths):
    """
    Convert the remaining clock into additional final-state Enteloot.

    Every batch is sized so the craft + travel + sale + return all fit before
    tick 5000. This deliberately avoids creating goods that cannot be sold
    before the run ends.
    """
    if sim.tick >= sim.total_ticks:
        return

    sale_towns = {
        "fish-n-chips": "Ixtal",
        "wool-garments": "Freljord",
        "stone-works": "Zaun",
        "roof-tiles": "Noxus",
    }

    sim.travel("Ixtal", paths)

    while sim.tick < sim.total_ticks:
        remaining = sim.total_ticks - sim.tick
        choices = []

        # Fish-n-chips has no round-trip movement cost because Ixtal both
        # crafts it and pays the best rate.
        fish_qty = min(sim.inventory["wheat"], sim.inventory["fish"] // 2)
        if fish_qty > 0 and remaining >= 2:
            fish_qty = min(fish_qty, remaining - 1)
            if fish_qty > 0:
                choices.append((49.0, fish_qty, "fish-n-chips", 2))

        # Other goods are worth the travel because their sale prices are
        # substantially higher. Their round-trip costs are amortised over
        # large batches.
        for item, denom, resource_qty, sale_price, town in [
            ("wool-garments", 3, sim.inventory["sheep"], 51, "Freljord"),
            ("stone-works", 5, sim.inventory["stone"], 59, "Zaun"),
            ("roof-tiles", None, None, 69, "Noxus"),
        ]:
            if item == "wool-garments":
                qty = resource_qty // denom
            elif item == "stone-works":
                qty = resource_qty // denom
            else:
                qty = min(sim.inventory["clay"] // 3,
                          sim.inventory["stone"] // 2)

            if qty <= 0:
                continue

            one_way = paths[("Ixtal", town)][0]
            full_cost = 2 * one_way + 1 + 1  # craft + travel + sell + return
            if remaining <= full_cost:
                continue

            qty = min(qty, remaining - full_cost)
            if qty <= 0:
                continue

            # Score the batch by Enteloot per tick including movement.
            value = sale_price * qty
            efficiency = value / (qty + full_cost)
            choices.append((efficiency, qty, item, full_cost))

        if not choices:
            break

        # Prefer the most valuable efficient batch. For very large batches,
        # the fixed travel overhead becomes negligible.
        _, qty, item, full_cost = max(
            choices,
            key=lambda x: (x[0], x[1], x[2])
        )

        destination = sale_towns[item]

        if not sim.craft(item, qty):
            break

        sim.travel(destination, paths)
        if sim.tick >= sim.total_ticks:
            # The batch was guaranteed to fit, so this is defensive only.
            break

        if not sim.sell(item, qty):
            break

        if destination != "Ixtal":
            sim.travel("Ixtal", paths)

def solve(data):
    paths = shortest_paths(build_graph(data))
    plan = choose_upgrade_plan(data)

    # Compute exact raw requirements for the complete 60-upgrade portfolio.
    raw_needed = Counter()
    components = Counter()

    for upgrades in plan.values():
        for upgrade in upgrades:
            raw_needed.update(raw_requirements_for_upgrade(upgrade))
            for component, qty in UPGRADES[upgrade]["components"].items():
                components[component] += qty

    sim = Simulator(data)

    # Gather scarce construction inputs and move to the affinity workshop.
    gather_raw_materials(sim, data, paths, raw_needed)

    # Craft the entire dependency tree once. All components are then globally
    # available in inventory for the later town builds.
    craft_all_components(sim, components)

    town_order = choose_town_order(data, paths)

    # Build one complete town at a time. Financing is done just before each
    # town, so Enteloot is invested quickly rather than unnecessarily hoarded.
    for town in town_order:
        if sim.tick >= sim.total_ticks:
            break

        town_cost = sum(UPGRADES[u]["cost"] for u in plan[town])
        finance_at_ixtal(sim, town_cost, paths)

        if sim.enteloot < town_cost:
            # No valid way to fund this town within the remaining tick budget.
            break

        sim.travel(town, paths)

        for upgrade in plan[town]:
            if not sim.build(town, upgrade):
                raise RuntimeError(
                    f"Build failed: {town}/{upgrade} at tick {sim.tick}, "
                    f"Enteloot={sim.enteloot}"
                )

    liquidate_remaining_time(sim, data, paths)

    return sim.actions, sim


def validate_submission(actions):
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")

    for action in actions:
        if not isinstance(action, dict) or "type" not in action:
            raise ValueError(f"Malformed action: {action}")

        kind = action["type"]

        if kind == "travel":
            if not isinstance(action.get("destination"), str):
                raise ValueError(f"Malformed travel action: {action}")
        elif kind in ("gather", "upkeep"):
            pass
        elif kind in ("buy", "sell", "craft"):
            if (
                not isinstance(action.get("item"), str)
                or not isinstance(action.get("quantity"), int)
                or action["quantity"] <= 0
            ):
                raise ValueError(f"Malformed {kind} action: {action}")
        elif kind == "build":
            if not isinstance(action.get("upgrade"), str):
                raise ValueError(f"Malformed build action: {action}")
        else:
            raise ValueError(f"Unknown action type: {kind}")


def write_submission(actions, filename):
    validate_submission(actions)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"actions": actions}, f, indent=2)


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "2.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "submission.txt"

    data = load_input(input_file)
    actions, sim = solve(data)

    write_submission(actions, output_file)

    built_count = sum(len(v) for v in sim.built.values())
    infrastructure = sum(
        UPGRADES[u]["score"]
        for upgrades in sim.built.values()
        for u in upgrades
    )

    print("Level 2 optimisation v5")
    print(f"Input: {input_file}")
    print(f"Actions: {len(actions)}")
    print(f"Final estimated tick: {sim.tick}/{sim.total_ticks}")
    print(f"Upgrades actually simulated: {built_count}/60")
    print(f"Infrastructure score: {infrastructure}")
    print(f"Enteloot remaining: {sim.enteloot}")
    print("Upgrade distribution:")
    for town in data["towns"]:
        print(f"  {town}: {len(sim.built[town])}")
    print(f"Submission: {output_file}")


if __name__ == "__main__":
    main()