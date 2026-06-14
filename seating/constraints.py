from __future__ import annotations
from .models import Assignment, Guest, Table, Relationship


def get_table_guests(assignment: Assignment, table_id: str) -> list[str]:
    return [g for g, t in assignment.items() if t == table_id]


def check_hard_constraints(
    assignment: Assignment,
    tables: list[Table],
    relationships: list[Relationship],
    guests: list[Guest],
) -> list[str]:
    """Returns a list of violation descriptions. Empty = fully feasible."""
    violations = []
    guest_map = {g.id: g for g in guests}

    for table in tables:
        occupants = get_table_guests(assignment, table.id)
        if len(occupants) < table.min_guests:
            violations.append(f"{table.name} underfull: {len(occupants)} < {table.min_guests}")
        if len(occupants) > table.max_guests:
            violations.append(f"{table.name} overfull: {len(occupants)} > {table.max_guests}")

    for table in tables:
        for guest_id in table.reserved_for:
            if assignment.get(guest_id) != table.id:
                violations.append(f"{guest_id} must be at {table.name}")

    for rel in relationships:
        table_a = assignment.get(rel.guest_a)
        table_b = assignment.get(rel.guest_b)
        if rel.hard_together and table_a != table_b:
            violations.append(f"{rel.guest_a} and {rel.guest_b} must sit together")
        if rel.hard_apart and table_a == table_b:
            violations.append(f"{rel.guest_a} and {rel.guest_b} must not sit together")

    for guest in guests:
        if guest.plus_one_of:
            if assignment.get(guest.id) != assignment.get(guest.plus_one_of):
                violations.append(f"{guest.id} (plus-one) must sit with {guest.plus_one_of}")

    for guest in guests:
        table_id = assignment.get(guest.id)
        tablemates = [
            guest_map[g] for g in get_table_guests(assignment, table_id)
            if g != guest.id
        ]
        shared_language = any(
            set(guest.languages) & set(tm.languages)
            for tm in tablemates
        )
        if not shared_language:
            violations.append(f"{guest.id} shares no language with their table")

    return violations
