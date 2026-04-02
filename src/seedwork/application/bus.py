
T = TypeVar('T')

class ICommandBus(ABC):
    """コマンド（書き込み系）の配送を抽象化します。"""
    @abstractmethod
    def send(self, command: Any) -> Any:
        pass

class IQueryBus(ABC):
    """クエリ（読み取り系）の配送を抽象化します。"""
    @abstractmethod
    def ask(self, query: Any) -> Any:
        pass

class InMemoryBus(ICommandBus, IQueryBus):
    """
    メモリ上での簡易配送実装。
    実稼働初期やテスト、小規模なモノリス構成で使用されます。
    """
    def __init__(self):
        self._handlers = {}

    def register(self, message_type: Type, handler: Any):
        self._handlers[message_type] = handler

    def send(self, command: Any) -> Any:
        handler = self._handlers.get(type(command))
        if not handler:
            raise Exception(f"No handler registered for {type(command)}")
        return handler.handle(command)

    def ask(self, query: Any) -> Any:
        handler = self._handlers.get(type(query))
        if not handler:
            raise Exception(f"No handler registered for {type(query)}")
        return handler.handle(query)
