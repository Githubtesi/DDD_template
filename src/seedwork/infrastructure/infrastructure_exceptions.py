from ..application.exceptions import AppException

class InfrastructureException(AppException):
    """インフラ層特有の例外の基底クラス。"""
    pass

class DatabaseConnectionError(InfrastructureException):
    """DB接続に失敗した際の例外。"""
    def __init__(self, message: str = "データベースへの接続に失敗しました"):
        super().__init__(message, code="DB_CONNECTION_ERROR")

class MappingError(InfrastructureException):
    """ドメインとDBモデルの変換に失敗した際の例外。"""
    def __init__(self, message: str):
        super().__init__(message, code="MAPPING_ERROR")
