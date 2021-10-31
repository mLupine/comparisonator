from dataclasses import dataclass

from src.entity.item import Item


@dataclass()
class Session:
    id: str
    name: str
    comparison_type: str
    items: list[Item]
    comparison_data: str = ""
