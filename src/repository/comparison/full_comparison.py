import json
import random
from dataclasses import asdict
from math import comb
from typing import Optional

from dacite import from_dict

from src.entity.comparison import Comparison
from src.entity.item import Item
from src.entity.session import Session
from src.error import AppError
from src.repository.comparison.comparison import ComparisonRepository


class FullComparisonRepository(ComparisonRepository):
    def __init__(self, session: Session):
        super().__init__(session)
        try:
            self._comparisons = [from_dict(data_class=Comparison, data=c) for c in json.loads(session.comparison_data)]
        except:
            self._comparisons = []

    @property
    def comparisons(self):
        return self._comparisons

    @comparisons.setter
    def comparisons(self, value):
        self._comparisons = value
        session = self.session
        session.comparison_data = json.dumps([asdict(c) for c in self._comparisons])
        self.session = session

    def get_pending_comparisons(self) -> list[set[Item]]:
        items = self.session.items
        finished_comparisons = [set(c.items) for c in self.get_finished_comparisons()]
        comparisons = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                combination = {items[i], items[j]}
                if combination not in finished_comparisons:
                    comparisons.append(combination)

        return comparisons

    def get_pending_comparison_count(self) -> Optional[int]:
        return comb(len(self.session.items), 2) - self.get_finished_comparison_count()

    def get_next_comparison(self) -> Optional[list[Item]]:
        pending = self.get_pending_comparisons()
        return list(random.choice(pending)) if len(pending) else None

    def get_finished_comparisons(self) -> list[Comparison]:
        return self.comparisons

    def get_finished_comparison_count(self) -> int:
        return len(self.comparisons)

    def save_comparison(self, comparison: Comparison) -> None:
        if set(comparison.items) in [set(c.items) for c in self.get_finished_comparisons()]:
            raise AppError("Comparison already exists")

        if set(comparison.items) not in self.get_pending_comparisons():
            raise AppError("Invalid comparison items")

        if comparison.winner < 0 or comparison.winner > len(comparison.items) - 1:
            raise AppError("Winner index out of range")

        comparisons = self.comparisons
        comparisons.append(comparison)
        self.comparisons = comparisons

    def get_results(self) -> list[tuple[str, int]]:
        results = {}
        for item in self.session.items:
            results[item.name] = 0

        for comparison in self.get_finished_comparisons():
            winner = comparison.items[comparison.winner]
            results[winner.name] += 1

        return_val = [(k, v) for k, v in results.items()]
        return_val.sort(key=lambda x: x[1], reverse=True)
        return return_val
