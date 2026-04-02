from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from contextlib import contextmanager

# SQLAlchemy の Base クラス。各エンティティの DB モデルはこの Base を継承します。
Base = declarative_base()

class Database:
    """
    データベースの接続とセッション管理を担うクラス。
    """
    def __init__(self, db_url: str, echo: bool = False):
        self._engine = create_engine(db_url, echo=echo)
        self._session_factory = sessionmaker(
            bind=self._engine, 
            autocommit=False, 
            autoflush=False
        )

    def create_database(self):
        """テーブルを作成します（開発・テスト用）。"""
        Base.metadata.create_all(self._engine)

    @property
    def session_factory(self):
        return self._session_factory

    @contextmanager
    def session(self):
        """コンテキストマネージャ形式でセッションを提供します。"""
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
