from database import SessionLocal
from fastapi.security import HTTPBasic
from fastapi.security import OAuth2PasswordBearer

security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
