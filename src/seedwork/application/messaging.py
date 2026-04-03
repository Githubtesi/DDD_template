from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
from .results import Result

# 型変数の定義
C = TypeVar('C') # Command type
R = TypeVar('R') # Result type
Q = TypeVar('Q') # Query type

class Command(ABC):
    """全てのコマンド（書き込み要求）の基底クラス"""
    pass

class Query(ABC):
    """全てのクエリ（読み取り要求）の基底クラス"""
    pass

class IUseCase(Generic[C, R], ABC):
    """
    書き込み系（Command）ハンドラーのインターフェース。
    ビジネスロジックを実行し、Resultオブジェクトを返します。
    """
    @abstractmethod
    def execute(self, command: C) -> Result[R]:
        pass

# ジェネリクスのエラーを回避するための制約付き型変数
T_Query = TypeVar('T_Query', bound=Query)
T_Result = TypeVar('T_Result')

class IQueryHandler(Generic[T_Query, T_Result], ABC):
    """
    読み取り系（Query）ハンドラーのインターフェース。
    データを取得し、DTOやリストを返します。
    """
    @abstractmethod
    def handle(self, query: T_Query) -> T_Result:
        pass
