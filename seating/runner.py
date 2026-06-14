from __future__ import annotations
from .models import Assignment, Guest, Table, Relationship, ScoringConfig
from .constraints import check_hard_constraints, get_table_guests
from .scoring import score_assignment
from .algorithms.greedy import greedy_assign
from .algorithms.local_search import local_search
from .algorithms.simulated_annealing import simulated_annealing


def optimize_seating(
    guests: list[Guest],
    tables: list[Table],
    relationships: list[Relationship],
    config: ScoringConfig,
) -> tuple[Assignment, float, list[str]]:
    """
    Full pipeline: greedy init → local search → simulated annealing.
    Returns (assignment, score, violations).
    """
    print("Step 1: Greedy initialization...")
    greedy = greedy_assign(guests, tables, relationships, config)
    print(f"  Greedy score: {score_assignment(greedy, guests, tables, relationships, config):.3f}")

    print("Step 2: Local search...")
    local = local_search(greedy, guests, tables, relationships, config)
    print(f"  Local search score: {score_assignment(local, guests, tables, relationships, config):.3f}")

    print("Step 3: Simulated annealing...")
    final = simulated_annealing(local, guests, tables, relationships, config)
    final_score = score_assignment(final, guests, tables, relationships, config)
    print(f"  Final score: {final_score:.3f}")

    violations = check_hard_constraints(final, tables, relationships, guests)
    if violations:
        print(f"  WARNING: {len(violations)} hard constraint violation(s):")
        for v in violations:
            print(f"    - {v}")
    else:
        print("  All hard constraints satisfied.")

    return final, final_score, violations


def print_assignment(assignment: Assignment, guests: list[Guest], tables: list[Table]):
    guest_map = {g.id: g for g in guests}
    print("\n=== SEATING CHART ===")
    for table in tables:
        occupants = get_table_guests(assignment, table.id)
        print(f"\n{table.name} ({len(occupants)} guests):")
        for gid in occupants:
            g = guest_map[gid]
            print(f"  - {g.name} [{g.category}, tier {g.prestige_tier}]")
