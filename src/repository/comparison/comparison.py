from abc import ABC
from typing import Optional, Any

from src.entity.comparison import Comparison
from src.entity.item import Item
from src.entity.session import Session
from src.repository.session import SessionRepository


class ComparisonRepository(ABC):
    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        SessionRepository().save_session(self._session)

    def get_pending_comparison_count(self) -> Optional[int]:
        pass

    def get_next_comparison(self) -> Optional[list[Item]]:
        pass

    def get_finished_comparisons(self) -> list[Comparison]:
        pass

    def get_finished_comparison_count(self) -> int:
        pass

    def save_comparison(self, comparison: Comparison) -> None:
        pass

    def get_results(self) -> list[tuple[str, Any]]:
        pass
