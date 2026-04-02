import sqlite3
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any, Generic, TypeVar

# =============================================================================
# SEEDWORK (Domain Base Classes - Based on python-ddd-seedwork)
# =============================================================================

# 想定ファイル: src.seedwork.domain.exceptions
class ValueObjectValidationError(Exception):
    """値オブジェクトのバリデーション失敗時にスローされる例外"""
    def __init__(self, message: str, class_name: str):
        self.message = message
        self.class_name = class_name
        super().__init__(f"Validation failed for {class_name}: {message}")

# 想定ファイル: src.seedwork.domain.value_object
@dataclass(frozen=True)
class ValueObject(ABC):
    """
    値オブジェクトの基底クラス。
    __post_init__ で validate を自動実行し、属性値で比較を行います。
    """
    def __post_init__(self):
        try:
            self.validate()
        except Exception as e:
            if not isinstance(e, ValueObjectValidationError):
                raise ValueObjectValidationError(str(e), self.__class__.__name__)
            raise e

    @abstractmethod
    def validate(self):
        """バリデーションロジック。失敗時は ValueObjectValidationError を raise する。"""
        pass

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ValueObject):
            return False
        return self.__dict__ == other.__dict__

# 想定ファイル: src.seedwork.domain.entity
@dataclass
class Entity(ABC):
    """
    エンティティの基底クラス。
    一意識別子 (id) によって同一性を判定します。
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

# 想定ファイル: src.seedwork.domain.aggregate_root
class AggregateRoot(Entity):
    """集約ルートの基底クラス。"""
    pass

# 想定ファイル: src.seedwork.domain.repositories
T = TypeVar('T', bound=AggregateRoot)

class Repository(Generic[T], ABC):
    """
    リポジトリの基底インターフェース。
    Seedwork パターンに従い、永続化の抽象化を提供します。
    """
    @abstractmethod
    def save(self, aggregate: T) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: uuid.UUID) -> Optional[T]:
        pass

# =============================================================================
# DOMAIN LAYER
# =============================================================================

# 想定ファイル: src.todo.domain.models.task.value_objects
@dataclass(frozen=True)
class TaskTitle(ValueObject):
    value: str

    def validate(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueObjectValidationError("Title cannot be empty", self.__class__.__name__)
        if len(self.value) > 100:
            raise ValueObjectValidationError("Title is too long", self.__class__.__name__)

@dataclass(frozen=True)
class TaskStatus(ValueObject):
    is_completed: bool = False

    def validate(self):
        if not isinstance(self.is_completed, bool):
            raise ValueObjectValidationError("Status must be boolean", self.__class__.__name__)

# 想定ファイル: src.todo.domain.models.task.entities
class Task(AggregateRoot):
    """Task 集約ルート。"""
    def __init__(
        self, 
        title: TaskTitle, 
        id: Optional[uuid.UUID] = None,
        status: Optional[TaskStatus] = None,
        created_at: Optional[datetime] = None
    ):
        super().__init__(id=id or uuid.uuid4())
        self.title = title
        self.status = status or TaskStatus()
        self.created_at = created_at or datetime.now()

    def complete(self):
        """タスクを完了状態にするビジネスロジック。"""
        self.status = TaskStatus(is_completed=True)

    def change_title(self, new_title: TaskTitle):
        """タイトルを変更するビジネスロジック。"""
        self.title = new_title

# 想定ファイル: src.todo.domain.repositories.task_repository
class TaskRepository(Repository[Task]):
    @abstractmethod
    def find_all(self) -> List[Task]:
        pass

# =============================================================================
# INFRASTRUCTURE LAYER
# =============================================================================

# 想定ファイル: src.todo.infrastructure.repositories.sqlite_task_repository
class SQLiteTaskRepository(TaskRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            is_completed INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def save(self, task: Task) -> None:
        query = """
        INSERT OR REPLACE INTO tasks (id, title, is_completed, created_at)
        VALUES (?, ?, ?, ?)
        """
        self.conn.execute(query, (
            str(task.id),
            task.title.value,
            1 if task.status.is_completed else 0,
            task.created_at.isoformat()
        ))
        self.conn.commit()

    def find_by_id(self, id: uuid.UUID) -> Optional[Task]:
        cursor = self.conn.execute(
            "SELECT id, title, is_completed, created_at FROM tasks WHERE id = ?", 
            (str(id),)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        return Task(
            id=uuid.UUID(row[0]),
            title=TaskTitle(row[1]),
            status=TaskStatus(is_completed=bool(row[2])),
            created_at=datetime.fromisoformat(row[3])
        )

    def find_all(self) -> List[Task]:
        cursor = self.conn.execute("SELECT id, title, is_completed, created_at FROM tasks")
        tasks = []
        for row in cursor.fetchall():
            tasks.append(Task(
                id=uuid.UUID(row[0]),
                title=TaskTitle(row[1]),
                status=TaskStatus(is_completed=bool(row[2])),
                created_at=datetime.fromisoformat(row[3])
            ))
        return tasks

# =============================================================================
# APPLICATION LAYER
# =============================================================================

# 想定ファイル: src.todo.application.use_cases.task_use_cases
class TaskApplicationService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, title_text: str) -> str:
        # TaskTitle のインスタンス化時に validate() が走り、不正なデータはここで弾かれる
        title = TaskTitle(title_text)
        task = Task(title=title)
        self.repository.save(task)
        return str(task.id)

    def complete_task(self, task_id_str: str):
        task_id = uuid.UUID(task_id_str)
        task = self.repository.find_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id_str} not found")
        
        task.complete()
        self.repository.save(task)

    def list_tasks(self) -> List[dict]:
        tasks = self.repository.find_all()
        return [
            {
                "id": str(t.id), 
                "title": t.title.value, 
                "completed": t.status.is_completed,
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for t in tasks
        ]

# =============================================================================
# E2E EXECUTION (Main Script)
# =============================================================================

if __name__ == "__main__":
    print("--- SQLite DDD E2E Scenario Starting ---")
    
    # 1. インフラのセットアップ (メモリ上の SQLite)
    connection = sqlite3.connect(":memory:")
    repository = SQLiteTaskRepository(connection)
    
    # 2. アプリケーションサービスの初期化
    app_service = TaskApplicationService(repository)
    
    try:
        # シナリオ A: 正常なタスク作成
        print("\n[Scenario A] Creating a valid task...")
        task_id = app_service.create_task("Finish DDD Sample")
        print(f"-> Success: Task created with ID {task_id[:8]}...")

        # シナリオ B: 不正なタスク作成 (バリデーションエラー)
        print("\n[Scenario B] Attempting to create an invalid task (empty title)...")
        try:
            app_service.create_task("   ") # 空文字
        except ValueObjectValidationError as e:
            print(f"-> Caught expected validation error: {e.message}")

        # シナリオ C: タスクを完了状態にする
        print(f"\n[Scenario C] Completing task {task_id[:8]}...")
        app_service.complete_task(task_id)
        print("-> Success: Task marked as completed.")

        # シナリオ D: 全件取得と結果検証
        print("\n[Scenario D] Fetching all tasks and verifying results...")
        tasks = app_service.list_tasks()
        for t in tasks:
            status = "DONE" if t['completed'] else "TODO"
            print(f" [{status}] {t['title']} (Created: {t['created_at']})")

        # 最終アサーション
        assert len(tasks) == 1
        assert tasks[0]['completed'] is True
        print("\n--- All E2E Scenarios Completed Successfully ---")

    finally:
        connection.close()
