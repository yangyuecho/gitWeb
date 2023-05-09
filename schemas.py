from pydantic import BaseModel
import typing as t
from datetime import datetime


class Message(BaseModel):
    message: str


class DBBase(BaseModel):
    id: int
    create_at: datetime
    update_at: datetime


class RepoBase(BaseModel):
    name: str
    path: t.Optional[str] = None
    is_private: t.Optional[bool] = False
    owner_id: t.Optional[int] = None


class RepoCreate(RepoBase):
    pass


class Repo(DBBase, RepoBase):
    pass

    class Config:
        orm_mode = True


class User(DBBase):
    username: str
    is_active: bool

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
