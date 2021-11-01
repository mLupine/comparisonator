import copy
import json
import random
from dataclasses import asdict
from typing import Any, Optional

from dacite import from_dict

from src.entity.comparison import Comparison
from src.entity.item import Item
from src.entity.pending_comparison import PendingComparison
from src.entity.session import Session
from src.error import AppError
from src.repository.comparison.comparison import ComparisonRepository


class AssumingComparisonRepository(ComparisonRepository):
    def __init__(self, session: Session):
        super().__init__(session)
        try:
            comparison_data = json.loads(session.comparison_data)
            self._ranking = [
                from_dict(data=item, data_class=Item)
                for item in comparison_data.get("ranking", [])
            ]
            self._remaining_items = [
                from_dict(data=item, data_class=Item)
                for item in comparison_data.get("remaining_items", [])
            ]
            self._comparisons = [
                from_dict(data_class=Comparison, data=c)
                for c in comparison_data.get("comparisons", [])
            ]
            self._pending_comparison = (
                from_dict(
                    data_class=PendingComparison,
                    data=comparison_data.get("pending_comparison"),
                )
                if comparison_data.get("pending_comparison")
                else None
            )
        except:
            items = copy.deepcopy(session.items)
            random.shuffle(items)
            self._remaining_items = items
            self._ranking = []
            self._comparisons = []
            self._pending_comparison = None

    @property
    def comparisons(self) -> list[Comparison]:
        return self._comparisons

    @comparisons.setter
    def comparisons(self, value):
        self._comparisons = value
        self._update_session_data()

    @property
    def ranking(self) -> list[Item]:
        return self._ranking

    @ranking.setter
    def ranking(self, value):
        self._ranking = value
        self._update_session_data()

    @property
    def remaining_items(self) -> list[Item]:
        return self._remaining_items

    @remaining_items.setter
    def remaining_items(self, value):
        self._remaining_items = value
        self._update_session_data()

    @property
    def pending_comparison(self) -> Optional[PendingComparison]:
        return self._pending_comparison

    @pending_comparison.setter
    def pending_comparison(self, value):
        self._pending_comparison = value
        self._update_session_data()

    def _update_session_data(self):
        session = self.session
        session.comparison_data = json.dumps(
            {
                "ranking": [asdict(item) for item in self._ranking],
                "comparisons": [asdict(c) for c in self._comparisons],
                "remaining_items": [
                    asdict(item) for item in self._remaining_items
                ],
                "pending_comparison": asdict(self._pending_comparison)
                if self._pending_comparison
                else None,
            }
        )
        self.session = session

    def get_pending_comparison_count(self) -> Optional[int]:
        return None

    def get_next_comparison(self) -> Optional[list[Item]]:
        if len(self.ranking) < 2:
            return self.remaining_items[:2]

        if self.pending_comparison:
            return [
                self.pending_comparison.item,
                self.ranking[self.pending_comparison.test_pos],
            ]

        if not len(self.remaining_items):
            return None

        return [self.remaining_items[0], self.ranking[0]]

    def get_finished_comparisons(self) -> list[Comparison]:
        return self.comparisons

    def get_finished_comparison_count(self) -> int:
        return len(self.comparisons)

    def save_comparison(self, comparison: Comparison) -> None:
        if set(comparison.items) in [
            set(c.items) for c in self.get_finished_comparisons()
        ]:
            raise AppError("Comparison already exists")

        if set(comparison.items) != set(self.get_next_comparison()):
            raise AppError("Invalid comparison items")

        if not 0 <= comparison.winner <= 1:
            raise AppError("Winner index out of range")

        comparisons = self.comparisons
        ranking = self.ranking
        remaining_items = self.remaining_items

        if len(ranking) < 2:  # no ranking yet
            ranking = [
                comparison.items[comparison.winner],
                comparison.items[int(not comparison.winner)],
            ]
            self.ranking = ranking
            self.pending_comparison = None
            self.remaining_items = remaining_items[2:]

        elif (
            comparison.winner == 0
        ):  # index 0 is always the item not in the ranking
            ranking.insert(
                ranking.index(comparison.items[1]), comparison.items[0]
            )
            self.ranking = ranking
            if not self.pending_comparison:
                self.remaining_items = remaining_items[1:]
            self.pending_comparison = None

        elif (
            comparison.winner == 1
        ):  # index 1 is always the item in the ranking
            if ranking.index(comparison.items[1]) >= len(ranking) - 1:
                ranking.append(comparison.items[0])
                self.ranking = ranking
                self.pending_comparison = None
            else:
                if not self.pending_comparison:
                    self.remaining_items = remaining_items[1:]
                self.pending_comparison = PendingComparison(
                    item=comparison.items[0],
                    test_pos=ranking.index(comparison.items[1]) + 1,
                )

        comparisons.append(comparison)
        self.comparisons = comparisons

    def get_results(self) -> list[tuple[str, Any]]:
        return [(item.name, None) for item in self.ranking]
