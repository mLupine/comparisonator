from dataclasses import dataclass

from src.entity.item import Item


@dataclass()
class Comparison:
    items: list[Item]
    winner: int
