from typing import Type

from src.entity.session import Session
from src.repository.comparison.comparison import ComparisonRepository
from src.repository.comparison.full_comparison import FullComparisonRepository


class ComparisonEngineRepository:
    def get_comparison_repository(self, session: Session) -> Type[ComparisonRepository]:
        if session.comparison_type == "full":
            return FullComparisonRepository

        raise NotImplementedError("Comparison type not implemented")
