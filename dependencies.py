from database import SessionLocal
from fastapi.security import HTTPBasic

security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
