from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    message: str


class RepoBase(BaseModel):
    name: str
    path: Optional[str] = None
    is_private: Optional[bool] = False
    owner_id: Optional[int] = None


class RepoCreate(RepoBase):
    pass


class Repo(RepoBase):
    id: int

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
