from ..application.identity import IIdentityContext, Identity

class StaticIdentityContext(IIdentityContext):
    """
    テストやバッチ処理などで使用する、固定の Identity を返す実装。
    実開発では、FastAPI のリクエストヘッダーから生成する 
    'HttpIdentityContext' などを作成します。
    """
    def __init__(self, user_id: str, username: str, roles: list[str] = None):
        self._identity = Identity(
            user_id=user_id,
            username=username,
            roles=roles or [],
            is_authenticated=True
        )

    def get_current_identity(self) -> Identity:
        return self._identity

class AnonymousIdentityContext(IIdentityContext):
    """未認証状態を返すコンテキスト。"""
    def get_current_identity(self) -> Identity:
        return Identity.anonymous()
