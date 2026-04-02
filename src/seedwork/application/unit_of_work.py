from abc import ABC, abstractmethod
from typing import Any

class IUnitOfWork(ABC):
    """
    ユニットオブワーク（UoW）のインターフェース。
    複数のリポジトリ操作を一つのトランザクションとして管理します。
    """

    def __enter__(self) -> "IUnitOfWork":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        コンテキストを抜ける際に、エラーがなければコミット、あればロールバックします。
        """
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    @abstractmethod
    def commit(self) -> None:
        """変更を確定させ、イベントを発行します。"""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """変更を破棄します。"""
        pass
