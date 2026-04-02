from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from .dto import DTO

T_Result = TypeVar("T_Result")

class Query(DTO):
    """
    読み取り専用の意図を表す基底クラス。
    副作用（データの更新）を持たない操作に使用します。
    """
    pass

class IQueryHandler(ABC, Generic[Query, T_Result]):
    """
    クエリを処理するハンドラのインターフェース。
    """
    @abstractmethod
    def handle(self, query: Query) -> T_Result:
        pass
