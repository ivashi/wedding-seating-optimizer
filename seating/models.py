from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

Assignment = dict[str, str]


@dataclass
class Guest:
    id: str
    name: str
    side: str                           # "bride" | "groom" | "both"
    languages: list[str]
    generation: str                     # "boomer" | "gen_x" | "millennial" | "gen_z"
    introversion: float                 # 0.0 (extrovert) → 1.0 (introvert)
    political_leaning: float            # 0.0 (left) → 1.0 (right)
    prestige_tier: int                  # 1 (inner circle) → N (extended)
    fields_of_interest: list[str]
    category: str                       # "groom_family" | "bride_family" | "friends" | etc.
    plus_one_of: Optional[str] = None   # guest id they're a plus-one of


@dataclass
class Relationship:
    guest_a: str
    guest_b: str
    affinity: float                     # -1.0 (feud) → 1.0 (close bond)
    hard_together: bool = False
    hard_apart: bool = False


@dataclass
class Table:
    id: str
    name: str
    min_guests: int
    max_guests: int
    reserved_for: list[str] = field(default_factory=list)  # hard-pinned guest ids


@dataclass
class ScoringConfig:
    """
    For each attribute:
      weight > 0 → optimize for homogeneity (similar people together)
      weight < 0 → optimize for diversity (spread people out)
      weight = 0 → ignore this attribute
    """
    introversion_weight: float = -0.8       # diverse tables (mix intro/extro)
    political_weight: float = 0.5           # mildly homogeneous
    generation_weight: float = 0.3          # mildly homogeneous
    prestige_weight: float = 0.9            # strongly homogeneous
    language_weight: float = 1.0            # must share a language
    side_weight: float = -0.6              # mix bride/groom sides
    field_weight: float = 0.7              # prefer shared interests
    relationship_weight: float = 2.0       # direct affinity scores weighted heavily
