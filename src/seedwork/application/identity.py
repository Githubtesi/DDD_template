from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class Identity:
    """
    現在操作を行っているユーザーの情報を表すDTO。
    """
    user_id: str
    username: str
    roles: List[str] = field(default_factory=list)
    is_authenticated: bool = True

    @classmethod
    def anonymous(cls) -> "Identity":
        """未認証ユーザーを返します。"""
        return cls(user_id="", username="anonymous", is_authenticated=False)

    def has_role(self, role: str) -> bool:
        return role in self.roles
