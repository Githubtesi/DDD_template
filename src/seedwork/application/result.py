from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

@dataclass(frozen=True)
class Result(Generic[T]):
    """
    ユースケースの実行結果をカプセル化するクラス。
    成功/失敗の状態と、成功時のデータまたは失敗時のエラーを保持します。
    """
    is_success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @classmethod
    def ok(cls, value: T = None) -> "Result[T]":
        return cls(is_success=True, value=value)

    @classmethod
    def fail(cls, error: str, error_code: str = "ERROR") -> "Result[T]":
        return cls(is_success=False, error=error, error_code=error_code)

    def __bool__(self) -> bool:
        return self.is_success
