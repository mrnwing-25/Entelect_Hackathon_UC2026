# 🏆 Level 2: Crafting and Infrastructure Optimisation

This solution is for **Level 2 of the Entelect Hackathons University Cup 2, Age of Enteland**.

The objective of Level 2 is to generate an ordered sequence of actions that develops the towns' economies within the available tick budget.

Level 2 introduces **crafting and building**, requiring the solution to decide:

- Where to gather or buy resources.
- Where to craft goods.
- Where to sell crafted goods.
- Which construction components to produce.
- Which infrastructure upgrades to build.
- In which towns upgrades should be constructed.
- In what order upgrades should be built.

The strategy must balance **time, Enteloot, resources, crafting, and infrastructure investment** to maximise the final score.

The exact algorithm and implementation details used by this solution should be documented from the submitted Python source code. This README distinguishes between the rules defined by the competition specification and the strategy implemented by the program.

---

# 🎯 Level Requirements

| Requirement | Level 2 |
|---|---|
| Crafting | Enabled |
| Building | Enabled |
| Fast routes | Not introduced until Level 3 |
| Mine nodes | Not introduced until Level 3 |
| Tools | Not introduced until Level 3 |
| Upkeep | Not introduced until Level 4 |
| Primary scoring focus | Infrastructure |
| Objective | Maximise the final score |
| Time limit | Defined by the level JSON input |
| Actions | Executed sequentially |
| Invalid actions | Skipped and consume 1 tick |
| Determinism | Required |

Level 2 includes the mechanics from Level 1 and adds crafting and building.

The main Level 2 focus areas are:

- Crafting resources into goods and transporting them to towns that pay the highest prices.
- Crafting construction components and handling their dependency chains.
- Building production upgrades early enough for their increased production to pay back.
- Sequencing civic upgrades according to their prerequisites.
- Spreading infrastructure across towns to benefit from the infrastructure distribution multiplier.

---

# 📋 Problem Description

The program must produce a valid sequence of actions for a simulated run through the towns and resource nodes of Enteland.

The player starts at the town and with the Enteloot amount specified in the level JSON file.

The starting inventory is empty, and all recipes available for that level are unlocked.

The objective is to grow the towns' economies as much as possible within the available tick limit.

The program must decide:

1. **Where to travel**
2. **When to gather resources**
3. **When to buy resources**
4. **What to craft**
5. **Where to craft**
6. **Where to sell goods**
7. **Which upgrades to build**
8. **Where to build upgrades**
9. **What order to build upgrades in**

Time and Enteloot are competing resources. Spending time travelling, gathering, crafting, or building leaves fewer ticks for other activities.

Infrastructure is the primary scoring driver in Level 2 and Level 3. Development spread across towns also contributes to the score through a distribution multiplier.

---

# ⚙️ Simulation Rules

The Level 2 simulation uses a single global tick clock.

Every action is processed sequentially.

For example:

```text
Action 1
    ↓
Ticks are consumed
    ↓
Passive systems update
    ↓
Action 2
    ↓
Ticks are consumed
    ↓
Passive systems update