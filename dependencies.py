import models
from database import SessionLocal
from fastapi.security import HTTPBasic
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from services.users import UserService
from sqlalchemy.orm import Session

security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # todo: check token
    user = UserService.find_user_by_username(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
