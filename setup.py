from database import SessionLocal
from fastapi.security import HTTPBasic

from sqlalchemy.orm import Session
# 创建所有表, 注释掉, 用 alembic 来管理数据库迁移
# models.Base.metadata.create_all(bind=engine)

security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
