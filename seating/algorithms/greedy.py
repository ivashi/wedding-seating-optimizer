from __future__ import annotations
from ..models import Assignment, Guest, Table, Relationship, ScoringConfig
from ..constraints import get_table_guests
from ..scoring import table_attribute_score


def greedy_assign(
    guests: list[Guest],
    tables: list[Table],
    relationships: list[Relationship],
    config: ScoringConfig,
) -> Assignment:
    """
    Build an initial assignment greedily:
      1. Pin reserved guests first
      2. Place must-sit-together clusters (union-find)
      3. Fill remaining guests one at a time, picking the table
         that most improves the score when they're added
    """
    assignment: Assignment = {}
    guest_map = {g.id: g for g in guests}

    for table in tables:
        for gid in table.reserved_for:
            assignment[gid] = table.id

    parent = {g.id: g.id for g in guests}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    for rel in relationships:
        if rel.hard_together:
            union(rel.guest_a, rel.guest_b)

    clusters: dict[str, list[str]] = {}
    for g in guests:
        clusters.setdefault(find(g.id), []).append(g.id)

    for cluster in sorted(clusters.values(), key=len, reverse=True):
        unassigned = [gid for gid in cluster if gid not in assignment]
        if not unassigned:
            continue

        best_table = None
        best_delta = float("-inf")

        for table in tables:
            occupants = get_table_guests(assignment, table.id)
            if len(occupants) + len(unassigned) > table.max_guests:
                continue

            current_occupants = [guest_map[g] for g in occupants]
            new_occupants = current_occupants + [guest_map[g] for g in unassigned]
            delta = (
                table_attribute_score(new_occupants, config)
                - table_attribute_score(current_occupants, config)
            )

            if delta > best_delta:
                best_delta = delta
                best_table = table.id

        if best_table:
            for gid in unassigned:
                assignment[gid] = best_table

    return assignment
