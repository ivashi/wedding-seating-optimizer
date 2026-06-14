from __future__ import annotations
import random
from ..models import Assignment, Guest, Table, Relationship, ScoringConfig
from ..constraints import check_hard_constraints
from ..scoring import score_assignment


def local_search(
    assignment: Assignment,
    guests: list[Guest],
    tables: list[Table],
    relationships: list[Relationship],
    config: ScoringConfig,
    max_iterations: int = 10_000,
) -> Assignment:
    """
    Hill climbing via random pairwise swaps.
    Stops when no improving swap is found (local optimum).
    """
    current = dict(assignment)
    current_score = score_assignment(current, guests, tables, relationships, config)
    guest_ids = [g.id for g in guests]

    for _ in range(max_iterations):
        improved = False

        for _ in range(200):
            a, b = random.sample(guest_ids, 2)
            if current[a] == current[b]:
                continue

            candidate = dict(current)
            candidate[a], candidate[b] = candidate[b], candidate[a]

            if check_hard_constraints(candidate, tables, relationships, guests):
                continue

            candidate_score = score_assignment(candidate, guests, tables, relationships, config)
            if candidate_score > current_score:
                current = candidate
                current_score = candidate_score
                improved = True
                break

        if not improved:
            break

    return current
