from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class ValueObject(ABC):
    """
    全ての値オブジェクトの基底クラス。
    frozen=True により、継承先でも値の変更を禁止する。
    """
    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self):
        """値の妥当性をチェックするロジックを強制する"""
        pass