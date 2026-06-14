# Wedding Seating Optimizer

Assigns wedding guests to tables by maximizing a configurable score across social compatibility, relationship affinities, and seating preferences — while enforcing hard constraints (capacity, couples, plus-ones, reserved seats).

Three algorithms are implemented and can be run independently or chained as a pipeline.

---

## Project Structure

```
seating/
├── models.py                  # Data classes: Guest, Relationship, Table, ScoringConfig
├── constraints.py             # Hard constraint checker
├── scoring.py                 # Score functions (pairwise affinity + table attributes)
├── runner.py                  # Full pipeline: greedy → local search → SA
└── algorithms/
    ├── greedy.py              # Greedy initialization
    ├── local_search.py        # Hill climbing via random swaps
    └── simulated_annealing.py # SA for escaping local optima
main.py                        # Example usage / entry point
```

---

## Quickstart

```bash
python main.py
```

Output:

```
Step 1: Greedy initialization...
  Greedy score: 10.242
Step 2: Local search...
  Local search score: 10.242
Step 3: Simulated annealing...
  Final score: 10.242
  All hard constraints satisfied.

=== SEATING CHART ===

Head Table (4 guests):
  - Ishan Vashi [groom_family, tier 1]
  ...
```

---

## Data Model

### `Guest`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier |
| `name` | `str` | Display name |
| `side` | `str` | `"bride"`, `"groom"`, or `"both"` |
| `languages` | `list[str]` | Spoken languages (e.g. `["english", "gujarati"]`) |
| `generation` | `str` | `"boomer"`, `"gen_x"`, `"millennial"`, `"gen_z"` |
| `introversion` | `float` | `0.0` (extrovert) → `1.0` (introvert) |
| `political_leaning` | `float` | `0.0` (left) → `1.0` (right) |
| `prestige_tier` | `int` | `1` (inner circle) → N (extended network) |
| `fields_of_interest` | `list[str]` | e.g. `["technology", "finance"]` |
| `category` | `str` | `"groom_family"`, `"bride_family"`, `"friends"`, etc. |
| `plus_one_of` | `str \| None` | Guest ID of their host (enforces same-table constraint) |

### `Relationship`

```python
Relationship("alice", "bob", affinity=0.9, hard_together=True)
Relationship("carol", "dave", affinity=-0.8, hard_apart=True)
```

| Field | Description |
|---|---|
| `affinity` | `-1.0` (feud) → `1.0` (close bond). Unspecified pairs default to `0.0`. |
| `hard_together` | Must be at the same table |
| `hard_apart` | Must not be at the same table |

### `Table`

```python
Table("t1", "Head Table", min_guests=2, max_guests=8, reserved_for=["bride_id", "groom_id"])
```

`reserved_for` pins specific guests to a table as a hard constraint.

---

## Scoring

### `ScoringConfig`

Controls how each attribute is weighted. **Positive weight = prefer homogeneity; negative weight = prefer diversity.**

| Attribute | Default | Rationale |
|---|---|---|
| `relationship_weight` | `2.0` | Affinities are the strongest signal |
| `prestige_weight` | `0.9` | Keep inner-circle guests together |
| `language_weight` | `1.0` | Everyone must share a language at their table |
| `field_weight` | `0.7` | Shared interests make for better conversation |
| `political_weight` | `0.5` | Mildly prefer similar leanings |
| `generation_weight` | `0.3` | Mild preference for same generation |
| `side_weight` | `-0.6` | Mix bride and groom sides |
| `introversion_weight` | `-0.8` | Mix introverts and extroverts |

Adjust any weight or set it to `0` to ignore that attribute entirely:

```python
config = ScoringConfig(side_weight=0.0, prestige_weight=1.5)
```

---

## Algorithms

### Greedy (`algorithms/greedy.py`)

Builds an initial assignment in one pass:
1. Pins reserved guests to their tables
2. Groups `hard_together` guests into clusters via union-find
3. Places each cluster at the table that maximises the marginal score improvement

Fast, deterministic, but gets stuck in poor local optima. Best used as a starting point for the other algorithms.

### Local Search (`algorithms/local_search.py`)

Hill climbing: repeatedly proposes random two-guest swaps and accepts any that improve the score. Stops when no improving swap is found across 200 attempts.

Good for quick refinement. Guaranteed not to make things worse, but will settle at the first local optimum it finds.

### Simulated Annealing (`algorithms/simulated_annealing.py`)

Like local search, but occasionally accepts worse solutions with probability `e^(Δscore / T)`. Temperature `T` starts high (broad exploration) and decays each round by `cooling_rate` (exploitation). Tracks the global best seen across all iterations.

Tunable parameters:

| Parameter | Default | Effect |
|---|---|---|
| `t_initial` | `10.0` | Higher = more early exploration |
| `t_final` | `0.01` | Lower = finer final exploitation |
| `cooling_rate` | `0.995` | Closer to `1.0` = slower cooling, more thorough |
| `iterations_per_temp` | `100` | More = better coverage per temperature step |

---

## Running Algorithms Independently

```python
from seating.algorithms.greedy import greedy_assign
from seating.algorithms.local_search import local_search
from seating.algorithms.simulated_annealing import simulated_annealing
from seating.scoring import score_assignment
from seating.constraints import check_hard_constraints

# Just greedy
assignment = greedy_assign(guests, tables, relationships, config)

# Greedy + SA (skip local search)
greedy = greedy_assign(guests, tables, relationships, config)
final = simulated_annealing(greedy, guests, tables, relationships, config, cooling_rate=0.99)

print(score_assignment(final, guests, tables, relationships, config))
print(check_hard_constraints(final, tables, relationships, guests))
```

---

## Hard Constraints

These are always enforced and will be reported as violations if broken:

- Table `min_guests` / `max_guests` capacity
- `reserved_for` pinned seats
- `hard_together` / `hard_apart` relationships
- Plus-ones must sit with their host
- Every guest must share at least one language with someone at their table
