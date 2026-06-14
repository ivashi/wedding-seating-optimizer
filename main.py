from seating import (
    Guest, Relationship, Table, ScoringConfig,
    optimize_seating, print_assignment,
)

guests = [
    Guest("ishan", "Ishan Vashi", "groom", ["english", "gujarati"],
          "millennial", 0.3, 0.4, 1, ["technology", "finance"], "groom_family"),
    Guest("anna", "Anna", "bride", ["english"],
          "millennial", 0.4, 0.3, 1, ["medicine", "art"], "bride_family"),
    Guest("mom_ishan", "Ishan's Mom", "groom", ["english", "gujarati"],
          "boomer", 0.5, 0.6, 1, ["cooking", "travel"], "groom_family"),
    Guest("dad_ishan", "Ishan's Dad", "groom", ["english", "gujarati"],
          "boomer", 0.4, 0.6, 1, ["finance", "cricket"], "groom_family"),
    Guest("mom_anna", "Anna's Mom", "bride", ["english"],
          "boomer", 0.6, 0.4, 1, ["art", "travel"], "bride_family"),
    Guest("friend_1", "Friend A", "groom", ["english"],
          "millennial", 0.2, 0.5, 2, ["technology", "music"], "friends"),
    Guest("friend_2", "Friend B", "bride", ["english"],
          "millennial", 0.7, 0.4, 2, ["medicine", "hiking"], "friends"),
]

relationships = [
    Relationship("ishan", "anna", affinity=1.0, hard_together=True),
    Relationship("ishan", "mom_ishan", affinity=0.9),
    Relationship("mom_ishan", "dad_ishan", affinity=1.0, hard_together=True),
    Relationship("mom_anna", "mom_ishan", affinity=0.3),
    Relationship("friend_1", "friend_2", affinity=0.5),
]

tables = [
    Table("t1", "Head Table", min_guests=2, max_guests=4, reserved_for=["ishan", "anna"]),
    Table("t2", "Family Table", min_guests=2, max_guests=4),
    Table("t3", "Friends Table", min_guests=2, max_guests=4),
]

if __name__ == "__main__":
    assignment, score, violations = optimize_seating(guests, tables, relationships, ScoringConfig())
    print_assignment(assignment, guests, tables)
