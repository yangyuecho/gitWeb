from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///db.sqlite3"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
) # connect_args={"check_same_thread": False}  仅用于SQLite
# 数据库会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 将用这个类继承，来创建每个数据库模型或类（ORM 模型）的基类
# Base = declarative_base()
@as_declarative()
class Base:
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    '''如果没有指定__tablename__  则默认使用model类名转换表名字'''
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()