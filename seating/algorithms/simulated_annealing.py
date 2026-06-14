from __future__ import annotations
import random
import math
from ..models import Assignment, Guest, Table, Relationship, ScoringConfig
from ..constraints import check_hard_constraints
from ..scoring import score_assignment


def simulated_annealing(
    initial_assignment: Assignment,
    guests: list[Guest],
    tables: list[Table],
    relationships: list[Relationship],
    config: ScoringConfig,
    t_initial: float = 10.0,
    t_final: float = 0.01,
    cooling_rate: float = 0.995,
    iterations_per_temp: int = 100,
) -> Assignment:
    """
    Explore the search space by accepting worse solutions with decreasing probability,
    allowing escape from local optima that hill climbing gets stuck in.

    Temperature schedule:
      high T → accept almost anything (broad exploration)
      low T  → only accept improvements (exploitation)
    """
    current = dict(initial_assignment)
    current_score = score_assignment(current, guests, tables, relationships, config)

    best = dict(current)
    best_score = current_score

    guest_ids = [g.id for g in guests]
    T = t_initial

    while T > t_final:
        for _ in range(iterations_per_temp):
            a, b = random.sample(guest_ids, 2)
            if current[a] == current[b]:
                continue

            candidate = dict(current)
            candidate[a], candidate[b] = candidate[b], candidate[a]

            if check_hard_constraints(candidate, tables, relationships, guests):
                continue

            candidate_score = score_assignment(candidate, guests, tables, relationships, config)
            delta = candidate_score - current_score

            if delta > 0 or random.random() < math.exp(delta / T):
                current = candidate
                current_score = candidate_score

            if current_score > best_score:
                best = dict(current)
                best_score = current_score

        T *= cooling_rate

    return best
