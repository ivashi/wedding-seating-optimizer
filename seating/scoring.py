from __future__ import annotations
import math
from collections import Counter
from .models import Assignment, Guest, Table, Relationship, ScoringConfig
from .constraints import get_table_guests


def pairwise_affinity_score(
    table_guests: list[Guest],
    relationships: list[Relationship],
    config: ScoringConfig,
) -> float:
    rel_map = {(r.guest_a, r.guest_b): r.affinity for r in relationships}
    rel_map.update({(b, a): v for (a, b), v in rel_map.items()})

    score = 0.0
    ids = [g.id for g in table_guests]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            score += rel_map.get((ids[i], ids[j]), 0.0)

    return score * config.relationship_weight


def _variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def _entropy(categories: list[str]) -> float:
    counts = Counter(categories)
    total = len(categories)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def table_attribute_score(
    table_guests: list[Guest],
    config: ScoringConfig,
) -> float:
    """
    Score table composition across all attributes.
    Positive weight → reward homogeneity; negative weight → reward diversity.
    Each raw score is normalized to [0, 1] before weighting.
    """
    if len(table_guests) < 2:
        return 0.0

    score = 0.0

    intro_variance = _variance([g.introversion for g in table_guests]) / 0.25
    if config.introversion_weight < 0:
        score += abs(config.introversion_weight) * intro_variance
    else:
        score += config.introversion_weight * (1 - intro_variance)

    pol_variance = _variance([g.political_leaning for g in table_guests]) / 0.25
    if config.political_weight < 0:
        score += abs(config.political_weight) * pol_variance
    else:
        score += config.political_weight * (1 - pol_variance)

    gen_entropy_norm = _entropy([g.generation for g in table_guests]) / math.log2(4)
    if config.generation_weight < 0:
        score += abs(config.generation_weight) * gen_entropy_norm
    else:
        score += config.generation_weight * (1 - gen_entropy_norm)

    max_tier = 4.0
    tier_variance = _variance([float(g.prestige_tier) for g in table_guests]) / ((max_tier / 2) ** 2)
    if config.prestige_weight < 0:
        score += abs(config.prestige_weight) * tier_variance
    else:
        score += config.prestige_weight * (1 - tier_variance)

    max_side_entropy = math.log2(3)
    side_entropy_norm = _entropy([g.side for g in table_guests]) / max_side_entropy if max_side_entropy > 0 else 0
    if config.side_weight < 0:
        score += abs(config.side_weight) * side_entropy_norm
    else:
        score += config.side_weight * (1 - side_entropy_norm)

    ids = [g.id for g in table_guests]
    field_map = {g.id: set(g.fields_of_interest) for g in table_guests}
    pair_count = 0
    shared_count = 0.0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            pair_count += 1
            shared_count += min(len(field_map[ids[i]] & field_map[ids[j]]), 1)
    if pair_count > 0:
        field_score = shared_count / pair_count
        if config.field_weight < 0:
            score += abs(config.field_weight) * (1 - field_score)
        else:
            score += config.field_weight * field_score

    return score


def score_assignment(
    assignment: Assignment,
    guests: list[Guest],
    tables: list[Table],
    relationships: list[Relationship],
    config: ScoringConfig,
) -> float:
    guest_map = {g.id: g for g in guests}
    total = 0.0

    for table in tables:
        occupants = [guest_map[gid] for gid in get_table_guests(assignment, table.id)]
        if not occupants:
            continue
        total += pairwise_affinity_score(occupants, relationships, config)
        total += table_attribute_score(occupants, config)

    return total
