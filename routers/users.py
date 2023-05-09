import dependencies as d
from fastapi import APIRouter
from fastapi import Form
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import schemas
from services.users import UserService

router = APIRouter(
    prefix="/api/user",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", tags=["users"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(d.get_db)):
    user_name = form_data.username
    user = UserService.find_user_by_username(db, user_name)
    if not user:
        raise HTTPException(status_code=400, detail="没有该用户")
    hashed_password = UserService.salted_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@router.post("/register", tags=["users"], response_model=schemas.User, responses={404: {"model": schemas.Message}})
async def register(user: schemas.UserCreate,
                   db: Session = Depends(d.get_db)):
    res = UserService.register(db, user)
    return res