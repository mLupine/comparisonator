from dataclasses import dataclass

from src.entity.item import Item


@dataclass()
class PendingComparison:
    item: Item
    test_pos: int
